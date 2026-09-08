"""네트워크 없는 4장 시연. 길이 단위는 문자이며 실제 모델 토큰 수가 아니다."""

from dataclasses import asdict
from decimal import Decimal
import json

from context_budget import Block, Principal, build_context, token_cost


def main():
    principal = Principal("hanul", "employee-1", "session-1", frozenset({"edu"}))
    blocks = [
        Block("edu-v2", "hanul", "document", "교육비 한도는 분기당 30만 원이다.",
              priority=10, doc_id="edu"),
        Block("other-company", "other", "document", "타 조직의 비공개 자료", doc_id="edu"),
        Block("other-session", "hanul", "history", "다른 대화의 내용",
              user="employee-1", session="session-2"),
        Block("long-history", "hanul", "history", "오래된 대화 " * 100,
              user="employee-1", session="session-1"),
    ]
    plan = build_context(principal, "교육비 한도는?", blocks, count=len,
                         window=500, output_reserve=100, margin=20,
                         count_method="demo-character-count-not-model-tokens")
    print(json.dumps(asdict(plan), ensure_ascii=False, indent=2))
    cost = token_cost(1000, 200, 400, input_rate=Decimal("2"),
                      cached_rate=Decimal("0.5"), output_rate=Decimal("8"))
    print("가상 사용량·가상 단가에 따른 비용:", cost, "통화 단위")


if __name__ == "__main__":
    main()
