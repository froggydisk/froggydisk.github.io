import unittest
from hybrid_search import keyword_search, reciprocal_rank_fusion


class HybridTests(unittest.TestCase):
    def test_identifier_and_no_match(self):
        docs=[('a','티켓 IT-1042는 노트북 수리 요청이다.'),('b','티켓 IT-1043은 계정 요청이다.')]
        self.assertEqual(keyword_search('IT-1042',docs)[0][0],'a')
        self.assertEqual(keyword_search('없는단어',docs),[])
        self.assertEqual(keyword_search('***',docs),[])

    def test_query_is_literal_terms(self):
        docs=[('a','OR 연산자'),('b','휴가 신청')]
        self.assertEqual([id for id,_ in keyword_search('OR',docs)],['a'])
        keyword_search('" OR * NOT (',docs)  # FTS 질의 문법으로 직접 실행하지 않는다

    def test_rrf_arithmetic_and_empty(self):
        result=reciprocal_rank_fusion([['a','b'],['b','c']],constant=0)
        self.assertEqual([id for id,_ in result],['b','a','c'])
        self.assertEqual(result[0][1],1.5)
        self.assertEqual(reciprocal_rank_fusion([[],[]]),[])
        self.assertEqual(reciprocal_rank_fusion([['z'],['a']],limit=1)[0][0],'a')

    def test_invalid_and_duplicates(self):
        with self.assertRaises(ValueError):
            reciprocal_rank_fusion([['a','a']])
        with self.assertRaises(ValueError):
            reciprocal_rank_fusion([['a']],constant=-1)
        with self.assertRaises(ValueError):
            keyword_search('q',[('a','x'),('a','y')])

if __name__=='__main__':
    unittest.main()
