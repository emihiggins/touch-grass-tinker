"""Atomic local project commitments. Not a provider-enforced cap or invoice.

Reservations survive crashes and are never automatically released. Ambiguous calls
retain their full reservation until billed usage is reconciled. All runners must
share this database; do not copy/reset it to regain headroom.
"""
from contextlib import contextmanager
from decimal import Decimal, ROUND_CEILING
import json
import sqlite3


def units(value):
    n=Decimal(str(value))
    if not n.is_finite() or n<0:raise ValueError('Invalid amount')
    return int((n*10**9).to_integral_value(rounding=ROUND_CEILING))


class Ledger:
    def __init__(self,path,authorization):
        self.path=str(path)
        self.authorization=json.dumps(authorization,sort_keys=True)
        self.total=units(authorization['total_project_cap_usd'])
        self.stages={s['name']:units(s['cap_usd']) for s in authorization['stages']}
        with self.transaction() as db:
            db.execute('CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS commitments (id TEXT PRIMARY KEY, stage TEXT NOT NULL, amount INTEGER NOT NULL, state TEXT NOT NULL, evidence TEXT NOT NULL)')
            row=db.execute("SELECT value FROM meta WHERE key='authorization'").fetchone()
            if row and row[0]!=self.authorization:raise ValueError('Authorization changed; explicit ledger migration required')
            db.execute("INSERT OR IGNORE INTO meta VALUES ('authorization',?)",(self.authorization,))

    @contextmanager
    def transaction(self):
        db=sqlite3.connect(self.path,timeout=10,isolation_level=None)
        try:
            db.execute('PRAGMA synchronous=FULL');db.execute('BEGIN IMMEDIATE')
            yield db
            db.commit()
        except BaseException:
            db.rollback();raise
        finally:db.close()

    def reconcile_prior(self,amount,evidence):
        """Explicit verified prior total, including rejected/ambiguous historical calls."""
        if not evidence:raise ValueError('Prior billing evidence required')
        n=units(amount)
        with self.transaction() as db:
            if db.execute("SELECT 1 FROM commitments WHERE stage!='prior'").fetchone():
                raise ValueError('Cannot replace prior usage after new commitments')
            if n>self.total:raise ValueError('Prior usage exceeds cap')
            db.execute("INSERT OR REPLACE INTO commitments VALUES ('prior','prior',?,'reconciled',?)",(n,evidence))

    def reserve(self,key,stage,amount,evidence):
        n=units(amount)
        if stage not in self.stages or not key or not evidence or n<=0:raise ValueError('Invalid reservation')
        with self.transaction() as db:
            if not db.execute("SELECT 1 FROM commitments WHERE id='prior'").fetchone():raise ValueError('Prior usage unreconciled')
            total=db.execute('SELECT COALESCE(SUM(amount),0) FROM commitments').fetchone()[0]
            used=db.execute('SELECT COALESCE(SUM(amount),0) FROM commitments WHERE stage=?',(stage,)).fetchone()[0]
            if total+n>self.total or used+n>self.stages[stage]:raise ValueError('Project or stage cap exceeded')
            # Duplicate keys fail even after settlement: never authorize resubmission.
            db.execute("INSERT INTO commitments VALUES (?,?,?,'reserved',?)",(key,stage,n,evidence))

    def settle(self,key,billed_amount,evidence):
        if not evidence:raise ValueError('Verified billing evidence required')
        n=units(billed_amount)
        with self.transaction() as db:
            row=db.execute('SELECT amount,state FROM commitments WHERE id=?',(key,)).fetchone()
            if not row or row[1]!='reserved':raise ValueError('No unresolved reservation')
            if n>row[0]:raise ValueError('Billed usage exceeds reserved bound; stop and reconcile externally')
            db.execute("UPDATE commitments SET amount=?,state='reconciled',evidence=? WHERE id=?",(n,evidence,key))

    def snapshot(self):
        with self.transaction() as db:
            return {'scope':'local_commitments_not_provider_enforcement','committed_usd':db.execute('SELECT COALESCE(SUM(amount),0) FROM commitments').fetchone()[0]/1e9,'unresolved':db.execute("SELECT COUNT(*) FROM commitments WHERE state='reserved'").fetchone()[0]}
