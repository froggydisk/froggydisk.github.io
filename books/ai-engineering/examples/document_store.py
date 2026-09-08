"""8장: 문서 단위 스냅샷 교체와 최신 ACL을 사용하는 SQLite 전수 검색."""
from dataclasses import dataclass, asdict
from datetime import date
import hashlib
import json
import sqlite3
import unicodedata
from context_budget import Principal
from vector_search import Passage, Vector, search, unit


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':')).encode()).hexdigest()


@dataclass(frozen=True)
class Revision:
    id: str
    text: str
    valid_from: str
    valid_until: str | None = None



def read_utf8(path):
    """실습의 입력 형식은 UTF-8 텍스트다. 파일 크기와 디코딩을 검증한다."""
    with open(path, 'rb') as stream:
        raw=stream.read(1000001)
    if len(raw)>1000000:
        raise ValueError('실습 입력 파일은 1MB 이하여야 한다')
    return raw.decode('utf-8-sig')


def iso_day(value):
    parsed = date.fromisoformat(value)
    if parsed.isoformat() != value:
        raise ValueError('날짜는 YYYY-MM-DD 형식이어야 한다')
    return value


def chunks(text, count, limit=480):
    """정규화 원문의 문자 구간을 보존한다. 겹침 없이 분할한다."""
    if type(limit) is not int or limit < 1:
        raise ValueError('양의 토큰 예산이 필요하다')
    text = unicodedata.normalize('NFC', text.replace('\r\n','\n').replace('\r','\n'))
    if not text.strip() or len(text) > 100000:
        raise ValueError('원문은 비어 있지 않고 100000자 이하여야 한다')
    pending = [(0,len(text))]
    result = []
    while pending:
        start,end = pending.pop()
        part = text[start:end]
        size = count(part)
        if type(size) is not int or size < 0:
            raise ValueError('토큰 계수 오류')
        if size <= limit:
            if part.strip():
                result.append((start,end,part))
            continue
        if end-start <= 1:
            raise ValueError('한 문자도 토큰 예산에 들어가지 않는다')
        middle = (start+end)//2
        # 중앙 가까운 문단 경계를 우선한다. 없으면 문자 경계로 나눈다.
        split = text.rfind('\n\n', start+(end-start)//4, middle+1)
        middle = split+2 if split >= 0 and split+2 < end else middle
        pending.extend([(middle,end),(start,middle)])
    return result


class Store:
    def __init__(self, path, *, space, dimension):
        if not space or type(dimension) is not int or dimension < 1:
            raise ValueError('공간과 차원이 필요하다')
        self.space, self.dimension = space, dimension
        self.db = sqlite3.connect(path, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS config (singleton INTEGER PRIMARY KEY CHECK(singleton=1), space TEXT, dimension INTEGER);
        CREATE TABLE IF NOT EXISTS heads (tenant TEXT, doc TEXT, sequence INTEGER, fingerprint TEXT, deleted INTEGER, PRIMARY KEY(tenant,doc));
        CREATE TABLE IF NOT EXISTS chunks (tenant TEXT, doc TEXT, revision TEXT, id TEXT, start INTEGER, end INTEGER, text TEXT, valid_from TEXT, valid_until TEXT, vector TEXT, PRIMARY KEY(tenant,doc,id));
        CREATE TABLE IF NOT EXISTS acl (tenant TEXT, doc TEXT, user TEXT, PRIMARY KEY(tenant,doc,user));
        ''')
        self.db.execute('INSERT OR IGNORE INTO config VALUES(1,?,?)',(space,dimension))
        row=self.db.execute('SELECT space,dimension FROM config').fetchone()
        if tuple(row) != (space,dimension):
            self.db.close()
            raise ValueError('저장소 공간 또는 차원이 다르다')

    def close(self):
        self.db.close()

    def replace(self, tenant, doc, sequence, revisions, embed, count, *, limit=480):
        """신뢰된 수집기가 보내는 문서 전체 스냅샷. 삭제는 빈 revisions다."""
        if not tenant or not doc or type(sequence) is not int or sequence < 1:
            raise ValueError('조직·문서·양의 소스 순번이 필요하다')
        revisions = sorted(revisions, key=lambda r:r.valid_from)
        seen=set()
        for i,r in enumerate(revisions):
            iso_day(r.valid_from)
            if not r.id or r.id in seen:
                raise ValueError('리비전 식별자 중복 또는 누락')
            seen.add(r.id)
            if r.valid_until is not None and iso_day(r.valid_until) <= r.valid_from:
                raise ValueError('시행 구간이 비어 있거나 뒤집혔다')
            if i and (revisions[i-1].valid_until is None or revisions[i-1].valid_until > r.valid_from):
                raise ValueError('시행 구간이 겹친다')
        fingerprint=digest({'revisions':[asdict(r) for r in revisions],
                            'space':self.space,'chunker':'nfc-bisect-v1','limit':limit})
        rows=[]
        for revision in revisions:
            for start,end,text in chunks(revision.text,count,limit):
                values=embed(text)
                if values.space != self.space or len(values.values) != self.dimension:
                    raise ValueError('임베딩 공간·차원 불일치')
                vector=unit(values.values)
                id=digest([tenant,doc,revision.id,start,end,text,fingerprint])
                rows.append((tenant,doc,revision.id,id,start,end,text,
                             revision.valid_from,revision.valid_until,json.dumps(vector)))
        self.db.execute('BEGIN IMMEDIATE')
        try:
            head=self.db.execute('SELECT * FROM heads WHERE tenant=? AND doc=?',(tenant,doc)).fetchone()
            if head and sequence <= head['sequence']:
                if sequence == head['sequence'] and fingerprint == head['fingerprint']:
                    self.db.execute('ROLLBACK')
                    return 'unchanged'
                raise ValueError('오래된 이벤트 또는 같은 순번의 다른 내용')
            self.db.execute('DELETE FROM chunks WHERE tenant=? AND doc=?',(tenant,doc))
            self.db.executemany('INSERT INTO chunks VALUES(?,?,?,?,?,?,?,?,?,?)',rows)
            self.db.execute('INSERT INTO heads VALUES(?,?,?,?,?) ON CONFLICT(tenant,doc) DO UPDATE SET sequence=excluded.sequence,fingerprint=excluded.fingerprint,deleted=excluded.deleted',
                            (tenant,doc,sequence,fingerprint,int(not revisions)))
            if not revisions:
                self.db.execute('DELETE FROM acl WHERE tenant=? AND doc=?',(tenant,doc))
            self.db.execute('COMMIT')
            return 'deleted' if not revisions else 'replaced'
        except BaseException:
            if self.db.in_transaction:
                self.db.execute('ROLLBACK')
            raise

    def grant(self, tenant, doc, user):
        cursor=self.db.execute('INSERT OR IGNORE INTO acl SELECT tenant,doc,? FROM heads WHERE tenant=? AND doc=? AND deleted=0',
                               (user,tenant,doc))
        if not cursor.rowcount and not self.db.execute('SELECT 1 FROM acl WHERE tenant=? AND doc=? AND user=?', (tenant,doc,user)).fetchone():
            raise ValueError('존재하는 문서만 권한을 부여할 수 있다')

    def revoke(self, tenant, doc, user):
        self.db.execute('DELETE FROM acl WHERE tenant=? AND doc=? AND user=?',(tenant,doc,user))

    def retrieve(self, query, principal, *, as_of, k=3):
        iso_day(as_of)
        if query.space != self.space or len(query.values) != self.dimension:
            raise ValueError('질문의 임베딩 공간·차원이 다르다')
        rows=self.db.execute('''SELECT c.* FROM chunks c JOIN acl a
            ON c.tenant=a.tenant AND c.doc=a.doc
            WHERE c.tenant=? AND a.user=? AND c.valid_from<=?
            AND (c.valid_until IS NULL OR ?<c.valid_until)''',
            (principal.tenant,principal.user,as_of,as_of)).fetchall()
        passages=[Passage(r['id'],r['tenant'],r['doc'],r['text'],Vector(self.space,tuple(json.loads(r['vector']))))
                  for r in rows if r['doc'] in principal.readable_docs]
        return search(query,passages,principal,k)

    def resolve(self, ids, principal, *, as_of):
        """선택 청크의 현재 권한·시행일·출처를 한 SQL 조회로 다시 확인한다."""
        iso_day(as_of)
        if not ids:
            return {}
        if len(ids)>20:
            raise ValueError('재검사 청크는 20개 이하여야 한다')
        slots=','.join('?' for _ in ids)
        rows=self.db.execute(f"""SELECT c.id,c.doc,c.revision,c.start,c.end,c.text,c.valid_from,c.valid_until
            FROM chunks c JOIN acl a ON c.tenant=a.tenant AND c.doc=a.doc
            WHERE c.tenant=? AND a.user=? AND c.id IN ({slots}) AND c.valid_from<=?
            AND (c.valid_until IS NULL OR ?<c.valid_until)""",
            (principal.tenant,principal.user,*ids,as_of,as_of)).fetchall()
        return {r['id']:dict(r) for r in rows if r['doc'] in principal.readable_docs}
