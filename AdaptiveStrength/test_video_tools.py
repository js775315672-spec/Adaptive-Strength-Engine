import cv2,numpy as np
from video_tools import locate,render

def test_tracking():
 rng=np.random.default_rng(4); p=rng.integers(0,255,(15,15),dtype=np.uint8); f=np.zeros((100,100),np.uint8);f[33:48,43:58]=p
 assert locate(f,p,45,35)[:2]==(50,40)
 assert locate(np.zeros_like(f),p,45,35) is None

def test_export(tmp_path):
 a=tmp_path/'a.mp4';b=tmp_path/'b.mp4';w=cv2.VideoWriter(str(a),cv2.VideoWriter_fourcc(*'mp4v'),20,(64,64));assert w.isOpened()
 for i in range(10):w.write(np.zeros((64,64,3),np.uint8))
 w.release();assert render(a,b,[dict(t=0,x=20,y=30,speed=.3,slow=False)],32)==10
 c=cv2.VideoCapture(str(b));ok,f=c.read();c.release();assert ok and f[:,32].max()>30
