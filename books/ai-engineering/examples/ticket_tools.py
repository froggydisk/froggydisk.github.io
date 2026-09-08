"""11장: 인증 주체·승인된 초안·멱등성을 강제하는 가상 티켓 저장소."""
from dataclasses import dataclass
import json
import sqlite3
from typing import Literal
from uuid import uuid4
from pydantic import BaseModel, ConfigDict, Field, field_validator


class TicketInput(BaseModel):
    model_config=ConfigDict(extra='forbid',strict=True)
    category: Literal['equipment','account']
    title: str=Field(min_length=1,max_length=120)
    description: str=Field(min_length=1,max_length=2000)

    @field_validator('title','description')
    @classmethod
    def nonblank(cls,value):
        if not value.strip():
            raise ValueError('공백만 있는 텍스트는 허용하지 않는다')
        return value


@dataclass(frozen=True)
class Actor:
    tenant: str
    user: str


class ToolError(ValueError):
    pass


class Tickets:
    def __init__(self,path):
        self.db=sqlite3.connect(path,isolation_level=None)
        self.db.row_factory=sqlite3.Row
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS ticket_grants(tenant TEXT,user TEXT,PRIMARY KEY(tenant,user));
        CREATE TABLE IF NOT EXISTS drafts(id TEXT PRIMARY KEY,tenant TEXT,user TEXT,payload TEXT,approved INTEGER DEFAULT 0);
        CREATE TABLE IF NOT EXISTS tickets(id TEXT PRIMARY KEY,draft TEXT UNIQUE,tenant TEXT,user TEXT,payload TEXT,status TEXT);
        CREATE TABLE IF NOT EXISTS ticket_audit(id INTEGER PRIMARY KEY,tenant TEXT,user TEXT,action TEXT,object_id TEXT);
        ''')

    def close(self):
        self.db.close()

    def grant(self,actor):
        self.db.execute('INSERT OR IGNORE INTO ticket_grants VALUES(?,?)',(actor.tenant,actor.user))

    def revoke(self,actor):
        self.db.execute('DELETE FROM ticket_grants WHERE tenant=? AND user=?',(actor.tenant,actor.user))

    def _allowed(self,actor):
        if not actor.tenant or not actor.user or not self.db.execute(
            'SELECT 1 FROM ticket_grants WHERE tenant=? AND user=?',(actor.tenant,actor.user)).fetchone():
            raise ToolError('permission_denied')

    def _audit(self,actor,action,id):
        self.db.execute('INSERT INTO ticket_audit(tenant,user,action,object_id) VALUES(?,?,?,?)',
                        (actor.tenant,actor.user,action,id))

    def prepare(self,actor,arguments):
        payload=TicketInput.model_validate(arguments).model_dump_json()
        id=uuid4().hex
        self.db.execute('BEGIN IMMEDIATE')
        try:
            self._allowed(actor)
            self.db.execute('INSERT INTO drafts(id,tenant,user,payload) VALUES(?,?,?,?)',
                            (id,actor.tenant,actor.user,payload))
            self._audit(actor,'prepared',id)
            self.db.execute('COMMIT')
            return {'draft_id':id,'preview':json.loads(payload),'status':'awaiting_confirmation'}
        except BaseException:
            if self.db.in_transaction:
                self.db.execute('ROLLBACK')
            raise

    def approve(self,actor,draft_id):
        """신뢰된 UI의 명시적 확인 이벤트 전용. 모델/MCP 도구로 노출하지 않는다."""
        self.db.execute('BEGIN IMMEDIATE')
        try:
            self._allowed(actor)
            row=self.db.execute('SELECT * FROM drafts WHERE id=? AND tenant=? AND user=?',
                                (draft_id,actor.tenant,actor.user)).fetchone()
            if row is None:
                raise ToolError('not_found')
            if not row['approved']:
                self.db.execute('UPDATE drafts SET approved=1 WHERE id=?',(draft_id,))
                self._audit(actor,'approved',draft_id)
            self.db.execute('COMMIT')
        except BaseException:
            if self.db.in_transaction:
                self.db.execute('ROLLBACK')
            raise

    def create(self,actor,draft_id):
        self.db.execute('BEGIN IMMEDIATE')
        try:
            self._allowed(actor)
            draft=self.db.execute('SELECT * FROM drafts WHERE id=? AND tenant=? AND user=?',
                                  (draft_id,actor.tenant,actor.user)).fetchone()
            if draft is None:
                raise ToolError('not_found')
            if not draft['approved']:
                raise ToolError('confirmation_required')
            existing=self.db.execute('SELECT * FROM tickets WHERE draft=?',(draft_id,)).fetchone()
            if existing:
                result={'ticket_id':existing['id'],'status':existing['status'],'replayed':True}
            else:
                id=uuid4().hex
                self.db.execute('INSERT INTO tickets VALUES(?,?,?,?,?,?)',
                                (id,draft_id,actor.tenant,actor.user,draft['payload'],'received'))
                self._audit(actor,'created',id)
                result={'ticket_id':id,'status':'received','replayed':False}
            self.db.execute('COMMIT')
            return result
        except BaseException:
            if self.db.in_transaction:
                self.db.execute('ROLLBACK')
            raise

    def get(self,actor,ticket_id):
        self._allowed(actor)
        row=self.db.execute('SELECT * FROM tickets WHERE id=? AND tenant=? AND user=?',
                            (ticket_id,actor.tenant,actor.user)).fetchone()
        if row is None:
            raise ToolError('not_found')
        return {'ticket_id':row['id'],'status':row['status'],**json.loads(row['payload'])}
