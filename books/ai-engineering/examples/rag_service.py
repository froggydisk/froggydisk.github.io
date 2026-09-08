"""9장: 권한 검색 → 문맥 예산 → 생성 → 인용 검증 → 출처 재확인."""
from dataclasses import dataclass, field
from typing import Protocol
from answer_contract import Answer, ContractError, validate_answer
from context_budget import Block, build_context
from model_client import GenerationResult


class Backend(Protocol):
    def count(self, input_text: str) -> int: ...
    def generate(self, input_text: str, output_limit: int) -> GenerationResult: ...


@dataclass(frozen=True)
class RagResult:
    status: str
    answer: Answer | None = None
    sources: list[dict] = field(default_factory=list)
    error_code: str | None = None
    usage: dict = field(default_factory=dict)


def respond(store, embedder, backend: Backend, principal, question, *, as_of,
            k=3, window=4096, output_reserve=512):
    if not isinstance(question,str) or not question.strip() or len(question)>4000:
        return RagResult('invalid_request',error_code='question')
    if type(k) is not int or not 1<=k<=20:
        return RagResult('invalid_request',error_code='k')
    try:
        query=embedder.encode([question],kind='query')[0]
        hits=store.retrieve(query,principal,as_of=as_of,k=k)
    except Exception:
        return RagResult('retrieval_failed',error_code='retrieval_unavailable')
    if not hits:
        return RagResult('insufficient_evidence',answer=Answer(
            status='insufficient_evidence',answer=None,citations=[],clarification=None))
    try:
        verified=store.resolve([h.id for h in hits],principal,as_of=as_of)
        if any(h.id not in verified or verified[h.id]['text']!=h.text for h in hits):
            return RagResult('evidence_changed',error_code='revalidate')
    except Exception:
        return RagResult('evidence_changed',error_code='revalidate_unavailable')
    # 요청 안의 짧은 별칭은 서버에서 실제 청크에 연결한다.
    aliases={f's{i+1}':hit for i,hit in enumerate(hits)}
    blocks=[Block(alias,principal.tenant,'document',hit.text,
                  priority=len(hits)-i,doc_id=hit.doc_id)
            for i,(alias,hit) in enumerate(aliases.items())]
    try:
        plan=build_context(principal,f'[기준일 {as_of}] {question}',blocks,
                           count=backend.count,window=window,output_reserve=output_reserve,
                           count_method='backend-complete-input')
    except Exception:
        return RagResult('context_failed',error_code='context_unavailable')
    if not plan.selected:
        return RagResult('context_failed',error_code='no_evidence_fits')
    evidence={alias:aliases[alias].text for alias in plan.selected}
    selected_ids=[aliases[alias].id for alias in plan.selected]

    def current():
        rows=store.resolve(selected_ids,principal,as_of=as_of)
        if len(rows)!=len(selected_ids):
            return None
        if any(rows[aliases[a].id]['text']!=evidence[a] for a in plan.selected):
            return None
        return rows

    try:
        if current() is None:
            return RagResult('evidence_changed',error_code='revalidate')
    except Exception:
        return RagResult('evidence_changed',error_code='revalidate_unavailable')
    try:
        generation=backend.generate(plan.input_text,plan.output_reserve)
    except Exception:
        return RagResult('generation_failed',error_code='generation_unavailable')
    usage={'input_tokens':generation.input_tokens,'output_tokens':generation.output_tokens}
    if generation.status!='ok':
        return RagResult('generation_failed',error_code=generation.status,usage=usage)
    try:
        answer=validate_answer(generation.text,evidence)
    except ContractError as exc:
        return RagResult('contract_failed',error_code=str(exc),usage=usage)
    try:
        latest=current()
    except Exception:
        return RagResult('evidence_changed',error_code='revalidate_unavailable',usage=usage)
    if latest is None:
        return RagResult('evidence_changed',error_code='revalidate',usage=usage)
    sources=[]
    for citation in answer.citations:
        row=latest[aliases[citation.source_id].id]
        sources.append({'source_id':citation.source_id,'chunk_id':row['id'],
                        'doc_id':row['doc'],'revision':row['revision'],
                        'start':row['start'],'end':row['end'],
                        'quote':citation.quote})
    return RagResult(answer.status,answer,sources,usage=usage)
