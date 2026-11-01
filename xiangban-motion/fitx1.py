import numpy as np, json, math
from PIL import Image
from scipy import ndimage
exec(open('fitkeys.py').read().split('def fit')[0])
key=np.array(Image.open('source/key1.png'))<128
S=c6&~((YY<1200)&(XX>=528)&beyond(X['A'],X['t0'],0))      # 靜態屋簷
win=(slice(1000,1110),slice(480,580))
Kw=key[win]; Sw=S[win]; Vw=Kw&~Sw
yy,xx=np.mgrid[win[0],win[1]]
hand=xHand.astype(float); a0x=math.degrees(math.atan2(X['t1'][1],X['t1'][0]))
best=None
for sc in np.arange(.40,1.01,.04):
  for da in range(-30,61,3):
    th=math.radians(da); c,s=math.cos(th),math.sin(th)
    for Px in range(470,560,3):
      for Py in range(1030,1120,3):
        qx=(xx-Px)/sc; qy=(yy-Py)/sc
        sx=X['B'][0]+c*qx+s*qy; sy=X['B'][1]-s*qx+c*qy
        t=ndimage.map_coordinates(hand,[sy,sx],order=0)>0.5
        tv=t&~Sw
        inter=(tv&Vw).sum(); uni=(tv|Vw).sum()
        if uni==0: continue
        iou=inter/uni
        if best is None or iou>best[0]: best=(iou,sc,da,Px,Py)
print('IoU %.3f scale %.2f rot %d P=(%d,%d)'%best)
iou,sc,da,Px,Py=best
K=json.load(open('source/keys.json')); K['1']['xiang']={'P':[float(Px),float(Py)],'ang':a0x+da,'scale':float(sc)}
json.dump(K,open('source/keys.json','w'))
