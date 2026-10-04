# 大甲育英店地址補註「大甲國中對面」

## 1. 基本資訊

- 日期：2026-10-04；專案：`C:\Users\User\Desktop\baby03-site`。
- 類型：業主指定內容更新；嚴重度 P3。
- 業主要求：baby03 首頁與大甲店專屬網址的地址增加 `(大甲國中對面)`，並建立維修紀錄、commit、存檔。
- 正式修改 commit：`fefdb2037864c7960717e192ab5dc9799e7592d2`；已推送 `origin/master`。
- GitHub Pages 部署 run：`37202861171`，`completed / success`，部署 SHA 與上述 commit 一致。

## 2. 問題描述

原地址為 `台中市大甲區育英路125號`，缺少業主指定的地標提示。首頁與大甲專頁都需顯示補註；此為內容補充，不宣稱原門牌或座標錯誤。

## 3. 根因分析

首頁與大甲 UTM 專頁共用 `index.html` 的 `DEFAULT_DATA.sec1` 大甲育英店資料。大甲專頁透過 `STORE_ROUTES`、`routedStoreIndex()` 置頂門市，地址仍由 `buildBtns()` 讀取同一 `addr` 欄位，因此只需修改一筆資料。

## 4. 修改內容

- 正式檔案：`index.html:288`，`DEFAULT_DATA.sec1` 大甲育英店 `addr`。
- 修改後：`台中市大甲區育英路125號(大甲國中對面)`。
- `git show fefdb20 -- index.html` 確認只有地址一行變更。
- LINE 連結、座標 `24.3528862,120.6227319`、UTM 分流、其他門市及 Meta 廣告設定均未修改。
- 使用 `apply_patch` 完成修改。首次 PowerShell 中文管線替換因編碼不符而 assert 失敗，未改檔；誤記的 PASS 已在 task log 以 FAIL 更正，後續依實際 diff 驗收。

## 5. 測試方式

執行以下正式版本與部署檢查：

```powershell
git diff --check -- index.html
git show --stat --oneline fefdb20
gh api repos/yuming740523-blip/baby03/actions/runs/37202861171 --jq '{status,conclusion,head_sha}'
```

另以 Python `requests.get()` 實際請求下表三個 HTTPS URL；逐 URL 檢查 HTTP 200、解析正式 `DEFAULT_DATA` 後唯一大甲項目的新地址／座標／LINE，以及完整來源（正規化換行後）與 `git show fefdb20:index.html` 一致。初次部署未完成時為 0/3，不列成功；部署成功後 20:41 與存檔前 20:44 都重驗通過。

## 6. 測試結果

| 正式網址 | HTTP | 新地址與正式來源 | 結果 |
|---|---:|---|---|
| `https://baby03.tw/` | 200 | 一致 | PASS |
| `https://baby03.tw/?utm_campaign=dajia_yuying&utm_content=dajia_page` | 200 | 一致 | PASS |
| `https://baby03.tw/?utm_source=fb&utm_medium=cpc&utm_campaign=dajia_1151016_opening&utm_content=dajia_opening_tea_v1` | 200 | 一致 | PASS |

正式 URL 驗證 3/3，assert 驗證 exit 0；`git diff --check` exit 0；GitHub Pages `success`。

## 7. 回歸風險

- 地圖仍使用既有數值座標，不用新增地標文字重新搜尋。
- 本輪瀏覽器工具無可用 surface，完成的是 HTTP 來源回讀，未驗證瀏覽器畫面、手機換行、Pixel 事件實際送達或 LINE 入群。
- 舊瀏覽器分頁若持有快取，需重新整理取得新版；正式 HTTP 回讀已取得新版。
- 既有未提交紀錄、備份與其他髒檔保留，不納入本次 commit。

## 8. 後續追蹤

本次地址補註沒有未完成修改。下次編輯門市資料時保留新地址；若要確認手機顯示，另以實際瀏覽器驗證。本輪只依業主提供的地標補註，未重新查核地標地理關係。

## 9. 本次結論

baby03 首頁、大甲專頁與現行廣告落地網址已取得含 `(大甲國中對面)` 的正式來源。內容修改已部署；本維修紀錄、專案索引與全域索引依業主要求建立，文件 commit 後再執行 `prog save` 並回讀四項存檔產物。
