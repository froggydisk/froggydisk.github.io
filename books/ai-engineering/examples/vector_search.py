"""7장: 정규화 코사인 전수 검색. 허용 문서만 점수를 계산한다."""
from dataclasses import dataclass
import math
from context_budget import Principal


def unit(values):
    v = tuple(values)
    if not v or any(type(x) not in (int, float) or not math.isfinite(x) for x in v):
        raise ValueError('유한한 숫자로 된 비어 있지 않은 벡터가 필요하다')
    scale = max(abs(x) for x in v)
    if scale == 0:
        raise ValueError('영벡터의 코사인은 정의하지 않는다')
    scaled = tuple(x / scale for x in v)
    norm = math.sqrt(math.fsum(x*x for x in scaled))
    return tuple(x / norm for x in scaled)


def cosine(a, b):
    left, right = unit(a), unit(b)
    if len(left) != len(right):
        raise ValueError('벡터 차원이 다르다')
    return max(-1.0, min(1.0, math.fsum(x*y for x, y in zip(left, right))))


@dataclass(frozen=True)
class Vector:
    space: str
    values: tuple[float, ...]


@dataclass(frozen=True)
class Passage:
    id: str
    tenant: str
    doc_id: str
    text: str
    vector: Vector


@dataclass(frozen=True)
class Hit:
    id: str
    doc_id: str
    text: str
    score: float


def search(query: Vector, passages, principal: Principal, k=3):
    if type(k) is not int or k < 1:
        raise ValueError('k는 양의 정수여야 한다')
    q = unit(query.values)
    rows, seen = [], set()
    for p in passages:
        if p.tenant != principal.tenant or p.doc_id not in principal.readable_docs:
            continue
        if p.id in seen:
            raise ValueError('허용 문서에 중복 청크 식별자가 있다')
        seen.add(p.id)
        if p.vector.space != query.space:
            raise ValueError('임베딩 공간이 다르다. 재색인이 필요하다')
        score = cosine(q, p.vector.values)
        rows.append(Hit(p.id, p.doc_id, p.text, score))
    return sorted(rows, key=lambda x: (-x.score, x.id))[:k]
