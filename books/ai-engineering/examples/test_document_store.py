import sqlite3
import tempfile
from pathlib import Path
import unittest
from context_budget import Principal
from document_store import Store, Revision, chunks, read_utf8
from vector_search import Vector


def embed(text):
    return Vector('test-space',(1,0))


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.path=str(Path(self.temp.name)/'index.db')
        self.store=Store(self.path,space='test-space',dimension=2)
        self.who=Principal('a','u','s',frozenset({'edu'}))
        self.old=Revision('v1','한도 20만 원','2026-01-01','2026-09-01')
        self.new=Revision('v2','한도 30만 원','2026-09-01')

    def tearDown(self):
        self.store.close()
        self.temp.cleanup()

    def put(self, seq=1, revisions=None, **kw):
        return self.store.replace('a','edu',seq,revisions if revisions is not None else [self.old,self.new],embed,len,**kw)

    def hits(self, day='2026-09-08', who=None):
        return self.store.retrieve(embed('q'),who or self.who,as_of=day)

    def test_intervals_persistence_and_authorization(self):
        self.put()
        self.assertEqual(self.hits(),[])
        self.store.grant('a','edu','u')
        self.assertEqual(self.hits('2026-08-31')[0].text,self.old.text)
        self.assertEqual(self.hits('2026-09-01')[0].text,self.new.text)
        self.assertEqual(self.hits('2025-12-31'),[])
        self.store.close()
        self.store=Store(self.path,space='test-space',dimension=2)
        self.assertEqual(self.hits()[0].text,self.new.text)
        self.store.revoke('a','edu','u')
        self.assertEqual(self.hits(),[])  # 동일한 오래된 Principal도 DB 회수 반영

    def test_replay_stale_and_delete_tombstone(self):
        self.assertEqual(self.put(),'replaced')
        self.assertEqual(self.put(),'unchanged')
        with self.assertRaises(ValueError):
            self.put(revisions=[self.new])
        self.store.grant('a','edu','u')
        self.assertEqual(self.put(2,[]),'deleted')
        with self.assertRaises(ValueError):
            self.put(1)
        self.assertEqual(self.hits(),[])
        self.put(3)
        self.assertEqual(self.hits(),[])  # 복원해도 ACL을 자동 복원하지 않는다

    def test_embedding_failure_keeps_old_snapshot(self):
        self.put()
        self.store.grant('a','edu','u')
        def failing(text):
            raise RuntimeError('embedding unavailable')
        with self.assertRaises(RuntimeError):
            self.store.replace('a','edu',2,[self.new],failing,len)
        self.assertEqual(self.hits()[0].text,self.new.text)
        self.assertEqual(self.store.db.execute('SELECT sequence FROM heads').fetchone()[0],1)

    def test_database_failure_rolls_back_delete(self):
        self.put()
        self.store.grant('a','edu','u')
        self.store.db.execute("CREATE TRIGGER fail_insert BEFORE INSERT ON chunks BEGIN SELECT RAISE(ABORT,'injected'); END")
        with self.assertRaises(sqlite3.IntegrityError):
            self.put(2,[Revision('v3','한도 40만 원','2026-09-01')])
        self.assertEqual(self.hits()[0].text,self.new.text)
        self.assertFalse(self.store.db.in_transaction)

    def test_update_during_embedding_cannot_overwrite_newer(self):
        self.put()
        other=Store(self.path,space='test-space',dimension=2)
        def racing(text):
            other.replace('a','edu',3,[self.new],embed,len)
            return embed(text)
        try:
            with self.assertRaises(ValueError):
                self.store.replace('a','edu',2,[self.new],racing,len)
            self.assertEqual(self.store.db.execute('SELECT sequence FROM heads').fetchone()[0],3)
        finally:
            other.close()

    def test_tenant_user_and_claim_intersection(self):
        self.put(); self.store.grant('a','edu','u')
        for who in (Principal('b','u','s',frozenset({'edu'})),
                    Principal('a','other','s',frozenset({'edu'})),
                    Principal('a','u','s',frozenset())):
            self.assertEqual(self.hits(who=who),[])

    def test_bad_intervals_and_spaces(self):
        for revisions in ([self.new,self.new],
                          [Revision('a','x','2026-01-01'),self.new],
                          [Revision('a','x','2026-01-01','2026-01-01')]):
            with self.assertRaises(ValueError):
                self.put(revisions=revisions)
        with self.assertRaises(ValueError):
            Store(self.path,space='different',dimension=2)
        with self.assertRaises(ValueError):
            self.store.replace('a','edu',1,[self.new],lambda t:Vector('test-space',(1,)),len)

    def test_utf8_input(self):
        path=Path(self.temp.name)/'source.txt'
        path.write_bytes(b'\xef\xbb\xbf'+ '교육비'.encode())
        self.assertEqual(read_utf8(path),'교육비')
        path.write_bytes(b'\xff')
        with self.assertRaises(UnicodeDecodeError):
            read_utf8(path)
        path.write_bytes(b'x'*1000001)
        with self.assertRaises(ValueError):
            read_utf8(path)

    def test_chunk_boundaries_and_normalization(self):
        raw='가나다라마\r\n\r\n바 사 아 자 차 카 타 파 하'
        expected=raw.replace('\r\n','\n')
        result=chunks(raw,len,6)
        for start,end,text in result:
            self.assertEqual(text,expected[start:end])
            self.assertLessEqual(len(text),6)
        self.assertEqual(''.join(t for _,_,t in result),expected)
        self.assertEqual(chunks('가',len,1),[(0,1,'가')])
        with self.assertRaises(ValueError):
            chunks('x',lambda t:2,1)

if __name__=='__main__':
    unittest.main()
