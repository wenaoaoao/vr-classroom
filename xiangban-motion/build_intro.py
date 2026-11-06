# 開頭「被寫出來」的書寫遮罩 → intro.json
# 依中文筆順，把 0 秒畫面（收起姿勢）的骨架分支組成筆畫；每筆沿骨架用圓頭粗線逐漸畫出，
# 並以「離哪一筆骨架最近」切出每筆的範圍，避免粗線提早露出旁邊的筆畫。兩隻手最後才長出來。
import numpy as np, json, potrace
from PIL import Image
from scipy import ndimage
m=np.array(Image.open('source/pose1-full.png').convert('L'))<128
B=json.load(open('source/pose1-branches.json'))['branches']
OX,OY=0,0
# 筆順：每筆 = [(分支編號, 是否反向)...]
STROKES=[
 ('巷 橫',      [(9,0),(10,0),(8,0)]),
 ('巷 左豎',    [(3,0),(11,0)]),
 ('巷 右豎',    [(4,0),(12,0)]),
 ('巷 屋頂',    [(21,0),(23,0),(22,0)]),
 ('巷 撇',      [(24,0),(31,0)]),
 ('巷 捺',      [(25,0),(29,0)]),
 ('巳 橫折',    [(32,0),(30,0),(37,1)]),
 ('巳 豎彎',    [(36,0),(38,0)]),
 ('伴 撇',      [(0,0)]),
 ('拐杖',       [(19,0),(16,0),(20,0),(39,0),(40,0)]),
 ('半 左點',    [(1,0),(6,0),(7,0)]),
 ('半 右點',    [(2,0)]),
 ('半 上橫',    [(17,0),(15,0)]),
 ('半 下橫',    [(34,0),(33,0)]),
 ('半 豎',      [(5,0),(18,0),(35,0)]),
]
HANDS=[('伴 手',(715,875),48),('巷 手',(508,1063),44)]   # 伴（長者）先
def oriented(bi,rev):
    p=B[bi]
    # 自動決定方向：從上（或左）往下（或右）寫；rev=1 則相反
    a,b=p[0],p[-1]
    first_is_start=(a[1]+0.35*a[0]) <= (b[1]+0.35*b[0])
    q=p if first_is_start else p[::-1]
    return q[::-1] if rev else q
def chain(parts):
    out=[]
    for bi,rev in parts:
        q=oriented(bi,rev)
        if out:
            # 接在上一段最近的一端
            if np.hypot(q[-1][0]-out[-1][0],q[-1][1]-out[-1][1])<np.hypot(q[0][0]-out[-1][0],q[0][1]-out[-1][1]): q=q[::-1]
        out+=q
    return out
def simplify(pl,step=6):
    pl=np.array(pl,float); keep=[pl[0]]
    for p in pl[1:]:
        if np.hypot(*(p-keep[-1]))>=step: keep.append(p)
    keep.append(pl[-1]); return np.array(keep)
H,W=m.shape; YY,XX=np.mgrid[0:H,0:W]
lab=np.zeros((H,W),int); lines=[]
for k,(name,parts) in enumerate(STROKES):
    pl=simplify(chain(parts)); lines.append((name,pl))
    for a,b in zip(pl[:-1],pl[1:]):
        n=int(np.hypot(*(b-a)))+1
        for u in np.linspace(0,1,n):
            x,y=(a+(b-a)*u).round().astype(int); lab[y,x]=k+1
handmask=np.zeros((H,W),bool)
for j,(name,(cx,cy),r) in enumerate(HANDS):
    c=((XX-cx)**2+(YY-cy)**2<r*r)&m; lab[c]=100+j; handmask|=c
# 每一筆的範圍：以這一筆「一般的」半徑（骨架上半徑的中位數）沿骨架往外長；
# 交叉處兩筆都會包含，歸給先寫的那一筆（交叉的方塊屬於先寫的筆畫，不會冒出菱形）；剩下的邊角歸給最近的一筆
dt=ndimage.distance_transform_edt(m)
regions=[]; taken=handmask.copy()
for k in range(len(STROKES)):
    sk=lab==k+1
    R=np.median(dt[sk])
    d=ndimage.distance_transform_edt(~sk)
    r=m&(d<=R+3)&~taken
    regions.append(r); taken|=r
left=m&~taken
if left.any():
    idx=ndimage.distance_transform_edt(lab==0,return_distances=False,return_indices=True)
    own0=lab[idx[0],idx[1]]
    for k in range(len(STROKES)): regions[k]|=left&(own0==k+1)
own=np.zeros((H,W),int)
for j in range(len(HANDS)): own[handmask&(lab==100+j)]=100+j
def path(mask):
    pl=potrace.Bitmap(~mask).trace(turdsize=4,alphamax=1.0,opticurve=True,opttolerance=0.3); out=[]
    for cv in pl:
        s=cv.start_point; d=f"M{s.x:.1f} {s.y:.1f}"
        for g in cv.segments:
            d+= f"L{g.c.x:.1f} {g.c.y:.1f}L{g.end_point.x:.1f} {g.end_point.y:.1f}" if g.is_corner else f"C{g.c1.x:.1f} {g.c1.y:.1f} {g.c2.x:.1f} {g.c2.y:.1f} {g.end_point.x:.1f} {g.end_point.y:.1f}"
        out.append(d+"Z")
    return "".join(out)
# 時間：每筆長度決定時長，下一筆在上一筆 75% 時開始
t=0.15; strokes=[]
for k,(name,pl) in enumerate(lines):
    L=float(np.sum(np.hypot(*np.diff(pl,axis=0).T)))
    dur=0.10+0.00042*L
    reg=ndimage.binary_dilation(regions[k],iterations=4)
    strokes.append({'name':name,'pts':[[round(float(x),1),round(float(y),1)] for x,y in pl],'d':'M'+'L'.join(f'{x:.0f} {y:.0f}' for x,y in pl),'len':round(L,1),
                    'clip':path(reg),'t0':round(t,3),'t1':round(t+dur,3)})
    t+=dur*0.62
hands=[]; t=strokes[-1]['t1']+0.05
for j,(name,(cx,cy),r) in enumerate(HANDS):
    reg=ndimage.binary_dilation(own==100+j,iterations=2)
    hands.append({'name':name,'cx':cx,'cy':cy,'r':r+10,'clip':path(reg),'t0':round(t,3),'t1':round(t+0.32,3)})
    t+=0.16
END=round(hands[-1]['t1']+0.12,3)
json.dump({'strokes':strokes,'hands':hands,'end':END,'width':112},open('intro.json','w'),ensure_ascii=False)
print('筆畫',len(strokes),'寫完',strokes[-1]['t1'],'手',[(h['name'],h['t0'],h['t1']) for h in hands],'開頭總長',END)
# 檢查：所有字形像素都被某一筆或手覆蓋
cov=handmask.copy()
for r in regions: cov|=r
print('未覆蓋像素',int((m&~cov).sum()))
