import math
import unittest
from context_budget import Principal
from vector_search import Vector, Passage, cosine, search, unit


class VectorTests(unittest.TestCase):
    def test_geometry(self):
        self.assertAlmostEqual(cosine([1, 0], [3, 0]), 1)
        self.assertAlmostEqual(cosine([1, 0], [0, 1]), 0)
        self.assertAlmostEqual(cosine([1, 0], [-1, 0]), -1)
        self.assertAlmostEqual(cosine([1, 1], [1, 0]), 1 / math.sqrt(2))

    def test_extreme_scale(self):
        self.assertAlmostEqual(cosine([1e308, 1e308], [1e-300, 1e-300]), 1)

    def test_invalid_vectors(self):
        for value in ([], [0, 0], [math.nan], [math.inf], [True], ['1']):
            with self.subTest(value=value), self.assertRaises(ValueError):
                unit(value)
        with self.assertRaises(ValueError):
            cosine([1], [1, 2])

    def test_authorization_before_ranking(self):
        who = Principal('a', 'u', 's', frozenset({'allowed','foreign'}))
        passages = [
            Passage('secret', 'a', 'secret', '비밀', Vector('wrong', (0,))),
            Passage('foreign', 'b', 'foreign', '다른 조직', Vector('wrong', (0,))),
            Passage('ok', 'a', 'allowed', '허용', Vector('v1', (0, 1))),
        ]
        result = search(Vector('v1', (1, 0)), passages, who, k=1)
        self.assertEqual([r.id for r in result], ['ok'])
        self.assertEqual(result[0].score, 0)
        revoked = Principal('a','u','s',frozenset())
        self.assertEqual(search(Vector('v1',(1,0)),passages,revoked), [])

    def test_order_ties_and_k(self):
        who = Principal('a','u','s',frozenset({'d'}))
        passages = [Passage(i,'a','d',i,Vector('v1',v)) for i,v in
                    [('z',(1,0)),('a',(1,0)),('b',(0,1))]]
        self.assertEqual([h.id for h in search(Vector('v1',(1,0)),passages,who,2)], ['a','z'])
        self.assertEqual(len(search(Vector('v1',(1,0)),passages,who,20)), 3)
        for k in (0,-1,True,1.5):
            with self.assertRaises(ValueError):
                search(Vector('v1',(1,0)),passages,who,k)

    def test_space_dimension_and_duplicate_ids(self):
        who = Principal('a','u','s',frozenset({'d'}))
        q = Vector('v1',(1,0))
        for v in (Vector('v2',(1,0)), Vector('v1',(1,))):
            with self.assertRaises(ValueError):
                search(q,[Passage('p','a','d','x',v)],who)
        p = Passage('p','a','d','x',q)
        with self.assertRaises(ValueError):
            search(q,[p,p],who)

if __name__ == '__main__':
    unittest.main()
