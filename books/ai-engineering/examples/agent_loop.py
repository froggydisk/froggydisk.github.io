"""12장: 단일 요청의 제한된 도구 선택 루프. 비용 단위는 가상 정책 크레딧이다."""
from dataclasses import dataclass, field
import json
import time
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field
from ticket_tools import TicketInput
from answer_contract import unique_object


class Action(BaseModel):
    model_config=ConfigDict(extra='forbid',strict=True)
    kind: Literal['get_ticket','prepare_ticket','finish']
    arguments: dict


class Lookup(BaseModel):
    model_config=ConfigDict(extra='forbid',strict=True)
    ticket_id: str=Field(pattern=r'^[0-9a-f]{32}$')


class Prepared(BaseModel):
    model_config=ConfigDict(extra='forbid',strict=True)
    draft_id: str=Field(pattern=r'^[0-9a-f]{32}$')
    preview: TicketInput
    status: Literal['awaiting_confirmation']


class TicketView(TicketInput):
    ticket_id: str=Field(pattern=r'^[0-9a-f]{32}$')
    status: Literal['received']


@dataclass(frozen=True)
class RunResult:
    status: str
    steps: int
    units: int
    events: list[dict]=field(default_factory=list)
    result: dict | None=None


def run(question, planner, tools, *, max_steps=4, max_units=12,
        timeout_seconds=30, clock=time.monotonic):
    """planner(question, observations)는 JSON 문자열을 반환한다.
    동기 호출을 강제로 취소하지 않는다. 종료 후 마감 초과를 검사한다.
    """
    if not isinstance(question,str) or not question.strip() or len(question)>4000:
        raise ValueError('질문이 필요하다')
    if any(type(x) is not int or x<1 for x in (max_steps,max_units)):
        raise ValueError('단계와 예산은 양의 정수여야 한다')
    if type(timeout_seconds) not in (int,float) or not 0<timeout_seconds<=300:
        raise ValueError('시간 한도는 0초 초과 300초 이하여야 한다')
    deadline=clock()+timeout_seconds
    events=[]; observations=[]; seen=set(); units=0
    def stopped(status,step,result=None):
        return RunResult(status,step,units,events.copy(),result)
    for step in range(1,max_steps+1):
        if clock()>=deadline:
            return stopped('deadline',step-1)
        if units+1>max_units:
            return stopped('budget',step-1)
        units+=1
        try:
            raw=planner(question,json.loads(json.dumps(observations)))
            if not isinstance(raw,str) or len(raw.encode())>16384:
                raise ValueError('planner output too large')
            action=Action.model_validate(json.loads(raw,object_pairs_hook=unique_object),strict=True)
        except Exception:
            events.append({'step':step,'stage':'plan','status':'invalid'})
            return stopped('planning_failed',step)
        if clock()>=deadline:
            return stopped('deadline',step)
        if action.kind=='finish':
            if action.arguments:
                return stopped('planning_failed',step)
            return stopped('completed' if observations else 'no_action',step,
                           observations[-1]['result'] if observations else None)
        try:
            schema=Lookup if action.kind=='get_ticket' else TicketInput
            arguments=schema.model_validate(action.arguments,strict=True).model_dump()
            tool=tools[action.kind]
        except Exception:
            return stopped('invalid_action',step)
        fingerprint=json.dumps([action.kind,arguments],sort_keys=True,ensure_ascii=False)
        if fingerprint in seen:
            return stopped('repeated_action',step)
        if units+2>max_units:
            return stopped('budget',step)
        seen.add(fingerprint);units+=2
        events.append({'step':step,'stage':'tool','tool':action.kind,'status':'started'})
        try:
            result=tool(**arguments)
            if not isinstance(result,dict) or len(json.dumps(result).encode())>65536:
                raise ValueError('invalid tool result')
            result=(Prepared if action.kind=='prepare_ticket' else TicketView).model_validate(result,strict=True).model_dump()
        except Exception:
            events.append({'step':step,'stage':'tool','tool':action.kind,'status':'unknown'})
            return stopped('execution_unknown',step)
        if clock()>=deadline:
            events.append({'step':step,'stage':'tool','tool':action.kind,'status':'late'})
            return stopped('execution_unknown',step)
        observations.append({'tool':action.kind,'result':result})
        events.append({'step':step,'stage':'tool','tool':action.kind,'status':'returned'})
        if action.kind=='prepare_ticket':
            return stopped('awaiting_confirmation',step,result)
    return stopped('step_limit',max_steps)
