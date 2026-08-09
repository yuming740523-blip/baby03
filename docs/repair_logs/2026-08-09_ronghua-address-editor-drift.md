# 2026-08-09 — 新增桃園榮華店 + 門市地址上架 + 修掉編輯器資料漂移地雷 + 首頁簡化與 SEO/分享圖

## A. 基本資訊

| 項目 | 內容 |
|---|---|
| 日期 | 2026-08-09 |
| 專案 | baby03.tw 落地頁（`yuming740523-blip/baby03` GitHub Pages + Cloudflare） |
| 影響範圍 | Production 首頁全體訪客／本機編輯器與部署流程／搜尋與社群分享預覽 |
| 嚴重度 | **P1**（其中「編輯器資料漂移」是隨時可能把線上 8 家門市洗成 6 家的未爆彈）+ P2/P3 功能與視覺變更 |
| 結案類型 | Bug Fix（資料漂移防護）+ Feature（新門市／地址／置頂公告／品牌頭圖）+ SEO 修正 |
| 相關 commit | `7e956a7` `3e92f38` `0e42ef3` `f030f78` `bb1696e` `cca4a34` `e990ebb` `81c0f1e`（共 8 筆，皆已 push） |
| 協作模式 | Codex 檢閱與規劃 → Opus 實作與驗證 → Codex 收尾確認（全程 9 輪 consult） |
| 授權 | 業主逐項指示；每次 push 前均取得明確同意 |

## B. 問題描述

本次由業主一句「新增桃園榮華店社群網址 + 調整首頁順序」開場，過程中連續追加需求，並在檢閱時挖出一個既存的高風險缺陷：

1. **新門市未上架**：桃園榮華店的 LINE 社群已開，但首頁沒有入口。
2. **⚠️ 編輯器資料漂移（本次最嚴重）**：`editor.html` 內建的 `DEFAULT_DATA` 早已過期（只有 6 家、缺士林葫東與桃園榮華），且**沒有任何路徑會去讀線上 `index.html` 的現況**。在一台沒有 localStorage 的機器上開編輯器按「一鍵部署」，會把線上 8 家門市直接洗成 6 家，並自動 `git commit + push`，全程無攔截。此缺陷在 6/10 加士林葫東時就已存在，只是沒被觸發。
3. **`featuredKeepBright` 是死欄位**：編輯器完全沒有 UI，只能手改 `index.html`；一旦編輯器那份過期，部署就會把門市亮暗態改壞。
4. **`normalizeUrl()` 三斜線 bug**：`saveCostcoConfig()` 用的網址正規化會把站內相對路徑 `/costco` 變成 `https:///costco`（潛在，尚未觸發）。
5. **meta description 與頁面不符**：資訊卡（服務保證／營業時間）移除後，描述仍宣稱「支援 LINE PAY／信用卡／匯款，開立電子發票」，搜尋點進來看不到對應內容。
6. **完全沒有 Open Graph 標籤**：本頁主要靠 LINE 分享與 FB 廣告貼文傳播，分享預覽卡片由平台自行猜測。

## C. 根因 / 背景

- **漂移根因**：`editor.html` 的 `load()` 是「localStorage → 否則用內建 DEFAULT_DATA」，內建那份是 hard-coded 快照，會隨每次直接改 `index.html` 而過期。正式產物（`index.html` 的 DATA 區塊）與編輯器種子資料**沒有任何同步機制**。
- **部署端無防線**：`deploy-server.py` 只做「找到標記 → 整段替換 → add/commit/push」，不比對現況、不檢查資料是否縮水。
- **爆炸半徑釐清**：實測 `STORE_ROUTES`（L251）位於 `@@DATA_END@@`（L245）**之後**，故 utm 分流邏輯不會被編輯器部署覆寫；真正會被洗掉的只有 DATA 區塊那 18 個 key。
- **地址欄位的新風險**：本次替 `sec1` 加了 `addr` 後，`saveEditBtn()` 原本是 `D[sec][idx] = {t, label, url}` 整個物件重建 → 只要在編輯器點一次「✏️ 編輯」再儲存，地址就會無聲消失，而既有 409 閘門只擋「門市消失」擋不住「欄位消失」。

## D. 修改內容

### D-1. `index.html`（正式產物）

| commit | 內容 |
|---|---|
| `7e956a7` | 新增桃園榮華店（URL 去掉 `?utm_source=invitation...` query）；順序改為 榮華→士林→板橋→三重→蓮埔→八德→中壢→苗栗；`featuredKeepBright` `[1,2]`→`[1,2,3]`；`STORE_ROUTES` 加 `/ronghua|榮華/`（**刻意不加 `/taoyuan|桃園/` 通則**，避免榮華與蓮埔互搶流量）；meta 門市數 6→8 |
| `0e42ef3` | `sec1` 每筆加 `addr`，8 家地址顯示在膠囊內店名正下方（`.btn-body` 上下兩行、置中對齊、`#333`）；白色資訊卡**暫時移除**（六個資料欄位完整保留 + 留可直接貼回的復原片段）；`hotDeals.on`→false、`widget3.on`→false；`sec1Title` 升為 `<h1>` |
| `bb1696e` | `widget.on`→false（關閉「發送訊息」Messenger 浮動鈕） |
| `cca4a34` | description 改成只描述頁面現有內容；title 改為「寶貝我愛你童裝｜美食團購 LINE 下單」；補 10 個 og:* 與 4 個 twitter:* |
| `e990ebb` | 置頂公告：沿用既有 `notice` 欄位（不新增 schema），`position:sticky`、黃底橘框粗字 |
| `81c0f1e` | 品牌頭圖 `brand-hero.{webp,jpg}`（1200×449）；分享圖 `og-image.jpg`（1200×630）；`twitter:card` `summary`→`summary_large_image` |

### D-2. `editor.html`（本機工具，**不版控**，已備份 `editor.html.bak-canonical-20260809-2040`）

- **改成以 `index.html` 為單一真實來源**：新增 `extractDataFromIndexHtml()` / `loadCanonicalData()` / `stableStringify()` / `diffKeys()` / `askDataSource()` / `bootstrapData()`；啟動時 `fetch('index.html')` 解析 DATA 當基準，草稿與線上不一致時跳視窗讓使用者選（預設建議載入線上），取不到線上資料時**明確報錯不靜默降級**。
- 補 `featuredKeepBright` 的 checkbox UI（主打店本身在存檔時被 filter 掉）。
- `normalizeUrl()` 改為委派 `fixUrl()`（保留 `/` 開頭）；`saveCostcoConfig()` 改用 `normalizeUrl`。
- 按鈕編輯 modal 新增「門市地址」欄位；`saveEditBtn()` 改用展開 `{...D[sec][idx], ...}` 保留既有欄位；`confirmAddBtn()` 帶 `addr`。

### D-3. `deploy-server.py`（有版控）

| commit | 內容 |
|---|---|
| `3e92f38` | 新增 `extract_data()` / `store_key()` / `missing_stores()`；寫檔前比對現況，**既有門市消失 → 409**，不寫檔不 commit 不 push；解析失敗也拒絕部署 |
| `f030f78` | 新增 `dropped_addresses()`；**既有門市地址消失 → 409**；新門市無地址合法不擋 |

門市 identity 用 `url` 優先、缺 url 才用 `label`（排序可合法改變，位置不能當識別）。

### D-4. 圖片資產（由業主提供的印刷完稿重製）

業主提供 `寶貝童裝招牌_完稿.ai`（300×90cm）與 `紅布條設計_完稿.ai`（300×60cm）詢問是否置頂。**原圖不適合直接上網頁**：5:1／3.33:1 是遠距觀看比例，390px 手機上小字僅 5~7px；招牌寫死「板橋宏國店」但本頁服務 8 家；QR code 在網頁上無用；紅布條是限時活動內容。

故以 PyMuPDF 4000px 渲染 + PIL 本機處理（**未經生成模型，避免品牌字形與 logo 變形**）重製：
- `brand-hero`：裁掉 QR 與店名膠囊；FB 藍條用其正下方乾淨背景 clone patch 覆蓋（超出高度處上下鏡射接續）
- `og-image`：以清乾淨的頭圖為基底，下方 181px 標語帶取頭圖底部平均色壓暗 62% 保持同色系，帶內加「美食團購 LINE 下單」

## E. 測試方式

**原則：真實瀏覽器 + 真實 deploy server + 真實 git，全程不做 mock；且不拿正式站當測試場。**

- **首頁**：`python -m http.server` 服務真實 repo → Playwright 開 390×844 與 1600×1000，讀 DOM／computed style／`elementFromPoint`／`getBoundingClientRect`，並以 iframe 真實載入各 utm 情境。
- **部署閘門**：`git clone --bare` 正式 repo 成假 remote，再 clone 出工作副本，把改好的 `editor.html`／`deploy-server.py` 複製進去跑真實 `deploy-server.py`。以 md5 確認沙箱跑的就是正式碼、沙箱 `index.html` 初始狀態與正式站一致。
- **線上**：push 後 poll `https://baby03.tw/?cb=<ts>`，下載 HTML 與正式檔 diff，再用 Playwright 實測線上 DOM 與 utm 分流。

## F. 測試結果

### F-1. 首頁（本機 + 線上）

| 檢查 | 結果 |
|---|---|
| 門市順序與亮暗態 | ⭐桃園榮華／亮：士林、板橋、三重／淡：蓮埔、八德、中壢、苗栗 ✓ |
| 8 家地址 | 全部正確、位於 `<a>` 內店名下方、店名中心與地址中心**誤差 0px** ✓ |
| utm 分流 | `ronghua`／`榮華`／`RONGHUA_1150801` 命中榮華；`sanchong_1150701` 仍導士林（例外規則存活）；`sanchong`→三重；`lianpu`→蓮埔；`banqiao`→板橋；`shilin`→士林；`taoyuan` 不誤命中 ✓ |
| 地址是否跟著 utm 重排 | `zhongli`／`miaoli`／`ronghua`／`lianpu` 置頂後地址皆正確跟隨 ✓ |
| 新 LINE 網址 | 去 query 後 `curl` 200，`og:title` = 寶貝美食團(桃園榮華店) ✓ |
| 資訊卡／熱門團購／好市多／發送訊息 | 四者皆已不渲染，浮動鈕只剩「查看訂單」 ✓ |
| Pixel 屬性 | 11 顆按鈕 `data-fb-event`/`data-store`/`data-channel`/`data-button` 全完整 ✓ |
| 點擊命中 | `elementFromPoint(膠囊中心).closest('a')` === 該 `<a>` ✓ |
| 置頂公告 | 捲動 900px 後距頂 0px、黏住時最上層確實是它 ✓ |
| 品牌頭圖 | 434px 視窗下 410×153，公告+頭圖僅佔首屏 23%，第一顆門市按鈕仍在首屏內 ✓ |
| SEO/OG | title 20 字、description 已無「LINE PAY／信用卡／匯款／電子發票」、og/twitter 各 1 份無重複且皆絕對網址 ✓ |
| 線上資產 | `brand-hero.webp` 回 `image/webp` 42,538B；`og-image.jpg` 回 `image/jpeg` 98,099B ✓ |

### F-2. 部署閘門（沙箱）

| 測試 | 結果 |
|---|---|
| 送 6 家舊草稿（既有門市消失） | **409**「桃園榮華店、士林葫東店」，index.html md5 不變、無 commit、無 push ✓ |
| 清空某既有門市 addr | **409** ✓ |
| 整個移除 addr 欄位 | **409** ✓ |
| 新增一家沒地址的門市 | 放行、寫檔、commit ✓ |
| 正常修改地址 | 放行 ✓ |
| 放行後 `STORE_ROUTES` 是否被波及 | **完全沒有**（在 DATA 區塊外）✓ |

### F-3. 編輯器（沙箱）

| 測試 | 結果 |
|---|---|
| 清空 localStorage 開啟 | 載入 **8 家**、`featuredKeepBright=[1,2,3]`、6 個漂移欄位全部對齊線上（**修復前是 6 家**）✓ |
| 植入 6 家舊草稿 | 跳衝突視窗，正確列出「線上 8 家｜草稿 6 家」與 4 個不一致欄位 ✓ |
| 選「載入正式站資料」 | 回到 8 家並回寫 localStorage ✓ |
| 好市多網址填 `/costco` | 存成 `/costco`，**無 `https:///`**（修復前會壞）✓ |
| **只改店名不碰地址 → 儲存** | `addr` 保留、欄位 `['t','label','url','addr']` 完整（**修復前會遺失**）✓ |
| 主打店視窗改高亮設定 | 存成 `[2,3]`，故意勾主打店本身會被正確排除 ✓ |

## G. 回歸風險

1. **`push` 成功這段始終未在沙箱驗到**：本機有全域 git push 封鎖 hook，沙箱 push 一律失敗。只驗到「閘門放行 → 寫檔 → commit」。實際 push 走本機 git，本次 8 筆皆成功。
2. **門市 identity 用 URL 優先**：日後若要**合法更換**某家門市的 LINE 網址、或要**刪掉**一家門市，會被 409 擋下，需人工流程（先改 `index.html` 再部署）。
3. **後 4 家地址是網路查來的**：桃園蓮埔／八德金和／中壢環北／苗栗國華取自商業登記資料（twincn／iyp 等），已去縣市前綴與「1樓」以統一格式。業主回覆「地址沒問題」，但未逐家實地核對。商業登記地址不保證等於實際店面地址。
4. **資訊卡復原時會出現重複公告**：`notice` 已被獨立拿來當置頂公告渲染，若把資訊卡整段貼回，同一句會出現兩次。已在復原註解中寫明需擇一保留。
5. **`editor.html` 不版控**：本次所有編輯器修復都不進 git，換機器／重灌就沒了，漂移會再發生一次。已備份為 `editor.html.bak-canonical-20260809-2040`。
6. **編輯器預覽不顯示地址**：`editor.html` 的 `buildBtns()` 未同步改（其按鈕內嵌編輯／刪除控制項，改結構風險高）。資料本身安全可編，只是預覽與正式站外觀有落差。
7. **黃色 sticky 公告與橘黃紅頭圖同時出現在首屏**：Codex 提出視覺可能太吵；已明確告知業主，業主看過預覽後確認採用。

## H. 後續追蹤

| # | 動作 | 類型 | 期限 |
|---|---|---|---|
| 1 | 後 4 家門市地址請業主實地核對 | 業主決定 | 有空時 |
| 2 | 信任訊號（服務保證／營業時間）是否回歸 | 業主決定 | 未定（業主說「暫時」移除） |
| 3 | 後 4 家門市是否解除 `opacity .65` 淡化 | 業主決定 | 未定 |
| 4 | 8 顆按鈕文字重複「美食團購LINE下單」是否精簡（**改文案會動到 Pixel 抓店名的 `label.match(/【([^】]+)】/)`**） | 業主決定 | 未定 |
| 5 | 「查看訂單」浮動鈕是否符合本頁流量目的 | 業主決定 | 未定 |
| 6 | 紅布條活動要不要放（需確認有效期、適用店別、下架日） | 業主決定 | 未定 |
| 7 | 頭圖下方補一行 HTML 說明文案（Codex 建議，本次未做因超出指示範圍） | 工程 | 隨時 |
| 8 | apex 與 www 的 canonical 策略 | 工程 | 隨時 |
| 9 | `images/` 2.6MB 未使用資產清理（`bg-4.jpg` 單檔 1.28MB；注意編輯器背景選單仍用 bg-2~bg-10） | 工程 | 隨時 |
| 10 | `editor.html` 納入版控的可行性（含 `PASS='baby03'` 明碼的取捨） | 工程 | 隨時 |
| 11 | `editor.html` 的 `showLineConfig()` 命名債（實際管的是 Messenger 不是 LINE） | 工程 | 隨時 |
| 12 | `editor.html` 預覽顯示地址（需改 `buildBtns()` 結構並回歸編輯／刪除操作） | 工程 | 隨時 |
| 13 | `deploy-server.py` 自動 push 無二次確認 | 工程 | 隨時 |
| 14 | FB 分享偵錯工具重新抓取 `https://baby03.tw/` 以更新舊快取 | 業主操作 | 即時 |
| 15 | `openMessenger()` 因關閉 Messenger 而成為死碼 | 工程 | 低優先 |

## I. 本次結論

- ✅ 桃園榮華店上架並置頂，8 家門市地址全數顯示於膠囊內店名下方。
- ✅ **修掉隨時可能把線上 8 家洗成 6 家的編輯器資料漂移未爆彈**：編輯器改以 `index.html` 為單一真實來源，部署端加兩道 409 閘門（門市消失／地址消失）。這是本次最有價值的產出，且是在檢閱過程中主動挖出來的，不在業主原始需求內。
- ✅ 首頁依業主指示簡化：資訊卡、熱門團購、好市多、發送訊息全部關閉，且**全部採可一鍵復原的做法**（資料開關或保留資料+復原註解），未刪任何資料。
- ✅ 補上 SEO 與社群分享基礎：title 對齊主訴求、description 不再宣稱頁面沒有的內容、OG/Twitter Card 從 0 補到 14 個標籤、分享圖由 500×500 純 logo 換成 1200×630 品牌設計圖。
- ✅ 印刷完稿沒有硬塞上網頁，而是取其品牌元素重製為網頁專用素材（本機處理、可重現、未經生成模型）。
- **流程**：全程「Codex 檢閱規劃 → Opus 實作驗證 → Codex 收尾確認」，共 9 輪 consult；其中一輪 Codex 回傳被污染的無關內容（resume 接錯 thread），已識破並開乾淨 thread 重問，未採信。每次 push 前皆取得業主明確同意。
- **自我修正**：過程中自己抓到並修掉三個錯誤——地址白字在淺綠背景讀不到、OG 圖第一版背景含原稿文字導致疊字、輪詢腳本因 shell 多位元組處理誤報線上漏店。均已如實向業主揭露。
