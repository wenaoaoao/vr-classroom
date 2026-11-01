import numpy as np, sys
from PIL import Image
from scipy import ndimage
S=3
def sigma_for(i,fps=30):
    t=i/fps
    return 4.5 if t<2.7 else max(0.0,4.5*(3.0-t)/0.3)      # 鬆開快結束時逐漸停止平滑
def clean(i):
    F=np.array(Image.open(f'cap/full_{i:03d}.png').convert('L'))<128
    M=np.array(Image.open(f'cap/mov_{i:03d}.png').convert('L'))<128
    sg=sigma_for(i)
    if sg<=0.05 or not M.any(): return F
    band=ndimage.binary_dilation(M,iterations=10)
    sm=ndimage.gaussian_filter(F.astype(float),sg)>0.5
    return np.where(band,sm,F)
if __name__=='__main__':
    for i in map(int,sys.argv[1:]):
        C=clean(i); F=np.array(Image.open(f'cap/full_{i:03d}.png').convert('L'))<128
        rgb=np.full(F.shape+(3,),255,np.uint8); rgb[C&F]=(100,85,75); rgb[F&~C]=(255,0,0); rgb[C&~F]=(0,120,255)
        Image.fromarray(rgb).save(f'cl_{i:03d}.png')
