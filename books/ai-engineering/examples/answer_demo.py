"""5장 로컬 검증 시연. 문자열은 저자가 작성한 가상 모델 출력이다."""
import json
from answer_contract import ContractError, validate_answer


def main():
    evidence={"edu-v2":"교육비 한도는 분기당 30만 원이다."}
    base={"status":"answered","answer":"분기당 30만 원이다.",
          "citations":[{"source_id":"edu-v2","quote":"분기당 30만 원이다."}],
          "clarification":None}
    for label,changes in [
        ("정상 계약",{}),
        ("출처 조작",{"citations":[{"source_id":"unknown","quote":"30만 원"}]}),
        ("의미 오류는 별도 평가 필요",{"answer":"매월 50만 원이다."}),
    ]:
        try:
            answer=validate_answer(json.dumps({**base,**changes},ensure_ascii=False),evidence)
            print(label,": contract_valid /",answer.answer)
        except ContractError as exc:
            print(label,": contract_failed /",str(exc))


if __name__ == "__main__":main()
