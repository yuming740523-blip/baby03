# 2026-08-23 — 士林／榮華依 utm 導向各店專屬美食團購 FB 社團

## A. 基本資訊

| 項目 | 內容 |
|---|---|
| 日期 | 2026-08-23 |
| 專案 | baby03.tw 落地頁（yuming740523-blip/baby03 GitHub Pages + Cloudflare Free）|
| 影響範圍 | Production／首頁「社群連結」區的美食團購 FB 社團按鈕（僅帶 utm 的廣告流量）|
| 嚴重度 | P2（Feature，fallback-safe，自然流量零變動）|
| 結案類型 | Feature 新增（社團層分店分流）|
| commit | `f814fdc`（1 file changed, +30 −0，只動 index.html）|
| 流程 | Codex 規劃 → Opus 實作 → Codex 完整檢閱（讀全檔）→ Opus 修 → Codex 收尾確認（本案共 7 輪 consult）|
| 授權 | 業主指定士林／榮華兩店社團網址；追加內湖後又裁定「這次只推士林／榮華」「檢閱通過直接 push」|

## B. 問題描述

首頁 sec2「社群連結」的 `🍴【美食團購】臉書社團` 是**全站共用**一顆（`babyiloveyou.pse.is/5gvz6r` → `groups/360124028800443`），
8 間門市不分家。業主要求：**社團網址要依各店進入**，並提供兩間店的專屬社團：

- 士林店 → `https://www.facebook.com/groups/980998417913637`
- 榮華店 → `https://www.facebook.com/groups/1360732452112600`

## C. 根因／背景

不是 bug，是既有功能的邊界。2026-06-05 上線的 utm→店別分流（見 `2026-06-05_utm-store-routing.md`）
**只作用在 sec1（門市 LINE 下單清單）**：命中就把該店置頂＋⭐高亮。
`buildBtns()` 對 sec2 完全不介入，社群連結三顆一律照 `DEFAULT_DATA` 原樣渲染 —— 所以社團層沒有任何分店概念。

## D. 修改內容（`index.html`，3 塊，全部在 `@@DATA_END@@` 之外）

1. **`STORE_FB_GROUPS` 對照表**（新增，緊接 `ROUTED_IDX` 之後）
   ```js
   const STORE_FB_GROUPS = {
       '士林葫東': { store: '士林葫東店', url: 'https://www.facebook.com/groups/980998417913637' },
       '桃園榮華': { store: '桃園榮華店', url: 'https://www.facebook.com/groups/1360732452112600' }
   };
   ```
   key 用既有 `STORE_ROUTES` 的店 key；`store` 欄位刻意與 sec1 label 的【】內文字一致。

2. **`routedStoreKey()`**（新增）：讀 `utm_campaign` + `utm_content`，回傳第一個命中的 `STORE_ROUTES.key`，
   無命中回 `''`。**刻意不從 `ROUTED_IDX` 反推** —— 那是 sec1 的陣列位置，日後某店從 sec1 拿掉，社團分流會跟著失效。
   為此接受了「與 `routedStoreIndex()` 重複三行讀 utm 的程式碼」，不動既有函式。

3. **`buildBtns()` 內 sec2 覆寫**（在原 if/else 決定 fi/keepBright 之後、`items.map` 之前）
   ```js
   const fbGroup = (sec === 'sec2') ? STORE_FB_GROUPS[ROUTED_KEY] : null;
   if (fbGroup) {
       items = items.map(b => (b && b.t === 'fb' && (b.label || '').includes('美食團購'))
           ? { ...b, url: fbGroup.url, label: '🍴【' + fbGroup.store + '】美食團購臉書社團' }
           : b);
   }
   ```

### 設計取捨（Codex 裁決）

| 取捨 | 決定 | 理由 |
|---|---|---|
| 對照表放哪 | DATA 區塊**外** | `deploy-server.py` 只替換 `@@DATA_START@@`~`@@DATA_END@@`，放外面才不會被編輯器一鍵部署洗掉 |
| 怎麼認出目標按鈕 | 同時比 `t === 'fb'` **且** label 含「美食團購」 | sec2 有兩顆 FB，只看 `t==='fb'` 會把全站共用的【童裝女裝用品】臉書社團一起改掉 |
| 要不要換按鈕文字 | 換 | Pixel 的 `store` 是從 label 的【】抓的；只換 url 不換 label，會變成「按鈕寫美食團購、實際進士林社團」，報表也失真 |
| pse.is 兩顆共用社團 | **不碰** | 業主要保留 lihi 的點擊統計與後台改目標彈性（該短網址頁自帶 `PicSeeURLClick` Pixel）|
| 沒專屬社團的 6 店與自然流量 | 不覆寫 = 用共用社團 | 隱藏按鈕會直接砍掉入口，得不償失 |

### 本次「只推一部分」的裁切

實作過程中業主追加了內湖店（門市＋社團）與 Android App 直開，最後裁定**這次只推士林／榮華**。
裁切前先備份完整版：`index.html.bak-neihu-deeplink-20260823`（未進版控）＋一份 git patch，
之後移除內湖門市／`neihu` 路由／內湖社團／App 直開整段／meta 文案改動（內湖不上線 → 原本的「全台 8 間門市…附各店地址」重新成立）。

## E. 測試方式

- 本機：`python -m http.server 8899 --bind 127.0.0.1`（Playwright 真實 Chromium，非 mock）
- 逐一 `browser_navigate` 後讀 DOM：`ROUTED_KEY` / `ROUTED_IDX` / sec1 置頂與高亮 / sec2 三顆的 label 與 href
- Pixel：stub `window.fbq` 後**實際 click**，bubble 階段 `preventDefault` 擋導航，讀事件參數
- 編輯器相容性：實開 `editor.html`（會 fetch index.html 抽 DATA），確認讀到的門市與 sec2 內容
- 語法：python 抽出 inline `<script>`（2 段）對主體跑 `node --check`（v22.12.0）
- 線上：push 後輪詢 `https://baby03.tw/?cb=<ts>` 直到出現 `STORE_FB_GROUPS`，再用 Playwright 打真實網址

## F. 測試結果

### F-1 本機（含裁切前的完整版共 11 組情境，裁切後複測 5 組全過）

| 情境 | ROUTED_KEY | sec1 | sec2 美食社團 |
|---|---|---|---|
| 無 utm | `''` | 8 店，榮華⭐、士林/板橋/三重亮 | `pse.is/5gvz6r`（原值）|
| `?utm_campaign=shilin_prod` | 士林葫東 | 士林置頂 | `groups/980998417913637`／【士林葫東店】|
| `?utm_campaign=ronghua_prod` | 桃園榮華 | 榮華置頂 | `groups/1360732452112600`／【桃園榮華店】|
| `?utm_campaign=sanchong_1150701` | 士林葫東 | 士林置頂 | `groups/980998417913637` |
| `?utm_campaign=neihu_0822` | `''` | 榮華⭐（內湖這次沒上）| `pse.is/5gvz6r` |

Pixel 實點：美食社團 `store=士林葫東店 route_store=士林葫東店/utm`、童裝社團 `store=童裝女裝用品` 且 url 未變、地圖鈕不送 Lead（三次點擊只有 2 筆事件）。
`node --check` → **JS SYNTAX OK**。編輯器實開讀到正確門市數、未跳草稿衝突框。

### F-2 線上（`https://baby03.tw`，push 後 try 2 即偵測到更新，40137 bytes）

| 網址 | 結果 |
|---|---|
| `/?cb=live1`（自然流量）| 榮華⭐、8 店、士林/板橋/三重亮 → **與上線前一致** ✓ |
| `?utm_campaign=shilin_prod` | 士林置頂＋士林社團，童裝仍 `pse.is/baby037` ✓ |
| `?utm_campaign=ronghua_prod` | 榮華置頂＋榮華社團 ✓ |
| `?utm_campaign=sanchong_1150701` | 仍導士林（既有例外規則未破）✓ |
| `utm_campaign=fbad_2026&utm_content=shilin_creative_a` | utm_content 也會命中 ✓ |
| `?utm_campaign=neihu_0822` | 不命中，落回榮華＋共用社團 ✓ |
| `ronghua_prod` + `utm_content=shilin_creative`（混合）| 依 `STORE_ROUTES` 順序榮華勝出，且 sec1 與 sec2 **同一店** ✓ |

各頁 console 無錯誤；線上 `typeof fbGroupIntent === 'undefined'` = true（App 直開確實沒跟著上線）。

## G. 回歸風險

1. **辨識條件綁在 label 文字**：日後在編輯器把「美食團購」四個字從 sec2 那顆 FB 按鈕拿掉，覆寫會靜默失效、退回共用社團（不會壞版，但分流沒了）。
2. **只有站內 sec2 會分流**：`go/fb-food.html`（meta refresh → `groups/360124028800443`）與 `pse.is` 短網址都沒動，
   廣告若直接投這兩個入口，不會依店分流。
3. **Pixel 報表切點**：士林／榮華命中時 `store` 從「美食團購」變成店名，Events Manager 舊報表的分組會出現斷點（刻意，為了分店歸因）。
4. **`sanchong_1150701` 例外規則連帶效果**：該 utm 會被判成士林，因此也會拿到士林專屬社團 —— 與 2026-08-08 建立的例外規則語意一致。
5. **判斷來源含 `utm_content`**：不是只看 campaign，`utm_content` 裡出現 `shilin`／`ronghua` 也會觸發。
6. **編輯器一鍵部署安全**：邏輯在 DATA 區塊外，`deploy-server.py` 只換 DATA（已讀碼＋實開編輯器確認）。

## H. 後續追蹤

| # | 事項 | 狀態 |
|---|---|---|
| 1 | 內湖店（sec1 第 9 店＋專屬社團 `groups/1569798504694646`）| 已實作並測過，**未上線**；等業主提供店址（無地址則無地圖鈕與距離）。還原用 `index.html.bak-neihu-deeplink-20260823` |
| 2 | Android App 直開 FB 社團（`intent://…package=com.facebook.katana` + `S.browser_fallback_url`）| 已實作並通過 42 組 UA×URL 桌面驗證，**未上線**；必須 Android 實機驗證（有裝/沒裝 FB App、Facebook Lite、FB/IG/LINE in-app、Firefox Android）|
| 3 | 觀察 Events Manager 的 `store` 分佈，確認士林／榮華社團點擊有分出來 | 數天後 |

## I. 本次結論

社團層的分店分流上線，士林／榮華的廣告流量點「美食團購臉書社團」會進各自的社團，
其餘門市與自然流量維持共用社團、行為零變動。改動 30 行、無刪除、無新依賴，
回滾方式＝`git revert f814fdc`，或直接移除 `STORE_FB_GROUPS` / `routedStoreKey()` / `buildBtns` 內那段 if。

### 本案可複用的教訓

1. **「只推一部分」要先備份完整版再裁切**，且裁完要用機器掃殘留關鍵字，不能靠肉眼確認沒留半截程式。
2. **殘留關鍵字要夠精確**：第一次掃 `intent://` 直接誤中既有 `openMessenger()` 的 `intent://user/`，
   差點把「已清乾淨」誤判成「沒清乾淨」。掃描字串要指向本次新增的獨有形態（`intent://www.facebook.com/groups`）。
3. **Codex 沙箱不一定能跑 parser check**，它自己也註明沒跑成 → 語法驗證要自己補（抽 inline script 跑 `node --check`）。
4. **「不改善」不等於「變差」**：一度把「內湖 utm 上線後落回榮華」講成上線風險，
   實際上線上原本就沒有內湖，前後行為相同。評估上線影響要跟**線上現況**比，不是跟本機開發版比。
5. **覆寫連結時 label 要一起換**，否則畫面文字、Pixel `store`、實際目的地三者會各說各話。
