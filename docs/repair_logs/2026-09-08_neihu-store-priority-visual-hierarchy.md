# 2026-09-08 — 內湖門市優先順位與卡片視覺層級調整

## A. 基本資訊

| 項目 | 內容 |
|---|---|
| 日期 | 2026-09-08 |
| 專案 | baby03.tw 落地頁（GitHub Pages + Cloudflare） |
| 影響範圍 | Production／首頁「美食團購 LINE 下單」門市清單 |
| 嚴重度 | P3（商業排序與視覺層級調整，無服務中斷） |
| 結案類型 | Feature / UI hierarchy adjustment |
| 正式程式 | `index.html` 的 `DEFAULT_DATA.sec1`、`featuredKeepBright`、`buildBtns()` |
| commits | `dfecf5f`、`3e3d28b` |
| 執行分工 | Codex 讀取／規劃／實作／驗證／上線；使用者明確授權「由 Codex 直接做」 |
| 最終驗證入口 | Chrome 143 `report` instance，CDP `8116`；未使用 `9222` |

## B. 問題描述

首頁自然流量原本以桃園榮華店放大置頂，內湖店排在最後且套用次要樣式；內湖廣告 UTM 雖能把內湖置頂，卻把士林、榮華、板橋、三重全部縮小，且榮華排在板橋／三重之前。

業主分兩次收斂最終需求：

1. 排序改為「內湖 → 士林 → 板橋 → 三重 → 榮華 → 其餘門市」。
2. 內湖是唯一放大並顯示 `⭐ 主力推薦`；士林維持正常；板橋、三重取消高亮，改成與榮華完全相同的次要效果。
3. 自然流量與內湖 UTM landing 必須一致；其他門市 UTM 的「命中店置頂放大」行為不得改。

## C. 根因分析

問題由兩個獨立入口共同造成：

1. `DEFAULT_DATA.sec1` 的實體陣列順序仍是榮華第一、內湖最後；自然流量直接依此順序渲染。
2. `featuredStore: 0` 會放大陣列第 0 筆，而 `featuredKeepBright: [1,2,3]` 會讓其後三筆保持正常，因此舊資料自然形成「榮華放大、士林／板橋／三重正常」。
3. `buildBtns()` 對 `ROUTED_KEY === '內湖'` 有獨立排序特例，舊 `rank` 只有「內湖、士林、榮華」，且 `keepBright = [0]`，使除內湖外的門市全部成為 `btn-secondary`。
4. 第一次調整後，業主進一步確認板橋／三重不需要正常亮度；因此自然流量的 `featuredKeepBright` 與內湖特例的 `keepBright` 都必須由 `[1,2,3]` 收斂為 `[1]`。

## D. 修改內容

### D-1 `dfecf5f` — 內湖改為第一順位

- 將 `DEFAULT_DATA.sec1` 排序改為：內湖、士林、板橋、三重、榮華、蓮埔、八德、中壢、苗栗。
- 每間門市既有 `label`、LINE URL、地址與座標原值搬動，未改資料內容。
- 內湖 UTM 特例 `rank` 同步為 `['內湖','士林葫東','板橋宏國','三重大有','桃園榮華']`。
- 保留其他門市 UTM、`sanchong_1150701` 例外規則及 Facebook 社團分流。

### D-2 `3e3d28b` — 板橋／三重改為榮華同級

- `DEFAULT_DATA.featuredKeepBright` 由 `[1,2,3]` 改為 `[1]`。
- 內湖 UTM 特例的 `keepBright` 同步由 `[1,2,3]` 改為 `[1]`。
- 最終 class：內湖 `btn-featured`；士林無額外 class；板橋、三重、榮華及後續門市均為 `btn-secondary`。

## E. 測試方式

1. 對正式 `index.html` 兩段 inline JavaScript 逐段做語法編譯檢查。
2. 以 Playwright 開啟正式頁面，直接讀門市 DOM 順序、class、實際寬度、computed opacity、唯一 featured 數量與水平溢位。
3. 驗證自然流量、內湖、士林、板橋、三重、榮華，以及既有 `sanchong_1150701` 士林例外路由。
4. 驗證 Facebook 美食社團網址仍依內湖／士林／榮華分流，其他店維持共用網址。
5. 分別以桌機 `1280×900`、手機 `375×812` 驗證。
6. push 後透過 Chrome 143 `report` instance 的 CDP `8116` 開啟 `https://baby03.tw/`，輪詢至新 class 生效，再重跑線上矩陣。
7. Git 檢查使用 `git diff --check`、staged allowlist、遠端 master SHA readback；既有未提交檔案不納入 commit。

## F. 測試結果

### F-1 語法與版本控制

- Inline JavaScript：`2/2 PASS`。
- `git diff --check`：PASS。
- `dfecf5f`：只修改 `index.html`，`14 insertions / 13 deletions`。
- `3e3d28b`：只修改 `index.html`，`3 insertions / 5 deletions`。
- GitHub `master` 最終 readback：`3e3d28b7c77592d1a012cc93816b29b82e2df599`。

### F-2 最終線上視覺結果

| 門市 | 桌機寬度 | 手機寬度 | opacity | 樣式 |
|---|---:|---:|---:|---|
| 內湖 | `520px` | `349px` | `1` | 唯一 `btn-featured`／主力推薦 |
| 士林 | `500px` | `336px` | `1` | 正常 |
| 板橋 | `480px` | `323px` | `0.65` | `btn-secondary` |
| 三重 | `480px` | `323px` | `0.65` | `btn-secondary` |
| 榮華 | `480px` | `323px` | `0.65` | `btn-secondary` |

- 第一階段本機：桌機 7 路由 + 手機 2 路由全部 PASS。
- 最終版本機 CDP `8116`：桌機 6 路由 + 手機 2 路由全部 PASS。
- 最終版線上 CDP `8116`：桌機 6 路由 + 手機 2 路由全部 PASS，部署輪詢第 1 次即讀到新版本。
- 每個情境都只有 1 個 featured；自然流量與內湖 UTM 的板橋／三重／榮華寬度及 opacity 完全一致；無水平溢位。
- 其他門市 UTM 仍維持命中店置頂放大，其餘縮小；Facebook 社團分流未退化。

## G. 回歸風險

1. `featuredKeepBright` 使用陣列 index；日後若在 `DEFAULT_DATA.sec1` 再換順序，必須同步確認亮度 index。
2. 內湖 UTM 有 `buildBtns()` 專屬分支；自然流量與內湖 landing 的商業層級改動必須同步兩個 `keepBright` 來源。
3. 編輯器可替換 `@@DATA_START@@` 到 `@@DATA_END@@`；透過編輯器重存門市資料時需確認 `featuredKeepBright: [1]` 未被舊草稿覆蓋。
4. `sanchong_1150701` 仍刻意導向士林；這是既有廣告歷史例外，本次未改。
5. Playwright／CDP 連接過程出現 Node `url.parse()` deprecation warning，屬驗證工具相依套件訊息，不是網站 console error，也不影響頁面結果。

## H. 後續追蹤

| # | 事項 | 狀態 |
|---|---|---|
| 1 | 觀察自然流量與內湖廣告入口的門市點擊分布 | 建議後續依 Pixel／社群數據觀察，不影響本次結案 |
| 2 | 日後若調整門市順序，同步檢查 `featuredKeepBright` 與內湖 `rank/keepBright` | 長期維護規則 |
| 3 | 本次需求的程式、部署與線上驗證 | 已完成，無待修項目 |

## I. 本次結論

`baby03.tw` 已完成門市商業順位與視覺層級調整：自然流量及內湖廣告入口都以內湖為第一順位且唯一放大，士林保持正常，板橋與三重依業主最後裁定改為和榮華完全相同的次要樣式。其他門市 UTM、LINE／Facebook 連結、Pixel 與既有三重例外規則均未修改。兩筆正式 commit 已 push，並由 Chrome 143 CDP `8116` 完成本機與線上桌機／手機驗證。
