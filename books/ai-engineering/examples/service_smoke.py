"""실제 로컬 가중치·파일 DB·HTTP·별도 CLI 프로세스의 연결 확인."""
import json
import os
from pathlib import Path
import secrets
import selectors
import subprocess
import sys
import tempfile
import time
import urllib.request
import urllib.error

ROOT=Path(__file__).parent

def main():
    with tempfile.TemporaryDirectory() as folder:
        command=[sys.executable,str(ROOT/'book_service.py'),'--state',folder]
        def cli(*args):
            run=subprocess.run(command+list(args),capture_output=True,text=True,check=True,timeout=120)
            return json.loads(run.stdout)
        initialized=cli('init')
        prepared=cli('prepare','노트북 점검','화면이 깜박인다.')
        created=cli('confirm',prepared['draft_id'],'--yes')
        replay=cli('confirm',prepared['draft_id'],'--yes')
        assert created['ticket_id']==replay['ticket_id'] and replay['replayed']
        viewed=cli('get',created['ticket_id'])
        token=secrets.token_urlsafe(32)
        env={**os.environ,'BOOK_LOCAL_TOKEN':token}
        runs=[]
        for version in ['rag-local-v2','rag-local-v1']:
            with tempfile.TemporaryFile(mode='w+t') as log:
                process=subprocess.Popen(command+['serve','--port','0','--prompt-version',version],
                                         stdout=subprocess.PIPE,stderr=log,text=True,env=env)
                try:
                    with selectors.DefaultSelector() as selector:
                        selector.register(process.stdout,selectors.EVENT_READ)
                        if not selector.select(60):
                            raise TimeoutError('server_not_ready')
                        ready=json.loads(process.stdout.readline())
                    url=f"http://127.0.0.1:{ready['port']}/ask"
                    def request(data,authorized=True):
                        headers={'Content-Type':'application/json'}
                        if authorized: headers['Authorization']='Bearer '+token
                        req=urllib.request.Request(url,data=json.dumps(data).encode(),headers=headers)
                        start=time.perf_counter()
                        try:
                            with urllib.request.urlopen(req,timeout=60) as response:
                                return dict(http=response.status,body=json.load(response),seconds=time.perf_counter()-start)
                        except urllib.error.HTTPError as exc:
                            return dict(http=exc.code,body=json.load(exc),seconds=time.perf_counter()-start)
                    denied=request({'question':'교육비 한도는?'},False)
                    invalid=request({'question':'교육비 한도는?','tenant':'other'})
                    answer=request({'question':'교육비 한도와 신청 순서는?'})
                    assert denied['http']==401 and invalid['http']==400
                    assert answer['http']==200 and answer['body']['release']==version
                    runs.append(dict(version=version,unauthorized=denied,invalid_fields=invalid,answer=answer))
                finally:
                    process.terminate()
                    try: process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        process.kill();process.wait(timeout=10)
                    process.stdout.close()
                log.seek(0)
                # 모델 진행 출력과 구분해 애플리케이션 JSON 로그만 남긴다.
                events=[]
                for line in log:
                    try: row=json.loads(line)
                    except ValueError: continue
                    if 'trace_id' in row: events.append(row)
                assert all('교육비' not in json.dumps(e,ensure_ascii=False) and token not in json.dumps(e) for e in events)
                runs[-1]['events']=events
        initialized.pop('state')
        print(json.dumps(dict(initialized=initialized,ticket=dict(prepared=prepared,created=created,replay=replay,viewed=viewed),
                              http=runs,scope='real_local_models_loopback_single_user_not_production'),ensure_ascii=False,indent=2))

if __name__=='__main__':main()
