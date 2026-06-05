# 2026-06-05 — 首頁 utm→店別動態分流上線（廣告帶 utm 自動 highlight 對應門市）

## A. 基本資訊

| 項目 | 內容 |
|---|---|
| 日期 | 2026-06-05 |
| 專案 | baby03.tw 落地頁 (yuming740523-blip/baby03 GitHub Pages + Cloudflare Free) |
| 影響範圍 | Production / 首頁帶 utm 訪客視覺（廣告流量）/ Pixel 歸因 |
| 嚴重度 | P2（新功能，fallback-safe，未動自然訪客體驗）|
| 結案類型 | Feature 新增（漏斗底店別分流）+ Pixel 歸因強化 |
| 相關 commit | `fae26ea`（utm→店別分流 + Pixel route_store）|
| 授權 | 業主下「改 baby03 / 做 utm 店別分流」「改 baby03 部署」（baby03-guard 放行）|

## B. 問題描述

7 間門市的廣告（板橋 D `utm_campaign=banqiao_A`、三重 `sanchong_dayou_1150517`、F `banqiao_F`）全部導向**同一個** baby03.tw 共用選單。原首頁**不依 utm 分流**：`utm_campaign` 只餵 Pixel 事件、不改版面；主推店 `featuredStore` 寫死。

現役 `featuredStore:0` = 三重大有店 ⭐、`featuredKeepBright:[1]` = 板橋宏國亮 → **板橋廣告點進去看到的主推竟是三重**，對板橋不利；且無法區分哪一支廣告（哪間店）帶人進哪個社群／社團。

業主需求：依廣告 utm **自動把對應門市置頂＋高亮**（板橋廣告→板橋亮、三重廣告→三重亮），並能分店量點擊。

## C. 根因 / 背景

- 原 `index.html` `buildBtns()` 用寫死的 `D.featuredStore`；`URLSearchParams` 僅出現在 Pixel 點擊 handler。
- 動態分流**從未實作**（非遺失）。查證 6 層交叉確認：live HTTP GET（三種 utm 回應 byte 相同）/ working tree / **git 全歷史**（`.git/logs/HEAD` 最後一筆 5/17「三重升主推」，無分流 commit）/ `go/*.html`（FB 社團轉址頁）/ `editor.html` / `C:\dev\baby03`（costco worker，非落地頁）/ `D:\程式設計\網頁專案`（部署筆記+截圖，全文搜零命中）。
- 業主一度以為「動態板橋三重已有」= 其實是**手動主推店切換**（4/16 設板橋→5/17 改三重），非 utm 自動分流。

## D. 修改內容（index.html 3 處，僅動邏輯不動 DATA）

1. **`const D` 後新增分流核心**：`STORE_ROUTES`（banqiao/sanchong/bade/lianpu/zhongli/miaoli，中英關鍵字）+ `routedStoreIndex()`（讀 `utm_campaign`+`utm_content`，命中→該店 index）+ `const ROUTED_IDX`（-1 = 無命中）。
2. **`buildBtns()`**：sec1 且 `ROUTED_IDX>=0` → 該店**置頂**（移到陣列首）+ `fi=0`/`keepBright=[0]`（⭐高亮、其餘淡化、**不 auto-open**）；否則落回原 `D.featuredStore`/`D.featuredKeepBright`。
3. **Pixel `Lead` 事件**（事件名不變）：加 `route_store`（路由到的門市）+ `route_source`（`utm`/`default`）。

**廣告端零改動**：D/三重/F 既有 utm_campaign 前綴直接命中。

## E. 測試方式

### E-1. 本機（部署前必做）
- `file://` 被 Playwright 擋 → `python -m http.server 8899 --directory <baby03-site>`（受 guard 保護時用授權詞放行）。
- Playwright 跑 4 情境，各 `browser_snapshot`（驗 DOM 首位+⭐）+ `browser_take_screenshot`：
  - `?utm_campaign=banqiao_A` / `?utm_campaign=sanchong_dayou_1150517` / 無 utm / `?utm_campaign=foobar_unknown_999`。

### E-2. 線上（部署後）
- `git push origin master` → poll `https://baby03.tw/?cb=<ts>`（cache-buster 繞 CF）直到出現 `STORE_ROUTES`。
- Playwright 實測線上 3 情境 + 自然訪客回歸。

## F. 測試結果

### F-1. 本機 4/4 全過
| 網址 | 結果 |
|---|---|
| `banqiao_A` | 🍴【板橋宏國店】置頂 + ⭐主力推薦 ✓ |
| `sanchong_dayou_1150517` | 🍴【三重大有店】置頂 + ⭐主力推薦 ✓ |
| 無 utm | 三重⭐ + 板橋第2亮（落回預設）✓ |
| `foobar_unknown_999` | 三重⭐（安全落回，不會壞）✓ |

### F-2. 線上（baby03.tw，push 後 try-1 即偵測 `STORE_ROUTES`，HTML 17045→18562 bytes）
| 網址 | 結果 |
|---|---|
| `baby03.tw/?utm_campaign=banqiao_A` | 板橋宏國 置頂 + ⭐ ✓ |
| `baby03.tw/?utm_campaign=sanchong_dayou_1150517` | 三重大有 置頂 + ⭐ ✓ |
| `baby03.tw/`（自然訪客）| 三重⭐ + 板橋第2亮，**與原本一致、未影響自然流量** ✓ |

## G. 回歸風險

1. **新店廣告 utm_campaign 須含店別關鍵字**（banqiao/sanchong/bade/lianpu/zhongli/miaoli，中英都認）；只給日期或 campaign ID → 落回預設（三重），不壞但不分流。
2. **editor 匯出安全**：分流邏輯在 `@@DATA_START@@/@@DATA_END@@` 區塊**外**，`exportHTML()` 只換 DATA 不洗邏輯。
3. **fallback-safe**：try/catch 包覆，例外或無命中一律落回 `featuredStore` 預設。
4. **FB 社團 join 仍無法用 utm 歸因**：FB 不給 per-link join + 7 店共用社團；真加入歸因只能靠社團**入會問題**。點擊層可用 Pixel `route_store` 分店（含美食團購社團按鈕）。

## H. 後續追蹤

| # | 動作 | 期限 |
|---|---|---|
| 1 | （選做）美食團購社團開「入會審核 + 門市問題」做真‧加入歸因 | 業主有空 |
| 2 | 觀察 Events Manager `route_store` 累積數據（板橋 vs 三重 點各社群/社團量）| 數天後 |
| 3 | 新店擴充：`STORE_ROUTES` 加一行 + 確認該店在 sec1 即可 | 隨時 |

## I. 本次結論

- ✅ utm→店別動態分流上線（commit `fae26ea`）：板橋廣告→板橋亮、三重廣告→三重亮、無 utm 落回三重預設。
- ✅ 點擊層歸因內建（Pixel `route_store`/`route_source`），含下方「美食團購臉書社團」按鈕。
- ✅ 廣告端零改動；本機 + 線上各情境全過；自然訪客體驗未變。
- 連帶：三重影片「漏斗底前置（utm→店別 highlight）」**已清**（但影片仍受 6/4–6/6 投放凍結 + 6/6 收盤等其他閘，本輪未動投放）。
- **流程**：本次全程依 5/01 建立的 baby03-guard 硬閘門（授權詞放行）+「本機測→給業主看→授權→push→線上實測回歸」閉環，作法固化於 `D:/程式設計/fb廣告/docs/ads/BABY03_LANDING_CHANGE_SOP.md`。
