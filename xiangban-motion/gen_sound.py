# 合成「巷伴」動態標準字的音效（與動畫時間軸對齊）→ sound/xiangban.wav
import numpy as np
from scipy.signal import butter, sosfilt
from scipy.io import wavfile
SR=48000; DUR=6.0
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
kalimba(1.86,783.99,.20,1.1,.45) # G5  握緊
kalimba(1.88,1046.5,.12,1.0,.55) # C6
for tp in (1.97,2.33):                # 握手搖兩下：每下一聲圓潤的低音「咚」
    pan(.22*np.sin(2*np.pi*130*t)*env(tp,.006,.10),.5)
    kalimba(tp+.01,392.0 if tp<2.2 else 440.0,.07,.5,.5)
# 3 燈亮（1.62–3.0）：溫暖的和弦鋪底慢慢亮起，加上一點閃爍
pad=np.zeros(len(t))
for f in [261.63,329.63,392.0,587.33]:  # C E G D（加九度，溫暖）
    for det in (-.6,.6):
        pad+=np.sin(2*np.pi*(f+det)*t)+.3*np.sin(2*np.pi*2*(f+det)*t)
pad=sosfilt(butter(2,1800,'low',fs=SR,output='sos'),pad)/14
up=np.clip((t-2.45)/1.0,0,1); up=up*up*(3-2*up)
dn=1-np.clip((t-4.3)/.8,0,1); dn=dn*dn*(3-2*dn)
pan(.16*pad*up*dn,.5)
for i,(t0,f) in enumerate([(2.85,1318.5),(3.2,2093.0)]):   # 閃爍：G6 E6 C7
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
# 電流嗡聲已拿掉（聽起來嚇人）
on_times=[K[i][0] for i in range(len(K)-1) if K[i][1]<.3 and K[i+1][1]>=.3]
for j,t0 in enumerate(on_times):                             # 開關聲：圓潤、小聲的「嗒」，像家裡的電燈開關
    n=sosfilt(butter(2,[700,2200],'band',fs=SR,output='sos'),rng.standard_normal(len(t)))
    tick=.5*n*env(t0-.004,.001,.008)+np.sin(2*np.pi*(520-20*j)*t)*env(t0-.004,.001,.035)
    tick=sosfilt(butter(2,2500,'low',fs=SR,output='sos'),tick)
    pan((.07 if j<len(on_times)-1 else .06)*tick,.4)
print('flicker on at',on_times)
# 4 燈暗（3.6–4.4）：輕輕落下的兩個音，回到安靜
kalimba(4.32,523.25,.09,1.0,.5)  # C5
kalimba(4.65,392.0,.08,1.3,.5)   # G4
# 收尾：輕微殘響
def reverb(x):
    y=x.copy()
    for d,g in [(.031,.35),(.047,.3),(.071,.25),(.113,.2),(.163,.15)]:
        n=int(d*SR); y[n:]+=g*x[:-n]
    return y
out[:,0]=reverb(out[:,0]); out[:,1]=reverb(out[:,1])
fade=np.clip((DUR-t)/.4,0,1); out*=fade[:,None]
out/=np.abs(out).max()/0.8
# 開頭書寫：每一筆一段輕柔的「刷」聲（像毛筆掃過紙），兩隻手長出時各一聲輕巧的拇指琴
I=json.load(open('intro.json')); IE=I['end']; n0=int(round(IE*SR))
fin=np.zeros((n0+len(out),2)); fin[n0:]=out
ti=np.arange(len(fin))/SR
rng2=np.random.default_rng(11)
for k,st in enumerate(I['strokes']):
    a,b=st['t0'],st['t1']; d=b-a
    nz=sosfilt(butter(2,[500,2600],'band',fs=SR,output='sos'),rng2.standard_normal(len(fin)))
    u=np.clip((ti-a)/d,0,1); e=np.sin(np.pi*u)**1.5*((ti>=a)&(ti<=b))
    e*=1+.25*np.sin(2*np.pi*(9+k%3)*ti)               # 一點點筆觸的抖動
    p=.35+.3*((k%5)/4)
    fin[:,0]+=.15*nz*e*np.sqrt(1-p); fin[:,1]+=.15*nz*e*np.sqrt(p)
for j,h in enumerate(I['hands']):
    f=880.0 if j==0 else 783.99
    tt=ti-h['t0']; ev=np.where(tt<0,0,np.where(tt<.004,tt/.004,np.exp(-(tt-.004)/.5)))
    sig=.09*ev*(np.sin(2*np.pi*f*ti)+.25*np.sin(2*np.pi*2*f*ti))
    fin[:,0]+=sig*(.65 if j==0 else .35); fin[:,1]+=sig*(.35 if j==0 else .65)
pk=np.abs(fin).max()
if pk>0.95: fin*=0.95/pk
wavfile.write('sound/xiangban.wav',SR,(fin*32767).astype(np.int16))
print('含開頭',round(len(fin)/SR,2),'秒')
print('ok',DUR,'s')
