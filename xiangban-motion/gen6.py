import json
KEY=json.load(open('source/keys.json')); KEY['lift']=-28; KEY['capW']=52.5
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
  body.debug #xiangSwell{fill:rgba(255,120,0,.7)} body.debug #xiangArmLive,body.debug #banArmLive{fill:rgba(0,160,0,.6)} body.debug #xiangHandLive path,body.debug #banHandLive path{fill:rgba(0,0,255,.5)}
</style>
</head>
<body>
<div class="stage">
<svg id="logo" viewBox="40 700 1300 670" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="巷伴">
  <defs><clipPath id="xiangSleeve" clipPathUnits="userSpaceOnUse"><path id="xiangSleevePath"/></clipPath><clipPath id="banSleeve" clipPathUnits="userSpaceOnUse"><rect x="0" y="755.5" width="1400" height="700"/></clipPath><radialGradient id="lampG" cx="45%" cy="40%" r="75%"><stop offset="0" stop-color="var(--lampIn)"/><stop offset="1" stop-color="var(--lampOut)"/></radialGradient></defs>
  <g id="all">
    <path d="@xiangTop"/>
    <path d="@xiangStatic"/>
    <path id="lamp" d="@window" opacity="0"/>
    <path d="@cane"/>
    <!-- 動態時：即時計算的手臂 + 原稿手掌 -->
    <g id="live">
      <path id="xiangSwell"/><g clip-path="url(#xiangSleeve)"><circle id="xiangJoint" r="0"/><path id="xiangArmLive"/><g id="xiangHandLive"><path d="@xiangHand"/></g></g>
      <g clip-path="url(#banSleeve)"><path id="banArmLive"/><g id="banHandLive"><path d="@banHand"/></g></g>
    </g>
    <!-- 靜止時：原稿手臂與手 -->
    <g id="rest" style="display:none" opacity="0">
      <path d="@xiangArm"/><path d="@xiangHand"/><path d="@banCap"/><path d="@banArm"/><path d="@banHand"/>
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
/* ================= 時間軸（秒）=================
   依設計者的三張關鍵姿勢：1 收起 → 2 伸手相握 → 3 鬆開回到標準字 */
const T={fade:[0,.45], ban:[.45,1.7], xiang:[.7,1.7], hold:[1.7,2.25], release:[2.25,3.1], lamp:1.85, end:4.6};
const KEY=@keys;   // 由設計稿量出的手腕位置 P 與手掌角度 ang
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

/* 生成手臂輪廓：先一段沿起點切線的直線（藏在袖口裡），再接一段貝茲曲線到手腕 */
function armPath(r,A,t0,P,ang,ext,extW,k0min=0){
  const Lrest=Math.hypot(r.B[0]-r.A[0],r.B[1]-r.A[1]), L=Math.hypot(P[0]-A[0],P[1]-A[1]);
  const s=Math.max(.2,Math.min(1.15,L/Lrest)), t1=[Math.cos(deg(ang)),Math.sin(deg(ang))];
  const k0=Math.max(r.k[0]*s,k0min);
  const ctrl=[A,[A[0]+t0[0]*k0,A[1]+t0[1]*k0],[P[0]-t1[0]*r.k[1]*s,P[1]-t1[1]*r.k[1]*s],P];
  const S1=[],S2=[],N=40, nrm=d=>[-d[1],d[0]];
  const push=(p,d,hw)=>{const n=nrm(d);S1.push([p[0]+n[0]*hw,p[1]+n[1]*hw]);S2.push([p[0]-n[0]*hw,p[1]-n[1]*hw]);};
  for(let i=24;i>=1;i--){const e=ext*i/24, w=extW?lerp(r.w[0],extW,Math.min(1,e/30)):r.w[0];
    push([A[0]-t0[0]*e,A[1]-t0[1]*e],t0,w/2);}
  for(let i=0;i<=N;i++){const u=i/N;let p=bez3(ctrl,u),d=bez3d(ctrl,u);const n=Math.hypot(d[0],d[1])||1;d=[d[0]/n,d[1]/n];
    if(i===N)p=[p[0]+d[0]*7,p[1]+d[1]*7];
    const of=widthAt(r.o,u); p=[p[0]-d[1]*of,p[1]+d[0]*of]; push(p,d,widthAt(r.w,u)/2);}
  const pts=S1.concat(S2.reverse());
  return 'M'+pts.map(p=>p[0].toFixed(1)+' '+p[1].toFixed(1)).join('L')+'Z';
}
function placeHand(el,r,P,ang){
  el.setAttribute('transform',`translate(${P[0]} ${P[1]}) rotate(${ang-angOf(r.t1)}) translate(${-r.B[0]} ${-r.B[1]})`);
}
const rot=(v,a)=>{const c=Math.cos(deg(a)),s=Math.sin(deg(a));return [v[0]*c-v[1]*s,v[0]*s+v[1]*c];};
const add=(a,b,k=1)=>[a[0]+b[0]*k,a[1]+b[1]*k];
const smooth=x=>x*x*(3-2*x);
/* 每隻手在時間 t 的姿態 */
function pose(key,t){
  const r=RIG[key], k1=KEY[1][key], k2=KEY[2][key], aR=angOf(r.t1), t0=r.t0;
  const g1=easeReach(clamp((t-T[key][0])/(T[key][1]-T[key][0])));          // 1 → 2
  const g2=easeSoft(clamp((t-T.release[0])/(T.release[1]-T.release[0]))); // 2 → 3
  let P,ang,lift=0;
  if(key==='xiang'){
    // 巷：手從肩膀（袖口）裡伸出，沿手臂方向冒出後往上勾
    const K1=add(r.A,t0,-115), c1=add(r.A,t0,30), c2=add(k2.P,[Math.cos(deg(k2.ang)),Math.sin(deg(k2.ang))],-45);
    P=bez3([K1,c1,c2,k2.P],g1);
    ang=lerp(angOf(t0),k2.ang,smooth(clamp((g1-.3)/.7)));
    lift=lerp(0,KEY.lift,smooth(clamp((g1-.2)/.8)));
  }else{
    // 伴：整條撇沿自己的方向從頂端滑出，手腕下彎伸向巷
    P=[lerp(k1.P[0],k2.P[0],g1),lerp(k1.P[1],k2.P[1],g1)];
    ang=lerp(k1.ang,k2.ang,g1);
  }
  // 2 → 3：鬆開，回到標準字
  P=[lerp(P[0],r.B[0],g2),lerp(P[1],r.B[1],g2)]; ang=lerp(ang,aR,g2); lift=lerp(lift,0,g2);
  return {P,ang,lift};
}
const $=id=>document.getElementById(id);
(function(){ // 巷的袖口：肩膀切線之外的半平面
  const r=RIG.xiang,A=r.A,t=r.t0,n=[-t[1],t[0]],F=2000;
  const p=[add(A,n,F),add(add(A,n,F),t,F),add(add(A,n,-F),t,F),add(A,n,-F)];
  document.getElementById('xiangSleevePath').setAttribute('d','M'+p.map(q=>q.join(' ')).join('L')+'Z');
})();
function render(t){
  $('all').setAttribute('opacity',easeOut(clamp((t-T.fade[0])/(T.fade[1]-T.fade[0]))));
  const tr=T.release[1], done=t>=tr+.3;
  $('rest').style.display=t>=tr?'':'none'; $('rest').setAttribute('opacity',clamp((t-tr)/.3));
  $('live').style.display=done?'none':'';
  if(!done){
    // 巷
    let r=RIG.xiang, s=pose('xiang',t), t0=rot(r.t0,s.lift);
    const dAlong=(s.P[0]-r.A[0])*r.t0[0]+(s.P[1]-r.A[1])*r.t0[1];
    $('xiangArmLive').setAttribute('d',dAlong>4?armPath(r,r.A,t0,s.P,s.ang,10,0,40*s.lift/KEY.lift):'');
    const J=$('xiangJoint'); J.setAttribute('cx',r.A[0]);J.setAttribute('cy',r.A[1]);J.setAttribute('r',dAlong>4?r.w[0]/2-.3:0);
    placeHand($('xiangHandLive'),r,s.P,s.ang);
    // 抬手時屋簷上緣跟著隆起：從屋脊附近平順過渡到手臂的新角度
    const E=r.topEdge, x0=E.x[0], x1=E.T0[0], y0=E.y[0], y1=E.T0[1];
    const m0=(E.y[2]-E.y[0])/(E.x[2]-E.x[0]), m1=t0[1]/t0[0], h=x1-x0;
    let up=[],dn=[];
    E.x.forEach((x,i)=>{const u=(x-x0)/h, h00=2*u**3-3*u*u+1,h10=u**3-2*u*u+u,h01=-2*u**3+3*u*u,h11=u**3-u*u;
      const H=h00*y0+h10*h*m0+h01*y1+h11*h*m1; up.push([x,Math.min(H,E.y[i])]); dn.push([x,E.y[i]+5]);});
    up.push([x1+2,y1]); dn.push([x1+2,y1+5]);
    $('xiangSwell').setAttribute('d',s.lift<-.5?'M'+up.concat(dn.reverse()).map(p=>p[0].toFixed(1)+' '+p[1].toFixed(1)).join('L')+'Z':'');
    // 伴：起點跟著手腕一起滑動
    r=RIG.ban; s=pose('ban',t);
    const A2=add(s.P,[r.A[0]-r.B[0],r.A[1]-r.B[1]]);
    $('banArmLive').setAttribute('d',armPath(r,A2,r.t0,s.P,s.ang,220,KEY.capW));
    placeHand($('banHandLive'),r,s.P,s.ang);
  }
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
html=html.replace('@rig',rig).replace('@keys',json.dumps(KEY))
open('index.html','w').write(html)
