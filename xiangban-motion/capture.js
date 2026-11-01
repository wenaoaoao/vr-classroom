// 逐格渲染手部區域 Q（原稿座標），各輸出「完整畫面」與「只有移動部分」兩張
const {chromium}=require('playwright');
const Q={x:380,y:740,w:575,h:480}, S=3, FPS=30, T_END=3.4;
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:Q.w*S,height:Q.h*S}});
await p.goto('file://'+require('path').resolve('rig.html')+'?capture');await p.waitForTimeout(300);
await p.evaluate(Q=>{const s=document.getElementById('logo');s.setAttribute('viewBox',`${Q.x} ${Q.y} ${Q.w} ${Q.h}`);
  s.style.cssText=`position:fixed;left:0;top:0;width:${Q.w*3}px;height:${Q.h*3}px;max-width:none;max-height:none`;
  document.querySelector('.stage').style.padding='0';},Q);
const n=Math.round(T_END*FPS);
for(let i=0;i<=n;i++){const t=i/FPS;
  await p.evaluate(t=>{seek(t);document.getElementById('all').setAttribute('opacity',1);document.getElementById('lamp').setAttribute('opacity',0);
    document.querySelectorAll('#all > path').forEach(e=>e.style.visibility='');},t);
  await p.screenshot({path:`cap/full_${String(i).padStart(3,'0')}.png`});
  await p.evaluate(()=>document.querySelectorAll('#all > path').forEach(e=>e.style.visibility='hidden'));
  await p.screenshot({path:`cap/mov_${String(i).padStart(3,'0')}.png`});
}
await b.close();console.log('frames',n+1);})();
