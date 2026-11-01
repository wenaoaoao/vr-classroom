# 每一格：後製平滑 → 以 potrace 描成向量（座標換回原稿）
import numpy as np, json, potrace, sys
from multiprocessing import Pool
import clean
Q=dict(x=380,y=740,w=575,h=480); S=3
def path(mask):
    pl=potrace.Bitmap(~mask).trace(turdsize=6,alphamax=1.0,opticurve=True,opttolerance=0.3); out=[]
    f=lambda p:f"{p.x/S+Q['x']:.1f} {p.y/S+Q['y']:.1f}"
    for cv in pl:
        d="M"+f(cv.start_point)
        for g in cv.segments:
            d+= f"L{f(g.c)}L{f(g.end_point)}" if g.is_corner else f"C{f(g.c1)} {f(g.c2)} {f(g.end_point)}"
        out.append(d+"Z")
    return "".join(out)
def job(i): return path(clean.clean(i))
if __name__=='__main__':
    n=int(sys.argv[1])
    with Pool(4) as p: frames=p.map(job,range(n))
    json.dump({'Q':Q,'fps':30,'frames':frames},open('frames.json','w'))
    print('frames',len(frames),'KB',sum(len(f) for f in frames)//1024)
