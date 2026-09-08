"""11장: 단일 로컬 데모 주체의 stdio MCP 서버. 승인 도구는 노출하지 않는다."""
import sys
from typing import Any
from mcp.server.fastmcp import FastMCP
from ticket_tools import Actor, Tickets


def main():
    if len(sys.argv)!=2:
        raise SystemExit('임시 티켓 DB 경로를 지정한다')
    tickets=Tickets(sys.argv[1])
    actor=Actor('hanul','demo')  # 호스트가 시작한 단일 사용자 실습 세션
    server=FastMCP('hanul-ticket-demo')

    @server.tool(structured_output=True)
    def prepare_ticket(category:str,title:str,description:str)->dict[str,Any]:
        """가상 IT 티켓의 확인용 초안을 만든다. 실제 등록은 하지 않는다."""
        return tickets.prepare(actor,dict(category=category,title=title,description=description))

    @server.tool(structured_output=True)
    def create_ticket(draft_id:str)->dict[str,Any]:
        """사용자가 확인한 초안만 등록한다. 같은 초안의 재실행은 기존 티켓을 반환한다."""
        return tickets.create(actor,draft_id)

    @server.tool(structured_output=True)
    def get_ticket(ticket_id:str)->dict[str,Any]:
        """현재 데모 사용자의 티켓을 조회한다."""
        return tickets.get(actor,ticket_id)

    try:
        server.run(transport='stdio')
    finally:
        tickets.close()

if __name__=='__main__':
    main()
