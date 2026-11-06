# 每一格：後製平滑 → 以 potrace 描成向量（座標換回原稿）
import numpy as np, json, potrace, sys
from multiprocessing import Pool
import clean
Q=dict(x=380,y=740,w=575,h=480); S=3; S_=S
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
# 伴的兩點獨立成一層（會像腳一樣晃），逐格輪廓裡不能含有它們
_o=np.array(Image.open('source/xiangban-logo.jpg').convert('L'))<128
_lab,_=ndimage.label(_o)
_yy,_xx=np.mgrid[0:Q['h']*S,0:Q['w']*S]
_d=(_lab==4)|(_lab==5)
DOTS=ndimage.binary_dilation(_d[(_yy//S+Q['y']).clip(0,1999),(_xx//S+Q['x']).clip(0,1389)],iterations=4)
def job(i):
    # 只保留移動部分附近的輪廓；靜態筆畫一律由原稿向量繪製，不會每格重描而蠕動
    C,M=clean.clean(i,want_m=True)   # M：這一格實際顯示的移動部分（開頭幾格含設計稿的手）
    F=np.array(Image.open(f'cap/full_{i:03d}.png').convert('L'))<128
    S=F&~M                                                     # 這一格的靜態筆畫
    staticOnly=ndimage.binary_dilation(S,iterations=4)&~ndimage.binary_dilation(M,iterations=6)
    H_,W_=S.shape; yy,xx=np.mgrid[0:H_,0:W_]; lx=xx/S_+Q['x']; ly=yy/S_+Q['y']
    staticOnly&=~((lx>735)&(lx<792)&(ly>935)&(ly<1010))   # 拐杖握把：兩手交會處，不做此裁切
    return path(C&ndimage.binary_dilation(M,iterations=24)&~staticOnly&~DOTS)
if __name__=='__main__':
    n=int(sys.argv[1])
    with Pool(4) as p: frames=p.map(job,range(n))
    json.dump({'Q':Q,'fps':30,'frames':frames},open('frames.json','w'))
    print('frames',len(frames),'KB',sum(len(f) for f in frames)//1024)
