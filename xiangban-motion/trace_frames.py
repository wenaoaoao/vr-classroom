# 每一格：後製平滑 → 以 potrace 描成向量（座標換回原稿）
import numpy as np, json, potrace, sys
from multiprocessing import Pool
import clean
Q=dict(x=380,y=740,w=575,h=480); S=3
def path(mask):
    pl=potrace.Bitmap(~mask).trace(turdsize=40,alphamax=1.0,opticurve=True,opttolerance=0.3); out=[]
    f=lambda p:f"{p.x/S+Q['x']:.1f} {p.y/S+Q['y']:.1f}"
    for cv in pl:
        d="M"+f(cv.start_point)
        for g in cv.segments:
            d+= f"L{f(g.c)}L{f(g.end_point)}" if g.is_corner else f"C{f(g.c1)} {f(g.c2)} {f(g.end_point)}"
        out.append(d+"Z")
    return "".join(out)
from PIL import Image
from scipy import ndimage
def job(i):
    # 只保留移動部分附近的輪廓；靜態筆畫一律由原稿向量繪製，不會每格重描而蠕動
    C,M=clean.clean(i,want_m=True)   # M：這一格實際顯示的移動部分（開頭幾格含設計稿的手）
    F=np.array(Image.open(f'cap/full_{i:03d}.png').convert('L'))<128
    S=F&~M                                                     # 這一格的靜態筆畫
    staticOnly=ndimage.binary_dilation(S,iterations=4)&~ndimage.binary_dilation(M,iterations=6)
    return path(C&ndimage.binary_dilation(M,iterations=24)&~staticOnly)
if __name__=='__main__':
    n=int(sys.argv[1])
    with Pool(4) as p: frames=p.map(job,range(n))
    json.dump({'Q':Q,'fps':30,'frames':frames},open('frames.json','w'))
    print('frames',len(frames),'KB',sum(len(f) for f in frames)//1024)
