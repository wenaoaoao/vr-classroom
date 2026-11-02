import json
KEY=json.load(open('source/keys.json')); KEY['lift']=float(__import__('os').environ.get('LIFT',0)); KEY['lean']=float(__import__('os').environ.get('LEAN',2)); KEY['dy2']=float(__import__('os').environ.get('DY',4)); KEY['dx2']=float(__import__('os').environ.get('DX',0)); KEY['capW']=52.5
D=json.load(open('layers5.json')); P=D['paths']; R=D['rig']
import numpy as np
for k in R:  # 平滑寬度並補償像素取樣 (+1px)
    u=np.linspace(0,1,len(R[k]['w']))
    for key,add_ in (('w',.6),('o',0)):
        raw=np.array(R[k][key]); c=np.polyfit(u,raw,3); sm=np.polyval(c,u)
        wgt=np.clip(np.minimum(u,1-u)/0.15,0,1)          # 兩端 15% 逐漸回到實測值（與手掌、頂端切口對齊）
        if k=='xiang': wgt=np.where(u<.3,0,wgt)        # 巷肩膀段保留沿空洞邊緣的實測值
        R[k][key]=[round(float(v)+add_,2) for v in raw*(1-wgt)+sm*wgt]
R['ban']['straight']=1
R['ban']['bendK']=float(__import__('os').environ.get('BENDK',3.5)); R['xiang']['bendK']=1.0
R['ban']['wEnd']=float(__import__('os').environ.get('WEND',1)); R['xiang']['wEnd']=float(__import__('os').environ.get('WENDX',1.5))
for _k in R:
    _r=R[_k]; _A=np.array(_r['A']); _B=np.array(_r['B']); _P=[_A,_A+_r['k'][0]*np.array(_r['t0']),_B-_r['k'][1]*np.array(_r['t1']),_B]
    _u=np.linspace(0,1,200)[:,None]; _c=(1-_u)**3*_P[0]+3*(1-_u)**2*_u*_P[1]+3*(1-_u)*_u**2*_P[2]+_u**3*_P[3]
    _r['Larc']=float(np.sum(np.linalg.norm(np.diff(_c,axis=0),axis=1)))
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
  <defs><clipPath id="notHole" clipPathUnits="userSpaceOnUse"><path clip-rule="evenodd" d="M0 0H1400V2000H0Z @roofHole"/></clipPath><filter id="weld" x="-10%" y="-10%" width="120%" height="120%" filterUnits="objectBoundingBox"><feMorphology operator="dilate" radius="2.2"/><feMorphology operator="erode" radius="2.2"/></filter><clipPath id="xiangSleeve" clipPathUnits="userSpaceOnUse"><path id="xiangSleevePath"/></clipPath><clipPath id="banSleeve" clipPathUnits="userSpaceOnUse"><rect x="0" y="755.5" width="1400" height="700"/></clipPath><radialGradient id="lampG" cx="45%" cy="40%" r="75%"><stop offset="0" stop-color="var(--lampIn)"/><stop offset="1" stop-color="var(--lampOut)"/></radialGradient></defs>
  <g id="all">
    <path d="@xiangTop"/>
    <path d="@xiangStatic"/>
    <path id="lamp" d="@window" opacity="0"/>
    <path d="@cane"/>
    <!-- 動態時：即時計算的手臂 + 原稿手掌 -->
    <g id="live">
      <path id="xiangSwell"/><g clip-path="url(#notHole)"><circle id="xiangJoint" r="0"/><path id="xiangArmLive"/><g id="xiangHandLive"><path d="@xiangHand"/></g></g>
      <g clip-path="url(#banSleeve)"><g><path id="banArmLive"/><g id="banHandLive"><path d="@banHand"/></g></g></g>
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
const T={fade:[0,.45], release:[2.25,3.1], lamp:1.62, end:4.4};
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
function armPath(r,A,t0,P,ang,ext,extW,k0min=0,hs=1,pre=0){
  const Lrest=Math.hypot(r.B[0]-r.A[0],r.B[1]-r.A[1]), L=Math.hypot(P[0]-A[0],P[1]-A[1]);
  const s=Math.max(.01,Math.min(1.15,L/Lrest)), t1=[Math.cos(deg(ang)),Math.sin(deg(ang))];
  // 控制柄不得超過手臂長度的 45%，避免短手臂扭成 Z 字
  const kcap=.45*L;
  // 手掌相對手臂轉得越多，末端控制柄越長，彎度分散到整條手臂，內側不會擠出折角
  const bend=Math.abs(ang-angOf(r.t1)), k1e=(r.k[1]+(r.bendK||0)*bend)*s;
  const k0=Math.min(Math.max(r.k[0]*s,k0min),kcap);
  let ctrl=[A,[A[0]+t0[0]*k0,A[1]+t0[1]*k0],[P[0]-t1[0]*Math.min(k1e,kcap),P[1]-t1[1]*Math.min(k1e,kcap)],P];
  if(r.straight){ // 伴：撇保持筆直，彎曲只集中在手腕前一小段
    const Ls=Math.hypot(P[0]-A[0],P[1]-A[1]);
    ctrl=[A,[A[0]+t0[0]*Ls*.62,A[1]+t0[1]*Ls*.62],[P[0]-t1[0]*Ls*.2,P[1]-t1[1]*Ls*.2],P];
  }
  if(pre>0){ // 曲線從肩膀後方 pre 處開始（藏在屋頂內），露出的部分永遠是單純的 C 形
    const A0=[A[0]-t0[0]*pre,A[1]-t0[1]*pre], Lp=Math.hypot(P[0]-A0[0],P[1]-A0[1]);
    // 二次曲線等效：兩個控制點都指向起點切線與終點切線的交點 X，曲線不可能有反曲點
    const den=t0[0]*t1[1]-t0[1]*t1[0];
    let lam=-1,mu=-1;
    if(Math.abs(den)>1e-3){const dx=P[0]-A0[0],dy=P[1]-A0[1]; lam=(dx*t1[1]-dy*t1[0])/den; mu=(dx*t0[1]-dy*t0[0])/den;}
    if(lam>Lp*.15&&mu>Lp*.15&&lam<Lp*1.5&&mu<Lp*1.5){
      const Xp=[A0[0]+t0[0]*lam,A0[1]+t0[1]*lam];
      ctrl=[A0,[A0[0]+(Xp[0]-A0[0])*2/3,A0[1]+(Xp[1]-A0[1])*2/3],[P[0]+(Xp[0]-P[0])*2/3,P[1]+(Xp[1]-P[1])*2/3],P];
    } else ctrl=[A0,[A0[0]+t0[0]*Lp*.42,A0[1]+t0[1]*Lp*.42],[P[0]-t1[0]*Lp*.33,P[1]-t1[1]*Lp*.33],P];
  }
  const LrA=r.Larc||Lrest, S1=[],S2=[],N=90, nrm=d=>[-d[1],d[0]];
  const push=(p,d,hw)=>{const n=nrm(d);S1.push([p[0]+n[0]*hw,p[1]+n[1]*hw]);S2.push([p[0]-n[0]*hw,p[1]-n[1]*hw]);};
  const o0=r.o[0], nn=[-t0[1],t0[0]];
  for(let i=40;i>=1;i--){const e=ext*i/40, w=extW?lerp(r.w[0],extW,smooth(Math.min(1,e/45))):r.w[0];
    push([A[0]-t0[0]*e+nn[0]*o0,A[1]-t0[1]*e+nn[1]*o0],t0,w/2);}
  // 寬度依「離起點的實際距離」取樣，靠手掌端再漸回參數 u：手臂很短時肩膀附近的寬度不會被壓縮
  let arc=0, prev=null;
  for(let i=0;i<=N;i++){const u0=i/N;let p=bez3(ctrl,u0),d=bez3d(ctrl,u0);const n=Math.hypot(d[0],d[1])||1;d=[d[0]/n,d[1]/n];
    if(prev)arc+=Math.hypot(p[0]-prev[0],p[1]-prev[1]); prev=p;
    const u=lerp(clamp((arc-pre)/LrA),u0,smooth(clamp((u0-.35)/.65)));
    const sc=lerp(1,hs,smooth(u)), of=widthAt(r.o,u)*sc; p=[p[0]-d[1]*of,p[1]+d[0]*of]; push(p,d,(widthAt(r.w,u)+(r.wEnd||0)*smooth(clamp((u-.88)/.12)))*sc/2);
    if(i===N){ // 伸進手掌 6px，並內縮，避免在手腕處露出角
      push([p[0]+d[0]*6,p[1]+d[1]*6],d,widthAt(r.w,u)*sc*.42);}}
  const pts=S1.concat(S2.reverse());
  return 'M'+pts.map(p=>p[0].toFixed(1)+' '+p[1].toFixed(1)).join('L')+'Z';
}
function placeHand(el,r,P,ang,hs=1){
  el.setAttribute('transform',`translate(${P[0]} ${P[1]}) rotate(${ang-angOf(r.t1)}) scale(${hs}) translate(${-r.B[0]} ${-r.B[1]})`);
}
const rot=(v,a)=>{const c=Math.cos(deg(a)),s=Math.sin(deg(a));return [v[0]*c-v[1]*s,v[0]*s+v[1]*c];};
const add=(a,b,k=1)=>[a[0]+b[0]*k,a[1]+b[1]*k];
const smooth=x=>x*x*(3-2*x);
/* ---------- 每隻手：一條幾何路徑 + 一條速度曲線 ----------
   伸手：沿路徑（以弧長均分）加速、減速，1.6 秒兩手同時接觸。
   握住：抵達前 0.1 秒就開始，兩手一起往上帶一下再落回（與抵達重疊，不會停頓）。
   鬆開：長者先放，青年晚 0.08 秒，結尾帶一點點回彈。 */
const M={contact:1.6, clasp:[1.5,2.2], up:5, tilt:1.5,
  ban:{start:.45, ease:cb(.42,0,.28,1), rel:[2.2,3.0]},
  xiang:{start:.55, ease:cb(.42,0,.28,1), rel:[2.28,3.05]}};
const easeRel=cb(.35,0,.2,1.06);
function arcTable(fn){ // 弧長重新取樣，讓 s 均勻對應距離
  const N=200,pts=[],acc=[0]; for(let i=0;i<=N;i++)pts.push(fn(i/N));
  for(let i=1;i<=N;i++)acc.push(acc[i-1]+Math.hypot(pts[i][0]-pts[i-1][0],pts[i][1]-pts[i-1][1]));
  const L=acc[N]; return s=>{const d=s*L;let i=1;while(i<N&&acc[i]<d)i++;const f=(d-acc[i-1])/((acc[i]-acc[i-1])||1);
    return [lerp(pts[i-1][0],pts[i][0],f),lerp(pts[i-1][1],pts[i][1],f)];};
}
let PATH=null;
function buildPaths(){
  const X=RIG.xiang,k1=KEY[1],k2=KEY[2],P2=[k2.xiang.P[0]+(KEY.dx2||0),k2.xiang.P[1]+(KEY.dy2||0)],P1=add(k1.xiang.P,X.t0,0);
  const a1=deg(k1.xiang.ang), a2=deg(k2.xiang.ang);
  PATH={
    // 巷：手一直接在屋簷末端；從第 1 張的位置往外、往上伸到第 2 張
    xiang:arcTable(u=>bez3([P1,[P1[0]+Math.cos(a1)*45,P1[1]+Math.sin(a1)*45+18],[P2[0]-Math.cos(a2)*45,P2[1]-Math.sin(a2)*45+20],P2],u)),
    ban:arcTable(u=>[lerp(k1.ban.P[0],k2.ban.P[0],u),lerp(k1.ban.P[1],k2.ban.P[1],u)])
  };
}
/* 巷：手腕繞肩膀後方的支點 Av 畫弧並伸長（極座標內插）；手掌角度＝手臂方向＋手腕彎曲，手腕彎曲稍落後 */
function xiangPose(s){
  const X=RIG.xiang,k1=KEY[1].xiang,k2=KEY[2].xiang;
  const Av=add(X.A,X.t0,-60);
  const P1=k1.P, P2=[k2.P[0]+(KEY.dx2||0),k2.P[1]+(KEY.dy2||0)];
  const pol=P=>[Math.hypot(P[0]-Av[0],P[1]-Av[1]),Math.atan2(P[1]-Av[1],P[0]-Av[0])*180/Math.PI];
  const [r1,th1]=pol(P1),[r2,th2]=pol(P2);
  const r=lerp(r1,r2,s), th=lerp(th1,th2,s);
  const P=[Av[0]+r*Math.cos(deg(th)),Av[1]+r*Math.sin(deg(th))];
  const b1=k1.ang-th1, b2=k2.ang-th2;
  const ang=th+lerp(b1,b2,clamp((s-.06)/.94));
  return {P,ang};
}
function pose(key,t){
  if(!PATH)buildPaths();
  const r=RIG[key],m=M[key],k1=KEY[1][key],k2=KEY[2][key],aR=angOf(r.t1);
  const s=m.ease(clamp((t-m.start)/(M.contact-m.start)));
  let P,ang,lift=0,hs=1,lean=0;
  if(key==='xiang'){ const q=xiangPose(s); P=q.P; ang=q.ang;
    hs=lerp(k1.scale||1,1,smooth(clamp(s/.8))); lift=KEY.lift*smooth(clamp((s-.25)/.75)); }
  else { P=PATH.ban(s); ang=lerp(k1.ang,k2.ang,smooth(s)); lean=KEY.lean*smooth(s); }
  const c=clamp((t-M.clasp[0])/(M.clasp[1]-M.clasp[0])), b=(1-Math.cos(2*Math.PI*c))/2;
  P=[P[0],P[1]-M.up*b]; ang-=M.tilt*b;
  // 鬆開：位置帶一點點回彈，角度不回彈（避免手腕來回扭）
  const u=clamp((t-m.rel[0])/(m.rel[1]-m.rel[0])), g=easeRel(u), ga=easeSoft(u);
  P=[lerp(P[0],r.B[0],g),lerp(P[1],r.B[1],g)]; ang=lerp(ang,aR,ga); lift=lerp(lift,0,ga); lean=lerp(lean,0,ga);
  return {P,ang,lift,hs,lean};
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
    $('xiangArmLive').setAttribute('d',dAlong>-55?armPath(r,r.A,t0,s.P,s.ang,2,0,0,s.hs,60):'');
    const J=$('xiangJoint'); J.setAttribute('cx',r.A[0]);J.setAttribute('cy',r.A[1]);J.setAttribute('r',0);
    placeHand($('xiangHandLive'),r,s.P,s.ang,s.hs);
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
    const A2=add(s.P,rot([r.A[0]-r.B[0],r.A[1]-r.B[1]],s.lean));
    $('banArmLive').setAttribute('d',armPath(r,A2,rot(r.t0,s.lean),s.P,s.ang,220,KEY.capW));
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
html=html.replace(' @roofHole"',' '+P['roofHole']+'"')
html=html.replace('@rig',rig).replace('@keys',json.dumps(KEY))
open('rig.html','w').write(html)
