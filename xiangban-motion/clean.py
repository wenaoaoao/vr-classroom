import numpy as np, sys
from PIL import Image
from scipy import ndimage
S=3
import json, os
J=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'cap','joints.json'))) if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)),'cap','joints.json')) else None
def sigma_for(i,fps=30):
    t=i/fps
    return 4.5 if t<2.7 else max(0.0,4.5*(3.0-t)/0.3)      # 鬆開快結束時逐漸停止平滑
# 設計稿第 1 張（精準對位後）在 Q 區域、3 倍解析度下的輪廓
_K1=None
def key1_mask(shape):
    global _K1
    if _K1 is None:
        base=os.path.dirname(os.path.abspath(__file__))
        reg=json.load(open(os.path.join(base,'source','key1reg.json') if os.path.exists(os.path.join(base,'source','key1reg.json')) else os.path.join(base,'key1reg.json')))
        src=Image.open(os.path.join(base,'source','keyposes.jpg') if os.path.exists(os.path.join(base,'source','keyposes.jpg')) else 'source/keyposes.jpg').convert('L')
        Qx,Qy=380,740; s,ox,oy=reg['s'],reg['ox'],reg['oy']; H,W=shape
        g=np.array(src.transform((W,H),Image.AFFINE,(s/S,0,Qx*s+ox,0,s/S,Qy*s+oy),resample=Image.BICUBIC,fillcolor=255)).astype(float)
        _K1=ndimage.gaussian_filter(g,1.2)<128
    return _K1
def sdf(m): return ndimage.distance_transform_edt(m)-ndimage.distance_transform_edt(~m)
def key1_weight(t):  # 0.45 秒前完全用手稿，0.75 秒前漸變到骨架
    if t<=.45: return 1.0
    if t>=.75: return 0.0
    u=(t-.45)/.30; return 1-u*u*(3-2*u)
def clean(i):
    F=np.array(Image.open(f'cap/full_{i:03d}.png').convert('L'))<128
    M=np.array(Image.open(f'cap/mov_{i:03d}.png').convert('L'))<128
    wk=key1_weight(i/30)
    if wk>0:   # 開頭：以設計稿第 1 張的輪廓為準，用距離場漸變到骨架
        K=key1_mask(F.shape); R=ndimage.binary_dilation(M,iterations=45)   # 只在兩隻手附近換成手稿輪廓
        H_,W_=F.shape; yy,xx=np.mgrid[0:H_,0:W_]; lx=xx/S+380; ly=yy/S+740
        keep=((ly>=1079)&(lx<=524.5)) | ((ly<1079)&(lx<446+(ly-1042)*0.889)&(ly>1000))   # 「巳」與屋頂三角形空洞一律用原稿
        R&=~keep
        v=(1-wk)*sdf(F)+wk*sdf(K); F=np.where(R,v>0,F)
        M=M|(R&F)
    sg=sigma_for(i)
    if sg<=0.05 or not M.any(): return F
    band=ndimage.binary_dilation(M,iterations=10)
    f=F.astype(float); b1=ndimage.gaussian_filter(f,sg); b2=ndimage.gaussian_filter(f,sg*2.4)
    # 接縫點周圍（半徑約 20 原稿 px）改用較強的平滑，向外平順過渡
    H,W=F.shape; yy,xx=np.mgrid[0:H,0:W]; wgt=np.zeros((H,W))
    for k,(R) in (('banWrist',62),('xiangWrist',55),('xiangShoulder',50),('banL',55),('banR',55),('xiangL',45),('xiangR',45)):
        x,y=J[i][k]; d=np.hypot(xx-x,yy-y); wgt=np.maximum(wgt,np.clip((R*1.4-d)/(R*.4),0,1))
    wgt*=sg/4.5
    v=(1-wgt)*b1+wgt*b2
    return np.where(band,v>0.5,F)
if __name__=='__main__':
    for i in map(int,sys.argv[1:]):
        C=clean(i); F=np.array(Image.open(f'cap/full_{i:03d}.png').convert('L'))<128
        rgb=np.full(F.shape+(3,),255,np.uint8); rgb[C&F]=(100,85,75); rgb[F&~C]=(255,0,0); rgb[C&~F]=(0,120,255)
        Image.fromarray(rgb).save(f'cl_{i:03d}.png')
