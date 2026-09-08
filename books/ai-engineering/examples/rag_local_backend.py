"""9장: 로컬 평문 생성에 JSON을 요청하고 사후 검증한다. 제약 디코딩은 아니다."""
import json
from answer_contract import INSTRUCTIONS, Answer

PROMPT_VERSION='rag-local-v1'
TASK='입력 JSON의 question에 답하라.'
INSTRUCTIONS_RAG=(INSTRUCTIONS+' 문서가 충돌해 결론을 정할 수 없으면 insufficient_evidence로 유보한다. '
    '반드시 JSON 객체 하나만 출력한다. 설명이나 마크다운 코드 블록은 붙이지 않는다. '
    '다음 JSON Schema를 따른다: '+json.dumps(Answer.model_json_schema(),ensure_ascii=False))


INSTRUCTIONS_RAG_V2 = INSTRUCTIONS_RAG + (
    '\n응답은 {로 시작해서 }로 끝난다. 백틱을 쓰지 않는다. 모든 필드를 반드시 쓴다. '
    'clarification이 없으면 null을 쓴다. 예시의 사실은 현재 질문의 근거가 아니다.\n'
    '예시: 자료가 "도서 대출 기간은 14일이다."이고 id가 s1일 때 대출 기간 질문의 출력:\n'
    '{"status":"answered","answer":"대출 기간은 14일이다.",'
    '"citations":[{"source_id":"s1","quote":"도서 대출 기간은 14일이다."}],"clarification":null}\n'
    '같은 자료로 주차 요금을 물으면 출력:\n'
    '{"status":"insufficient_evidence","answer":null,"citations":[],"clarification":null}\n'
    '서로 다른 문서가 같은 조건에 다른 금액을 제시하면 순위로 정답을 고르지 말고 유보한다.'
)


class LocalBackend:
    def __init__(self, model, *, prompt_version="rag-local-v1"):
        self.model=model
        self.prompt_version=prompt_version
        self.instructions=INSTRUCTIONS_RAG if prompt_version=="rag-local-v1" else INSTRUCTIONS_RAG_V2
        if prompt_version not in ("rag-local-v1","rag-local-v2"):
            raise ValueError("알 수 없는 프롬프트 버전")

    def count(self, input_text):
        return self.model.prepare(TASK,instructions=self.instructions,context=input_text)['input_ids'].shape[-1]

    def generate(self, input_text, output_limit):
        return self.model.generate(TASK,instructions=self.instructions,
                                   context=input_text,output_limit=output_limit)
