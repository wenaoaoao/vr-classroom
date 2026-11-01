import numpy as np, potrace, json, math, sys
from PIL import Image, ImageDraw
from scipy import ndimage, optimize
SRC=sys.argv[1] if len(sys.argv)>1 else "source/xiangban-logo.jpg"
img=np.array(Image.open(SRC).convert('L'))
H,W=img.shape; m=img<128; lab,_=ndimage.label(m); c=lambda i: lab==i
YY,XX=np.mgrid[0:H,0:W]
def poly(p):
    im=Image.new('L',(W,H),0); ImageDraw.Draw(im).polygon(p,fill=1); return np.array(im).astype(bool)
def beyond(p,u,off=0): return (XX-p[0])*u[0]+(YY-p[1])*u[1] > off
def path(mask):
    pl=potrace.Bitmap(~mask).trace(turdsize=10,alphamax=1.0,opticurve=True,opttolerance=0.2); out=[]
    for cv in pl:
        s=cv.start_point; d=f"M{s.x:.1f} {s.y:.1f}"
        for g in cv.segments:
            d+= f"L{g.c.x:.1f} {g.c.y:.1f}L{g.end_point.x:.1f} {g.end_point.y:.1f}" if g.is_corner else f"C{g.c1.x:.1f} {g.c1.y:.1f} {g.c2.x:.1f} {g.c2.y:.1f} {g.end_point.x:.1f} {g.end_point.y:.1f}"
        out.append(d+"Z")
    return "".join(out)
def bez(P,u):
    u=np.asarray(u)[:,None]; return (1-u)**3*P[0]+3*(1-u)**2*u*P[1]+3*(1-u)*u**2*P[2]+u**3*P[3]
def fit(pts,edt):
    pts=np.array(pts,float); A=pts[0]; B=pts[-1]
    t0=pts[2]-pts[0]; t0/=np.linalg.norm(t0); t1=pts[-1]-pts[-3]; t1/=np.linalg.norm(t1)
    def err(k):
        P=np.array([A,A+k[0]*t0,B-k[1]*t1,B]); cur=bez(P,np.linspace(0,1,300))
        return sum(np.min(np.linalg.norm(cur-p,axis=1)) for p in pts)
    k=optimize.minimize(err,[30,30],method='L-BFGS-B',bounds=[(10,90),(10,90)]).x
    P=np.array([A,A+k[0]*t0,B-k[1]*t1,B])
    us=np.linspace(0,1,21); pts=bez(P,us)
    d=(-3*(1-us)[:,None]**2*P[0]+(3*(1-us)**2-6*(1-us)*us)[:,None]*P[1]+(6*(1-us)*us-3*us**2)[:,None]*P[2]+3*us[:,None]**2*P[3])
    d/=np.linalg.norm(d,axis=1)[:,None]; nrm=np.stack([-d[:,1],d[:,0]],1)
    g=ndimage.map_coordinates
    w=[];o=[]
    for p,n in zip(pts,nrm):
        def reach(sign):
            t=0.0
            while t<80:
                q=p+sign*(t+.25)*n
                if g(img.astype(float),[[q[1]],[q[0]]],order=1)[0]>=128: break
                t+=.25
            return t
        a,b=reach(1),reach(-1); w.append(a+b); o.append((a-b)/2)
    return dict(A=A.tolist(),B=B.tolist(),t0=t0.tolist(),t1=t1.tolist(),k=k.tolist(),w=w,o=o)
c6,c2=c(6),c(2)
# ---- 巷 手臂：肩膀 x=542 起，手腕 x=648 ----
xc=[(x,(lambda ys:(ys.min()+ys.max())/2)(np.where(c6[1040:1200,x])[0]+1040)) for x in range(549,634,3)]
X=fit(xc,ndimage.distance_transform_edt(c6))
upper=(YY<1200)&(XX>=528)
xStatic=c6&~(upper&beyond(X['A'],X['t0'],0))
xArm  =c6&upper&beyond(X['A'],X['t0'],-1)&~beyond(X['B'],X['t1'],1)
xHand =c6&upper&beyond(X['B'],X['t1'],-1)&(XX>590)
# ---- 伴 手臂：撇頂端 y≈784 以下到手腕 ----
bc=[((lambda xs:(xs.min()+xs.max())/2)(np.where(c2[y,640:900])[0]+640),y) for y in range(784,908,3)]
B_=fit(bc,ndimage.distance_transform_edt(c2))
shaft=(YY>1001)&(XX>760)
cres=poly([(762,965),(845,928),(845,1001),(762,1001)])
bCap =c2&~shaft&~beyond(B_['A'],B_['t0'],0)
bArm =c2&~shaft&~cres&beyond(B_['A'],B_['t0'],-1)&~beyond(B_['B'],B_['t1'],1)
bHand=c2&~shaft&~cres&beyond(B_['B'],B_['t1'],-1)
cresO=poly([(757,967),(845,928),(845,1001),(757,1001)])   # 握把多留一點疊在手下
import os
_k1='key1.png' if os.path.exists('key1.png') else 'source/key1.png'
key1=np.array(Image.open(_k1).convert('L'))<128
handleL=key1&poly([(708,950),(772,950),(772,1003),(708,1003)])&c2   # 設計稿第 1 張：握把左半
cane =c2&(shaft|cresO) | handleL
win=ndimage.binary_fill_holes(c6)&~c6; wl,_=ndimage.label(win); win=wl==wl[1145,370]
out={'paths':{'xiangTop':path(c(1)),'xiangStatic':path(xStatic),'xiangArm':path(xArm),'xiangHand':path(xHand),
  'banCap':path(bCap),'banArm':path(bArm),'banHand':path(bHand),'cane':path(cane),
  'banMain':path(c(3)),'dot1':path(c(4)),'dot2':path(c(5)),'window':path(win)},
  'rig':{'xiang':X,'ban':B_}}
# 巷的屋簷上緣（抬手時用來做隆起過渡）
_A=np.array(X['A']); _t=np.array(X['t0']); _n=np.array([-_t[1],_t[0]]); _T0=_A-_n*X['w'][0]/2
_xs=list(range(475,int(_T0[0])+1,3))
out['rig']['xiang']['topEdge']={'x':_xs,'y':[float(980+np.where(c6[980:1120,x])[0].min()) for x in _xs],'T0':_T0.tolist()}
json.dump(out,open('layers5.json','w'))
print(json.dumps(out['rig'],indent=0)[:900])
