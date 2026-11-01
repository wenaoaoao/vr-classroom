import json
D=json.load(open('layers5.json')); P=D['paths']; R=D['rig']
import numpy as np
for k in R:  # 平滑寬度並補償像素取樣 (+1px)
    R[k]['w']=[round(v+.6,2) for v in R[k]['w']]; R[k]['o']=[round(v,2) for v in R[k]['o']]
rig=json.dumps(R)
html='''<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>巷伴 動態標準字 — 雙手</title>
<style>
  :root{--ink:#634F44;--bg:#FFFFFF;--lampIn:#FFF1D2;--lampOut:#F2CB86}
  body.dark{--ink:#FFFFFF;--bg:#000000;--lampIn:#FFE7B0;--lampOut:#F0B04F}
  html,body{margin:0;height:100%;background:var(--bg);transition:background .5s;font-family:system-ui,"PingFang TC","Noto Sans TC",sans-serif}
  .stage{height:100%;display:flex;align-items:center;justify-content:center;padding:0 6vw;box-sizing:border-box}
  svg{width:100%;max-width:1000px;max-height:80vh;height:auto;overflow:visible}
  #logo path,#logo circle{fill:var(--ink);transition:fill .5s}
  #logo #lamp{fill:url(#lampG)}
  .ui{position:fixed;left:50%;bottom:24px;transform:translateX(-50%);display:flex;gap:10px}
  .ui button{border:1px solid currentColor;background:transparent;color:var(--ink);padding:8px 16px;border-radius:999px;font-size:13px;letter-spacing:.05em;cursor:pointer;opacity:.6}
  .ui button:hover{opacity:1}
  body.capture .ui{display:none}
  body.debug #xiangArmLive,body.debug #banArmLive{fill:rgba(0,160,0,.6)} body.debug #xiangHandLive path,body.debug #banHandLive path{fill:rgba(0,0,255,.5)}
</style>
</head>
<body>
<div class="stage">
<svg id="logo" viewBox="40 700 1300 670" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="巷伴">
  <defs><radialGradient id="lampG" cx="45%" cy="40%" r="75%"><stop offset="0" stop-color="var(--lampIn)"/><stop offset="1" stop-color="var(--lampOut)"/></radialGradient></defs>
  <g id="all">
    <path d="@xiangTop"/>
    <path d="@xiangStatic"/>
    <path id="lamp" d="@window" opacity="0"/>
    <path d="@cane"/>
    <path d="@banCap"/>
    <!-- 動態時：即時計算的手臂 + 原稿手掌 -->
    <g id="live">
      <path id="xiangArmLive"/><g id="xiangHandLive"><path d="@xiangHand"/></g>
      <path id="banArmLive"/><g id="banHandLive"><path d="@banHand"/></g>
    </g>
    <!-- 靜止時：原稿手臂與手 -->
    <g id="rest" style="display:none" opacity="0">
      <path d="@xiangArm"/><path d="@xiangHand"/><path d="@banArm"/><path d="@banHand"/>
    </g>
    <path d="@banMain"/><path d="@dot1"/><path d="@dot2"/>
  </g>
</svg>
</div>
<div class="ui">
  <button onclick="play()">重新播放</button>
  <button onclick="document.body.classList.toggle('dark')">黑底 / 白底</button>
</div>
<script>
const RIG=@rig;
/* ================= 時間軸（秒） =================
   長者（伴）先伸手；青年（巷）晚一步，但兩手同時抵達。 */
const T={
  fade:[0,.5],
  ban:{start:.5, arrive:2.0},
  xiang:{start:.8, arrive:2.0},
  squeeze:.75,            // 抵達後「握一下」的長度
  lamp:2.3, end:4.2
};
/* 起始姿態：手腕位置、手掌角度、手腕走的弧線控制點 */
const POSE={
  // 巷：手臂極短、手掌下垂，從下方往上伸到定位
  xiang:{P0:[570,1120], ang0:36, C:[652,1200], over:6, k0x:45, k1x:20, k0min:34},
  // 伴：撇極短、手掌收在上方，向左下畫弧後落到拐杖握把
  ban:{P0:[832,812], ang0:140, C:[728,858], over:3.5, k0x:55, k1x:20, k0min:42}
};

/* ---------- 工具 ---------- */
const lerp=(a,b,t)=>a+(b-a)*t, clamp=t=>Math.max(0,Math.min(1,t));
function cb(x1,y1,x2,y2){ // CSS cubic-bezier
  return t=>{ if(t<=0)return 0; if(t>=1)return 1; let lo=0,hi=1,u=t;
    for(let i=0;i<30;i++){u=(lo+hi)/2;const x=3*(1-u)*(1-u)*u*x1+3*(1-u)*u*u*x2+u*u*u; if(x<t)lo=u; else hi=u;}
    return 3*(1-u)*(1-u)*u*y1+3*(1-u)*u*u*y2+u*u*u; };
}
const easeReach=cb(.5,0,.1,1), easeSoft=cb(.4,0,.3,1), easeOut=cb(.16,1,.3,1);
const deg=a=>a*Math.PI/180, angOf=v=>Math.atan2(v[1],v[0])*180/Math.PI;
const bez3=(p,u)=>[0,1].map(i=>(1-u)**3*p[0][i]+3*(1-u)**2*u*p[1][i]+3*(1-u)*u*u*p[2][i]+u**3*p[3][i]);
const bez3d=(p,u)=>[0,1].map(i=>3*(1-u)**2*(p[1][i]-p[0][i])+6*(1-u)*u*(p[2][i]-p[1][i])+3*u*u*(p[3][i]-p[2][i]));
const quad=(a,c,b,t)=>[0,1].map(i=>(1-t)**2*a[i]+2*(1-t)*t*c[i]+t*t*b[i]);
function widthAt(w,u){const x=u*(w.length-1),i=Math.min(w.length-2,Math.floor(x));return lerp(w[i],w[i+1],x-i);}

/* 依手腕位置 P 與手掌角度 ang，生成一條平滑、粗細漸變的手臂 */
function armPath(r,P,ang,e,ps){
  const A=r.A, Lrest=Math.hypot(r.B[0]-A[0],r.B[1]-A[1]), L=Math.hypot(P[0]-A[0],P[1]-A[1]);
  const s=Math.max(.25,L/Lrest), t1=[Math.cos(deg(ang)),Math.sin(deg(ang))];
  // 起點切線延長（隨抵達逐漸收回到原稿值），避免肩膀處折角
  const k0=Math.max(r.k[0],ps.k0min)*s+ps.k0x*(1-e)*s, k1=r.k[1]*s+ps.k1x*(1-e)*s;
  const ctrl=[A,[A[0]+r.t0[0]*k0,A[1]+r.t0[1]*k0],[P[0]-t1[0]*k1,P[1]-t1[1]*k1],P];
  const N=40,L1=[],L2=[];
  for(let i=0;i<=N;i++){const u=i/N;let p=bez3(ctrl,u),d=bez3d(ctrl,u);const n=Math.hypot(d[0],d[1])||1;d=[d[0]/n,d[1]/n];
    // 兩端各多延伸一點，藏進身體與手掌下面
    if(i===0)p=[p[0]-d[0]*8,p[1]-d[1]*8]; if(i===N)p=[p[0]+d[0]*7,p[1]+d[1]*7];
    const hw=widthAt(r.w,u)/2, of=widthAt(r.o,u); p=[p[0]-d[1]*of,p[1]+d[0]*of]; L1.push([p[0]-d[1]*hw,p[1]+d[0]*hw]); L2.push([p[0]+d[1]*hw,p[1]-d[0]*hw]);}
  const pts=L1.concat(L2.reverse());
  return 'M'+pts.map(p=>p[0].toFixed(1)+' '+p[1].toFixed(1)).join('L')+'Z';
}
function placeHand(el,r,P,ang){
  const a0=angOf(r.t1);
  el.setAttribute('transform',`translate(${P[0]} ${P[1]}) rotate(${ang-a0}) translate(${-r.B[0]} ${-r.B[1]})`);
}
function armState(key,t){
  const r=RIG[key], ps=POSE[key], tm=T[key], a1=angOf(r.t1);
  const p=clamp((t-tm.start)/(tm.arrive-tm.start)), e=easeReach(p);
  let P=quad(ps.P0,ps.C,r.B,e), ang=lerp(ps.ang0,a1,e);
  // 抵達後一起「握一下」：沿手腕方向再伸一點再回來
  const q=(t-tm.arrive)/T.squeeze;
  if(q>0&&q<1){const o=Math.sin(Math.PI*easeSoft(q))*ps.over*(1-q*.3);P=[P[0]+r.t1[0]*o,P[1]+r.t1[1]*o];}
  return {P,ang,e};
}
const $=id=>document.getElementById(id);
function render(t){
  $('all').setAttribute('opacity',easeOut(clamp((t-T.fade[0])/(T.fade[1]-T.fade[0]))));
  // 抵達並握完之後，原稿手臂淡入蓋上（0.3 秒），再收起即時手臂
  const tr=Math.max(T.ban.arrive,T.xiang.arrive)+T.squeeze, done=t>=tr+.3;
  $('rest').style.display=t>=tr?'':'none'; $('rest').setAttribute('opacity',clamp((t-tr)/.3));
  $('live').style.display=done?'none':'';
  if(!done) for(const k of ['xiang','ban']){const s=armState(k,t);
    $(k+'ArmLive').setAttribute('d',armPath(RIG[k],s.P,s.ang,s.e,POSE[k])); placeHand($(k+'HandLive'),RIG[k],s.P,s.ang);}
  // 燈：暖機式亮起
  const l=t-T.lamp; let o=0;
  if(l>0){o=l<.45?.6*easeSoft(l/.45):l<.65?lerp(.6,.5,(l-.45)/.2):lerp(.5,1,easeOut(clamp((l-.65)/.75)));}
  $('lamp').setAttribute('opacity',o);
}
let t0=null,raf=null,paused=false;
function frame(now){if(t0===null)t0=now;const t=(now-t0)/1000;render(t);if(t<T.end)raf=requestAnimationFrame(frame);}
function play(){cancelAnimationFrame(raf);t0=null;raf=requestAnimationFrame(frame);}
window.seek=t=>{cancelAnimationFrame(raf);render(t);};
const q=new URLSearchParams(location.search);
['dark','capture','debug'].forEach(k=>q.has(k)&&document.body.classList.add(k));
if(matchMedia('(prefers-reduced-motion: reduce)').matches) render(99); else {render(0);play();}
</script>
</body>
</html>'''
for k,v in P.items(): html=html.replace('"@'+k+'"','"'+v+'"')
html=html.replace('@rig',rig)
open('index.html','w').write(html)
