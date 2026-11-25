import numpy as np
from engine import stats

def profile(points,scale):
 a=np.asarray(points,float); travel=(a[0,2]-a[-1,2])*scale
 if travel<=0: raise ValueError('invalid ascent')
 p=(a[0,2]-a[:,2])*scale/travel
 if np.any(np.diff(p)<-.03): raise ValueError('nonmonotonic ascent')
 p=np.maximum.accumulate(p); x=(a[:,1]-a[0,1])*scale
 return np.interp(np.linspace(0,1,21),p,x).tolist()

def compare(rows,kg,curve):
 refs=[p for r in rows if abs(r['kg']-kg)<=10 and r['rpe']<=8 and r['data'].get('successful') for p in r['data'].get('profiles',[]) if p is not None]
 if len(refs)<5:return {'support':len(refs),'rms_m':None}
 ref=np.median(refs,axis=0); d=np.asarray(curve)-ref
 return {'support':len(refs),'rms_m':float(np.sqrt(np.mean(d*d))),'reference_m':ref.tolist(),'deviation_m':stats(abs(d))}

def rest_fatigue(rows,kg,reps,rest):
 if rest is None:return {'support':0,'loss':None}
 a=[r['data']['loss'] for r in rows if abs(r['kg']-kg)<=5 and r['reps']==reps and r['data'].get('rest_seconds') is not None and abs(r['data']['rest_seconds']-rest)<=30]
 return {'support':len(a),'loss':float(np.median(a)) if len(a)>=5 else None}

def joint_samples(points, joints):
 t=np.asarray(points,float)[:,0]; out={}
 for name, samples in joints.items():
  a=np.asarray(samples,float)
  if a.shape!=(len(t),3) or not np.isfinite(a).all() or not np.allclose(a[:,0],t,atol=.001,rtol=0) or np.any(a[:,2]<.75) or np.any(a[:,2]>1):raise ValueError('joint timestamps/confidence invalid')
  out[name]=a[:,1].tolist()
 return out
