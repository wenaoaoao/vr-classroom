# 巷伴 動態標準字｜現況摘要

給接手的人或其他對話快速了解目前版本。詳細參數與重新產生步驟見 `README.md`。

## 檔案位置
- GitHub：https://github.com/wenaoaoao/vr-classroom/tree/claude/pensive-galileo-ao16f5/xiangban-motion
- 分支：`claude/pensive-galileo-ao16f5`（尚未合併到主分支）
- 資料夾：`xiangban-motion/`

## 成品
| 用途 | 檔案 |
|---|---|
| 網頁嵌入 | `embed/xiangban-logo.js`（`<xiangban-logo trigger="load" sound></xiangban-logo>`），範例 `embed/example.html` |
| 單頁播放 | `index.html` |
| 有聲影片 | `xiangban-light-sound.mp4`、`xiangban-dark-sound.mp4` |
| 無聲影片／GIF | `xiangban-light.mp4`、`xiangban-dark.mp4`、`xiangban-light.gif`、`xiangban-dark.gif`、`xiangban-hands-closeup.gif` |
| 音效 | `sound/xiangban.wav`、`sound/xiangban.mp3` |
| 透明背景 GIF（簡報用） | `transparent/xiangban-light-transparent-loop.gif`（咖啡色字，淺色投影片）、`transparent/xiangban-dark-transparent-loop.gif`（白字，深色投影片）；`-once` 版本只播一次 |
| 逐格對照圖 | `frames-contact-sheet.png`（回饋時可用格數指出位置） |

## 設計概念
專案：給社區「媒合者」使用的青銀互助工具組；理念「長者不只是被照顧，而是還被需要」。
動態：長者（伴，握拐杖）先伸手，青年（巷）跟上，兩手真的握在一起，家（巳）的窗燈亮起。

## 目前動作（約 4.1 秒停在標準字，燈 5.1 秒暗完）
| 秒 | 動作 |
|---|---|
| 0–0.45 | 以收起姿勢淡入（設計稿 `source/keyposes.jpg` 第 1 張） |
| 0.45 / 0.55 | 長者（伴）先伸手、青年（巷）跟上，手臂由短伸長 |
| 1.6 | 兩手碰到 |
| 1.6–1.85 | 伴的手包住巷的手，真的握緊（`source/keyposes2.jpg` 第 3 張）；整組字輕彈一下 |
| 1.8–2.9 | 「伴」上面兩點像開心晃腳一樣晃兩下，其餘時間不動 |
| 1.85–2.65 | 握手上下搖兩下 |
| 1.87–2.45 | 窗燈像老式日光燈閃四下後亮穩 |
| 2.65–3.75 | 鬆開、兩手收回 |
| 3.77–4.1 | 漸變回原稿標準字，之後靜止 |
| 4.3–5.1 | 窗燈慢慢暗掉 |

## 音效（程式合成，無版權問題）
伸手：兩聲拇指琴＋輕柔氣流聲；碰到：木頭輕敲；握緊：明亮和音；握手兩下：圓潤低音「咚」；燈：輕柔開關聲「嗒」＋溫暖和弦；燈暗：兩個落下的音。

## 已試過、被否決的方向
- 整塊字滑入、拐杖鐘擺、巳整個變金色閃爍（不夠高級）
- 開頭依筆順「寫出來」（已撤回）
- 日光燈電流嗡聲、尖銳的啟動器喀聲（太嚇人）
- 兩點從頭晃到尾（太亂，改成只在握住時晃）

## 回饋方式
看 `frames-contact-sheet.png`，用「格數＋位置」描述問題（例如「#54 伴的手腕」），修正最快。
