import cv2,numpy as np,json
from fastapi.testclient import TestClient
from app import app

def test_video_api(tmp_path):
 p=tmp_path/'test.mp4'; w=cv2.VideoWriter(str(p),cv2.VideoWriter_fourcc(*'mp4v'),20,(160,160)); rng=np.random.default_rng(4); patch=rng.integers(0,255,(15,15,3),dtype=np.uint8)
 for i in range(41):
  y=100-2*(i if i<=20 else 40-i); f=np.zeros((160,160,3),np.uint8);f[y-7:y+8,73:88]=patch;w.write(f)
 w.release(); c=TestClient(app); params=dict(start=0,end=2,x=80,y=100,width=160,scale=.005)
 r=c.post('/track-video',files={'video':('test.mp4',p.read_bytes())},data={'params':json.dumps(params)});assert r.status_code==200,r.text; d=r.json();assert len(d['reps'])==1;assert max(abs(q[2]-(100-2*min(i,40-i))) for i,q in enumerate(d['points']))<=1
 trace=[dict(t=t,x=x,y=y,speed=.2,slow=False) for t,x,y in d['points']];r=c.post('/render-video',files={'video':('test.mp4',p.read_bytes())},data={'params':json.dumps(dict(trace=trace,center=80))});assert r.status_code==200;out=tmp_path/'out.mp4';out.write_bytes(r.content);cap=cv2.VideoCapture(str(out));assert int(cap.get(cv2.CAP_PROP_FRAME_COUNT))==41;cap.release()
 params['end']=3;r=c.post('/track-video',files={'video':('test.mp4',p.read_bytes())},data={'params':json.dumps(params)});assert r.status_code==400
