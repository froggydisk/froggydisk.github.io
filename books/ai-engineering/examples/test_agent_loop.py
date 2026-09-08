import json
import unittest
from agent_loop import run

ID='a'*32
ACTION=json.dumps({'kind':'get_ticket','arguments':{'ticket_id':ID}})
VIEW={'ticket_id':ID,'status':'received','category':'equipment','title':'화면 고장','description':'가상 증상'}


class LoopTests(unittest.TestCase):
    def test_observe_then_finish(self):
        def planner(q,observations):
            if observations:
                self.assertEqual(observations[0]['result'],VIEW)
                return '{"kind":"finish","arguments":{}}'
            return ACTION
        result=run('조회',planner,{'get_ticket':lambda **kw:VIEW.copy()})
        self.assertEqual(result.status,'completed')
        self.assertEqual((result.steps,result.units),(2,4))

    def test_no_action_is_not_completed_work(self):
        self.assertEqual(run('조회',lambda q,o:'{"kind":"finish","arguments":{}}',{}).status,'no_action')

    def test_repeated_call_and_budget(self):
        calls=[]
        def tool(**kw):
            calls.append(1);return VIEW.copy()
        result=run('조회',lambda q,o:ACTION,{'get_ticket':tool})
        self.assertEqual(result.status,'repeated_action')
        self.assertEqual(len(calls),1)
        result=run('조회',lambda q,o:ACTION,{'get_ticket':tool},max_units=1)
        self.assertEqual(result.status,'budget')
        self.assertEqual(len(calls),1)

    def test_step_limit(self):
        result=run('조회',lambda q,o:ACTION,{'get_ticket':lambda **kw:VIEW.copy()},max_steps=1)
        self.assertEqual(result.status,'step_limit')

    def test_deadline_after_planning_prevents_tool(self):
        t=[0]
        def planner(q,o):
            t[0]=2;return ACTION
        result=run('조회',planner,{'get_ticket':lambda **kw:self.fail('late tool')},
                   timeout_seconds=1,clock=lambda:t[0])
        self.assertEqual(result.status,'deadline')

    def test_late_tool_is_unknown(self):
        t=[0]
        def tool(**kw):
            t[0]=2;return VIEW.copy()
        result=run('조회',lambda q,o:ACTION,{'get_ticket':tool},timeout_seconds=1,clock=lambda:t[0])
        self.assertEqual(result.status,'execution_unknown')
        self.assertIsNone(result.result)

    def test_invalid_plan_and_tool_payload(self):
        for raw in ('{"kind":"create_ticket","arguments":{}}',
                    '{"kind":"finish","kind":"get_ticket","arguments":{}}',
                    '```json {} ```'):
            self.assertEqual(run('조회',lambda q,o:raw,{}).status,'planning_failed')
        self.assertEqual(run('조회',lambda q,o:ACTION,{'get_ticket':lambda **kw:{'status':'done'}}).status,'execution_unknown')

    def test_plan_mutation_does_not_rewrite_observation(self):
        def planner(q,o):
            if o:
                o[0]['result']['status']='fabricated'
                return '{"kind":"finish","arguments":{}}'
            return ACTION
        result=run('조회',planner,{'get_ticket':lambda **kw:VIEW.copy()})
        self.assertEqual(result.result['status'],'received')

if __name__=='__main__':
    unittest.main()
