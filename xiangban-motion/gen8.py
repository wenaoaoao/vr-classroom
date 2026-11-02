# 產生逐格向量播放版 index.html
import json
L=json.load(open('layers5.json'))['paths']; F=json.load(open('frames.json')); Q=F['Q']
inset=3
clip=f"M0 0H1400V2000H0Z M{Q['x']+inset} {Q['y']+inset}V{Q['y']+Q['h']-inset}H{Q['x']+Q['w']-inset}V{Q['y']+inset}Z"
static=''.join(f'<path d="{L[k]}"/>' for k in ['xiangTop','xiangStatic','cane','banMain','dot1','dot2'])
rest=''.join(f'<path d="{L[k]}"/>' for k in ['xiangTop','xiangStatic','xiangArm','xiangHand','cane','banCap','banArm','banHand','banMain','dot1','dot2'])
html=f'''<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>巷伴 動態標準字</title>
<style>
  :root{{--ink:#634F44;--bg:#FFFFFF;--lampIn:#FFF1D2;--lampOut:#F2CB86}}
  body.dark{{--ink:#FFFFFF;--bg:#000000;--lampIn:#FFE7B0;--lampOut:#F0B04F}}
  html,body{{margin:0;height:100%;background:var(--bg);transition:background .5s;font-family:system-ui,"PingFang TC","Noto Sans TC",sans-serif}}
  .stage{{height:100%;display:flex;align-items:center;justify-content:center;padding:0 6vw;box-sizing:border-box}}
  svg{{width:100%;max-width:1000px;max-height:80vh;height:auto;overflow:visible}}
  #logo path{{fill:var(--ink);transition:fill .5s}}
  #logo #lamp{{fill:url(#lampG)}}
  .ui{{position:fixed;left:50%;bottom:24px;transform:translateX(-50%);display:flex;gap:10px}}
  .ui button{{border:1px solid currentColor;background:transparent;color:var(--ink);padding:8px 16px;border-radius:999px;font-size:13px;letter-spacing:.05em;cursor:pointer;opacity:.6}}
  .ui button:hover{{opacity:1}}
  body.capture .ui{{display:none}}
</style>
</head>
<body>
<div class="stage">
<svg id="logo" viewBox="40 700 1300 670" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="巷伴">
  <defs>
    <clipPath id="outsideQ" clipPathUnits="userSpaceOnUse"><path clip-rule="evenodd" d="{clip}"/></clipPath>
    <radialGradient id="lampG" cx="45%" cy="40%" r="75%"><stop offset="0" stop-color="var(--lampIn)"/><stop offset="1" stop-color="var(--lampOut)"/></radialGradient>
  </defs>
  <g id="all">
    <g id="play">{static}<path id="frame"/></g>
    <g id="rest" style="display:none">{rest}</g>
    <path id="lamp" d="{L['window']}" opacity="0"/>
  </g>
</svg>
</div>
<div class="ui">
  <button onclick="play()">重新播放</button>
  <button onclick="document.body.classList.toggle('dark')">黑底 / 白底</button>
</div>
<script>
/* 手部區域的逐格向量輪廓：由 gen7.py 的骨架動畫逐格渲染，接縫附近做輕微平滑後重新描邊（trace_frames.py） */
const FR={json.dumps(F['frames'])};
const FPS={F['fps']}, LAST=FR.length-1, END=LAST/FPS;
const clamp=t=>Math.max(0,Math.min(1,t)), lerp=(a,b,t)=>a+(b-a)*t;
function cb(x1,y1,x2,y2){{return t=>{{if(t<=0)return 0;if(t>=1)return 1;let lo=0,hi=1,u=t;for(let i=0;i<30;i++){{u=(lo+hi)/2;const x=3*(1-u)*(1-u)*u*x1+3*(1-u)*u*u*x2+u*u*u;if(x<t)lo=u;else hi=u;}}return 3*(1-u)*(1-u)*u*y1+3*(1-u)*u*u*y2+u*u*u;}}}}
const easeOut=cb(.16,1,.3,1), easeSoft=cb(.4,0,.3,1);
const $=id=>document.getElementById(id);
const FADE=.45; const FLK={json.dumps(json.load(open('flicker.json'))['keys'])}, FLOFF={json.dumps(json.load(open('flicker.json'))['off'])};
function lampAt(t){{const K=FLK;let o=0;if(t>=K[0][0]){{o=K[K.length-1][1];for(let i=0;i<K.length-1;i++){{if(t<K[i+1][0]){{const u=(t-K[i][0])/(K[i+1][0]-K[i][0]);o=K[i][1]+(K[i+1][1]-K[i][1])*(i===K.length-2?easeOut(u):u);break;}}}}}}return o*(1-easeSoft(clamp((t-FLOFF[0])/FLOFF[1])));}}
function render(t){{
  $('all').setAttribute('opacity',easeOut(clamp(t/FADE)));
  const done=t>=END;
  $('play').style.display=done?'none':''; $('rest').style.display=done?'':'none';
  if(!done)$('frame').setAttribute('d',FR[Math.min(LAST,Math.round(t*FPS))]);
  $('lamp').setAttribute('opacity',lampAt(t));
}}
let t0=null,raf=null;
function frame(now){{if(t0===null)t0=now;const t=(now-t0)/1000;render(t);if(t<4.5)raf=requestAnimationFrame(frame);}}
function play(){{cancelAnimationFrame(raf);t0=null;raf=requestAnimationFrame(frame);}}
window.seek=t=>{{cancelAnimationFrame(raf);render(t);}};
const q=new URLSearchParams(location.search);
['dark','capture'].forEach(k=>q.has(k)&&document.body.classList.add(k));
if(matchMedia('(prefers-reduced-motion: reduce)').matches) render(99); else {{render(0);play();}}
</script>
</body>
</html>'''
open('index.html','w').write(html); print('KB',len(html)//1024)
