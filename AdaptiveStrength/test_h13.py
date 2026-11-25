import pytest
from test_h12 import setup
from approval import submit
from ledger import reserve,listing

def fixture(tmp_path):
 s,d=setup(tmp_path); r=submit(s,tmp_path,d); p=d['pred']; return s,d,dict(receipt=r['receipt'],exercise='squat',start=p[0][0],end=p[-1][0])
def test_idempotent(tmp_path):
 s,d,q=fixture(tmp_path); a=reserve(s,tmp_path,q); assert a==reserve(s,tmp_path,q); assert len(listing(s))==1; assert not a['learning_approved']; assert s.rows('squat')==[]
def test_overlap(tmp_path):
 s,d,q=fixture(tmp_path);reserve(s,tmp_path,q)
 with pytest.raises(ValueError):reserve(s,tmp_path,dict(q,exercise='bench'))
def test_tamper(tmp_path):
 s,d,q=fixture(tmp_path);(tmp_path/(d['digest']+'.mp4')).write_bytes(b'bad')
 with pytest.raises(ValueError):reserve(s,tmp_path,q)
def test_rejected(tmp_path):
 s,d,q=fixture(tmp_path);d['synthetic']=True;q['receipt']=submit(s,tmp_path,d)['receipt']
 with pytest.raises(ValueError):reserve(s,tmp_path,q)
