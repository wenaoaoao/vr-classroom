// 逐格渲染手部區域 Q（原稿座標），各輸出「完整畫面」與「只有移動部分」兩張
const {chromium}=require('playwright');
const Q={x:380,y:740,w:575,h:480}, S=3, FPS=30, T_END=4.1;
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:Q.w*S,height:Q.h*S}});
await p.goto('file://'+require('path').resolve('rig.html')+'?capture');await p.waitForTimeout(300);
await p.evaluate(Q=>{const s=document.getElementById('logo');s.setAttribute('viewBox',`${Q.x} ${Q.y} ${Q.w} ${Q.h}`);
  s.style.cssText=`position:fixed;left:0;top:0;width:${Q.w*3}px;height:${Q.h*3}px;max-width:none;max-height:none`;
  document.querySelector('.stage').style.padding='0';},Q);
const n=Math.round(T_END*FPS); const J=[];
for(let i=0;i<=n;i++){const t=i/FPS;
  await p.evaluate(t=>{seek(t);document.getElementById('all').setAttribute('opacity',1);document.getElementById('lamp').setAttribute('opacity',0);
    document.querySelectorAll('#all > path').forEach(e=>e.style.visibility='');},t);
  // 記錄接縫點（手腕、肩膀、伴的頂端交接）在 Q 畫素座標中的位置
  J.push(await p.evaluate(({t,Q,S})=>{const f=p=>[(p[0]-Q.x)*S,(p[1]-Q.y)*S];
    const sb=pose('ban',t), sx=pose('xiang',t), rb=RIG.ban, rx=RIG.xiang;
    const A2=[sb.P[0]+rb.A[0]-rb.B[0], sb.P[1]+rb.A[1]-rb.B[1]];
    const corners=(s,r,hs)=>{const a=s.ang*Math.PI/180,n=[-Math.sin(a),Math.cos(a)],h=r.w[r.w.length-1]/2*(hs||1);
      return [f([s.P[0]+n[0]*h,s.P[1]+n[1]*h]),f([s.P[0]-n[0]*h,s.P[1]-n[1]*h])];};
    const [bL,bR]=corners(sb,rb,1),[xL,xR]=corners(sx,rx,sx.hs);
    return {banWrist:f(sb.P), xiangWrist:f(sx.P), xiangShoulder:f(rx.A), banTop:f(A2), banL:bL, banR:bR, xiangL:xL, xiangR:xR};},{t,Q,S}));
  await p.screenshot({path:`cap/full_${String(i).padStart(3,'0')}.png`});
  await p.evaluate(()=>document.querySelectorAll('#all > path').forEach(e=>e.style.visibility='hidden'));
  await p.screenshot({path:`cap/mov_${String(i).padStart(3,'0')}.png`});
}
require('fs').writeFileSync('cap/joints.json',JSON.stringify(J));
await b.close();console.log('frames',n+1);})();
