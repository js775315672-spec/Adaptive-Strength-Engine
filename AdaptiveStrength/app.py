from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from engine import Store
from learning import personal_grind,candidates,checkpoint,rollback
from advanced import detail,split
from personal import profile,compare,rest_fatigue,joint_samples
from feedback import active,forecast,resolve,errors,fatigue
from h9 import screen,register
app=FastAPI(); root=Path(__file__).parent
@app.get('/')
def home(): return FileResponse(root/'index.html')
@app.post('/analyze')
def run(d:dict):
 try:
  kg=float(d['kg']); rpe=float(d['rpe']); exercise=str(d['exercise']); scale=float(d['scale']); center=float(d['center']); store=Store(root/'personal.sqlite'); rows=store.rows(exercise); threshold=personal_grind([r for r in rows if abs(r['kg']-kg)<=10]); reps=[detail(p,scale,center,kg,threshold,joint_samples(p,d.get('joints',{}).get(str(i),{}))) for i,p in enumerate(d['reps'])]; speeds=[r['mean_speed'] for r in reps]; loss=max(0,100*(1-speeds[-1]/max(speeds))); data={'first_speed':speeds[0],'metrics':reps,'loss':loss}; rest=d.get('rest_seconds'); rest=float(rest) if rest is not None else None;
  if rest is not None and not 0<=rest<=3600:raise ValueError('invalid rest')
  curves=[]
  for p,m in zip(d['reps'],reps):
   try:curve=profile(p,scale)
   except ValueError:curve=None
   curves.append(curve);m['personal_path']=compare(rows,kg,curve) if curve is not None else None
  data.update(profiles=curves,successful=d.get('successful') is True,rest_seconds=rest);rec=store.recommend(exercise,kg,len(reps),rpe,reps,loss)
  if d.get('save') and d.get('quality_confirmed') is not True: raise ValueError('추적 품질 확인 필요')
  if d.get('save'): raise ValueError('H10 validation mode: new learning records disabled until independently verified')
  model=checkpoint(store,exercise,store.rows(exercise)) if d.get('save') else None; mid,chosen=active(store,exercise); options=candidates(rows,rec,chosen); rec['model']=chosen; rec['model_id']=mid; [o.update(fatigue(rows,o['kg'],o['reps'])) for o in options]; [o.update(rest_fatigue(rows,o['kg'],o['reps'],rest)) for o in options]; screen(options,store,exercise); store.db.close(); return dict(reps=reps,loss=loss,recommendation=rec,candidates=options,grind_threshold=threshold,checkpoint=model)
 except Exception as e: raise HTTPException(400,str(e))
@app.get('/history')
def history(exercise:str):
 s=Store(root/'personal.sqlite'); r=s.rows(exercise,False);s.db.close();return r

@app.post("/split")
def segments(d:dict):
 try:return {"reps":split(d["points"],float(d["scale"]))}
 except Exception as e:raise HTTPException(400,str(e))

@app.post('/rollback')
def restore(d:dict):
 s=Store(root/'personal.sqlite')
 try:return {'restored':rollback(s,str(d['exercise']))}
 finally:s.db.close()

@app.post('/forecast')
def make_forecast(d:dict):
 s=Store(root/'personal.sqlite')
 try:return register(s,str(d['exercise']),float(d['kg']),int(d['reps']))
 except Exception as e:raise HTTPException(400,str(e))
 finally:s.db.close()
@app.post('/feedback')
def record_feedback(d:dict):
 s=Store(root/'personal.sqlite')
 try:raise ValueError('H11: unverified feedback disabled')
 except Exception as e:raise HTTPException(400,str(e))
 finally:s.db.close()
@app.get('/errors')
def error_report(exercise:str):
 s=Store(root/'personal.sqlite')
 try:return errors(s,exercise)
 finally:s.db.close()

from fastapi import UploadFile, File, Form
from starlette.background import BackgroundTask
from tempfile import TemporaryDirectory
import json
from integration import track_video
from video_tools import render

def copy_video(upload,path):
 with open(path,'wb') as f:
  total=0
  while chunk:=upload.file.read(1024*1024):
   total+=len(chunk)
   if total>250*1024*1024: raise ValueError('250 MB limit')
   f.write(chunk)

@app.post('/track-video')
def track_endpoint(video:UploadFile=File(...),params:str=Form(...)):
 try:
  with TemporaryDirectory() as tmp:
   p=Path(tmp)/'input.mp4';copy_video(video,p);return track_video(p,**json.loads(params))
 except Exception as e:raise HTTPException(400,str(e))

@app.post('/render-video')
def render_endpoint(video:UploadFile=File(...),params:str=Form(...)):
 tmp=TemporaryDirectory()
 try:
  p=Path(tmp.name)/'input.mp4';out=Path(tmp.name)/'analysis.mp4';copy_video(video,p);d=json.loads(params);render(p,out,d['trace'],d['center']);return FileResponse(out,media_type='video/mp4',filename='analysis.mp4',background=BackgroundTask(tmp.cleanup))
 except Exception as e:
  tmp.cleanup();raise HTTPException(400,str(e))

from h8 import archive_video,pose_video,correction
@app.post('/archive-video')
def archive_endpoint(video:UploadFile=File(...),params:str=Form(...)):
 s=Store(root/'personal.sqlite')
 try:
  with TemporaryDirectory() as tmp:
   p=Path(tmp)/'input.mp4';copy_video(video,p);return {'digest':archive_video(s,p,root/'videos',str(json.loads(params)['exercise']))}
 except Exception as e:raise HTTPException(400,str(e))
 finally:s.db.close()
@app.post('/pose-video')
def pose_endpoint(video:UploadFile=File(...),params:str=Form(...)):
 try:
  d=json.loads(params)
  if sum(map(len,d['reps']))>3600:raise ValueError('3600 sample limit')
  with TemporaryDirectory() as tmp:
   p=Path(tmp)/'input.mp4';copy_video(video,p);return pose_video(p,d['reps'],d['width'],root/'pose_landmarker_lite.task')
 except Exception as e:raise HTTPException(400,str(e))
@app.get('/calibration')
def calibration(exercise:str):
 s=Store(root/'personal.sqlite')
 try:
  mid,_=active(s,exercise);return {'model_id':mid,'calibration':correction(s,exercise,mid)}
 finally:s.db.close()

@app.get('/videos')
def video_list():
 s=Store(root/'personal.sqlite')
 try:
  s.db.execute('CREATE TABLE IF NOT EXISTS videos(digest TEXT PRIMARY KEY, exercise TEXT, ts REAL)')
  return [dict(digest=d,exercise=e,ts=t) for d,e,t in s.db.execute('SELECT digest,exercise,ts FROM videos ORDER BY ts DESC')]
 finally:s.db.close()

@app.get('/videos/{digest}')
def video_read(digest:str):
 import re
 if not re.fullmatch(r'[a-f0-9]{64}',digest):raise HTTPException(404)
 p=root/'videos'/(digest+'.mp4')
 if not p.is_file():raise HTTPException(404)
 return FileResponse(p,media_type='video/mp4')

from validation import audit
@app.post('/validation')
def validation_endpoint(d:dict):
 try:return audit(d['pred'],d['reference'],float(d['scale']),float(d['center']),float(d['kg']),d.get('synthetic') is True)
 except Exception as e:raise HTTPException(400,str(e))

from approval import submit
@app.post('/review-receipt')
def review_receipt(d:dict):
 s=Store(root/'personal.sqlite')
 try:return submit(s,root/'videos',d)
 except Exception as e:raise HTTPException(400,str(e))
 finally:s.db.close()

from ledger import reserve,listing
@app.post('/set-review')
def set_review(d:dict):
 s=Store(root/'personal.sqlite')
 try:return reserve(s,root/'videos',d)
 except Exception as e:raise HTTPException(400,str(e))
 finally:s.db.close()
@app.get('/set-reviews')
def set_reviews():
 s=Store(root/'personal.sqlite')
 try:return listing(s)
 finally:s.db.close()
