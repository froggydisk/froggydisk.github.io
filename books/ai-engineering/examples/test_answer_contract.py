import copy
import json
import unittest

import httpx2
from openai import OpenAI

from answer_contract import ContractError, answer_question, output_config, validate_answer
from context_budget import Block, Principal
from test_model_client import response_body


EVIDENCE = {"edu-v2": "교육비 한도는 분기당 30만 원이다. 구매 전 승인이 필요하다."}
VALID = {"status": "answered", "answer": "분기당 30만 원이다.",
         "citations": [{"source_id": "edu-v2", "quote": "분기당 30만 원이다."}],
         "clarification": None}


class AnswerTests(unittest.TestCase):
    def check(self, obj):return validate_answer(json.dumps(obj, ensure_ascii=False), EVIDENCE)

    def test_valid(self):self.assertEqual(self.check(VALID).status,"answered")

    def test_all_non_answer_states(self):
        for status, question in [("needs_clarification","어떤 신청인가?"),
                                  ("insufficient_evidence",None)]:
            self.assertEqual(self.check(dict(status=status,answer=None,citations=[],
                                            clarification=question)).status,status)

    def test_extra_missing_and_wrong_type(self):
        for change in [dict(extra="허용 안 됨"),dict(answer=300000),dict(status="forbidden")]:
            with self.subTest(change=change), self.assertRaises(ContractError):
                self.check({**VALID,**change})
        obj=copy.deepcopy(VALID);del obj["clarification"]
        with self.assertRaises(ContractError):self.check(obj)

    def test_invalid_state_combinations(self):
        for change in [dict(answer=None),dict(citations=[]),dict(clarification="질문"),
                       dict(status="insufficient_evidence"),dict(answer="   ")]:
            with self.subTest(change=change), self.assertRaises(ContractError):
                self.check({**VALID,**change})

    def test_unknown_source_and_false_quote(self):
        for citation in [dict(source_id="not-sent",quote="분기당 30만 원이다."),
                         dict(source_id="edu-v2",quote="매월 50만 원이다."),
                         dict(source_id="edu-v2",quote=" ")]:
            with self.subTest(citation=citation), self.assertRaises(ContractError):
                self.check({**VALID,"citations":[citation]})

    def test_duplicate_citations(self):
        with self.assertRaisesRegex(ContractError,"duplicate_citation"):
            self.check({**VALID,"citations":VALID["citations"]*2})

    def test_duplicate_json_keys(self):
        with self.assertRaisesRegex(ContractError,"duplicate_key"):
            validate_answer('{"status":"answered","status":"insufficient_evidence"}',EVIDENCE)

    def test_oversized_and_broken_json(self):
        with self.assertRaisesRegex(ContractError,"output_too_large"):
            validate_answer("가"*22000,EVIDENCE)
        with self.assertRaisesRegex(ContractError,"invalid_structure"):
            validate_answer('```json\n{}\n```',EVIDENCE)

    def test_not_a_semantic_entailment_checker(self):
        # 참조·인용이 맞아도 답변 주장이 틀릴 수 있음을 의도적으로 드러낸다.
        result=self.check({**VALID,"answer":"한도는 매월 50만 원이다."})
        self.assertEqual(result.answer,"한도는 매월 50만 원이다.")

    def test_schema_closed_and_all_required(self):
        schema=output_config()["format"]["schema"]
        for node in [schema,*schema["$defs"].values()]:
            self.assertFalse(node["additionalProperties"])
            self.assertEqual(set(node["properties"]),set(node["required"]))

    def run_pipeline(self, answer=VALID, refusal=False):
        sent=[]
        def handler(request):
            body=json.loads(request.content);sent.append(body)
            if request.url.path.endswith('/input_tokens'):
                return httpx2.Response(200,json={"object":"response.input_tokens","input_tokens":100})
            response=response_body()
            content=response["output"][0]["content"][0]
            content["text"]=json.dumps(answer,ensure_ascii=False)
            if refusal:
                response["output"][0]["content"]=[{"type":"refusal","refusal":"거절"}]
            return httpx2.Response(200,json=response)
        p=Principal("hanul","employee-1","session-1",frozenset({"edu"}))
        blocks=[Block("edu-v2","hanul","document",EVIDENCE["edu-v2"],doc_id="edu")]
        with OpenAI(api_key="fixture",max_retries=0,
                    http_client=httpx2.Client(transport=httpx2.MockTransport(handler))) as client:
            result=answer_question(client,"fixture-model",p,"교육비 한도는?",blocks,window=2000)
        return result,sent

    def test_full_pipeline_schema_counted_and_sent(self):
        result,sent=self.run_pipeline()
        self.assertEqual(result.status,"contract_valid")
        for key in ("model","input","instructions","text"):
            self.assertEqual(sent[-2][key],sent[-1][key])
        self.assertTrue(sent[-1]["text"]["format"]["strict"])

    def test_failed_contract_redacts_raw_text(self):
        result,_=self.run_pipeline({**VALID,"citations":[{"source_id":"secret","quote":"SECRET"}]})
        self.assertEqual(result.status,"contract_failed")
        self.assertEqual(result.generation.text,"")
        self.assertNotIn("SECRET",str(result))

    def test_refusal_not_parsed_as_answer(self):
        result,_=self.run_pipeline(refusal=True)
        self.assertEqual(result.status,"generation_failed")
        self.assertEqual(result.generation.status,"refused")


if __name__ == "__main__":unittest.main()
