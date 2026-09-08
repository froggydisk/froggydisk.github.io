"""실제 SDK와 HTTP 모의 전송으로 응답 계약을 검증한다. 네트워크 호출 없음."""

import json
import unittest

import httpx2
from openai import OpenAI

from model_client import generate


def response_body(status="completed"):
    return {
        "id": "resp_fixture", "object": "response", "created_at": 0,
        "model": "fixture-model", "status": status, "error": None,
        "incomplete_details": None, "instructions": None, "metadata": {},
        "parallel_tool_calls": True, "temperature": 1, "top_p": 1,
        "tool_choice": "auto", "tools": [],
        "output": [{"id": "msg_fixture", "type": "message", "role": "assistant",
                    "status": "completed", "content": [
                        {"type": "output_text", "text": "분기당 30만 원이다.", "annotations": []}
                    ]}],
        "usage": {"input_tokens": 30, "output_tokens": 8, "total_tokens": 38,
                  "input_tokens_details": {"cached_tokens": 0},
                  "output_tokens_details": {"reasoning_tokens": 0}},
    }


def encode_event(kind, **payload):
    return ("event: " + kind + "\ndata: " +
            json.dumps({"type": kind, "sequence_number": 0, **payload}) + "\n\n").encode()


class BrokenStream(httpx2.SyncByteStream):
    def __iter__(self):
        yield encode_event("response.output_text.delta", delta="임시 답변", item_id="msg_fixture",
                           output_index=0, content_index=0, logprobs=[])
        raise httpx2.ReadError("fixture: interrupted connection")


class ModelClientTests(unittest.TestCase):
    def call(self, handler, *, stream=False):
        calls = []
        def capture(request):
            calls.append(request)
            return handler(request)
        with OpenAI(api_key="not-a-real-key", max_retries=0,
                    http_client=httpx2.Client(transport=httpx2.MockTransport(capture))) as client:
            result = generate(client, "fixture-model", "교육비 한도는?", streaming=stream)
        self.assertEqual(len(calls), 1)
        return result, calls[0]

    def test_completed_response_and_request_contract(self):
        result, request = self.call(lambda _: httpx2.Response(
            200, json=response_body(), headers={"x-request-id": "req_fixture"}))
        self.assertEqual(result.status, "ok")
        self.assertEqual(result.text, "분기당 30만 원이다.")
        self.assertEqual(result.request_id, "req_fixture")
        self.assertEqual(result.input_tokens, 30)
        body = json.loads(request.content)
        self.assertEqual(request.url.path, "/v1/responses")
        self.assertFalse(body["store"])
        self.assertEqual(body["max_output_tokens"], 512)

    def test_incomplete_text_is_not_returned(self):
        result, _ = self.call(lambda _: httpx2.Response(200, json=response_body("incomplete")))
        self.assertEqual(result.status, "incomplete")
        self.assertEqual(result.text, "")

    def test_refusal(self):
        body = response_body()
        body["output"][0]["content"] = [{"type": "refusal", "refusal": "제공할 수 없다"}]
        result, _ = self.call(lambda _: httpx2.Response(200, json=body))
        self.assertEqual(result.status, "refused")

    def test_no_text_is_not_success(self):
        body = response_body(); body["output"] = []
        result, _ = self.call(lambda _: httpx2.Response(200, json=body))
        self.assertEqual(result.status, "unexpected_output")

    def test_tool_request_is_not_executed_or_accepted(self):
        body = response_body()
        body["output"] = [{"type": "function_call", "name": "create_ticket",
                           "call_id": "call_fixture", "arguments": "{}"}]
        result, _ = self.call(lambda _: httpx2.Response(200, json=body))
        self.assertEqual(result.status, "unexpected_output")

    def test_http_errors_are_classified_without_raw_message(self):
        for code, expected in [(400, "bad_request"), (401, "authentication"),
                               (403, "permission"), (429, "rate_or_quota"), (500, "http_error")]:
            with self.subTest(code=code):
                result, _ = self.call(lambda _: httpx2.Response(code, json={
                    "error": {"message": "sensitive fixture text", "type": "test"}}))
                self.assertEqual(result.error_code, expected)
                self.assertNotIn("sensitive", str(result))

    def test_timeout(self):
        def handler(request):
            raise httpx2.ReadTimeout("fixture", request=request)
        result, _ = self.call(handler)
        self.assertEqual(result.error_code, "timeout")

    def test_connection_error(self):
        def handler(request):
            raise httpx2.ConnectError("fixture", request=request)
        result, _ = self.call(handler)
        self.assertEqual(result.error_code, "connection")

    def test_stream_completion(self):
        content = encode_event("response.completed", response=response_body())
        result, _ = self.call(lambda _: httpx2.Response(200, content=content,
                         headers={"content-type": "text/event-stream"}), stream=True)
        self.assertEqual(result.status, "ok")

    def test_stream_without_terminal_event(self):
        content = encode_event("response.output_text.delta", delta="30만 원",
                               item_id="msg_fixture", output_index=0, content_index=0, logprobs=[])
        result, _ = self.call(lambda _: httpx2.Response(200, content=content,
                         headers={"content-type": "text/event-stream"}), stream=True)
        self.assertEqual(result.status, "interrupted")
        self.assertEqual(result.text, "")

    def test_broken_stream(self):
        result, _ = self.call(lambda _: httpx2.Response(200, stream=BrokenStream(),
                         headers={"content-type": "text/event-stream"}), stream=True)
        self.assertEqual(result.status, "interrupted")
        self.assertEqual(result.text, "")

    def test_stream_failed_and_incomplete(self):
        for kind, status in [("response.failed", "upstream_error"),
                             ("response.incomplete", "incomplete")]:
            with self.subTest(kind=kind):
                content = encode_event(kind, response=response_body(kind.split(".")[1]))
                result, _ = self.call(lambda _: httpx2.Response(200, content=content,
                                  headers={"content-type": "text/event-stream"}), stream=True)
                self.assertEqual(result.status, status)
                self.assertEqual(result.text, "")

    def test_usage_missing_remains_unknown(self):
        body = response_body(); body["usage"] = None
        result, _ = self.call(lambda _: httpx2.Response(200, json=body))
        self.assertIsNone(result.input_tokens)

    def test_invalid_json(self):
        result, _ = self.call(lambda _: httpx2.Response(200, content=b"not json",
                                  headers={"content-type": "application/json"}))
        self.assertEqual(result.status, "unexpected_output")


if __name__ == "__main__":
    unittest.main()
