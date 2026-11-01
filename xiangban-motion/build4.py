import numpy as np, potrace, json, math
from PIL import Image, ImageDraw
from scipy import ndimage
img=np.array(Image.open('source/xiangban-logo.jpg').convert('L'))
H,W=img.shape; m=img<128; lab,_=ndimage.label(m); c=lambda i: lab==i
YY,XX=np.mgrid[0:H,0:W]
def poly(p):
    im=Image.new('L',(W,H),0); ImageDraw.Draw(im).polygon(p,fill=1); return np.array(im).astype(bool)
def beyond(p,u,off=0):  # (x-p)·u > off
    return (XX-p[0])*u[0]+(YY-p[1])*u[1] > off
def path(mask):
    pl=potrace.Bitmap(~mask).trace(turdsize=10,alphamax=1.0,opticurve=True,opttolerance=0.2); out=[]
    for cv in pl:
        s=cv.start_point; d=f"M{s.x:.1f} {s.y:.1f}"
        for g in cv.segments:
            d+= f"L{g.c.x:.1f} {g.c.y:.1f}L{g.end_point.x:.1f} {g.end_point.y:.1f}" if g.is_corner else f"C{g.c1.x:.1f} {g.c1.y:.1f} {g.c2.x:.1f} {g.c2.y:.1f} {g.end_point.x:.1f} {g.end_point.y:.1f}"
        out.append(d+"Z")
    return "".join(out)
def unit(a,b):
    v=np.array(b,float)-np.array(a,float); return v/np.linalg.norm(v)
# ---- 巷 ----
xS=(540,1098); xW=(648,1140); xu=unit(xS,xW)
upper=YY<1200
xArm = c(6)&upper&beyond(xS,xu)&~beyond(xW,xu,5)
xHand= c(6)&upper&beyond(xW,xu)&(XX>590)
xStatic = c(6)&~(upper&beyond(xS,xu,1))
xL=float(np.dot(np.array(xW)-xS,xu))
# ---- 伴 ----
shaft=(YY>1001)&(XX>760)
cres = poly([(768,962),(845,928),(845,1001),(768,1001)])
cresO = poly([(762,965),(845,928),(845,1001),(762,1001)])
bS=(863,756); bW=(756,926); bu=unit(bS,bW)
bArm = c(2)&~shaft&~cres&~beyond(bW,bu,5)
bHand= c(2)&~shaft&~cres&beyond(bW,bu)
cane = c(2)&(shaft|cresO)
bL=float(np.dot(np.array(bW)-bS,bu))
win=ndimage.binary_fill_holes(c(6))&~c(6); wl,_=ndimage.label(win); win=wl==wl[1145,370]
L={'xiangTop':path(c(1)),'xiangStatic':path(xStatic),'xiangArm':path(xArm),'xiangHand':path(xHand),
   'banArm':path(bArm),'banHand':path(bHand),'cane':path(cane),'banMain':path(c(3)),'dot1':path(c(4)),'dot2':path(c(5)),'window':path(win),
   'geo':{'xS':xS,'xu':list(xu),'xL':xL,'bS':bS,'bu':list(bu),'bL':bL}}
json.dump(L,open('layers4.json','w')); print(L['geo'])
