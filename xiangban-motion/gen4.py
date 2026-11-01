import json, math
L=json.load(open('layers4.json')); G=L['geo']
T=4.4
def pct(t): return f"{t/T*100:.2f}%"
EASE_REACH="cubic-bezier(.55,0,.12,1)"
EASE_SOFT="cubic-bezier(.35,0,.35,1)"
def arm_kf(name, S, u, Lr, start, end, s0, rot0, overshoot=1.045):
    a=math.degrees(math.atan2(u[1],u[0]))
    # 關鍵影格： (時間, s, 旋轉, easing)
    keys=[(0,s0,rot0,None),(start,s0,rot0,EASE_REACH),(end,1,0,EASE_SOFT),(end+.28,overshoot,0,EASE_SOFT),(end+.7,1,0,None),(T,1,0,None)]
    outer=[];arm=[];hand=[]
    for i,(t,s,r,e) in enumerate(keys):
        ef=f"animation-timing-function:{e};" if e else ""
        outer.append(f"{pct(t)}{{transform:rotate({r:.2f}deg);{ef}}}")
        arm.append(f"{pct(t)}{{transform:translate({S[0]}px,{S[1]}px) rotate({a:.3f}deg) scaleX({s:.4f}) rotate({-a:.3f}deg) translate({-S[0]}px,{-S[1]}px);{ef}}}")
        d=(s-1)*Lr
        hand.append(f"{pct(t)}{{transform:translate({d*u[0]:.2f}px,{d*u[1]:.2f}px);{ef}}}")
    return (f"@keyframes {name}Rot{{{''.join(outer)}}}\n  @keyframes {name}Arm{{{''.join(arm)}}}\n  @keyframes {name}Hand{{{''.join(hand)}}}")
# 長者（伴）先伸：0.55s 起，2.05s 抵達；青年（巷）0.85s 起，同時抵達
kf_b=arm_kf('ban',G['bS'],G['bu'],G['bL'],0.55,2.05,0.22,9)
kf_x=arm_kf('xiang',G['xS'],G['xu'],G['xL'],0.85,2.05,0.12,24)
lamp_on=2.35
html=f'''<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>巷伴 動態標準字 — 雙手</title>
<style>
  :root{{--ink:#634F44;--bg:#FFFFFF;--lampIn:#FFF1D2;--lampOut:#F2CB86}}
  body.dark{{--ink:#FFFFFF;--bg:#000000;--lampIn:#FFE7B0;--lampOut:#F0B04F}}
  html,body{{margin:0;height:100%;background:var(--bg);transition:background .5s;font-family:system-ui,"PingFang TC","Noto Sans TC",sans-serif}}
  .stage{{height:100%;display:flex;align-items:center;justify-content:center;padding:0 6vw;box-sizing:border-box}}
  svg{{width:100%;max-width:1000px;max-height:80vh;height:auto;overflow:visible}}
  .ink{{fill:var(--ink);transition:fill .5s}}
  #logo *{{transform-box:view-box}}
  #logo .a{{animation-duration:{T}s;animation-fill-mode:both;animation-timing-function:linear}}

  /* 0 淡入 */
  #all{{animation-name:fade}}
  @keyframes fade{{0%{{opacity:0;animation-timing-function:cubic-bezier(.4,0,.2,1)}}{pct(.5)}{{opacity:1}}100%{{opacity:1}}}}

  /* 1 長者的手（伴）：先伸出。撇由短伸長、向下掃到拐杖握把 */
  #banRot{{transform-origin:{G['bS'][0]}px {G['bS'][1]}px;animation-name:banRot}}
  #banArm{{transform-origin:0 0;animation-name:banArm}}
  #banHand{{transform-origin:0 0;animation-name:banHand}}
  /* 2 青年的手（巷）：從屋旁由短伸長，從下垂抬起，同一瞬間抵達 */
  #xiangRot{{transform-origin:{G['xS'][0]}px {G['xS'][1]}px;animation-name:xiangRot}}
  #xiangArm{{transform-origin:0 0;animation-name:xiangArm}}
  #xiangHand{{transform-origin:0 0;animation-name:xiangHand}}
  {kf_b}
  {kf_x}

  /* 3 握到之後，家裡的燈亮起 */
  #lamp{{animation-name:warm}}
  @keyframes warm{{0%,{pct(lamp_on)}{{opacity:0;animation-timing-function:cubic-bezier(.3,0,.2,1)}}{pct(lamp_on+.45)}{{opacity:.6}}{pct(lamp_on+.65)}{{opacity:.5;animation-timing-function:cubic-bezier(.16,1,.3,1)}}{pct(lamp_on+1.4)},100%{{opacity:1}}}}

  .ui{{position:fixed;left:50%;bottom:24px;transform:translateX(-50%);display:flex;gap:10px}}
  .ui button{{border:1px solid currentColor;background:transparent;color:var(--ink);padding:8px 16px;border-radius:999px;font-size:13px;letter-spacing:.05em;cursor:pointer;opacity:.6}}
  .ui button:hover{{opacity:1}}
  body.capture .ui{{display:none}}
  @media (prefers-reduced-motion:reduce){{#logo .a{{animation-duration:0s!important;animation-delay:-10s!important}}}}
</style>
</head>
<body>
<div class="stage">
<svg id="logo" viewBox="40 700 1300 670" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="巷伴">
  <defs>
    <radialGradient id="lampG" cx="45%" cy="40%" r="75%"><stop offset="0" stop-color="var(--lampIn)"/><stop offset="1" stop-color="var(--lampOut)"/></radialGradient>
  </defs>
  <g id="all" class="a">
    <!-- 巷 -->
    <path class="ink" d="{L['xiangTop']}"/>
    <path class="ink" d="{L['xiangStatic']}"/>
    <circle class="ink" cx="{G['xS'][0]}" cy="{G['xS'][1]}" r="31.5"/>
    <path id="lamp" class="a" d="{L['window']}" fill="url(#lampG)" opacity="0"/>
    <g id="xiangRot" class="a">
      <g id="xiangArm" class="a"><path class="ink" d="{L['xiangArm']}"/></g>
      <g id="xiangHand" class="a"><path class="ink" d="{L['xiangHand']}"/></g>
    </g>
    <!-- 伴：拐杖固定不動 -->
    <path class="ink" d="{L['cane']}"/>
    <g id="banRot" class="a">
      <g id="banArm" class="a"><path class="ink" d="{L['banArm']}"/></g>
      <g id="banHand" class="a"><path class="ink" d="{L['banHand']}"/></g>
    </g>
    <path class="ink" d="{L['banMain']}"/>
    <path class="ink" d="{L['dot1']}"/>
    <path class="ink" d="{L['dot2']}"/>
  </g>
</svg>
</div>
<div class="ui">
  <button onclick="replay()">重新播放</button>
  <button onclick="document.body.classList.toggle('dark')">黑底 / 白底</button>
</div>
<script>
  function replay(){{const s=document.getElementById('logo');s.replaceWith(s.cloneNode(true));}}
  const q=new URLSearchParams(location.search);
  ['dark','capture'].forEach(k=>q.has(k)&&document.body.classList.add(k));
  window.seek=t=>document.getAnimations().forEach(a=>{{a.pause();a.currentTime=t*1000;}});
</script>
</body>
</html>'''
open('index.html','w').write(html)
