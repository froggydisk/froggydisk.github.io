"""10장: 허용된 후보에서 FTS5 키워드 검색과 순위 융합을 비교한다."""
import re
import sqlite3



def lexical_text(text):
    # 한국어 조사 앞의 숫자를 분리한다. 형태소 분석이나 동의어 처리는 아니다.
    return re.sub(r'(?<=[0-9])(?=[가-힣])|(?<=[가-힣])(?=[0-9])', ' ', text)


def keyword_search(question, documents, *, limit=10):
    """documents는 호출자가 권한·시행일을 검사한 (id,text) 목록이다.
    실습에서는 매번 메모리 색인을 만들므로 운영 지연 기준선으로 쓰지 않는다.
    """
    if type(limit) is not int or limit<1:
        raise ValueError('limit는 양의 정수여야 한다')
    terms=list(dict.fromkeys(re.findall(r'[A-Za-z]+-\d+|[^\W_]+',lexical_text(question.lower()))))
    if not terms:
        return []
    if len(terms)>64:
        raise ValueError('질의 항목은 64개 이하여야 한다')
    documents=list(documents)
    if len({id for id,_ in documents})!=len(documents):
        raise ValueError('문서 식별자가 중복된다')
    expression=' OR '.join('"'+term.replace('"','""')+'"' for term in terms)
    db=sqlite3.connect(':memory:')
    try:
        db.execute('CREATE VIRTUAL TABLE corpus USING fts5(id UNINDEXED,text,tokenize="unicode61")')
        db.executemany('INSERT INTO corpus(id,text) VALUES(?,?)',[(id,lexical_text(text)) for id,text in documents])
        # FTS5 bm25는 작은 값이 먼저다. 코사인의 정렬 방향과 다르다.
        return [(id,score) for id,score in db.execute(
            'SELECT id,bm25(corpus) FROM corpus WHERE corpus MATCH ? ORDER BY bm25(corpus),id LIMIT ?',
            (expression,limit))]
    finally:
        db.close()


def reciprocal_rank_fusion(rankings, *, constant=60, limit=10):
    if type(constant) is not int or constant<0 or type(limit) is not int or limit<1:
        raise ValueError('상수는 음수가 아닌 정수, limit는 양의 정수여야 한다')
    scores={}
    for ranking in rankings:
        ranking=list(ranking)
        if len(set(ranking))!=len(ranking):
            raise ValueError('한 순위 목록에 같은 항목이 반복된다')
        for rank,id in enumerate(ranking,start=1):
            scores[id]=scores.get(id,0.0)+1/(constant+rank)
    return sorted(scores.items(),key=lambda row:(-row[1],row[0]))[:limit]
