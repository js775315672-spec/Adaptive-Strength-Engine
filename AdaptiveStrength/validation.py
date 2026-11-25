"""Independent comparison of tracked and manually annotated ascending trajectories."""
import numpy as np
from engine import analyze

def audit(pred, reference, scale, center, kg, synthetic=False):
    p,r=np.asarray(pred,float),np.asarray(reference,float)
    for a in (p,r):
        if a.ndim!=2 or a.shape[1]!=3 or len(a)<5 or not np.isfinite(a).all() or np.any(np.diff(a[:,0])<=0): raise ValueError('invalid trajectory')
    if not np.isfinite([scale,center,kg]).all() or scale<=0 or kg<=0: raise ValueError('invalid calibration')
    if abs(p[0,0]-r[0,0])>0.001 or abs(p[-1,0]-r[-1,0])>0.001 or max(np.diff(r[:,0]))>.101: raise ValueError('reference must cover same ascent with <=100 ms spacing')
    xy=np.column_stack([np.interp(p[:,0],r[:,0],r[:,i]) for i in (1,2)])
    err=np.linalg.norm(p[:,1:]-xy,axis=1)*scale*100
    a,b=analyze(p,scale,center,kg),analyze(r,scale,center,kg)
    result=dict(position_rmse_cm=float(np.sqrt(np.mean(err**2))),position_max_cm=float(max(err)),speed_error_mps=abs(a['mean_speed']-b['mean_speed']),path_error_pp=abs(a['error_pct']-b['error_pct']),grind_error_s=abs(a['grind_seconds']-b['grind_seconds']),predicted=a,reference=b)
    passed=result['position_rmse_cm']<=1 and result['position_max_cm']<=2 and result['speed_error_mps']<=.05 and result['path_error_pp']<=2 and result['grind_error_s']<=.2
    return dict(**result,threshold_pass=bool(passed),source='synthetic' if synthetic else 'unverified_user_reference',learning_approved=False)
