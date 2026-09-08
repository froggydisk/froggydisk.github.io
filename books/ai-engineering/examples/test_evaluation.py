from copy import deepcopy
import unittest
from evaluation import evaluate

class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.record={'rows':[{'id':'a','result':{'status':'answered'}},
                             {'id':'b','result':{'status':'generation_failed'}}]}
        self.expected={'a':'answered','b':'insufficient_evidence'}

    def test_failed_request_stays_in_denominator(self):
        result=evaluate(self.record,self.expected)
        self.assertEqual((result['cases'],result['status_matches']),(2,1))
        self.assertEqual(result['adoption'],'hold')

    def test_missing_case(self):
        self.record['rows'].pop()
        with self.assertRaisesRegex(ValueError,'case_set_mismatch'):
            evaluate(self.record,self.expected)

    def test_duplicate_case(self):
        self.record['rows'].append(deepcopy(self.record['rows'][0]))
        with self.assertRaisesRegex(ValueError,'case_set_mismatch'):
            evaluate(self.record,self.expected)
