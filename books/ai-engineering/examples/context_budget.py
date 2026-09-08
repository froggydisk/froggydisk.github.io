"""4장: 권한 검사 뒤 문맥을 조립한다. count는 전체 요청의 토큰 수 함수다."""

from dataclasses import dataclass
from decimal import Decimal
import json
from typing import Callable


@dataclass(frozen=True)
class Principal:
    tenant: str
    user: str
    session: str
    readable_docs: frozenset[str]


@dataclass(frozen=True)
class Block:
    id: str
    tenant: str
    kind: str
    text: str
    priority: int = 0
    doc_id: str | None = None
    user: str | None = None
    session: str | None = None


@dataclass(frozen=True)
class ContextPlan:
    input_text: str
    selected: tuple[str, ...]
    omitted_for_budget: tuple[str, ...]
    input_tokens: int
    output_reserve: int
    count_method: str


def permitted(block: Block, principal: Principal) -> bool:
    if block.tenant != principal.tenant:
        return False
    if block.kind == "document":
        return block.doc_id is not None and block.doc_id in principal.readable_docs
    if block.kind == "history":
        return block.user == principal.user and block.session == principal.session
    return False


def render(question: str, blocks: list[Block]) -> str:
    # JSON escaping preserves data boundaries; it is not a prompt-injection defense.
    return json.dumps({"question": question, "context": [
        {"id": b.id, "kind": b.kind, "text": b.text} for b in blocks
    ]}, ensure_ascii=False, separators=(",", ":"))


def build_context(principal: Principal, question: str, blocks: list[Block], *,
                  count: Callable[[str], int], window: int, output_reserve: int,
                  margin: int = 0, count_method: str) -> ContextPlan:
    if not all((principal.tenant, principal.user, principal.session, question.strip(), count_method)):
        raise ValueError("사용자 범위·질문·계수 방법이 필요하다")
    if any(type(x) is not int or x < 0 for x in (window, output_reserve, margin)):
        raise ValueError("예산은 음수가 아닌 정수여야 한다")
    if window <= output_reserve + margin or output_reserve == 0:
        raise ValueError("입력과 출력 예산이 필요하다")
    allowed = [b for b in blocks if permitted(b, principal)]
    if len({b.id for b in allowed}) != len(allowed):
        raise ValueError("허용된 문맥의 식별자가 중복된다")
    allowed.sort(key=lambda b: (-b.priority, b.id))
    cap = window - output_reserve - margin

    def measured(items):
        text = render(question, items)
        value = count(text)
        if type(value) is not int or value < 0:
            raise ValueError("계수 결과는 음수가 아닌 정수여야 한다")
        return text, value

    selected = []
    omitted = []
    text, size = measured(selected)
    if size > cap:
        raise ValueError("질문과 필수 지시문이 입력 예산을 초과한다")
    for block in allowed:
        candidate, candidate_size = measured(selected + [block])
        if candidate_size <= cap:
            selected.append(block)
            text, size = candidate, candidate_size
        else:
            omitted.append(block.id)
    return ContextPlan(text, tuple(b.id for b in selected), tuple(omitted), size,
                       output_reserve, count_method)


def provider_counter(client, model: str, instructions: str,
                     text_config: dict | None = None) -> Callable[[str], int]:
    """호출마다 공식 입력 계수 API에 완성된 지시문과 입력을 전달한다."""
    def count(text):
        options = {"text": text_config} if text_config is not None else {}
        result = client.responses.input_tokens.count(
            model=model, instructions=instructions, input=text, **options)
        return result.input_tokens
    return count


def token_cost(input_tokens: int | None, output_tokens: int | None,
               cached_tokens: int | None, *, input_rate: Decimal,
               cached_rate: Decimal, output_rate: Decimal) -> Decimal | None:
    """같은 통화의 백만 토큰당 단가. 이 세 항목 외 요금은 별도로 계산한다."""
    for rate in (input_rate, cached_rate, output_rate):
        if not rate.is_finite() or rate < 0:
            raise ValueError("단가는 유한한 음수 아닌 값이어야 한다")
    for value in (input_tokens, output_tokens, cached_tokens):
        if value is not None and (type(value) is not int or value < 0):
            raise ValueError("사용량은 음수가 아닌 정수여야 한다")
    if any(x is None for x in (input_tokens, output_tokens, cached_tokens)):
        return None
    if cached_tokens > input_tokens:
        raise ValueError("캐시 사용량은 전체 입력을 넘을 수 없다")
    return (Decimal(input_tokens - cached_tokens) * input_rate
            + Decimal(cached_tokens) * cached_rate
            + Decimal(output_tokens) * output_rate) / Decimal(1_000_000)
