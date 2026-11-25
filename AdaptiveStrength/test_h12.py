import hashlib
import pytest
from engine import Store
from approval import submit
from test_validation import trajectory

def setup(tmp_path):
 p=trajectory(); b=b'fixture only'; digest=hashlib.sha256(b).hexdigest();(tmp_path/(digest+'.mp4')).write_bytes(b)
 return Store(tmp_path/'db'),dict(digest=digest,pred=p,reference=p,scale=.005,center=80,kg=100)
def test_receipt_idempotent(tmp_path):
 s,d=setup(tmp_path);a=submit(s,tmp_path,d);b=submit(s,tmp_path,d);assert a==b and a['status']=='PENDING' and not a['learning_approved'];assert s.db.execute('select count(*) from reviews').fetchone()[0]==1

def test_tamper(tmp_path):
 s,d=setup(tmp_path);(tmp_path/(d['digest']+'.mp4')).write_bytes(b'changed');
 with pytest.raises(ValueError):submit(s,tmp_path,d)
def test_synthetic_rejected(tmp_path):
 s,d=setup(tmp_path);d['synthetic']=True;assert submit(s,tmp_path,d)['status']=='REJECTED'
