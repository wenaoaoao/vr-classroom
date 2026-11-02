# 合成「巷伴」動態標準字的音效（與動畫時間軸對齊）→ sound/xiangban.wav
import numpy as np
from scipy.signal import butter, sosfilt
from scipy.io import wavfile
SR=48000; DUR=5.2
t=np.arange(int(SR*DUR))/SR
out=np.zeros((len(t),2))
def env(t0,a,d,tt=t):   # 指數衰減包絡，a 秒起音
    x=tt-t0; e=np.where(x<0,0,np.where(x<a,x/a,np.exp(-(x-a)/d))); return e
def pan(sig,p): out[:,0]+=sig*np.sqrt(1-p); out[:,1]+=sig*np.sqrt(p)
def kalimba(t0,f,amp,d=0.9,p=.5):  # 拇指琴：基音＋非諧波泛音，起音柔和
    s=sum(a*np.sin(2*np.pi*f*m*t)*env(t0,.004,d*k) for m,a,k in [(1,1,1),(2.0,.25,.5),(5.4,.08,.18),(6.9,.04,.12)])
    pan(amp*s,p)
def wood(t0,f,amp,p=.5):           # 木頭輕敲：短促低頻＋一點顆粒
    rng=np.random.default_rng(int(t0*100))
    n=sosfilt(butter(2,[600,3000],'band',fs=SR,output='sos'),rng.standard_normal(len(t)))
    s=np.sin(2*np.pi*f*t*(1+.15*np.exp(-np.clip(t-t0,0,None)*40)))*env(t0,.002,.09)+.25*n*env(t0,.001,.012)
    pan(amp*s,p)
# 1 伸手（0.45–1.6 秒）：輕柔的氣流上揚，像布料摩擦
rng=np.random.default_rng(7)
noise=rng.standard_normal(len(t))
for lo,hi,a,p in [(300,1400,.05,.62),(250,1100,.045,.36)]:   # 伴（右）先、巷（左）後
    sw=sosfilt(butter(2,[lo,hi],'band',fs=SR,output='sos'),noise)
    st=.45 if p>.5 else .58
    g=np.clip((t-st)/(1.6-st),0,1); g=np.sin(np.pi*g)**2*np.where(t<1.6,1,0)
    pan(a*sw*g,p)
# 兩聲輕巧的拇指琴，標出兩隻手先後起步
kalimba(.45,659.25,.10,.6,.66)   # E5 長者先
kalimba(.62,587.33,.09,.6,.34)   # D5 青年跟上
# 2 握住（1.6 秒）：木頭輕敲＋明亮的拇指琴和音
wood(1.60,190,.32,.5)
kalimba(1.61,783.99,.20,1.1,.45) # G5
kalimba(1.63,1046.5,.12,1.0,.55) # C6
# 3 燈亮（1.62–3.0）：溫暖的和弦鋪底慢慢亮起，加上一點閃爍
pad=np.zeros(len(t))
for f in [261.63,329.63,392.0,587.33]:  # C E G D（加九度，溫暖）
    for det in (-.6,.6):
        pad+=np.sin(2*np.pi*(f+det)*t)+.3*np.sin(2*np.pi*2*(f+det)*t)
pad=sosfilt(butter(2,1800,'low',fs=SR,output='sos'),pad)/14
up=np.clip((t-2.2)/1.0,0,1); up=up*up*(3-2*up)
dn=1-np.clip((t-3.6)/.8,0,1); dn=dn*dn*(3-2*dn)
pan(.16*pad*up*dn,.5)
for i,(t0,f) in enumerate([(2.45,1318.5),(2.8,2093.0)]):   # 閃爍：G6 E6 C7
    kalimba(t0,f,.035,.5,.3+.2*i)
# 3b 日光燈：依 flicker.json 的亮度曲線，閃亮時「喀」一聲，亮著時有 120Hz 電流聲
import json
FL=json.load(open('flicker.json')); K=FL['keys']; OFF=FL['off']
def lamp(tt):
    o=np.interp(tt,[k[0] for k in K],[k[1] for k in K],left=0,right=K[-1][1])
    u=np.clip((tt-OFF[0])/OFF[1],0,1); return o*(1-u*u*(3-2*u))
L=lamp(t)
L=sosfilt(butter(1,60,'low',fs=SR,output='sos'),L)          # 讓亮度變化帶一點點慣性，避免爆音
hum=sum(a*np.sin(2*np.pi*120*m*t+m) for m,a in [(1,1),(2,.35),(3,.12)])   # 只留低沉的基音和兩個柔和泛音
hum=sosfilt(butter(2,500,'low',fs=SR,output='sos'),hum)                      # 去掉刺耳高頻（不再有「滋滋」嘶聲）
steady=np.where(t<2.3,1,0.25+0.75*np.exp(-(t-2.3)/0.4))       # 亮穩後嗡聲退到很遠的背景
pan(.026*hum*L*steady,.42)
on_times=[K[i][0] for i in range(len(K)-1) if K[i][1]<.3 and K[i+1][1]>=.3]
for j,t0 in enumerate(on_times):                             # 啟動器「喀」：短促金屬聲＋一點低頻
    n=sosfilt(butter(2,1800,'high',fs=SR,output='sos'),rng.standard_normal(len(t)))
    click=n*env(t0-.004,.0008,.006)+.6*np.sin(2*np.pi*(2400+300*j)*t)*env(t0-.004,.0005,.01)+.5*np.sin(2*np.pi*140*t)*env(t0-.004,.001,.03)
    pan((.16 if j<len(on_times)-1 else .12)*click,.4)
print('flicker on at',on_times)
# 4 燈暗（3.6–4.4）：輕輕落下的兩個音，回到安靜
kalimba(3.62,523.25,.09,1.0,.5)  # C5
kalimba(3.95,392.0,.08,1.3,.5)   # G4
# 收尾：輕微殘響
def reverb(x):
    y=x.copy()
    for d,g in [(.031,.35),(.047,.3),(.071,.25),(.113,.2),(.163,.15)]:
        n=int(d*SR); y[n:]+=g*x[:-n]
    return y
out[:,0]=reverb(out[:,0]); out[:,1]=reverb(out[:,1])
fade=np.clip((DUR-t)/.4,0,1); out*=fade[:,None]
out/=np.abs(out).max()/0.8
wavfile.write('sound/xiangban.wav',SR,(out*32767).astype(np.int16))
print('ok',DUR,'s')
