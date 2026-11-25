import math, sqlite3, json, time
import numpy as np

def stats(x):
 a=np.asarray(x,float); return dict(max=float(a.max()),min=float(a.min()),mean=float(a.mean()),max90=float(a.max()*.9)) if len(a) else None

def analyze(points,scale,center,kg,grind=.15):
 a=np.asarray(points,float)
 if a.ndim!=2 or a.shape[1]!=3 or len(a)<5 or not np.isfinite(a).all() or not (scale>0 and kg>0): raise ValueError('유효한 좌표, 거리 보정, 중량 필요')
 t,x,y=a.T; dt=np.diff(t)
 if np.any(dt<=0) or np.any(dt>.2): raise ValueError('시간 공백 또는 역순')
 # user marks ascent only; centered smoothing with edge preservation
 ys=y.copy(); ys[1:-1]=(y[:-2]+2*y[1:-1]+y[2:])/4
 v=-np.diff(ys)*scale/dt; travel=(y[0]-y[-1])*scale
 if travel<.03: raise ValueError('상승 거리 부족')
 d=np.abs(x-center)*scale; rms=float(np.sqrt(np.mean(d*d)))
 slow=(v<grind)&(v>=0); slow[0]=slow[-1]=False
 return dict(speed=stats(v),mean_speed=float(travel/(t[-1]-t[0])),travel=float(travel),deviation=stats(d),rms=rms,error_pct=rms/travel*100,grind_seconds=float(dt[slow].sum()),grind_threshold=grind,bar_reference_moment=stats(d*kg*9.80665),duration=float(t[-1]-t[0]))

class Store:
 def __init__(self,path):
  self.db=sqlite3.connect(path); self.db.execute('CREATE TABLE IF NOT EXISTS sets(id INTEGER PRIMARY KEY, ts REAL, exercise TEXT, kg REAL, reps INTEGER, rpe REAL, data TEXT, archived INTEGER DEFAULT 0)');self.db.commit()
 def add(self,exercise,kg,reps,rpe,data):
  if not exercise or not (0<kg<=1000 and 1<=reps<=100 and 0<=rpe<=10): raise ValueError('입력 범위 오류')
  with self.db:
   self.db.execute('INSERT INTO sets(ts,exercise,kg,reps,rpe,data) VALUES(?,?,?,?,?,?)',(time.time(),exercise,kg,reps,rpe,json.dumps(data,allow_nan=False)))
   self.db.execute('UPDATE sets SET archived=1 WHERE exercise=? AND (ts<? OR id NOT IN (SELECT id FROM sets WHERE exercise=? ORDER BY ts DESC,id DESC LIMIT 200))',(exercise,time.time()-30*86400,exercise))
 def rows(self,exercise,active=True):
  q='SELECT kg,reps,rpe,data,ts FROM sets WHERE exercise=?'+(' AND archived=0 AND ts>=?' if active else '')+' ORDER BY ts,id'; args=(exercise,time.time()-30*86400) if active else (exercise,)
  return [dict(kg=k,reps=r,rpe=p,data=json.loads(d),ts=t) for k,r,p,d,t in self.db.execute(q,args)]
 def recommend(self,exercise,kg,reps,rpe,metrics,loss):
  rows=self.rows(exercise); factor=.9 if rpe>=9.5 or loss>=30 else .95 if rpe>=9 or loss>=20 else 1
  reason='초기 보수 규칙'; model=None
  if metrics and (max(m['error_pct'] for m in metrics)>=8 or max(m['grind_seconds'] for m in metrics)>=1):factor=min(factor,.95)
  if rpe>=10:return dict(kg=None,reps=0,reason='최대 노력: 추가 세트 보류',model=None,active=len(rows),warning='휴식 후 재평가')
  return dict(kg=max(0,math.floor(kg*factor/2.5)*2.5),reps=max(1,reps-(2 if factor<=.9 else 1 if factor<1 else 0)),reason=reason,model=model,active=len(rows),warning='추천 후보일 뿐. 통증, 어지럼, 호흡곤란 또는 실패 반복 시 중단. 충분히 휴식 후 판단.')
