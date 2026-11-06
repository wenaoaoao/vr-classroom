# 產生開頭書寫遮罩的 SVG defs 與 JS（gen8.py、gen_embed.py 共用）
import json
def make():
    I=json.load(open('intro.json'))
    W=I['width']; defs=[]; mask=[]
    for k,s in enumerate(I['strokes']):
        defs.append(f'<clipPath id="wc{k}" clipPathUnits="userSpaceOnUse"><path d="{s["clip"]}"/></clipPath>')
        mask.append(f'<g clip-path="url(#wc{k})"><path id="ws{k}" d="" fill="none" stroke="#fff" stroke-width="{W}" stroke-linecap="round" stroke-linejoin="round"/></g>')
    for j,h in enumerate(I['hands']):
        defs.append(f'<clipPath id="hc{j}" clipPathUnits="userSpaceOnUse"><path d="{h["clip"]}"/></clipPath>')
        mask.append(f'<g clip-path="url(#hc{j})"><circle id="wh{j}" cx="{h["cx"]}" cy="{h["cy"]}" r="0" fill="#fff"/></g>')
    svg=''.join(defs)+'<mask id="writeMask" maskUnits="userSpaceOnUse" x="0" y="0" width="1400" height="2000">'+''.join(mask)+'</mask>'
    data={'end':I['end'],'s':[[s['t0'],s['t1'],s['pts']] for s in I['strokes']],'h':[[h['t0'],h['t1'],h['r']] for h in I['hands']]}
    js=('const XBI='+json.dumps(data)+';\n'
        'function xbInOut(u){return u<.5?4*u*u*u:1-Math.pow(-2*u+2,3)/2;}\n'
        'function xbPart(P,f){if(!P.L){P.L=[0];for(let i=1;i<P.length;i++)P.L.push(P.L[i-1]+Math.hypot(P[i][0]-P[i-1][0],P[i][1]-P[i-1][1]));}'
        'const T=P.L[P.length-1]*f;let d="M"+P[0][0]+" "+P[0][1];for(let i=1;i<P.length;i++){if(P.L[i]<=T){d+="L"+P[i][0]+" "+P[i][1];}else{const a=(T-P.L[i-1])/(P.L[i]-P.L[i-1]||1);'
        'd+="L"+(P[i-1][0]+(P[i][0]-P[i-1][0])*a).toFixed(1)+" "+(P[i-1][1]+(P[i][1]-P[i-1][1])*a).toFixed(1);break;}}return d+(T<0.5?"l0.1 0":"");}\n'
        'function xbIntro(get,t){'
        'XBI.s.forEach((s,k)=>{const u=Math.max(0,Math.min(1,(t-s[0])/(s[1]-s[0])));get("ws"+k).setAttribute("d",u>0?xbPart(s[2],xbInOut(u)):"");});'
        'XBI.h.forEach((h,j)=>{const u=Math.max(0,Math.min(1,(t-h[0])/(h[1]-h[0])));'
        'const b=u<1?1-Math.pow(1-u,3)*(1+2.2*u):1;get("wh"+j).setAttribute("r",(h[2]*Math.max(0,b)).toFixed(1));});}\n')
    return svg,js,I['end']
