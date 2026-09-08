"""11장: 실제 별도 프로세스 MCP 연결. 확인 이벤트는 가상 픽스처로 주입한다."""
import asyncio
from datetime import datetime, timezone
from importlib.metadata import version
import json
from pathlib import Path
import sys
import tempfile
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from ticket_tools import Tickets, Actor


async def run():
    with tempfile.TemporaryDirectory() as temp:
        path=str(Path(temp)/'tickets.db')
        actor=Actor('hanul','demo')
        host=Tickets(path)
        host.grant(actor)
        try:
            params=StdioServerParameters(command=sys.executable,
                args=[str(Path(__file__).with_name('mcp_ticket_server.py')),path])
            async with stdio_client(params) as (read,write):
                async with ClientSession(read,write) as session:
                    initialized=await session.initialize()
                    listed=await session.list_tools()
                    names=[t.name for t in listed.tools]
                    assert set(names)=={'prepare_ticket','create_ticket','get_ticket'}
                    prepared=await session.call_tool('prepare_ticket',{
                        'category':'equipment','title':'화면이 켜지지 않음','description':'가상 자산 DEMO-01의 화면 고장'})
                    assert not prepared.isError
                    draft=prepared.structuredContent['draft_id']
                    denied=await session.call_tool('create_ticket',{'draft_id':draft})
                    assert denied.isError
                    # 실제 UI 승인 아님: 테스트가 명시적 확인 이벤트를 재현한다.
                    host.approve(actor,draft)
                    first=await session.call_tool('create_ticket',{'draft_id':draft})
                    again=await session.call_tool('create_ticket',{'draft_id':draft})
                    assert not first.isError and not again.isError
                    a,b=first.structuredContent,again.structuredContent
                    assert a['ticket_id']==b['ticket_id'] and b['replayed']
                    fetched=await session.call_tool('get_ticket',{'ticket_id':a['ticket_id']})
                    assert not fetched.isError and fetched.structuredContent['status']=='received'
                    host.revoke(actor)
                    revoked=await session.call_tool('get_ticket',{'ticket_id':a['ticket_id']})
                    assert revoked.isError
                    count=host.db.execute('SELECT count(*) FROM tickets').fetchone()[0]
                    assert count==1
                    print(json.dumps({'recorded_at':datetime.now(timezone.utc).isoformat(),
                        'mcp_sdk':version('mcp'),'protocol':initialized.protocolVersion,
                        'tools':names,'confirmation_source':'테스트 픽스처; 실제 사용자 확인 아님',
                        'unapproved_is_error':denied.isError,'created':a,'replayed':b,
                        'fetched':fetched.structuredContent,'revoked_is_error':revoked.isError,
                        'ticket_count':count},ensure_ascii=False,indent=2))
        finally:
            host.close()

if __name__=='__main__':
    asyncio.run(run())
