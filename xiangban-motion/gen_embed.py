# 從 index.html 取出向量與逐格資料，產生可嵌入任何網頁的元件 embed/xiangban-logo.js
import re, json
h=open('index.html',encoding='utf-8').read()
grp=lambda gid: re.search(r'<g id="%s"[^>]*>(.*?)</g>'%gid,h,re.S).group(1)
static=re.sub(r'<path id="frame"/>','',grp('play'))
rest=grp('rest')
lamp=re.search(r'<path id="lamp" d="([^"]+)"',h).group(1)
frames=json.loads(re.search(r'const FR=(\[.*?\]);',h,re.S).group(1))
svg=f'''<svg viewBox="40 700 1300 670" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="巷伴" part="svg">
<defs><radialGradient id="lampG" cx="45%" cy="40%" r="75%"><stop offset="0" stop-color="var(--xiangban-lamp-in,#FFF1D2)"/><stop offset="1" stop-color="var(--xiangban-lamp-out,#F2CB86)"/></radialGradient></defs>
<g id="all"><g id="play">{static}<path id="frame"/></g><g id="rest" style="display:none">{rest}</g><path id="lamp" d="{lamp}" opacity="0"/></g></svg>'''
js=r'''/*!
 * 巷伴 動態標準字 <xiangban-logo>
 * 用法：
 *   <script src="xiangban-logo.js" defer></script>
 *   <xiangban-logo></xiangban-logo>
 * 屬性：
 *   trigger="load"     開啟網頁就播放（預設：捲動到看得見時才播放）
 *   delay="0.3"        延遲幾秒才開始
 *   static             不播放動畫，直接顯示完成的標準字
 *   sound              播放音效（瀏覽器規定：訪客點過頁面後才能出聲；還沒點過時動畫照常、靜音播放）
 * 顏色（CSS 變數，可寫在任何外層元素上）：
 *   --xiangban-ink: #634F44;        字色
 *   --xiangban-lamp-in: #FFF1D2;    窗燈中心
 *   --xiangban-lamp-out: #F2CB86;   窗燈外圈
 * JavaScript：document.querySelector('xiangban-logo').play()  重新播放
 * 使用者在系統中開啟「減少動態效果」時，會直接顯示完成的標準字。
 */
(()=>{
const SVG=__SVG__;
const SND='data:audio/mpeg;base64,__SND__';
const FR=__FRAMES__;
const FPS=30, LAST=FR.length-1, END=LAST/FPS, FADE=.45, TOTAL=5.4;
const FLK=__FLK__, FLOFF=__FLOFF__;
const clamp=t=>Math.max(0,Math.min(1,t)), lerp=(a,b,t)=>a+(b-a)*t;
function cb(x1,y1,x2,y2){return t=>{if(t<=0)return 0;if(t>=1)return 1;let lo=0,hi=1,u=t;for(let i=0;i<30;i++){u=(lo+hi)/2;const x=3*(1-u)*(1-u)*u*x1+3*(1-u)*u*u*x2+u*u*u;if(x<t)lo=u;else hi=u;}return 3*(1-u)*(1-u)*u*y1+3*(1-u)*u*u*y2+u*u*u;}}
const easeOut=cb(.16,1,.3,1), easeSoft=cb(.4,0,.3,1);
function lampAt(t){const K=FLK;let o=0;if(t>=K[0][0]){o=K[K.length-1][1];for(let i=0;i<K.length-1;i++){if(t<K[i+1][0]){const u=(t-K[i][0])/(K[i+1][0]-K[i][0]);o=K[i][1]+(K[i+1][1]-K[i][1])*(i===K.length-2?easeOut(u):u);break;}}}return o*(1-easeSoft(clamp((t-FLOFF[0])/FLOFF[1])));}
function popAt(t){const a=1.72,p=1.9,b=2.5;if(t<=a||t>=b)return 1;const u=t<p?easeOut((t-a)/(p-a)):1-easeSoft((t-p)/(b-p));return 1+.045*u;}
class XiangbanLogo extends HTMLElement{
  connectedCallback(){
    if(this._init)return; this._init=true;
    const root=this.attachShadow({mode:'open'});
    root.innerHTML='<style>:host{display:inline-block;width:100%;max-width:1000px;line-height:0}svg{width:100%;height:auto;overflow:visible}path{fill:var(--xiangban-ink,#634F44)}#lamp{fill:url(#lampG)}</style>'+SVG;
    const q=s=>root.getElementById(s);
    this._el={all:q('all'),play:q('play'),rest:q('rest'),frame:q('frame'),lamp:q('lamp')};
    const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
    if(this.hasAttribute('static')||reduce){this._render(99);return;}
    this._render(0);
    const go=()=>setTimeout(()=>this.play(),(parseFloat(this.getAttribute('delay'))||0)*1000);
    if(this.getAttribute('trigger')==='load'||!('IntersectionObserver' in window)){go();return;}
    const io=new IntersectionObserver(es=>{if(es.some(e=>e.isIntersecting)){io.disconnect();go();}},{threshold:.4});
    io.observe(this);
  }
  _render(t){
    const e=this._el;
    e.all.setAttribute('opacity',easeOut(clamp(t/FADE)));
    const sc=popAt(t); e.all.setAttribute('transform',`translate(690 1035) scale(${sc}) translate(-690 -1035)`);
    const done=t>=END;
    e.play.style.display=done?'none':''; e.rest.style.display=done?'':'none';
    if(!done)e.frame.setAttribute('d',FR[Math.min(LAST,Math.round(t*FPS))]);
    e.lamp.setAttribute('opacity',lampAt(t));
  }
  play(){
    cancelAnimationFrame(this._raf); let t0=null;
    if(this.hasAttribute('sound')){try{if(!this._audio)this._audio=new Audio(SND);this._audio.currentTime=0;const pr=this._audio.play();if(pr)pr.catch(()=>{});}catch(e){}}
    const step=now=>{if(t0===null)t0=now;const t=(now-t0)/1000;this._render(t);
      if(t<TOTAL)this._raf=requestAnimationFrame(step);else this.dispatchEvent(new Event('ended'));};
    this._raf=requestAnimationFrame(step);
  }
  seek(t){cancelAnimationFrame(this._raf);this._render(t);}
}
if(!customElements.get('xiangban-logo'))customElements.define('xiangban-logo',XiangbanLogo);
})();
'''
import base64
FL=json.load(open('flicker.json'))
js=js.replace('__FLK__',json.dumps(FL['keys'])).replace('__FLOFF__',json.dumps(FL['off']))
js=js.replace('__SND__',base64.b64encode(open('sound/xiangban.mp3','rb').read()).decode()).replace('__SVG__',json.dumps(svg,ensure_ascii=False)).replace('__FRAMES__',json.dumps(frames))
open('embed/xiangban-logo.js','w',encoding='utf-8').write(js)
print('xiangban-logo.js KB',len(js.encode())//1024)
