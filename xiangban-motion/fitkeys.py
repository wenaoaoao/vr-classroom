import numpy as np, json, math
from PIL import Image
from scipy import ndimage, signal
orig=np.array(Image.open('/tmp/claude-0/-home-user-vr-classroom/55aee804-124e-5075-8d61-d924741d0c98/images/1.jpg').convert('L'))<128
H,W=orig.shape; YY,XX=np.mgrid[0:H,0:W]
lab,_=ndimage.label(orig)
R=json.load(open('layers5.json'))['rig']
def beyond(p,u,off=0): return (XX-p[0])*u[0]+(YY-p[1])*u[1]>off
c6,c2=lab==6,lab==2
from PIL import ImageDraw
def poly(p):
    im=Image.new('L',(W,H),0); ImageDraw.Draw(im).polygon(p,fill=1); return np.array(im).astype(bool)
X,B=R['xiang'],R['ban']
xHand=c6&(YY<1200)&beyond(X['B'],X['t1'],-1)&(XX>590)
shaft=(YY>1001)&(XX>760); cres=poly([(762,965),(845,928),(845,1001),(762,1001)])
bHand=c2&~shaft&~cres&beyond(B['B'],B['t1'],-1)
def fit(key,hand,W0,win,angs):
    best=None
    ys,xs=np.where(hand); y0,y1,x0,x1=ys.min()-20,ys.max()+20,xs.min()-20,xs.max()+20
    tpl=hand[y0:y1,x0:x1].astype(float)
    ring=ndimage.binary_dilation(hand[y0:y1,x0:x1],iterations=8)&~hand[y0:y1,x0:x1]
    cx,cy=W0[0]-x0,W0[1]-y0
    kx0,ky0,kx1,ky1=win; K=key[ky0:ky1,kx0:kx1].astype(float)*2-1
    for a in angs:
        t=ndimage.rotate(tpl,a,reshape=False,order=1)  # rotates about center of tpl
        rg=ndimage.rotate(ring.astype(float),a,reshape=False,order=1)
        tt=t-rg   # 手掌 +1，外圈 -1（外圈必須是白的）
        cor=signal.fftconvolve(K,tt[::-1,::-1],mode='valid')
        iy,ix=np.unravel_index(np.argmax(cor),cor.shape); sc=cor[iy,ix]/(t.sum()+rg.sum())
        if best is None or sc>best[0]:
            # 求出手腕點經旋轉後的新位置
            h,w=t.shape; ccx,ccy=(w-1)/2,(h-1)/2; r=math.radians(a)
            dx,dy=cx-ccx,cy-ccy
            # ndimage.rotate 正角度 = 影像逆時針（y 向下座標下為 -a）
            nx=ccx+dx*math.cos(r)+dy*math.sin(r); ny=ccy-dx*math.sin(r)+dy*math.cos(r)
            best=(sc,a,kx0+ix+nx,ky0+iy+ny)
    return best
out={}
for k in [1,2]:
    key=np.array(Image.open(f'source/key{k}.png'))<128
    bx=fit(key,xHand,X['B'],(380,900,900,1300),range(-60,61,2))
    bb=fit(key,bHand,B['B'],(560,700,900,1120),range(-60,61,2))
    a0x=math.degrees(math.atan2(X['t1'][1],X['t1'][0])); a0b=math.degrees(math.atan2(B['t1'][1],B['t1'][0]))
    out[k]={'xiang':{'score':bx[0],'P':[bx[2],bx[3]],'ang':a0x-bx[1]},'ban':{'score':bb[0],'P':[bb[2],bb[3]],'ang':a0b-bb[1]}}
print(json.dumps(out,indent=1))
json.dump(out,open('source/keys.json','w'))
