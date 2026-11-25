import numpy as np
from engine import analyze,stats

def detail(points,scale,center,kg,grind=.15,joints=None):
 r=analyze(points,scale,center,kg,grind); t,x,y=np.asarray(points,float).T; dt=np.diff(t); ys=y.copy();ys[1:-1]=(y[:-2]+2*y[1:-1]+y[2:])/4; v=-np.diff(ys)*scale/dt
 progress=(y[0]-ys[:-1])*scale/r['travel']; valid=(progress>=.1)&(progress<=.9); slow=valid&(v>=0)&(v<grind); runs=[]; start=None
 for i,flag in enumerate(np.r_[slow,False]):
  if flag and start is None:start=i
  if not flag and start is not None:
   if t[i]-t[start]>=.15:
    j=start+int(np.argmin(v[start:i]));runs.append(dict(start=float(t[start]),end=float(t[i]),seconds=float(t[i]-t[start]),min_speed=float(v[j]),position_pct=float(progress[j]*100),recovery_speed=float(max(v[i:min(i+5,len(v))],default=v[j]))))
   start=None
 r['grinding']=runs;r['grind_seconds']=sum(a['seconds'] for a in runs);r['trace']=[dict(t=float(t[i]),x=float(x[i]),y=float(y[i]),speed=float(v[i]),deviation=float((x[i]-center)*scale),slow=bool(slow[i])) for i in range(len(v))]
 r['joint_moments']={}
 for name,j in (joints or {}).items():
  a=np.asarray(j,float)
  if a.shape!=t.shape or not np.isfinite(a).all():raise ValueError('joint sample mismatch')
  arm=abs(x-a)*scale;r['joint_moments'][name]={'arm_m':stats(arm),'bar_only_nm':stats(arm*kg*9.80665)}
 return r

def split(points,scale):
 a=np.asarray(points,float)
 if a.ndim!=2 or a.shape[1]!=3 or len(a)<5 or not np.isfinite(a).all() or not scale>0:raise ValueError('invalid track')
 result=[];start=None;top=None
 for i in range(1,len(a)):
  dt=a[i,0]-a[i-1,0]
  if not 0<dt<=.2: start=top=None;continue
  speed=(a[i-1,2]-a[i,2])*scale/dt
  if speed>.04:
   if start is None:start=i-1
   top=i
  elif speed<-.04 and start is not None:
   if top-start>=4 and a[top,0]-a[start,0]>=.25 and (a[start,2]-a[top,2])*scale>=.08:result.append(a[start:top+1].tolist())
   start=top=None
 return result
