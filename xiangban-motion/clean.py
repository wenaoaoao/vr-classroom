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
_K={}
def key_mask(n,shape):
    if n not in _K:
        base=os.path.dirname(os.path.abspath(__file__))
        fn=f'key{n}reg.json'
        reg=json.load(open(os.path.join(base,'source',fn) if os.path.exists(os.path.join(base,'source',fn)) else os.path.join(base,fn)))
        src=Image.open(os.path.join(base,'source','keyposes.jpg') if os.path.exists(os.path.join(base,'source','keyposes.jpg')) else 'source/keyposes.jpg').convert('L')
        Qx,Qy=380,740; s,ox,oy=reg['s'],reg['ox'],reg['oy']; H,W=shape
        g=np.array(src.transform((W,H),Image.AFFINE,(s/S,0,Qx*s+ox,0,s/S,Qy*s+oy),resample=Image.BICUBIC,fillcolor=255)).astype(float)
        _K[n]=ndimage.gaussian_filter(g,1.2)<128
    return _K[n]
def key1_mask(shape): return key_mask(1,shape)
def sdf(m): return ndimage.distance_transform_edt(m)-ndimage.distance_transform_edt(~m)
def key1_weight(t):  # 0.45 秒前完全用手稿，0.75 秒前漸變到骨架
    if t<=.45: return 1.0
    if t>=.75: return 0.0
    u=(t-.45)/.30; return 1-u*u*(3-2*u)
def key2_weight(t):   # 握住期間用設計稿第 2 張
    if t<1.35 or t>2.45: return 0.0
    if t<1.6: u=(t-1.35)/.25; return u*u*(3-2*u)
    if t<=2.2: return 1.0
    u=(t-2.2)/.25; return 1-u*u*(3-2*u)
def clasp_shift(K,t):  # 握住時兩手一起往上帶：越靠近相握處位移越多，手臂根部不動
    c=min(1,max(0,(t-1.5)/0.7)); b=(1-np.cos(2*np.pi*c))/2; up=5.0*b*S
    if up<0.05: return K
    H_,W_=K.shape; yy,xx=np.mgrid[0:H_,0:W_]
    cx,cy=(705-380)*S,(1060-740)*S; d=np.hypot(xx-cx,yy-cy)/S
    w=np.clip((150-d)/100,0,1); w=w*w*(3-2*w)
    return ndimage.map_coordinates(K.astype(float),[yy+up*w,xx],order=1)>0.5
def clean(i, want_m=False):
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
    w2=key2_weight(i/30)
    if w2>0:
        K2=clasp_shift(key_mask(2,F.shape),i/30); R2=ndimage.binary_dilation(M,iterations=45)
        H_,W_=F.shape; yy,xx=np.mgrid[0:H_,0:W_]; lx=xx/S+380; ly=yy/S+740
        R2&=~(((ly>=1079)&(lx<=524.5)) | ((ly<1079)&(lx<446+(ly-1042)*0.889)&(ly>1000)))
        v=(1-w2)*sdf(F)+w2*sdf(K2); F=np.where(R2,v>0,F); M=M|(R2&F)
    sg=sigma_for(i)
    if sg<=0.05 or not M.any(): return (F,M) if want_m else F
    band=ndimage.binary_dilation(M,iterations=10)
    f=F.astype(float); b1=ndimage.gaussian_filter(f,sg); b2=ndimage.gaussian_filter(f,sg*2.4)
    # 接縫點周圍（半徑約 20 原稿 px）改用較強的平滑，向外平順過渡
    H,W=F.shape; yy,xx=np.mgrid[0:H,0:W]; wgt=np.zeros((H,W))
    for k,(R) in (('banWrist',62),('xiangWrist',55),('xiangShoulder',50),('banL',55),('banR',55),('xiangL',45),('xiangR',45)):
        x,y=J[i][k]; d=np.hypot(xx-x,yy-y); wgt=np.maximum(wgt,np.clip((R*1.4-d)/(R*.4),0,1))
    wgt*=sg/4.5
    v=(1-wgt)*b1+wgt*b2
    out=np.where(band,v>0.5,F)
    return (out,M) if want_m else out
if __name__=='__main__':
    for i in map(int,sys.argv[1:]):
        C=clean(i); F=np.array(Image.open(f'cap/full_{i:03d}.png').convert('L'))<128
        rgb=np.full(F.shape+(3,),255,np.uint8); rgb[C&F]=(100,85,75); rgb[F&~C]=(255,0,0); rgb[C&~F]=(0,120,255)
        Image.fromarray(rgb).save(f'cl_{i:03d}.png')
