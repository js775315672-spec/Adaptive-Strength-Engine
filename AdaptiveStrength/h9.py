"""Model-scoped calibration and conservative candidate screening."""
import math,time
from feedback import active,predict
from h8 import correction

def calibrated(store,exercise,kg):
 mid,model=active(store,exercise); raw=predict(model,kg)
 cal=correction(store,exercise,mid) if raw is not None else None
 value=raw+cal['bias'] if cal else raw
 if value is not None and (not math.isfinite(value) or value<=0): value=None
 return dict(model_id=mid,raw=raw,predicted=value,calibration=cal)

def screen(options,store,exercise):
 for o in options:
  p=calibrated(store,exercise,o['kg']);o['predicted_first_speed']=p['predicted'];o['raw_first_speed']=p['raw'];o['calibration']=p['calibration']
  o['review_required']=o.get('loss') is None or o['loss']>=20 or o.get('median_rpe') is None or o['median_rpe']>=9
 return options

def register(store,exercise,kg,reps):
 if not (math.isfinite(kg) and 0<kg<=1000 and 1<=reps<=100):raise ValueError('invalid load/reps')
 p=calibrated(store,exercise,kg)
 if p['predicted'] is None:raise ValueError('학습 범위 부족')
 with store.db:
  cols={r[1] for r in store.db.execute('pragma table_info(forecasts)')}
  if 'raw_predicted' not in cols:store.db.execute('alter table forecasts add column raw_predicted REAL')
  c=store.db.execute('insert into forecasts(exercise,ts,kg,reps,predicted,model_id,raw_predicted) values(?,?,?,?,?,?,?)',(exercise,time.time(),kg,reps,p['predicted'],p['model_id'],p['raw']))
 return dict(id=c.lastrowid,**p)
