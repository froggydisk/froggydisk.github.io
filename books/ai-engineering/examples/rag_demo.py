"""9장: 실제 E5 검색과 Qwen 생성의 통합 기록. 모든 데이터는 가상이다."""
from dataclasses import asdict
from datetime import datetime, timezone
import argparse
import json
from pathlib import Path
import tempfile
import time
from context_budget import Principal
from document_store import Store, Revision, read_utf8
from embedding_model import Embedder, SPACE
from local_model import LocalModel, MODEL_ID, REVISION
from rag_local_backend import LocalBackend, PROMPT_VERSION
from rag_service import respond


class Recorder(LocalBackend):
    def __init__(self, model, **options):
        super().__init__(model, **options)
        self.calls=[]

    def generate(self,input_text,output_limit):
        count=self.count(input_text)
        start=time.perf_counter()
        result=super().generate(input_text,output_limit)
        assert result.input_tokens==count
        self.calls.append({'input':json.loads(input_text),'counted_tokens':count,
                           'seconds':time.perf_counter()-start,'generation':asdict(result)})
        return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--prompt-version",choices=["rag-local-v1","rag-local-v2"],default="rag-local-v1")
    args=parser.parse_args()
    embedder=Embedder(offline=True)
    backend=Recorder(LocalModel(offline=True),prompt_version=args.prompt_version)
    embed=lambda t:embedder.encode([t],kind='passage')[0]
    count=lambda t:len(embedder.tokenizer('passage: '+t)['input_ids'])
    text=read_utf8(Path(__file__).parent/'fixtures'/'policies'/'edu-v2.txt')
    rows=[]
    with tempfile.TemporaryDirectory() as temp:
        store=Store(str(Path(temp)/'index.db'),space=SPACE,dimension=384)
        try:
            store.replace('hanul','edu',1,[Revision('v2',text,'2026-09-01')],embed,count)
            store.grant('hanul','edu','reader')
            who=Principal('hanul','reader','demo',frozenset({'edu','notice'}))
            for id,question in [('R01','교육비 한도와 신청 순서는?'),
                                ('R02','해외 출장 숙박비 한도는 얼마야?')]:
                result=respond(store,embedder,backend,who,question,as_of='2026-09-08')
                rows.append({'id':id,'question':question,'result':asdict(result)})
            store.replace('hanul','notice',1,[Revision('v1','교육비 한도는 분기당 50만 원이다.','2026-09-01')],embed,count)
            store.grant('hanul','notice','reader')
            result=respond(store,embedder,backend,who,'교육비 한도는 얼마야?',as_of='2026-09-08')
            rows.append({'id':'R03','question':'교육비 한도는 얼마야?','result':asdict(result)})
            store.revoke('hanul','edu','reader'); store.revoke('hanul','notice','reader')
            before=len(backend.calls)
            result=respond(store,embedder,backend,who,'교육비 한도는?',as_of='2026-09-08')
            assert len(backend.calls)==before
            rows.append({'id':'R04','question':'교육비 한도는?','result':asdict(result)})
        finally:
            store.close()
    print(json.dumps({'recorded_at':datetime.now(timezone.utc).isoformat(),
        'generation_model':MODEL_ID,'revision':REVISION,'embedding_space':SPACE,
        'prompt_version':backend.prompt_version,'device':'cpu','dtype':'float32','threads':4,
        'window':4096,'max_new_tokens':512,'do_sample':False,'enable_thinking':False,
        'rows':rows,'model_calls':backend.calls},ensure_ascii=False,indent=2,
        default=lambda x:x.model_dump()))

if __name__=='__main__':
    main()
