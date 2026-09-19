# 2026-09-19 — 大甲育英與內湖門市查核座標、落地頁分流與新增門市 SOP

## A. 基本資訊

| 項目 | 內容 |
|---|---|
| 日期 | 2026-09-19 |
| 專案 | baby03.tw 落地頁（GitHub Pages + Cloudflare） |
| 影響範圍 | Production／首頁與大甲、內湖 UTM 專屬落地頁的門市卡片、地圖與距離功能 |
| 嚴重度 | P2（門市資料完整性與轉換入口正確性；未造成服務中斷） |
| 結案類型 | Bug Fix / Store onboarding data integrity / Production verification |
| 正式程式 | index.html 的 DEFAULT_DATA.sec1、routedStoreKey()、buildBtns()、renderDistances() |
| 正式 commits | 71db1bb、47ad049、e2d52d8、a884e42 |
| 部署 | GitHub master → GitHub Pages + Cloudflare；最終正式 SHA 為 a884e4260834fe1759ca6e3f8d898592701a8325 |

## B. 問題描述

業主新增「大甲育英店」後，要求其專屬落地頁以大甲店置頂，並提供完整門牌與 LINE 社群連結。其後業主指出：新增門市不能只留可點地圖的地址，必須一併查核座標，否則使用者按「離我多遠」時該店不會參與距離計算。

查核發現：

1. 大甲育英店初次上架後需要補入門牌查核座標，並確認 ?utm_campaign=dajia_yuying&utm_content=dajia_page 可把大甲店置頂。
2. 既有內湖店已有完整地址，但 DEFAULT_DATA.sec1 缺少 lat、lng；地圖只能退回地址字串搜尋，距離元件不會建立 data-lat、data-lng。
3. 原有流程沒有把「新店必須有已查核座標」寫成發布硬條件，容易再次出現只有地址、沒有距離功能的半完成門市。

## C. 根因分析

1. buildBtns() 只在門市資料的 lat、lng 都是數值時，才以座標產生 Google Maps query，並把兩個值寫入距離元件的 data-lat、data-lng。
2. renderDistances() 只巡覽具有這兩個 data attribute 的元素；因此內湖缺座標時不會顯示直線距離。
3. 新店上架資料檢核未有明文化發布契約，導致「地址可開地圖」被誤認為功能完整。

## D. 查核座標與資料修復

| 門市 | 完整門牌 | WGS84 緯度 | WGS84 經度 | 查核來源 |
|---|---|---:|---:|---|
| 大甲育英店 | 台中市大甲區育英路125號 | 24.3528862 | 120.6227319 | [臺中市 GIS 門牌資料](https://data.gov.tw/dataset/177460) |
| 內湖店 | 台北市內湖區內湖路一段629巷36弄2號 | 25.0813093 | 121.5746678 | [臺北市門牌位置數值資料](https://data.taipei/dataset/detail?id=b7c8e724-1e98-45ee-a0bd-f3840623ed97) |

內湖門牌在臺北市資料中唯一命中麗山里、內湖路一段629巷36弄2號的 TWD97 點位；依相同座標系統轉為上述 WGS84 數值。大甲資料採臺中市政府提供、含 WGS84 經緯度欄位的門牌資料。

## E. 修改內容

### E-1 大甲育英店與專屬落地頁

- 71db1bb：新增大甲育英店 LINE 社群、地址與門市資料。
- 47ad049：在 routedStoreKey() 新增 dajia、大甲、育英路由，讓 ?utm_campaign=dajia_yuying&utm_content=dajia_page 命中大甲店；既有 UTM 通用排序邏輯使命中店在該落地頁第一順位且為 featured。
- e2d52d8：補入大甲育英店的 lat 24.3528862、lng 120.6227319。

### E-2 內湖既有門市座標回補

- a884e42：只在內湖店既有 addr 後新增 lat 25.0813093、lng 121.5746678。
- 未改動內湖 LINE 社群連結、地址、UTM 路由、Facebook 社團、Pixel 事件或其他門市資料。

### E-3 新門市上架 SOP

- e2d52d8 新增 docs/STORE_ONBOARDING_SOP.md。
- SOP 明定每一間新增至 DEFAULT_DATA.sec1 的門市，在發布前必須同時具有名稱／LINE、完整門牌、權威來源查核的 WGS84 數值 lat、lng。
- SOP 亦規定發布前與發布後都要確認地圖 query 使用座標，且距離元件帶有 data-lat、data-lng。

## F. 驗證方式與結果

1. 讀取正式資料並以 Node 解析內湖項目：lat=25.0813093、lng=121.5746678，且內湖 UTM 路由下為第一張 featured 卡片，PASS。
2. git diff --check：PASS；座標 commit 僅修改 index.html 的兩個欄位。
3. 本機以 python -m http.server 8125 --bind 127.0.0.1 提供實際頁面，Chrome 143 CDP 9222 開啟內湖專屬 URL：
   - 第一張卡片的 data-lat／data-lng 為 25.0813093／121.5746678；
   - 地圖連結 query 為 25.0813093,121.5746678；
   - 呼叫正式 renderDistances(25.0813093, 121.5746678) 後，內湖卡片顯示「直線約 100m 內」；
   - 全部 PASS，測試伺服器與登記 port 已釋放。
4. 推送 a884e42 後，以帶快取識別的正式內湖 URL 重新開啟 https://baby03.tw/，重做座標、地圖 query 與距離顯示檢查，全部 PASS。
5. git ls-remote origin refs/heads/master 回讀 SHA 與本機 HEAD 均為 a884e4260834fe1759ca6e3f8d898592701a8325。

## G. 可複用定論

「可開地圖」不等於「距離功能完整」。門市地址僅能作為無座標時的地圖搜尋退路；要讓地圖精確定位、距離元件參與計算，以及對新增資料保持一致，必須把完整門牌查核後的 WGS84 lat、lng 一併寫入 DEFAULT_DATA.sec1。

自 2026-09-19 起，新增門市一律依 docs/STORE_ONBOARDING_SOP.md 執行；既有門市若被發現缺座標，必須另行查核、取得授權後補登，不得把地址或地圖按鈕當作完成證據。

## H. 風險與範圍界線

1. 本次以 SOP 固化發布流程；deploy-server.py 的既有新店容錯邏輯未改，技術上仍可能放行沒有座標的新資料。因此發布者必須遵守 SOP 的發布前／後實測，若日後要改為技術 fail-closed，需另行授權修改部署閘門。
2. 門牌資料與座標若因地址異動而改變，必須重新依權威資料查核，不可沿用舊座標猜測。
3. 本次未修改其他既有未提交檔案，也未回收或重寫歷史備份檔。

## I. 結論

大甲育英店已具備專屬 UTM 落地頁、已查核座標與距離功能；內湖既有門市的座標缺口已補齊並由正式站回讀確認。新門市 SOP 已生效，將「門牌已查核的數值座標」列為發布硬條件。本案四筆正式程式／文件 commit 均已推送，內湖最終部署版本已由遠端 SHA 與實際 DOM 交叉驗證。
