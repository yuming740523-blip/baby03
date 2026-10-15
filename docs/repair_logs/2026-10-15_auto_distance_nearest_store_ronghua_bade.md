# 2026-10-15 — 載入顯示門市距離、最近門市跳轉與榮華地址對齊八德

## 1. 基本資訊

- 日期：2026-10-15；專案：C:/Users/User/Desktop/baby03-site。
- 類型：門市距離／最近門市操作功能與門市地址資料修正；嚴重度 P2。
- 正式程式提交：bcfad71c3afeab60a226be564e8ebb3b052e4d93（index.html）。
- GitHub Pages workflow：38598224802，completed/success，headSha 與上述 commit 相同。
- 正式站：https://baby03.tw/。

## 2. 問題描述

進站時沒有直接取得定位，因此首頁門市卡及預選門市詳情不會立即顯示距離。舊版定位按鈕只取得位置並更新距離，沒有在按下時切換至最近門市資訊。榮華門市資料仍使用「桃園區榮華街63巷23號」及舊座標，與八德金和門市的位置資料不同。

本次需求保留北、中、南分區與門市卡原順序；按下最近門市按鈕時才開啟最近門市詳情。榮華門市地址、座標需與八德金和一致，LINE／Facebook 既有路由維持原設定。

## 3. 根因分析

- 舊版 initGeo() 只在定位按鈕的 click handler 內呼叫 getCurrentPosition()，沒有在頁面初始化時請求位置；詳情距離欄位只有等待使用者按按鈕的提示文字。
- 舊版定位成功後只呼叫 renderDistances()，沒有依定位結果找出最近門市、更新詳情卡及捲動到詳情卡。
- DEFAULT_DATA.sec1 的榮華門市 addr、lat、lng 留有舊值。commit 前資料為「桃園區榮華街63巷23號」、24.974607、121.3209675；本次改為與八德金和相同的地址與座標。

## 4. 修改內容

正式程式 commit bcfad71c3afeab60a226be564e8ebb3b052e4d93 只修改 index.html：

- 頁面初始化後呼叫定位流程；成功時更新各店卡片與目前詳情卡的直線距離，並保留「非車程」標示。
- 定位按鈕改為「查看離我最近的門市」。按下後依門市座標計算 Haversine 直線距離，切換最近門市詳情並捲動至資訊卡；門市卡陣列、分區及原排序未改。
- 榮華門市 addr、lat、lng 改為與八德金和相同值。LINE URL 及 UTM／Facebook 路由未在此 commit 中修改。

## 5. 測試方式

- 讀取 bcfad71 commit 與其 parent diff，核對程式修改範圍及榮華舊資料。
- 執行 gh run view 38598224802 --repo yuming740523-blip/baby03 --json databaseId,status,conclusion,headSha,workflowName,event,createdAt,updatedAt,url 回讀 Pages workflow。
- 對正式站 https://baby03.tw/ 發出 HTTP 請求，檢查目前 HTML 的功能標記；比較本機 index.html 與正式站 HTML，並另外排除 Cloudflare 注入的 beacon script 後比對。
- 使用線上 Playwright Chromium，以瀏覽器授權及設定的測試座標，在 320px 與 390px 檢查載入距離、最近門市按鈕、卡片順序、榮華 UTM 路由與水平溢出。未使用 Chrome remote debugging port 9222。

## 6. 測試結果

- GitHub Pages workflow 38598224802 為 completed/success，headSha 等於正式程式 commit bcfad71c3afeab60a226be564e8ebb3b052e4d93。
- 正式站 HTTP 回應為 200。回讀 HTML 含「查看離我最近的門市」、自動定位呼叫及八德金和地址與座標。Cloudflare 在回應尾端注入一段 beacon script；移除此注入區塊後，正式站 HTML 與本機 index.html 字元及 UTF-8 bytes 相同（61,097 bytes）。
- 設定 viewport 390px 的首頁測試：定位成功後 11 間有座標門市顯示距離；以八德金和附近座標按按鈕，詳情切換為「八德金和店」、地址為「八德區大和里金和路51號」，距離顯示「直線約 100m 內（非車程）」。門市卡順序不變，documentElement 的 clientWidth 與 scrollWidth 相等，無水平溢出。
- 設定 viewport 320px 的 utm_campaign=ronghua 測試：路由詳情為桃園榮華店，LINE 入口仍使用既有八德共用 URL；定位後 11 間有座標門市顯示距離，詳情距離顯示為直線距離。最近門市按鈕依測試座標切換至內湖店，門市卡及北／中／南區原順序不變；documentElement 的 clientWidth 與 scrollWidth 相等，無水平溢出。

## 7. 回歸風險

- 既有正式 Chromium 320／390px 驗收已確認拒絕定位後仍可手動選店；本次文件編寫未重跑拒絕授權分支。實體裝置 GPS 精度，以及使用者長時間停留在定位權限對話框後才回應的情境，尚未驗證。
- 榮華 UTM 路由的 LINE 目標、士林／榮華 Facebook 群組目的地 href 及門市排序已有正式站核對紀錄；本次未重新執行 Facebook 路由檢查，也未實際加入外部社團。
- 正式站回讀的 HTML 含 Cloudflare beacon 注入；比對時明確移除該注入 script，未將未處理的原始回應宣稱為 byte-equal。

## 8. 後續追蹤

本次正式程式部署、首頁 320／390px 定位流程檢查及榮華 UTM 路由檢查已完成。既有正式 Chromium 驗收已確認拒絕定位後仍可手動選店；此工作包未重跑該分支。實體裝置 GPS 精度與長時間等待權限對話框的情境仍未驗證；外部 Facebook 社團未實際加入。

## 9. 本次結論

bcfad71 已部署至正式站。允許定位後，首頁載入即顯示門市直線距離；按最近門市按鈕會開啟最近門市詳情，北／中／南分區及門市卡順序保持不變。榮華地址與座標已改為和八德金和相同值，LINE 路由回讀維持原目標。Pages workflow、正式站回讀及 320／390px 瀏覽器檢查完成；既有正式 Chromium 驗收已確認拒絕定位後仍可手動選店，本次文件編寫未重跑該分支。實體 GPS 精度、長時間等待權限對話框及實際加入 Facebook 社團未驗。
