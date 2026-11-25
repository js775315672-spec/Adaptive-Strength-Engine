import json,time
from engine import Store
from feedback import schema,resolve
from h9 import register,calibrated,screen

def test_calibrated_loop(tmp_path):
 s=Store(tmp_path/'db');schema(s)
 m=dict(lo=50,hi=150,intercept=.8,slope=-.004)
 s.db.execute('insert into models values(1,?,?,?,1)',('squat',time.time(),json.dumps(m)))
 for i in range(12):
  p=register(s,'squat',100,3);resolve(s,p['id'],100,3,.45)
 p=register(s,'squat',100,3);assert abs(p['predicted']-.45)<1e-8;assert abs(p['raw']-.4)<1e-8
 resolve(s,p['id'],100,3,.45);assert abs(calibrated(s,'squat',100)['predicted']-.45)<1e-8
 assert calibrated(s,'squat',200)['predicted'] is None
 s.db.execute('update models set active=0');assert calibrated(s,'squat',100)['predicted'] is None

def test_screen(tmp_path):
 s=Store(tmp_path/'db');o=screen([dict(kg=100,loss=25,median_rpe=8)],s,'squat')[0];assert o['review_required'] and o['predicted_first_speed'] is None
