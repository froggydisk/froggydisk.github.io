"""12장: 고정된 대역 계획기로 루프 제어를 시연한다. 실제 LLM 추론은 아니다."""
from dataclasses import asdict
import json
from pathlib import Path
import tempfile
from agent_loop import run
from ticket_tools import Actor, Tickets


def main():
    with tempfile.TemporaryDirectory() as temp:
        store=Tickets(str(Path(temp)/'tickets.db'))
        actor=Actor('hanul','demo');store.grant(actor)
        tools={'prepare_ticket':lambda **kw:store.prepare(actor,kw),
               'get_ticket':lambda ticket_id:store.get(actor,ticket_id)}
        try:
            proposal={'kind':'prepare_ticket','arguments':{'category':'equipment',
                      'title':'화면 고장','description':'가상 노트북의 화면이 켜지지 않는다.'}}
            planner=lambda q,o:json.dumps(proposal,ensure_ascii=False)
            draft=run('화면 고장을 접수해 줘',planner,tools)
            assert draft.status=='awaiting_confirmation'
            assert store.db.execute('SELECT count(*) FROM tickets').fetchone()[0]==0
            # 신뢰된 호스트의 확인 이벤트를 테스트가 재현한다.
            store.approve(actor,draft.result['draft_id'])
            created=store.create(actor,draft.result['draft_id'])
            def reader(question,observations):
                return json.dumps({'kind':'finish','arguments':{}} if observations else
                    {'kind':'get_ticket','arguments':{'ticket_id':created['ticket_id']}})
            read=run('상태를 확인해 줘',reader,tools)
            repeated=run('상태를 확인해 줘',lambda q,o:reader(q,[]),tools)
            limited=run('접수해 줘',planner,tools,max_units=1)
            assert read.status=='completed' and read.result['status']=='received'
            assert repeated.status=='repeated_action' and limited.status=='budget'
            print(json.dumps({'planner':'대역 규칙 함수; 모델 추론 아님',
                'confirmation':'테스트 픽스처','draft':asdict(draft),'read':asdict(read),
                'repeated':asdict(repeated),'budget':asdict(limited)},ensure_ascii=False,indent=2))
        finally:
            store.close()

if __name__=='__main__':
    main()
