# 移除首頁「11 間營運門市 · 2 間準備中」標語

## 1. 基本資訊

- 日期：2026-10-15；專案：`C:\Users\User\Desktop\baby03-site`。
- 程式改動與部署日期：2026-10-14 晚間。
- 類型：首頁文案／區塊移除；嚴重度 P3。
- 正式程式提交：`a629b472f7fff70e5226d0847a30d3973faeba9f`。
- GitHub Pages workflow：`38592640300`，`completed/success`，`headSha` 與程式提交相同。

## 2. 問題描述

首頁原有標語顯示營運門市數量與準備中門市數量。本次依需求移除該標語，並確認門市卡片及準備中狀態仍留在首頁。

## 3. 根因分析

`index.html::render()` 原本輸出 `region-count` 標題，內容使用 `${D.sec1.length}` 顯示營運門市數量，並固定顯示「2 間準備中」。本次需求是移除這個首頁展示標題；未涉及門市資料或資料筆數修正。

## 4. 修改內容

- 正式程式 commit `a629b472f7fff70e5226d0847a30d3973faeba9f` 唯一 diff 是從 `render()` 刪除：

  ```html
  <h1 class="region-count">🌼 ${D.sec1.length} 間營運門市 · 2 間準備中 🌼</h1>
  ```

- 此 commit 未修改門市資料或其他程式區塊。

## 5. 測試方式

- GitHub Pages workflow 回讀狀態與 `headSha`。
- 正式首頁 HTTP 回讀，並與本機首頁 HTML 比對 bytes。
- 使用線上 Playwright Chromium 於 320px、390px 檢查首頁的 `.region-count`、門市卡、準備中按鈕，實際點擊榮華 LINE 入口，並檢查 `pageerror` 與水平溢出。

## 6. 測試結果

- Workflow `38592640300` 為 `completed/success`，其 `headSha` 等於正式程式 commit `a629b472f7fff70e5226d0847a30d3973faeba9f`。
- 正式首頁 HTTP 200；首頁 HTML 與本機來源 byte-equal。
- 320px 與 390px：`.region-count` 為 0、門市卡共 13 張、準備中按鈕 disabled 共 2 張。榮華 LINE 點擊仍指向正確目的地；`pageerror` 0，水平溢出 0。

## 7. 回歸風險

- 本次正式站瀏覽器檢查限於 320px、390px 及第 6 節所列項目；沒有宣稱其他 UTM 路由、社群入口、Pixel 或門市操作已重新完整驗收。
- 標語移除不會更動 `D.sec1` 或準備中門市資料；本次以門市卡數量及兩張 disabled 卡確認首頁仍呈現 13 張卡、其中 2 張準備中。

## 8. 後續追蹤

本次標語移除與所列正式站檢查已完成，沒有新增程式待辦。未列入本次的功能不視為重新驗收。

## 9. 本次結論

首頁營運／準備中門市數量標語已於 2026-10-14 晚間移除並成功部署。正式首頁 HTTP 與來源比對通過；320px、390px 線上 Chromium 確認標語不存在、13 張門市卡及 2 張 disabled 準備中卡仍在，榮華 LINE 入口正確，且無頁面錯誤或水平溢出。
