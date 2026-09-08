"""17–18장: localhost 단일 사용자 RAG 서버와 신뢰된 티켓 관리 CLI.

HTTPServer는 로컬 교육용이다. 실제 외부 배포용 인증/프록시/워커 서버가 아니다.
"""
import argparse
from dataclasses import asdict
from datetime import date
from http.server import BaseHTTPRequestHandler, HTTPServer
import hmac
import json
import os
from pathlib import Path
import sys
import time
from uuid import uuid4

from answer_contract import unique_object
from context_budget import Principal
from document_store import Store, Revision, read_utf8
from ticket_tools import Tickets, Actor

ROOT = Path(__file__).parent
WHO = Principal('hanul','reader','local',frozenset({'edu'}))
ACTOR = Actor('hanul','reader')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--state',type=Path,default=Path('/tmp/hanul-book'))
    sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('init')
    server=sub.add_parser('serve')
    server.add_argument('--port',type=int,default=8765)
    server.add_argument('--prompt-version',choices=['rag-local-v1','rag-local-v2'],default='rag-local-v2')
    prepare=sub.add_parser('prepare')
    prepare.add_argument('title'); prepare.add_argument('description')
    confirm=sub.add_parser('confirm'); confirm.add_argument('draft_id')
    confirm.add_argument('--yes',action='store_true',help='신뢰된 사람이 미리 확인한 초안만 지정한다')
    get=sub.add_parser('get'); get.add_argument('ticket_id')
    args=parser.parse_args()
    args.state.mkdir(parents=True,exist_ok=True,mode=0o700)
    if args.command in {'prepare','confirm','get'}:
        tickets=Tickets(str(args.state/'tickets.db'))
        try:
            if args.command=='prepare':
                result=tickets.prepare(ACTOR,dict(category='equipment',title=args.title,description=args.description))
            elif args.command=='confirm':
                if not args.yes:
                    parser.error('초안 내용을 확인한 뒤 --yes를 명시해야 한다')
                tickets.approve(ACTOR,args.draft_id)
                result=tickets.create(ACTOR,args.draft_id)
            else:
                result=tickets.get(ACTOR,args.ticket_id)
            print(json.dumps(result,ensure_ascii=False))
        finally:
            tickets.close()
        return
    if args.command=='serve':
        token=os.environ.get('BOOK_LOCAL_TOKEN','')
        if len(token)<24 or not token.isascii():
            parser.error('BOOK_LOCAL_TOKEN에 24자 이상의 ASCII 로컬 토큰을 설정한다')
    from embedding_model import Embedder, SPACE
    embedder=Embedder(offline=True)
    store=Store(str(args.state/'index.db'),space=SPACE,dimension=384)
    try:
        if args.command=='init':
            store.replace('hanul','edu',1,[Revision('v2',read_utf8(ROOT/'fixtures/policies/edu-v2.txt'),'2026-09-01')],
                          lambda text:embedder.encode([text],kind='passage')[0],
                          lambda text:len(embedder.tokenizer('passage: '+text)['input_ids']))
            store.grant('hanul','edu','reader')
            tickets=Tickets(str(args.state/'tickets.db'))
            try:
                tickets.grant(ACTOR)
            finally:
                tickets.close()
            print(json.dumps(dict(status='initialized',state=str(args.state))))
            return
        from local_model import LocalModel
        from rag_local_backend import LocalBackend
        from rag_service import respond
        backend=LocalBackend(LocalModel(offline=True),prompt_version=args.prompt_version)
        class Handler(BaseHTTPRequestHandler):
            def log_message(self,*args):
                pass  # 기본 URL/IP 로그 대신 아래 허용 필드만 기록한다.
            def setup(self):
                super().setup()
                self.connection.settimeout(3)
            def reply(self,code,payload):
                raw=json.dumps(payload,ensure_ascii=False,default=lambda x:x.model_dump()).encode()
                self.send_response(code)
                self.send_header('Content-Type','application/json; charset=utf-8')
                self.send_header('Content-Length',str(len(raw)))
                self.send_header('Cache-Control','no-store')
                self.end_headers()
                self.wfile.write(raw)
            def do_POST(self):
                trace=uuid4().hex; started=time.perf_counter(); status='invalid_request'
                try:
                    if self.path!='/ask':
                        self.reply(404,{'status':'not_found'}); return
                    if not hmac.compare_digest(self.headers.get('Authorization','').encode(), ('Bearer '+token).encode()):
                        status='unauthorized'; self.reply(401,{'status':status}); return
                    lengths=self.headers.get_all('Content-Length',[])
                    if self.headers.get('Transfer-Encoding') or len(lengths)!=1:
                        self.reply(400,{'status':status}); return
                    length=int(lengths[0])
                    if not 0<length<=16384:
                        self.reply(413,{'status':'input_too_large'}); return
                    raw=self.rfile.read(length)
                    if len(raw)!=length:
                        raise ValueError('incomplete_body')
                    obj=json.loads(raw,object_pairs_hook=unique_object)
                    if not isinstance(obj,dict) or set(obj)!={'question'}:
                        raise ValueError('invalid_fields')
                    result=respond(store,embedder,backend,WHO,obj['question'],as_of=date.today().isoformat())
                    status=result.status
                    self.reply(200,{'trace_id':trace,'release':args.prompt_version,'result':asdict(result)})
                except (ValueError,UnicodeError,TimeoutError):
                    self.reply(400,{'trace_id':trace,'status':'invalid_request'})
                except (BrokenPipeError,ConnectionResetError):
                    status='client_disconnected'
                finally:
                    print(json.dumps(dict(trace_id=trace,status=status,prompt_version=args.prompt_version,
                                          elapsed_ms=round((time.perf_counter()-started)*1000,2))),file=sys.stderr,flush=True)
        httpd=HTTPServer(('127.0.0.1',args.port),Handler)
        print(json.dumps(dict(status='ready',port=httpd.server_port,prompt=args.prompt_version)),flush=True)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            httpd.server_close()
    finally:
        store.close()


if __name__=='__main__':
    main()
