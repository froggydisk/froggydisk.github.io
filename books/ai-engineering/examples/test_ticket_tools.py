from pathlib import Path
import sqlite3
import tempfile
import unittest
from pydantic import ValidationError
from ticket_tools import Actor, Tickets, ToolError


class TicketTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.path=str(Path(self.temp.name)/'tickets.db')
        self.store=Tickets(self.path)
        self.actor=Actor('hanul','u')
        self.store.grant(self.actor)
        self.args={'category':'equipment','title':'화면 고장','description':'가상 자산 고장'}

    def tearDown(self):
        self.store.close();self.temp.cleanup()

    def draft(self):
        return self.store.prepare(self.actor,self.args)['draft_id']

    def test_confirmation_and_idempotency_across_connections(self):
        draft=self.draft()
        with self.assertRaisesRegex(ToolError,'confirmation_required'):
            self.store.create(self.actor,draft)
        self.store.approve(self.actor,draft)
        first=self.store.create(self.actor,draft)
        other=Tickets(self.path)
        try:
            repeated=other.create(self.actor,draft)
        finally:
            other.close()
        self.assertEqual(first['ticket_id'],repeated['ticket_id'])
        self.assertTrue(repeated['replayed'])
        self.assertEqual(self.store.db.execute('SELECT count(*) FROM tickets').fetchone()[0],1)
        self.assertEqual(self.store.db.execute("SELECT count(*) FROM ticket_audit WHERE action='created'").fetchone()[0],1)

    def test_other_actor_and_tenant(self):
        draft=self.draft();self.store.approve(self.actor,draft)
        result=self.store.create(self.actor,draft)
        for other in (Actor('hanul','other'),Actor('else','u')):
            self.store.grant(other)
            with self.assertRaisesRegex(ToolError,'not_found'):
                self.store.create(other,draft)
            with self.assertRaisesRegex(ToolError,'not_found'):
                self.store.get(other,result['ticket_id'])

    def test_revocation_blocks_replay_and_read(self):
        draft=self.draft();self.store.approve(self.actor,draft)
        result=self.store.create(self.actor,draft)
        self.store.revoke(self.actor)
        for call in (lambda:self.store.create(self.actor,draft),
                     lambda:self.store.get(self.actor,result['ticket_id'])):
            with self.assertRaisesRegex(ToolError,'permission_denied'):
                call()

    def test_changed_draft_requires_new_confirmation(self):
        first=self.draft();self.store.approve(self.actor,first)
        self.args['description']='다른 내용'
        second=self.draft()
        with self.assertRaisesRegex(ToolError,'confirmation_required'):
            self.store.create(self.actor,second)
        id=self.store.create(self.actor,first)['ticket_id']
        self.assertEqual(self.store.get(self.actor,id)['description'],'가상 자산 고장')

    def test_input_schema_rejects_identity_and_invalid_fields(self):
        for change in ({'user':'admin'},{'category':'admin'},{'title':' '},{'title':123}):
            with self.assertRaises(ValidationError):
                self.store.prepare(self.actor,self.args|change)
        self.assertEqual(self.store.db.execute('SELECT count(*) FROM drafts').fetchone()[0],0)

    def test_audit_failure_rolls_back_ticket(self):
        draft=self.draft();self.store.approve(self.actor,draft)
        self.store.db.execute("CREATE TRIGGER fail_audit BEFORE INSERT ON ticket_audit WHEN NEW.action='created' BEGIN SELECT RAISE(ABORT,'injected'); END")
        with self.assertRaises(sqlite3.IntegrityError):
            self.store.create(self.actor,draft)
        self.assertEqual(self.store.db.execute('SELECT count(*) FROM tickets').fetchone()[0],0)
        self.assertFalse(self.store.db.in_transaction)

if __name__=='__main__':
    unittest.main()
