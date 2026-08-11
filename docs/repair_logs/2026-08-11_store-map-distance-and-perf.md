# 2026-08-11 — 門市地址可開地圖 + 直線距離 + 誤點修復 + 首頁效能優化

## A. 基本資訊

| 項目 | 內容 |
|---|---|
| 日期 | 2026-08-11 |
| 專案 | baby03.tw 落地頁（`yuming740523-blip/baby03` GitHub Pages + Cloudflare Free） |
| 影響範圍 | Production 首頁全體訪客／Meta Pixel Lead 歸因／本機部署閘門（`deploy-server.py`） |
| 嚴重度 | **P2**（新功能為主）+ 內含兩個 P1 級未爆彈修復：座標資料漂移、地址熱區誤點污染 Lead |
| 結案類型 | Feature（地圖入口／距離顯示）+ Bug Fix（誤點、資料漂移防護、CDN 快取殘留）+ 效能優化 |
| 相關 commit | `789ae09` `63c9d4a` `9755fcd` `2c3bfd7` `44ed4ee`（共 5 筆，皆已 push） |
| 協作模式 | Codex 規劃 → Opus 實作驗證 → Codex 收尾確認（全程 5 輪 consult，含 2 次方案裁決、2 次收尾、1 次完整檢閱） |
| 授權 | 業主逐項指示；push 前取得明確同意；臨時公開測試網址亦逐次取得同意並於測完關閉 |

## B. 問題描述

業主需求：「點選地址後可連結地圖顯示，以及設計可以距離多少顯示」，後續追加「點入群 & 點地點容易點錯」與「要做 PageSpeed 測試（手機跑很慢）」。

實作過程中發現的既存／新生缺陷：

1. **HTML 結構衝突**：門市整列原本就是一顆 `<a href=LINE>`，要讓地址可點就得在 `<a>` 內再放 `<a>`（非法 HTML，行動裝置命中不可預期）。
2. **⚠️ Pixel 污染風險**：Pixel 監聽是 `closest('[data-fb-event]')`，只要地圖點擊發生在該 `<a>` 內就會誤發 Lead，直接灌水廣告轉換數據。
3. **⚠️ 誤點（第一版做完才實測到）**：把整條地址做成連結後，熱區只有 **18px 高 × 298px 寬**，上下左右緊貼 LINE 熱區、零緩衝（iOS 建議 44×44）→ 想點地圖點到 LINE、想點 LINE 點到地址。
4. **⚠️ 定位按鈕永久卡死**：`getCurrentPosition` 的 `timeout` 依 W3C 規格**不包含等待使用者授權的時間**，實測 Chrome 在權限對話框未被回答時 8 秒 timeout 永不觸發，按鈕永遠停在 disabled +「定位中…」（實測等 20 秒仍無反應）。
5. **⚠️ 座標資料漂移未爆彈**：新增的 `lat/lng` 沒有任何部署保護。編輯器載入時是「用線上資料補齊 localStorage 草稿的缺漏 top-level key」，只要某台機器留著加座標之前的舊 `sec1` 草稿，整段 `sec1` 會勝出、8 筆座標被無聲洗掉，而既有兩道 409 只看得到「門市消失」與「地址消失」。與 2026-08-09 的地址漂移同一類。
6. **⚠️ CDN 舊快取吃掉效能收益（上線後才發現）**：`bg.jpg` 重壓後 URL 沒變，Cloudflare 邊緣繼續服務 15 小時前的舊檔，第一次上線後傳輸量只降 8KB 而非 120KB。
7. **文案與新互動不符**：地址改成不可點後，三句定位失敗的降級訊息仍寫「仍可點地址開啟地圖」，指向一個點不動的東西。
8. 業主手機實測「很慢」— 實為測試環境假象（本機 `python -m http.server` 經 Cloudflare 臨時通道，無壓縮、無 CDN、單執行緒），非線上速度。

## C. 根因 / 背景

- **誤點根因**：把「資訊文字」與「主 CTA」放在同一個容器內、又讓資訊文字本身成為可點連結，等於在主 CTA 中央挖了一條細長的競爭熱區。正解是把地圖入口收斂成單一有邊界、符合最小觸控尺寸的按鈕，資訊文字回歸不可點。
- **Pixel 污染根因**：事件委派用 `closest()` 往上找，只要新的可點元素落在帶 `data-fb-event` 的祖先內就會被算成轉換。
- **定位卡死根因**：規格層面 `timeout` 不涵蓋授權等待，因此不能把 UI 解鎖託付給 geolocation 的 error callback。
- **座標漂移根因**：與 8/09 同源 —— 編輯器草稿以 top-level key 為粒度覆蓋線上資料，新增欄位不會被既有閘門保護。
- **CDN 殘留根因**：靜態資產以 URL 為快取鍵，內容換掉但檔名不變 → 邊緣快取不會失效。且 `render()` 會用 `DEFAULT_DATA.bg` 的 inline style 蓋掉 CSS 的背景設定，只改 CSS 無效。
- **效能現況**：線上舊版 Lighthouse mobile 93 分、LCP 3.2s、384KB。真正的肥肉是 `bg.jpg` 139KB（417×626 的平滑圖卻壓成 139KB，只有 11,647 種顏色）與 Meta Pixel 173KB（歸因命脈，不可動）。

## D. 修改內容

### D-1. `index.html`（正式產物）

| commit | 內容 |
|---|---|
| `63c9d4a` | **結構**：膠囊本體 `<a>` → `<div class="btn-link">`；內含 `.btn-hit`（`position:absolute; inset:0; z-index:1`，鋪滿整顆膠囊＝進 LINE 的熱區，`data-fb-event="Lead"` **只掛在這裡**）與 `.btn-map`（右側 44×44 有邊界按鈕，`pointer-events:auto; z-index:3`，唯一會開地圖的地方）；`.btn-body` 設 `pointer-events:none` 讓店名與地址的點擊一律穿透給 LINE；`.featured-badge` 補 `pointer-events:none`（凸出膠囊那半塊原本是點不到的死角）；`.btn-link:active` → `.btn-link:has(.btn-hit:active)`；≤360px media query |
| `63c9d4a` | **資料**：8 家門市新增 flat 的 `lat`/`lng`（Google Maps 逐筆查證門牌） |
| `63c9d4a` | **距離**：`haversineKm()` / `formatDistance()` / `renderDistances()` / `initGeo()`；使用者按鈕觸發才定位（落地頁自動彈權限會傷轉換）；**12 秒 UI 看門狗**只解鎖介面、不取消底層請求（晚一步授權距離仍會補上）；文案一律標「直線」「非車程」 |
| `63c9d4a` | **Pixel 隔離**：click 監聽開頭加 `if (e.target.closest('[data-map-link]')) return;` 作為第二道保險 |
| `63c9d4a` | **效能**：`bg.jpg` 重壓 139KB→19.9KB（PSNR 43dB）；`background-attachment` 手機改 `scroll`、≥769px 才 `fixed`；LCP 頭圖補 `srcset` 600/900/1200w + `sizes`，`fetchpriority=high`／非 lazy／`width-height` 全數保留 |
| `9755fcd` | 定位按鈕文案 →「📍 點擊顯示離我多遠」（業主手機實測後指定） |
| `2c3bfd7` | 三句降級文案「仍可點地址開啟地圖」→「仍可點『地圖』按鈕」+ 1 處失效註解 |
| `44ed4ee` | 背景圖改版本化檔名 `images/bg-20260811.jpg`（CSS 與 `DEFAULT_DATA.bg` **兩處都要改**，只改一處無效） |

### D-2. `deploy-server.py`（部署閘門，第三道 409）

| commit | 內容 |
|---|---|
| `789ae09` | 新增 `_coord()`（排除 `bool`，因為它是 `int` 子類別）與 `dropped_coords()`：既有門市原本有合法數值座標、這次卻缺失或非數值 → **409 拒絕部署**。新門市沒座標仍放行（編輯器沒有座標欄位）。掛在既有兩道閘門之後、寫檔之前 |

### D-3. 新增資產

`images/bg-20260811.jpg`(19.9KB)、`images/brand-hero-600.webp`(18.1KB)、`images/brand-hero-900.webp`(29.3KB)。舊 `images/bg.jpg` 保留不刪（避免外部引用失效）。

### D-4. 刻意不做（Codex 裁決）

不自動依距離排序、不動 utm 分流與 `featuredStore`、不接 Google Maps／Distance Matrix API、不移除 Meta Pixel、不 lazy-load LCP 圖、不改 `editor.html`、不用 AVIF（實測比 WebP 大）、背景不做 `image-set`（只多省 12.7KB 卻要背 fallback 與 `D.bg` 耦合風險）。

## E. 測試方式

全部在真實應用上執行，無 mock、無單元測試。

1. **本機**：`python -m http.server 8765`（正式檔案）+ 另起 8766 服務 `git show HEAD:index.html` 的改動前版本做同條件 A/B。
2. **命中與跳轉**：Playwright 真實滑鼠座標點擊 + `document.elementFromPoint` + 攔截實際導覽 URL（`request.isNavigationRequest()`）+ 覆寫 `window.fbq` 收集事件。
3. **定位**：`context.grantPermissions` + `setGeolocation` 覆寫座標；另用 `addInitScript` 把 `getCurrentPosition` 改成永不 callback，直接驗證看門狗。
4. **部署閘門**：沙箱複製 repo + `git init --bare` 假 remote，跑**真** `deploy-server.py`（`md5sum` 確認與正式碼相同），POST 7 種 payload。
5. **編輯器來回**：用 `deploy-server.py` 自己的 `extract_data()` 解析 → 依其 `json.dumps(ensure_ascii=False, indent=4)` 寫回 → 再解析比對。
6. **效能**：本機 Lighthouse 12.8.2 mobile 各 5 次取中位數；線上部署後再各 3 次。
7. **手機實機**：cloudflared 臨時 HTTPS 網址（業主自己的手機，測完立即關閉）。
8. **線上驗收**：`curl` 抓正式站 HTML 比對特徵字串 + Playwright 對 `https://baby03.tw/` 實點（**route 封鎖 `connect.facebook.net` 與 `facebook.com/tr`，避免在廣告數據留下假事件**）。

## F. 測試結果

**命中與跳轉（線上正式站實測）**

| 點擊位置 | 實際跳轉 | Pixel |
|---|---|---|
| 膠囊本體／店名／圖示／⭐徽章 | `line.me`（該店） | Lead ×1 |
| 地址文字／距離文字 | `line.me`（該店） | Lead ×1 |
| **地圖鈕**（第 1、3 家分別測） | `google.com/maps/…query=<該店座標>` | **0 次** |
| 地圖鈕左緣外 6px | `line.me` | Lead ×1 |

**幾何**：390px 膠囊高 102~106px、地圖鈕 44×44 全部在框內；320px + 三重最長地址換 3 行 → 膠囊 131px、鈕仍 44×44、無水平溢出。

**定位**：板橋車站 → 板橋 1.9km／士林 8.9km／苗栗 82km；中壢環北路 → 中壢店 700m（皆與實際直線距離相符）。拒絕／不支援走降級訊息；權限不回應時 12 秒看門狗解鎖介面，晚一步授權距離仍補上。

**距離格式邊界**：0.05→約100m內／0.1→約100m／0.949→約900m／0.96→約1.0km／9.94→約9.9km／9.96→約10km／133.7→約134km。

**部署閘門**：座標全失／單店失／座標變字串 → 皆 409；門市消失／地址消失 → 仍 409（回歸正常）；新增沒座標的門市 → 放行並寫檔 commit。編輯器來回：資料完全相同、檔案長度差 0（不會產生多餘 diff）。

**utm 回歸**：`banqiao_A` 板橋置頂高亮 7 家淡化；士林例外規則 `sanchong_1150701` 仍導士林；地圖鈕與門市 1:1 配對；sec2 不長地圖鈕；`a a` 巢狀連結 0；0 pageerror。

**效能**

| 指標 | 線上舊版 | 線上新版 |
|---|---|---|
| Performance | 93 | **96** |
| LCP | 3.2s | **2.78s** |
| 總傳輸 | 384 KB | **257 KB（−127KB）** |
| FCP | 1.2s | 1.21s |
| TBT / CLS | 30ms / 0 | 36ms / 0 |

本機同條件 A/B（各 5 次中位數）：LCP 1.95→1.20s、傳輸 325→205KB、分數 99→100。

## G. 回歸風險

1. **TBT 28→49ms（本機）／30→36ms（線上）**：誤點修復讓每張卡多 5 個 DOM 節點（×8 張）。Codex 判定可接受（距 200ms 門檻仍遠），若日後門市數大增或線上 TBT 逼近 150ms 需重新檢視。
2. **卡片變高**：74px → 102px，8 張約多捲 240px。以高度換清楚的命中區，Codex 判定合理。
3. **`sizes` 與版面耦合**：`(max-width:524px) calc(100vw - 24px), 500px` 的 524 = `.container` max-width 500 + body padding 12×2。日後改版面要同步改。
4. **背景圖換圖 SOP**：必須換檔名，不可原地覆蓋，否則再踩 CDN 舊快取（已寫進註解）。
5. **編輯器新增門市不會有座標** → 該店只有地圖鈕、無距離（已做降級，不會壞頁）。
6. **`:has()`** 舊瀏覽器不支援 → 只是少了按壓動畫，功能不受影響。
7. `_coord()` 與前端 `hasGeo` 未檢查 `NaN`/`Infinity`/經緯度範圍（Codex 列為非阻擋，可日後補 `math.isfinite()` 與 ±90/±180 範圍）。
8. 重複點定位按鈕可能有多個 geolocation callback 互相覆蓋狀態文字（結果仍正確，非阻擋）。

## H. 後續追蹤

| # | 項目 | 狀態 |
|---|---|---|
| 1 | Cloudflare HTML 邊緣快取（TTFB 650ms→50~150ms） | **未做**。Free 方案 Edge TTL 最低 2 小時，Codex 裁決「除非能保證每次部署後 purge，否則先不要開」。作法已備妥：Cache Rules + **Cache Key 必須設 Ignore query string**（廣告流量每支 utm 不同，否則快取會被切碎） |
| 2 | `deploy-server.py` 自動 purge | 未做，需業主提供 Cloudflare API Token |
| 3 | 8 家座標實地核對 | 未做。後 4 家地址本身來自商業登記（8/09 既有風險） |
| 4 | 蓮埔里別不一致 | Google 回「南埔里」、站上寫「慈文里」，門牌一致，暫採用 |
| 5 | `editor.html` 仍不版控 | 8/09 既有風險，未解 |
| 6 | 編輯器補座標欄位 | Codex 裁決現階段不做 |

## I. 本次結論

需求「地址可開地圖 + 顯示距離」已上線，並在過程中揪出並修掉四個原需求沒提到的問題：**地址細長熱區造成的誤點與 Lead 灌水風險、定位按鈕永久卡死、座標資料漂移未爆彈、CDN 舊快取吃掉全部效能收益**。

三個關鍵取捨：地圖入口收斂成 44×44 按鈕而非整條地址可點（用卡片高度換命中精準度）；背景圖只做 JPEG 重壓不做 WebP（省 119KB 已達標，避免 `D.bg` 耦合風險）；距離只顯示不排序（不動業主指定的 ⭐主力推薦與 utm 分流商業規則）。

效能方面同時釐清「手機很慢」是臨時通道造成的假象，線上實測 93→96 分、傳輸 −127KB；剩下最大宗是 Meta Pixel 的 173KB，屬廣告歸因命脈不可動。
