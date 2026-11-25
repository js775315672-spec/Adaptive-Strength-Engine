import time
from learning import *
from engine import Store

def rows():return [dict(kg=100+i%4*10,reps=3+i%2,rpe=8,ts=time.time(),data={'first_speed':1.5-(100+i%4*10)*.008,'metrics':[{'mean_speed':.4}]}) for i in range(20)]
def test_fit():assert fit(rows())['mae']<1e-8
def test_cold():assert fit(rows()[:5]) is None
def test_grind():assert abs(personal_grind(rows())-.14)<1e-8
def test_candidates():assert all(c['kg']<=120 and c['reps']<=5 for c in candidates(rows(),{'kg':120,'reps':5}))
def test_stop():assert candidates(rows(),{'kg':None,'reps':0})==[]
def test_checkpoint(tmp_path):
 s=Store(tmp_path/'a.db'); first=checkpoint(s,'squat',rows()); assert first
 r=rows();r[-1]['data']['first_speed']+=.01;assert checkpoint(s,'squat',r)==first
 assert s.db.execute('SELECT count(*) FROM models').fetchone()[0]==1
 assert not rollback(s,'squat');s.db.close()

def test_real_rollback(tmp_path):
 from feedback import active,forecast
 import pytest
 s=Store(tmp_path/'b.db');first=checkpoint(s,'squat',rows());mid,_=active(s,'squat')
 r=rows()
 for row in r:row['data']['first_speed']+=.2
 second=checkpoint(s,'squat',r);assert second!=first
 mid2,_=active(s,'squat');assert mid2!=mid
 assert forecast(s,'squat',110,3)['predicted']==pytest.approx(.82)
 assert rollback(s,'squat');assert active(s,'squat')[0]==mid
 assert forecast(s,'squat',110,3)['predicted']==pytest.approx(.62)
 assert not rollback(s,'squat');s.db.close()
