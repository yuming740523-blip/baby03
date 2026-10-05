# 新莊中港店新增、首頁排序與專屬落地頁

## 1. 基本資訊

- 日期：2026-10-05；專案：`C:\Users\User\Desktop\baby03-site`。
- 類型：新增門市與落地頁內容更新；嚴重度 P2（門市上架資料完整性未閉環）。
- 業主要求新增新莊中港店，並將其排在首頁第 4 位及建立專屬落地頁。
- 正式程式修改分兩筆已推送 commit：`9a0ebc5` 新增門市資料；`f061e1f` 調整排序並新增路由。
- 專屬落地頁是共用 `index.html` 的 UTM 網址 `https://baby03.tw/?utm_campaign=xinzhuang_zhonggang&utm_content=xinzhuang_page`，不是獨立 HTML 檔。
- LINE 社群：`https://line.me/ti/g2/yCDJ5lTIskMFOjrSFEb1BixRrMLS6Br8js4fPA?utm_source=invitation&utm_medium=link_copy&utm_campaign=default`。
- 地址依業主提供原文記錄：`新北市新莊區恆安里中港路50號(鄰新莊國小)`。

## 2. 問題描述

網站原有 10 間門市，沒有新莊中港店。新增資料後，需求再擴充為首頁第 4 位及由新莊專屬 UTM 進站時置頂、放大的落地頁。修改已部署，但發布後回查發現新店沒有 WGS84 數值 `lat`、`lng`，也沒有座標地圖查詢與距離元件資料。

## 3. 根因分析

`DEFAULT_DATA.sec1` 是首頁與 UTM 落地頁共用的門市資料來源；既有 `STORE_ROUTES`、`routedStoreIndex()` 與 `buildBtns()` 可依路由將指定店置頂及放大，因此新增一筆門市資料、移至第 4 位並加一條路由即可完成前述展示需求。

但本次新增流程未依 `docs/STORE_ONBOARDING_SOP.md` 先查核完整門牌的權威地理資料並取得 WGS84 座標。地址文字是業主提供的輸入，不能視為獨立門牌查核；既有大甲與內湖座標流程也不能替代新莊查核。故網站需求已實作並經路徑驗證，門市完整上架契約仍未符合 SOP。

## 4. 修改內容

- `9a0ebc5`：在 `DEFAULT_DATA.sec1` 新增新莊中港店名稱、完整 LINE URL 與業主提供地址，共 6 行。
- `f061e1f`：將新莊中港店移至第 4 位，新增 `/xinzhuang|新莊|中港/i` 路由識別 `新莊中港`，沿用既有置頂與放大行為。
- 其餘門市欄位及既有分流未修改；本輪沒有變更 Meta 廣告。
- 本維修紀錄及專案／全域索引依業主要求歸檔；既有未提交檔案不納入本次文件 commit，全域索引位於專案 Git 外。

## 5. 測試方式

- 本機正式 `index.html`：以 PowerShell UTF-8 here-string 管線執行 `python -X utf8 -`，在真實 inline JavaScript 上執行 `node --check`，並以 Playwright Chromium 驗證手機寬 390、桌面寬 1280 的首頁及路由頁。同步逐項核對 13 條路徑（首頁 1 + campaign 12，其中包含新莊路由）與 3 種新莊 `utm_content`（英文 `xinzhuang_page`、中文「新莊」、中文「中港」）。
- 正式站：逐 URL HTTP 回讀首頁、新莊專頁、大甲、內湖及三重舊 UTM 例外（特殊士林）共 5 個 URL；比較正式資料及來源與 `f061e1f`，僅排除 Cloudflare 自動注入的 beacon。線上 Playwright 驗證手機及桌面首頁／新莊專頁共 4 個版面，並回歸大甲、內湖與特殊士林（三重舊 UTM 例外）3 種既有分流。
- 歸檔前由主協調者另行以 PowerShell UTF-8 here-string 管線執行 `python -X utf8 -`，使用 `urllib.request` 逐一回讀首頁與新莊專頁，檢查 HTTP、完整來源及新店資料。

## 6. 測試結果

- 本機 `node --check` 與 Playwright 成功；13 條路徑通過，新莊三種 `utm_content` 均命中預期門市。首頁第 4 位；專頁第 1 張 featured 主力推薦；LINE、地址與地圖按鈕符合輸入；11 店筆數與本輪指定欄位核對通過（新莊座標仍缺）；無橫向溢出或 `pageerror`。
- 歸檔前正式站追加回讀：首頁與新莊專頁 HTTP `2/2` 為 200，11 店資料及來源符合 `f061e1f`（僅排除 Cloudflare beacon），新莊位於資料第 4 位；`lat`、`lng` 均缺失。
- 14:24 正式站歷史驗證：以下 5 URL 均 HTTP 200，來源符合 `f061e1f`（排除 Cloudflare beacon），`5/5 PASS`：

  | URL | HTTP／source 結果 |
  |---|---|
  | `https://baby03.tw/` | 200／PASS |
  | `https://baby03.tw/?utm_campaign=xinzhuang_zhonggang&utm_content=xinzhuang_page` | 200／PASS |
  | `https://baby03.tw/?utm_campaign=dajia_yuying&utm_content=dajia_page` | 200／PASS |
  | `https://baby03.tw/?utm_campaign=neihu_0822` | 200／PASS |
  | `https://baby03.tw/?utm_campaign=sanchong_1150701` | 200／PASS |

  同次線上 Playwright 首頁與新莊專頁手機／桌面 `4/4`；大甲、內湖、特殊士林（三重舊 UTM 例外）分流回歸 `3/3`；無 JS 錯誤。此歷史 5/5 與歸檔前追加回讀 2/2 分開計列。
- 驗證過程更正紀錄：13:58 一次驗證在全文 assert 提前中止，當時錯誤的 PASS 已於同分鐘更正為 FAIL；13:59 以 UTF-8 修正後真實執行 exit 0。14:00 正式站仍是舊版 10 店，不算發布完成；14:01 回讀雖有 11 店，來源差異仍待查；14:02 確認唯一差異是 Cloudflare beacon，排除該注入後才判定來源吻合。14:23曾把 12 條 campaign 全稱作既有分流，當分鐘已更正分母為首頁 1 + campaign 12（含新莊）= 13 條路徑。
- 未使用獨立測試腳本；命令輸出留在當次執行紀錄，不宣稱存在永久測試檔。

## 7. 回歸風險

- **已知未符合 SOP**：新莊缺少經完整門牌查核的 WGS84 數值座標，地圖只能依地址搜尋，無法提供座標定位及距離；發布硬條件未滿足。先前「無未完成事項」的結論不完整，應以本紀錄更正。
- LINE URL 在頁面 DOM 與按鈕中符合輸入，不代表實際入群成功。
- 未驗證 Pixel 事件送達或付費廣告成效；Meta 廣告設定未變更。
- 本紀錄所列 HTTP 與瀏覽器結果不代表曾呼叫部署 API；正式程式 commit 已 push，正式站則以逐 URL 回讀及實際瀏覽器驗證為據。

## 8. 後續追蹤

以完整門牌向權威地圖或政府門牌資料來源查核新莊中港店，確認結果確為該門牌，記錄查核日期及來源連結，再補入 WGS84 數值 `lat`、`lng`。之後驗證座標地圖 query、距離元件的 `data-lat`／`data-lng`，並於正式站回讀確認。完成前不得宣稱門市完整上架契約已閉環。

## 9. 本次結論

新莊中港店已新增並發布，首頁排第 4，專屬 UTM 網址可將門市置頂放大；本機與正式站路由、呈現及既有分流驗證通過。由於缺少 SOP 要求的權威門牌座標查核及 WGS84 `lat`／`lng`，門市完整上架尚未完成，待後續查核補值及正式驗證。
