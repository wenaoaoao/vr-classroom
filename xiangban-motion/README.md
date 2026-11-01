# 巷伴 動態標準字

打開 `index.html` 就能播放（純 SVG + CSS，不需要任何套件）。`xiangban-light.mp4` / `xiangban-dark.mp4` / `.gif` 是 10 秒的預覽錄影。

## 動態邏輯

| 時間 | 動作 | 意涵 |
|---|---|---|
| 0–1.4s | 「巷」從左、「伴」從右靠過來，兩隻手相碰，碰到的地方亮起一圈暖光 | 兩手相牽 |
| 1.6s 起循環 | 兩個字同步向彼此靠近 5px 再分開，像牽著手輕輕擺 | 陪伴 |
| 1.6s 起循環 | 拐杖以握把為軸左右擺 ±3.2° | 長者 |
| 1.9s | 「巳」像開燈一樣閃兩下後亮起，窗格透出暖光，之後緩緩呼吸 | 溫暖的家 |

## 調整參數（都在 `index.html` 的 `<style>` 裡）

- 顏色：`--ink`（字色）、`--light`（巳亮起的顏色）、`--glass`（窗格的光）
- 拐杖擺幅：`@keyframes cane` 裡的 `3.2deg`；速度：`#cane` 的 `3.2s`
- 牽手擺動：`@keyframes swayL / swayR` 裡的 `5px`
- 開燈閃爍節奏：`@keyframes switchOn`；呼吸強度：`@keyframes breathe` 的 `.72`
- 網址加 `?dark` 預設黑底；加 `?capture` 隱藏按鈕（錄影用）。
