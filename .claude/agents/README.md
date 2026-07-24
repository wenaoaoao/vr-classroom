# DoseDial 專業視角 Review Agents

四個可直接呼叫的 Claude Code subagent，模擬畢業製作開發過程中會遇到的四種專業視角。放在 `.claude/agents/` 下即為專案自動載入，不用每次手動貼 system prompt。

## 角色列表

| 檔案 | 角色 | 何時用 |
|---|---|---|
| `assistive-tech-advisor.md` | 輔具設計專業顧問 | 需求定義階段，確認使用情境沒有偏掉 |
| `industrial-designer.md` | 工業設計師（結構/機構） | 動手建模前，確認機構在 3D 列印下可行 |
| `visual-brand-designer.md` | 視覺／品牌設計師 | 機構定案後，定調品牌與介面方向 |
| `thesis-reviewer.md` | 畢業製作審查委員 | 最後階段，壓力測試整份提案的論述邏輯 |

## 怎麼呼叫

直接在對話裡指名角色即可，例如：

> 用 industrial-designer 這個 agent 看一下這個卡榫機構的公差設計

或直接描述需求，Claude 會依 `description` 自動挑選對應角色。

## 交叉比對（建議）

工業設計與審查委員最常抓到彼此看不到的問題，可以同一輪一起叫兩個角色對同一份設計稿給意見：

> 同時用 industrial-designer 和 thesis-reviewer 看一下這版簡報稿的機構說明段落

## 建議使用順序

1. `assistive-tech-advisor` → 確認需求定義
2. `industrial-designer` → 確認機構可行性
3. `visual-brand-designer` → 定調視覺與介面
4. `thesis-reviewer` → 壓力測試論述邏輯，模擬正式審查

每次拿到回饋後，建議簡短記錄「這個角色抓到的問題」與「打算怎麼調整」，之後寫進企劃書的「設計過程」章節也很有用。

## 各角色的盲區

每個角色的檔案末尾都附有「這個角色通常不會告訴你的事」，提醒不要只靠單一角色的回饋就定案——四個角色合起來才是完整的審查視角。
