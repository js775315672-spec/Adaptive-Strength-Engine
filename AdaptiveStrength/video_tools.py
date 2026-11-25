import cv2
import numpy as np

def locate(frame, template, x, y, radius=32):
    h,w=template.shape; a=max(0,x-radius-w//2); b=max(0,y-radius-h//2)
    roi=frame[b:y+radius+h//2+1,a:x+radius+w//2+1]
    if min(template.shape)<3 or template.std()<8 or roi.shape[0]<h or roi.shape[1]<w:return None
    scores=cv2.matchTemplate(roi,template,cv2.TM_CCOEFF_NORMED)
    _,best,_,(u,v)=cv2.minMaxLoc(scores)
    scores[max(0,v-h//2):v+h//2+1,max(0,u-w//2):u+w//2+1]=-1
    if best<.8 or best-float(scores.max())<.08:return None
    return a+u+w//2,b+v+h//2,float(best)

def render(source,dest,trace,center):
    cap=cv2.VideoCapture(str(source)); fps=cap.get(cv2.CAP_PROP_FPS); w=int(cap.get(3)); h=int(cap.get(4))
    if not cap.isOpened() or fps<=0:cap.release();raise ValueError('invalid video')
    out=cv2.VideoWriter(str(dest),cv2.VideoWriter_fourcc(*'mp4v'),fps,(w,h)); i=0; j=0; path=[]
    try:
        if not out.isOpened():raise ValueError('encoder unavailable')
        while True:
            ok,f=cap.read()
            if not ok:break
            t=i/fps
            while j<len(trace) and trace[j]['t']<=t:
                q=trace[j];path.append((round(q['x']),round(q['y'])));j+=1
            cv2.line(f,(round(center),0),(round(center),h-1),(255,200,0),1)
            if len(path)>1:cv2.polylines(f,[np.array(path,np.int32)],False,(0,180,255),2)
            if j and t-trace[j-1]['t']<=.1:
                q=trace[j-1];cv2.putText(f,f"{q['speed']:.2f} m/s {'SLOW' if q['slow'] else ''}",(8,24),0,.55,(0,0,255) if q['slow'] else (255,255,255),2)
            out.write(f);i+=1
    finally:cap.release();out.release()
    if not i:raise ValueError('empty video')
    return i
