"""7장: 가상 문서의 실제 임베딩·전수 검색 기록."""
from dataclasses import asdict
from datetime import datetime, timezone
from importlib.metadata import version
import argparse
import json
import platform
import time
from context_budget import Principal
from embedding_model import Embedder, MODEL_ID, REVISION, SPACE
from vector_search import Passage, search

DOCUMENTS = [
    ('edu-v2', '직원 교육비 한도는 분기당 30만 원이다. 구매 전에 팀장의 승인을 받고 지원 포털에서 신청한다.'),
    ('leave-v1', '연차 휴가는 근태 시스템에서 신청한다. 팀장의 승인을 받아야 한다.'),
    ('travel-v1', '국내 출장 교통비는 영수증을 첨부해 비용 정산 시스템에서 신청한다.'),
    ('account-v1', '계정 비밀번호를 잊었다면 로그인 화면의 비밀번호 재설정을 선택한다.'),
    ('equipment-v1', '노트북 고장은 IT 지원 티켓으로 접수한다. 자산 번호와 증상을 함께 적는다.'),
]
QUESTIONS = [
    ('E01', '업무 관련 강의를 결제하려는데 얼마까지 지원되나요?', ['edu-v2']),
    ('E02', '휴가를 쓰려면 어디서 허락받아야 하나요?', ['leave-v1']),
    ('E03', '로그인이 안 돼요. 암호를 기억하지 못하겠어요.', ['account-v1']),
    ('E04', '교육비는 팀장 승인 없이 먼저 결제해도 되나요?', ['edu-v2']),
    ('E05', '해외 출장 호텔 숙박비 한도는 얼마인가요?', []),
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--offline', action='store_true')
    args = parser.parse_args()
    start = time.perf_counter()
    model = Embedder(offline=args.offline)
    loaded = time.perf_counter()
    vectors = model.encode([t for _, t in DOCUMENTS], kind='passage')
    passages = [Passage(i, 'hanul', i, t, v) for (i, t), v in zip(DOCUMENTS, vectors)]
    indexed = time.perf_counter()
    principal = Principal('hanul', 'reader', 'demo', frozenset(i for i, _ in DOCUMENTS))
    rows = []
    for id, question, relevant in QUESTIONS:
        started = time.perf_counter()
        query = model.encode([question], kind='query')[0]
        encoded_at = time.perf_counter()
        hits = search(query, passages, principal, k=3)
        rows.append({'id':id, 'question':question, 'relevant':relevant,
                     'embedding_seconds':encoded_at-started,
                     'search_seconds':time.perf_counter()-encoded_at,
                     'hits':[asdict(h) for h in hits]})
    print(json.dumps({'recorded_at':datetime.now(timezone.utc).isoformat(),
        'model':MODEL_ID, 'revision':REVISION, 'space':SPACE, 'dimension':len(vectors[0].values),
        'platform':platform.platform(), 'python':platform.python_version(),
        'packages':{p:version(p) for p in ('torch','transformers','huggingface-hub')},
        'device':'cpu','dtype':'float32','threads':4,'offline':args.offline,
        'load_seconds':loaded-start,'document_embedding_seconds':indexed-loaded,
        'documents':[{'id':i,'text':t} for i,t in DOCUMENTS], 'rows':rows}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
