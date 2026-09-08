import json
from pathlib import Path
import tempfile
import unittest
from context_budget import Principal
from document_store import Store, Revision
from model_client import GenerationResult
from rag_service import respond
from vector_search import Vector


class Embeddings:
    def encode(self,texts,kind):
        return [Vector('test',(1,0)) for _ in texts]


class Backend:
    def __init__(self):
        self.calls=[]
        self.before_count=lambda:None
        self.after_generate=lambda:None
        self.transform=lambda x:x
        self.count_fn=lambda text:10

    def count(self,text):
        self.before_count()
        return self.count_fn(text)

    def generate(self,text,output_limit):
        self.calls.append(text)
        first=json.loads(text)['context'][0]
        raw={'status':'answered','answer':'교육비는 30만 원이다.',
             'citations':[{'source_id':first['id'],'quote':first['text']}],'clarification':None}
        result=self.transform(raw)
        self.after_generate()
        return GenerationResult('ok',json.dumps(result,ensure_ascii=False),input_tokens=10,output_tokens=10)


class RagTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.store=Store(str(Path(self.temp.name)/'db'),space='test',dimension=2)
        self.emb=Embeddings(); self.backend=Backend()
        self.who=Principal('a','u','s',frozenset({'edu','other'}))
        self.store.replace('a','edu',1,[Revision('v2','교육비는 30만 원이다.','2026-09-01')],
                           lambda t:Vector('test',(1,0)),len)
        self.store.grant('a','edu','u')

    def tearDown(self):
        self.store.close(); self.temp.cleanup()

    def run_rag(self,**kw):
        return respond(self.store,self.emb,self.backend,self.who,'교육비 한도는?',as_of='2026-09-08',**kw)

    def test_valid_citation_resolves_to_real_revision(self):
        result=self.run_rag()
        self.assertEqual(result.status,'answered')
        self.assertEqual(result.sources[0]['doc_id'],'edu')
        self.assertEqual(result.sources[0]['revision'],'v2')
        self.assertEqual(result.sources[0]['source_id'],'s1')
        self.assertEqual(len(result.sources[0]['chunk_id']),64)

    def test_initial_revalidation_stops_context_count(self):
        self.store.resolve=lambda *args,**kwargs:{}
        self.backend.before_count=lambda:self.fail('재검사 실패 뒤 계수했다')
        self.assertEqual(self.run_rag().status,'evidence_changed')
        self.assertEqual(self.backend.calls,[])

    def test_no_candidates_skips_generation(self):
        self.store.revoke('a','edu','u')
        self.assertEqual(self.run_rag().status,'insufficient_evidence')
        self.assertEqual(self.backend.calls,[])

    def test_missing_budget_is_not_missing_knowledge(self):
        self.backend.count_fn=lambda text:100 if json.loads(text)['context'] else 10
        result=self.run_rag(window=50,output_reserve=10)
        self.assertEqual(result.status,'context_failed')
        self.assertEqual(result.error_code,'no_evidence_fits')
        self.assertEqual(self.backend.calls,[])

    def test_revocation_during_count_stops_generation(self):
        self.backend.before_count=lambda:self.store.revoke('a','edu','u')
        self.assertEqual(self.run_rag().status,'evidence_changed')
        self.assertEqual(self.backend.calls,[])

    def test_revocation_after_generation_discards_answer(self):
        self.backend.after_generate=lambda:self.store.revoke('a','edu','u')
        result=self.run_rag()
        self.assertEqual(result.status,'evidence_changed')
        self.assertIsNone(result.answer)
        self.assertEqual(result.sources,[])
        self.assertNotIn('30만',repr(result))

    def test_revision_change_after_generation_discards_answer(self):
        self.backend.after_generate=lambda:self.store.replace('a','edu',2,
            [Revision('v3','교육비는 40만 원이다.','2026-09-01')],lambda t:Vector('test',(1,0)),len)
        self.assertEqual(self.run_rag().status,'evidence_changed')

    def test_unknown_and_budget_omitted_citations(self):
        self.store.replace('a','other',1,[Revision('v1','다른 안내','2026-01-01')],lambda t:Vector('test',(1,0)),len)
        self.store.grant('a','other','u')
        self.backend.count_fn=lambda text:100 if len(json.loads(text)['context'])>1 else 10
        def wrong(raw):
            raw['citations'][0]['source_id']='s2'
            return raw
        self.backend.transform=wrong
        result=self.run_rag(window=50,output_reserve=10)
        self.assertEqual(result.status,'contract_failed')
        self.assertEqual(result.error_code,'unknown_source')
        self.assertIsNone(result.answer)

    def test_semantic_error_is_not_proven_by_quote_check(self):
        def wrong(raw):
            raw['answer']='교육비 한도는 300만 원이다.'
            return raw
        self.backend.transform=wrong
        self.assertEqual(self.run_rag().status,'answered')

    def test_non_answer_and_generation_error(self):
        self.backend.transform=lambda raw:{'status':'insufficient_evidence','answer':None,
                                          'citations':[],'clarification':None}
        self.assertEqual(self.run_rag().status,'insufficient_evidence')
        self.backend.generate=lambda *args:GenerationResult('incomplete')
        result=self.run_rag()
        self.assertEqual(result.status,'generation_failed')
        self.assertEqual(result.error_code,'incomplete')

    def test_stage_errors_and_invalid_request(self):
        self.backend.count_fn=lambda text:(_ for _ in ()).throw(RuntimeError('secret'))
        self.assertEqual(self.run_rag().status,'context_failed')
        self.assertEqual(self.run_rag(k=0).status,'invalid_request')
        self.emb.encode=lambda *args,**kwargs:(_ for _ in ()).throw(RuntimeError('secret'))
        result=self.run_rag()
        self.assertEqual(result.status,'retrieval_failed')
        self.assertNotIn('secret',repr(result))

if __name__=='__main__':
    unittest.main()
