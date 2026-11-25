import cv2, math
from video_tools import locate
from advanced import split

def track_video(path, start, end, x, y, width, scale):
    if not all(math.isfinite(v) for v in (start,end,x,y,width,scale)) or not (0<=start<end<=start+120 and 32<=width<=1920 and scale>0): raise ValueError('invalid tracking parameters')
    cap=cv2.VideoCapture(str(path)); points=[]; scores=[]
    try:
        fps=cap.get(cv2.CAP_PROP_FPS)
        if not cap.isOpened() or not 5<=fps<=240: raise ValueError('unsupported FPS')
        first=round(start*fps); cap.set(cv2.CAP_PROP_POS_FRAMES,first)
        for i in range(first,math.floor(end*fps)+1):
            ok,f=cap.read()
            if not ok: raise ValueError('video ended before selected interval')
            f=cv2.resize(f,(int(width),round(f.shape[0]*width/f.shape[1]))); gray=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY)
            if not points:
                x,y=round(x),round(y)
                if not 8<=x<gray.shape[1]-8 or not 8<=y<gray.shape[0]-8: raise ValueError('seed outside frame')
                template=gray[y-7:y+8,x-7:x+8].copy()
                if template.std()<8: raise ValueError('low texture seed')
            else:
                hit=locate(gray,template,x,y)
                if hit is None: raise ValueError(f'tracking lost at {i/fps:.3f}s; reseed shorter interval')
                x,y,s=hit; scores.append(s)
            points.append([i/fps,x,y])
        return dict(points=points,reps=split(points,scale),min_match=min(scores,default=0),fps=fps)
    finally: cap.release()
