from engine import Store
from feedback import schema
from h8 import archive_video,correction
import time

def test_archive(tmp_path):
 s=Store(tmp_path/'db');p=tmp_path/'v';p.write_bytes(b'example');a=archive_video(s,p,tmp_path/'videos','squat');assert a==archive_video(s,p,tmp_path/'videos','squat');assert len(list((tmp_path/'videos').iterdir()))==1;assert s.db.execute('select count(*) from videos').fetchone()[0]==1

def test_calibration(tmp_path):
 s=Store(tmp_path/'db');schema(s);assert correction(s,'squat',1) is None
 for i in range(12):s.db.execute('insert into forecasts(exercise,ts,kg,reps,predicted,actual,model_id) values(?,?,?,?,?,?,?)',('squat',time.time()+i,100,3,.4,.45,1))
 r=correction(s,'squat',1);assert r['mae']<1e-9;assert correction(s,'squat',2) is None
 s.db.execute('update forecasts set actual=.35 where id>9');assert correction(s,'squat',1) is None
