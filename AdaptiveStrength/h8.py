import hashlib, json, time, math
from pathlib import Path
import numpy as np

def archive_video(store, source, folder, exercise):
 folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
 digest=hashlib.sha256()
 with open(source,'rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):digest.update(chunk)
 key=digest.hexdigest(); target=folder/(key+'.mp4')
 if not target.exists():
  import shutil
  shutil.copyfile(source,target)
 with store.db:
  store.db.execute('CREATE TABLE IF NOT EXISTS videos(digest TEXT PRIMARY KEY, exercise TEXT, ts REAL)')
  store.db.execute('INSERT OR IGNORE INTO videos VALUES(?,?,?)',(key,exercise,time.time()))
 return key

def correction(store,exercise,model_id):
 # chronological calibration, disjoint holdout; never modifies base checkpoint
 if model_id is None:return None
 cols={r[1] for r in store.db.execute('pragma table_info(forecasts)')}
 raw='COALESCE(raw_predicted,predicted)' if 'raw_predicted' in cols else 'predicted'
 rows=store.db.execute(f'SELECT {raw},actual FROM forecasts WHERE exercise=? AND model_id=? AND actual IS NOT NULL AND ts>=? ORDER BY ts,id',(exercise,model_id,time.time()-30*86400)).fetchall()[-200:]
 if len(rows)<12:return None
 a=np.asarray(rows,float);n=int(len(a)*.75);bias=float(np.clip(np.median(a[:n,1]-a[:n,0]),-.1,.1));base=float(np.mean(abs(a[n:,0]-a[n:,1])));mae=float(np.mean(abs(a[n:,0]+bias-a[n:,1])))
 if mae>=base-1e-9:return None
 return dict(bias=bias,mae=mae,baseline=base,n=len(rows))

def pose_video(path,reps,width,model_path):
 import cv2
 from mediapipe.tasks import python
 from mediapipe.tasks.python import vision
 import mediapipe as mp
 if not Path(model_path).is_file():raise ValueError('로컬 pose_landmarker_lite.task 모델 필요')
 cap=cv2.VideoCapture(str(path));fps=cap.get(cv2.CAP_PROP_FPS)
 if not math.isfinite(fps) or fps<=0:cap.release();raise ValueError('invalid FPS')
 opts=vision.PoseLandmarkerOptions(base_options=python.BaseOptions(model_asset_path=str(model_path)),running_mode=vision.RunningMode.IMAGE)
 out={}
 try:
  with vision.PoseLandmarker.create_from_options(opts) as detector:
   for i,rep in enumerate(reps):
    joints={name:[] for name in ('left_hip','right_hip','left_knee','right_knee','left_shoulder','right_shoulder','left_elbow','right_elbow')}
    for t,x,y in rep:
     cap.set(cv2.CAP_PROP_POS_FRAMES,round(t*fps));ok,frame=cap.read()
     if not ok:raise ValueError('frame unavailable')
     result=detector.detect(mp.Image(image_format=mp.ImageFormat.SRGB,data=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)))
     if not result.pose_landmarks:raise ValueError('pose missing')
     for name,idx in zip(joints,(23,24,25,26,11,12,13,14)):
      p=result.pose_landmarks[0][idx];joints[name].append([t,p.x*width,p.visibility or 0])
    out[str(i)]={k:v for k,v in joints.items() if all(q[2]>=.75 for q in v)}
 finally:cap.release()
 return out
