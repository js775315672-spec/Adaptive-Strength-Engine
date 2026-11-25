import json,time,math
import numpy as np

def personal_grind(rows):
 speeds=[m['mean_speed'] for r in rows for m in r['data'].get('metrics',[]) if m.get('mean_speed',0)>0]
 return float(np.clip(np.median(speeds)*.35,.05,.25)) if len(speeds)>=10 else .15

def fit(rows):
 if len(rows)<12:return None
 x=np.array([[r['kg'],r['reps']] for r in rows],float); y=np.array([r['data']['first_speed'] for r in rows]); n=int(len(x)*.75)
 if len(set(x[:n,0]))<3 or len(set(x[:n,1]))<2:return None
 # predict first-rep speed from load only; reps are outcome, not predictor
 X=np.column_stack([np.ones(len(x)),x[:,0]]); w=np.exp(-(time.time()-np.array([r['ts'] for r in rows[:n]]))/(14*86400)); b=np.linalg.lstsq(X[:n]*np.sqrt(w[:,None]),y[:n]*np.sqrt(w),rcond=None)[0]; mae=float(np.mean(abs(X[n:]@b-y[n:]))); base=float(np.mean(abs(y[n:]-np.mean(y[:n]))))
 if b[1]>=0 or mae>=base:return None
 return dict(intercept=float(b[0]),slope=float(b[1]),mae=mae,baseline=base,lo=float(x[:n,0].min()),hi=float(x[:n,0].max()),n=len(rows))

def candidates(rows,rec,model=None):
 if rec['kg'] is None:return []
 out=[]
 for kg in sorted(set([rec['kg'],max(2.5,rec['kg']-2.5),max(2.5,rec['kg']-5)]),reverse=True):
  for reps in sorted(set([rec['reps'],max(1,rec['reps']-1)]),reverse=True):
   similar=[r for r in rows if abs(r['kg']-kg)<=5 and r['reps']>=reps]; pred=None if not model or not model['lo']<=kg<=model['hi'] else max(0,model['intercept']+model['slope']*kg)
   out.append(dict(kg=kg,reps=reps,predicted_first_speed=pred,observed_support=len(similar),median_rpe=float(np.median([r['rpe'] for r in similar])) if similar else None))
 return out

def checkpoint(store,exercise,rows):
 store.db.execute('CREATE TABLE IF NOT EXISTS models(id INTEGER PRIMARY KEY, exercise TEXT, ts REAL, data TEXT, active INTEGER)'); model=fit(rows)
 if model is None:return None
 with store.db:
  old=store.db.execute('SELECT data FROM models WHERE exercise=? AND active=1',(exercise,)).fetchone()
  if old:
   previous=json.loads(old[0]); n=int(len(rows)*.75); hold=rows[n:]
   if hold and all(previous['lo']<=r['kg']<=previous['hi'] for r in hold):
    old_mae=float(np.mean([abs(previous['intercept']+previous['slope']*r['kg']-r['data']['first_speed']) for r in hold]))
    if old_mae<=model['mae']+1e-9:return previous
   if previous==model:return previous
  store.db.execute('UPDATE models SET active=0 WHERE exercise=?',(exercise,));store.db.execute('INSERT INTO models(exercise,ts,data,active) VALUES(?,?,?,1)',(exercise,time.time(),json.dumps(model)))
 return model

def rollback(store,exercise):
 with store.db:
  a=store.db.execute('SELECT id FROM models WHERE exercise=? AND active=1',(exercise,)).fetchone(); b=store.db.execute('SELECT id FROM models WHERE exercise=? AND id<? ORDER BY id DESC LIMIT 1',(exercise,a[0] if a else 0)).fetchone()
  if not b:return False
  store.db.execute('UPDATE models SET active=(id=?) WHERE exercise=?',(b[0],exercise));return True
