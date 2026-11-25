import json,time,math
import numpy as np

def schema(s):
 s.db.execute('CREATE TABLE IF NOT EXISTS forecasts(id INTEGER PRIMARY KEY, exercise TEXT, ts REAL, kg REAL, reps INTEGER, predicted REAL, actual REAL, model_id INTEGER)');s.db.execute('CREATE TABLE IF NOT EXISTS models(id INTEGER PRIMARY KEY, exercise TEXT, ts REAL, data TEXT, active INTEGER)');s.db.commit()
def active(s,exercise):
 schema(s);r=s.db.execute('SELECT id,data FROM models WHERE exercise=? AND active=1',(exercise,)).fetchone();return (r[0],json.loads(r[1])) if r else (None,None)
def predict(model,kg):
 if not model or not model['lo']<=kg<=model['hi']:return None
 v=model['intercept']+model['slope']*kg;return v if math.isfinite(v) and v>0 else None
def forecast(s,exercise,kg,reps):
 if not (math.isfinite(kg) and 0<kg<=1000 and 1<=reps<=100):raise ValueError("invalid load/reps")
 mid,m=active(s,exercise);v=predict(m,kg)
 if v is None:raise ValueError('활성 모델 또는 학습 범위 부족')
 with s.db:
  c=s.db.execute('INSERT INTO forecasts(exercise,ts,kg,reps,predicted,model_id) VALUES(?,?,?,?,?,?)',(exercise,time.time(),kg,reps,v,mid));return dict(id=c.lastrowid,predicted=v,model_id=mid)
def resolve(s,id,kg,reps,actual):
 schema(s)
 if not math.isfinite(actual) or actual<=0:raise ValueError('유효한 실제 속도 필요')
 with s.db:
  c=s.db.execute('UPDATE forecasts SET actual=? WHERE id=? AND kg=? AND reps=? AND actual IS NULL',(actual,id,kg,reps))
  if c.rowcount!=1:raise ValueError('예측 ID 또는 중량/횟수 불일치, 이미 기록됨')
 return dict(id=id,actual=actual)
def errors(s,exercise):
 schema(s);a=s.db.execute('SELECT predicted,actual FROM forecasts WHERE exercise=? AND actual IS NOT NULL AND ts>=?',(exercise,time.time()-30*86400)).fetchall();return dict(n=len(a),mae=float(np.mean([abs(p-v) for p,v in a])) if a else None)
def fatigue(rows,kg,reps):
 similar=[r for r in rows if abs(r['kg']-kg)<=5 and r['reps']==reps and 'loss' in r['data']];return dict(n=len(similar),median_loss=float(np.median([r['data']['loss'] for r in similar])) if len(similar)>=5 else None)
