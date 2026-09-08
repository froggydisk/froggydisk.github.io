"""10장: 동일한 가상 자료·질문에서 의미/키워드/순위 융합을 비교한다."""
from datetime import datetime, timezone
import json
import sqlite3
import time
from context_budget import Principal
from embedding_demo import DOCUMENTS
from embedding_model import Embedder, SPACE
from hybrid_search import keyword_search, reciprocal_rank_fusion
from vector_search import Passage, search

DOCUMENTS=DOCUMENTS+[
    ('ticket-1042','티켓 IT-1042는 노트북 화면 고장이다. 상태는 접수다.'),
    ('ticket-1043','티켓 IT-1043은 계정 로그인 오류다. 상태는 처리 중이다.'),
]
CASES=[
    ('H01','업무 관련 강의를 결제하려는데 얼마까지 지원되나요?',['edu-v2']),
    ('H02','암호가 생각나지 않아서 접속하지 못해요.',['account-v1']),
    ('H03','IT-1042',['ticket-1042']),
    ('H04','IT-1043 상태',['ticket-1043']),
    ('H05','교육비 한도',['edu-v2']),
    ('H06','해외 출장 호텔 숙박비 한도',[]),
]


def main():
    model=Embedder(offline=True)
    vectors=model.encode([t for _,t in DOCUMENTS],kind='passage')
    passages=[Passage(id,'hanul',id,text,v) for (id,text),v in zip(DOCUMENTS,vectors)]
    principal=Principal('hanul','reader','demo',frozenset(id for id,_ in DOCUMENTS))
    rows=[]
    for id,question,relevant in CASES:
        start=time.perf_counter()
        query=model.encode([question],kind='query')[0]
        dense=search(query,passages,principal,k=3)
        dense_time=time.perf_counter()-start
        start=time.perf_counter()
        lexical=keyword_search(question,DOCUMENTS,limit=3)
        lexical_time=time.perf_counter()-start
        start=time.perf_counter()
        fusion=reciprocal_rank_fusion([[h.id for h in dense],[i for i,_ in lexical]],limit=3)
        fusion_time=time.perf_counter()-start
        rows.append({'id':id,'question':question,'relevant':relevant,
            'dense':[(h.id,h.score) for h in dense], 'keyword':lexical,'rrf':fusion,
            'seconds':{'dense_including_query_embedding':dense_time,
                       'keyword_including_index_build':lexical_time,'fusion_only':fusion_time}})
    print(json.dumps({'recorded_at':datetime.now(timezone.utc).isoformat(),
        'embedding_space':SPACE,'sqlite':sqlite3.sqlite_version,
        'documents':DOCUMENTS,'lexical_preprocessing':'digit-hangul-boundary-v1','rrf_constant':60,'candidate_limit':3,
        'rows':rows},ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
