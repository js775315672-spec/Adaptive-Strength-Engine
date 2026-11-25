import json,pytest
from engine import Store
from feedback import *
def test_feedback(tmp_path):
 s=Store(tmp_path/'db');schema(s);m=dict(lo=100,hi=200,intercept=1.5,slope=-.005);s.db.execute('INSERT INTO models(exercise,ts,data,active) VALUES(?,?,?,1)',('squat',time.time(),json.dumps(m)));s.db.commit();f=forecast(s,'squat',150,5);assert f['predicted']==.75
 with pytest.raises(ValueError):resolve(s,f['id'],150,4,.7)
 resolve(s,f['id'],150,5,.7);assert errors(s,'squat')['mae']==pytest.approx(.05)
 with pytest.raises(ValueError):resolve(s,f['id'],150,5,.7)
 with pytest.raises(ValueError):forecast(s,'squat',250,5)
def test_fatigue():
 rows=[dict(kg=100,reps=5,data={'loss':20})]*5;assert fatigue(rows,100,5)['median_loss']==20;assert fatigue(rows,100,4)['median_loss'] is None
