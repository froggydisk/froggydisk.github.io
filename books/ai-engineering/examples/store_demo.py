"""8장: 실제 E5 벡터와 임시 SQLite 파일로 문서 생명주기를 재현한다."""
from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
import tempfile
from context_budget import Principal
from document_store import Store, Revision, read_utf8
from embedding_model import Embedder, SPACE, REVISION, MODEL_ID


def main():
    model=Embedder(offline=True)
    count=lambda t:len(model.tokenizer('passage: '+t)['input_ids'])
    embed=lambda t:model.encode([t],kind='passage')[0]
    query=model.encode(['교육비 한도와 승인 절차는?'],kind='query')[0]
    who=Principal('hanul','reader','demo',frozenset({'edu'}))
    source=Path(__file__).parent/'fixtures'/'policies'
    versions=[Revision('v1',read_utf8(source/'edu-v1.txt'),'2026-01-01','2026-09-01'),
              Revision('v2',read_utf8(source/'edu-v2.txt'),'2026-09-01')]
    with tempfile.TemporaryDirectory() as temp:
        path=str(Path(temp)/'index.db')
        store=Store(path,space=SPACE,dimension=384)
        try:
            initial=store.replace('hanul','edu',1,versions,embed,count,limit=80)
            store.grant('hanul','edu','reader')
            old=store.retrieve(query,who,as_of='2026-08-31')
            current=store.retrieve(query,who,as_of='2026-09-08')
            assert old and '20만' in old[0].text
            assert current and '30만' in current[0].text
            store.close()
            store=Store(path,space=SPACE,dimension=384)
            reopened=store.retrieve(query,who,as_of='2026-09-08')
            assert [asdict(x) for x in reopened]==[asdict(x) for x in current]
            store.revoke('hanul','edu','reader')
            revoked=store.retrieve(query,who,as_of='2026-09-08')
            assert revoked==[]
            store.grant('hanul','edu','reader')
            deleted=store.replace('hanul','edu',2,[],embed,count,limit=80)
            try:
                store.replace('hanul','edu',1,versions,embed,count,limit=80)
            except ValueError as e:
                stale_error=str(e)
            else:
                raise AssertionError('오래된 이벤트가 문서를 복원했다')
            assert store.retrieve(query,who,as_of='2026-09-08')==[]
            print(json.dumps({'recorded_at':datetime.now(timezone.utc).isoformat(),
                'sqlite':sqlite3.sqlite_version,'model':MODEL_ID,'revision':REVISION,
                'initial':initial,'before_effective_date':[asdict(x) for x in old],
                'current':[asdict(x) for x in current],'reopened_equal':True,
                'revoked_results':revoked,'delete':deleted,'stale_error':stale_error},
                ensure_ascii=False,indent=2))
        finally:
            store.close()

if __name__=='__main__':
    main()
