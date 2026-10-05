# 新莊中港店新增、首頁排序與專屬落地頁

## 1. 基本資訊

- 日期：2026-10-05；專案：`C:\Users\User\Desktop\baby03-site`。
- 類型：新增門市、落地頁與座標完整性修復；嚴重度 P2（門市上架資料完整性）。
- 業主要求新增新莊中港店，並將其排在首頁第 4 位及建立專屬落地頁。
- 正式程式修改分三筆已推送 commit：`9a0ebc5` 新增門市資料；`f061e1f` 調整排序並新增路由；`f3eaf0c` 補入已查核座標。
- 專屬落地頁是共用 `index.html` 的 UTM 網址 `https://baby03.tw/?utm_campaign=xinzhuang_zhonggang&utm_content=xinzhuang_page`，不是獨立 HTML 檔。
- LINE 社群：`https://line.me/ti/g2/yCDJ5lTIskMFOjrSFEb1BixRrMLS6Br8js4fPA?utm_source=invitation&utm_medium=link_copy&utm_campaign=default`。
- 地址依業主提供原文記錄：`新北市新莊區恆安里中港路50號(鄰新莊國小)`。

## 2. 問題描述

網站原有 10 間門市，沒有新莊中港店。新增資料後，需求再擴充為首頁第 4 位及由新莊專屬 UTM 進站時置頂、放大的落地頁。首次發布後回查發現新店缺 WGS84 數值 `lat`、`lng`，因此地圖使用地址字串且沒有距離元件資料；歸檔時又只列後續待辦，未完成座標查核與修復。使用者再次指出後，立即按 SOP 查核、補值、發布及正式站回讀。

## 3. 根因分析

`DEFAULT_DATA.sec1` 是首頁與 UTM 落地頁共用的門市資料來源；既有 `STORE_ROUTES`、`routedStoreIndex()` 與 `buildBtns()` 可依路由將指定店置頂及放大，因此新增一筆門市資料、移至第 4 位並加一條路由即可完成前述展示需求。

本次初次新增流程漏讀並未遵循 `docs/STORE_ONBOARDING_SOP.md`，未先以完整門牌查核權威點位；歸檔時又錯把完成新增／排序／落地頁當作完整上架，並將座標只留待辦。這是已發生的流程缺失及不完整完工回報。業主提供的地址文字不能代替獨立門牌查核，大甲與內湖座標也不能替代新莊查核。2026-10-05 使用者追問後已按官方門牌資料補查並修正，詳見第 4、6 節。

## 4. 修改內容

- `9a0ebc5`：在 `DEFAULT_DATA.sec1` 新增新莊中港店名稱、完整 LINE URL 與業主提供地址，共 6 行。
- `f061e1f`：將新莊中港店移至第 4 位，新增 `/xinzhuang|新莊|中港/i` 路由識別 `新莊中港`，沿用既有置頂與放大行為。
- `f3eaf0c`：完成 2026-10-05 座標補修，只新增該店 `lat: 25.0384301`、`lng: 121.4554353`；地址與 LINE 連結、排序、路由及其他 10 店資料均保留。
- 座標查核來源：新北市民政局[新北市門牌位置數值資料](https://data.ntpc.gov.tw/datasets/d7b568ab-3819-40c8-a6e7-a6b199443101)，資料描述 `11509`、月更新、總筆數 1,989,458；全檔下載 URL：`https://data.ntpc.gov.tw/api/datasets/d7b568ab-3819-40c8-a6e7-a6b199443101/csv/zip`。於 2026-10-05 取得 HTTP 200 的 ZIP 後，依縣市／行政區代碼、里、路及門牌掃描全檔，完整門牌唯一命中 1/1：`countycode=65000`、`areacode=65000050`、`恆安里`、`neighbor=009`、`中港路`、無巷弄、原始門牌 `５０號`、`X_3826=295957.643000`、`Y_3826=2770111.4681000`。內政部行政區代碼資料確認 `65000050` 為新北市新莊區。EPSG:3826 以 `pyproj 3.8.0`、`Transformer.from_crs(..., always_xy=True)` 轉 EPSG:4326 得 `lat=25.038430105191015`、`lng=121.45543532750331`，寫入 7 位小數；Root 獨立重讀原始列並重做正反向座標轉換，座標吻合且反轉誤差小於 1 mm。初次查詢曾以錯誤行政區碼篩選而得到 0 筆，隨即更正為新莊區碼；該次 0 筆是查詢條件錯誤，不代表官方資料缺門牌。
- 其餘門市欄位及既有分流未修改；本輪沒有變更 Meta 廣告。
- 本維修紀錄及專案／全域索引依業主要求歸檔；既有未提交檔案不納入本次文件 commit，全域索引位於專案 Git 外。

## 5. 測試方式

- 本機正式 `index.html`：以 PowerShell UTF-8 here-string 管線執行 `python -X utf8 -`，在真實 inline JavaScript 上執行 `node --check`，並以 Playwright Chromium 驗證手機寬 390、桌面寬 1280 的首頁及路由頁。同步逐項核對 13 條路徑（首頁 1 + campaign 12，其中包含新莊路由）與 3 種新莊 `utm_content`（英文 `xinzhuang_page`、中文「新莊」、中文「中港」）。
- 座標補修後本機：同樣以 PowerShell UTF-8 here-string 執行 `python -X utf8 -`，對正式 inline JavaScript 跑 `node --check`，再用 Chromium 開啟正式 `index.html` file URI；手機寬 390、桌面寬 1280 分別測首頁及新莊 UTM 專頁，並核對門市順序、地圖／距離資料與正式距離 renderer。
- 正式站：逐 URL HTTP 回讀首頁、新莊專頁、大甲、內湖及三重舊 UTM 例外（特殊士林）共 5 個 URL；比較正式資料及來源與 `f061e1f`，僅排除 Cloudflare 自動注入的 beacon。線上 Playwright 驗證手機及桌面首頁／新莊專頁共 4 個版面，並回歸大甲、內湖與特殊士林（三重舊 UTM 例外）3 種既有分流。
- 歸檔前由主協調者另行以 PowerShell UTF-8 here-string 管線執行 `python -X utf8 -`，使用 `urllib.request` 逐一回讀首頁與新莊專頁，檢查 HTTP、完整來源及新店資料。
- 座標補修正式驗證：Root 於 `2026-10-05 14:59` 以正式 HTTPS 首頁與新莊 UTM 專頁做逐 URL HTTP、完整來源及線上 Chromium 回讀；確認正式來源等於 `f3eaf0c:index.html`（僅排除 Cloudflare beacon），且 11 店資料齊全。

## 6. 測試結果

- 本機 `node --check` 與初次 Playwright 成功；13 條路徑通過，新莊三種 `utm_content` 均命中預期門市。首頁第 4 位；專頁第 1 張 featured 主力推薦；LINE、地址與地圖按鈕符合輸入；11 店筆數與當時指定欄位核對通過；無橫向溢出或 `pageerror`。這是補座標前的歷史結果。
- 座標補修後本機驗證 `node --check` exit 0；file URI Playwright 首頁／新莊 UTM 專頁的手機 390、桌面 1280 共 `4/4 PASS`。新莊地圖 query、距離 `data-lat`／`data-lng` 正確；正式 `renderDistances()` 依已查核座標顯示「直線約 100m 內」；無橫向溢出或 `pageerror`。本項不是裝置 GPS 測試。
- 歸檔前正式站追加回讀的歷史結果：首頁與新莊專頁 HTTP `2/2` 為 200，11 店資料及來源符合當時的 `f061e1f`（僅排除 Cloudflare beacon），新莊位於資料第 4 位，但 `lat`、`lng` 均缺失；此結果未完成座標契約。
- 14:24 正式站歷史驗證：以下 5 URL 均 HTTP 200，來源符合 `f061e1f`（排除 Cloudflare beacon），`5/5 PASS`：

  | URL | HTTP／source 結果 |
  |---|---|
  | `https://baby03.tw/` | 200／PASS |
  | `https://baby03.tw/?utm_campaign=xinzhuang_zhonggang&utm_content=xinzhuang_page` | 200／PASS |
  | `https://baby03.tw/?utm_campaign=dajia_yuying&utm_content=dajia_page` | 200／PASS |
  | `https://baby03.tw/?utm_campaign=neihu_0822` | 200／PASS |
  | `https://baby03.tw/?utm_campaign=sanchong_1150701` | 200／PASS |

  同次線上 Playwright 首頁與新莊專頁手機／桌面 `4/4`；大甲、內湖、特殊士林（三重舊 UTM 例外）分流回歸 `3/3`；無 JS 錯誤。此歷史 5/5 與歸檔前追加回讀 2/2 分開計列。
- `f3eaf0c` 座標補修正式站驗收：HTTP 首頁及新莊專頁 `2/2` 均 200，完整來源均與 `f3eaf0c:index.html` 相符（只排除 Cloudflare beacon）。線上 Playwright 手機 390、桌面 1280 的首頁／新莊專頁共 `4/4`；11 店、新莊首頁第 4、專頁第 1 featured、LINE 與地址原文均正確，地圖 query 為 `25.0384301,121.4554353`，距離元件 `data-lat`／`data-lng` 正確；無 `pageerror` 或橫向溢出。正式 `renderDistances(25.0384301,121.4554353)` 回傳 11，新莊顯示「直線約 100m 內」；以內湖座標 `renderDistances(25.0813093,121.5746678)` 回傳 11，新莊顯示「直線約 13km」，Root 獨立 Haversine 為 `12.921830545469051km`。這是以已查核門市座標呼叫正式距離 renderer 的驗證，不是裝置定位測試。
- 驗證過程更正紀錄：13:58 一次驗證在全文 assert 提前中止，當時錯誤的 PASS 已於同分鐘更正為 FAIL；13:59 以 UTF-8 修正後真實執行 exit 0。14:00 正式站仍是舊版 10 店，不算發布完成；14:01 回讀雖有 11 店，來源差異仍待查；14:02 確認唯一差異是 Cloudflare beacon，排除該注入後才判定來源吻合。14:23曾把 12 條 campaign 全稱作既有分流，當分鐘已更正分母為首頁 1 + campaign 12（含新莊）= 13 條路徑。
- 未使用獨立測試腳本；命令輸出留在當次執行紀錄，不宣稱存在永久測試檔。

## 7. 回歸風險

- 新莊原先缺少經完整門牌查核的 WGS84 座標、違反新增門市 SOP，且曾被不完整回報為已完成；此歷史缺失已於 `f3eaf0c` 補正並經正式站回讀，座標地圖及距離元件均完成驗證。目前此項上架契約已閉環。
- LINE URL 在頁面 DOM 與按鈕中符合輸入，不代表實際入群成功。
- 未驗證裝置 GPS 是否能取得定位、Pixel 事件是否送達、實際 LINE 入群或付費廣告成效；Meta 廣告設定未變更。上述項目不是門市座標缺口。
- 本紀錄所列 HTTP 與瀏覽器結果不代表曾呼叫部署 API；正式程式 commit 已 push，正式站則以逐 URL 回讀及實際瀏覽器驗證為據。

## 8. 後續追蹤

新莊座標查核、WGS84 補值、座標地圖 query、距離元件及正式站回讀已完成，沒有待辦座標補修。真實裝置 GPS、Pixel 送達、實際入群及廣告成效未在本案驗證，不影響門市座標契約結案。

## 9. 本次結論

新莊中港店新增、首頁第 4 位排序、專屬 UTM 落地頁及權威門牌座標均已發布並通過本機與正式站回讀。初次漏遵 SOP、歸檔時只列待辦及不完整完工回報均保留為歷史事實；使用者再次指出後，已由 `f3eaf0c` 補齊座標並完成驗收，門市完整上架契約現已閉環。
