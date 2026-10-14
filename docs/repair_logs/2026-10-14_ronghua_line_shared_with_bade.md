# 榮華門市 LINE 社群改為與八德共用

## 1. 基本資訊

- 日期：2026-10-14；專案：`C:\Users\User\Desktop\baby03-site`。
- 類型：門市 LINE 目的地內容更新；嚴重度 P3。
- 影響範圍：正式站 `index.html` 中榮華門市的 LINE 社群 URL。
- 正式程式提交：`ae3913ecfc05b534d82242f341e68ac6599116e2`，基線 `97134c6`；GitHub Pages workflow `38589918223` 狀態為 success。
- 共用目的地：`https://line.me/ti/g2/Op9gU_Jp1O0452mwLTlcklV03TegLNy9Q9df2w`。

## 2. 問題描述

本次需求是讓榮華門市 LINE 入口改用與八德共用的 LINE 社群目的地。需確認首頁榮華門市入口及 `utm_campaign=ronghua` 路由頁的主入口與詳情入口都採用該目的地，且八德原有連結不變。

## 3. 根因分析

榮華門市資料原先在 `DEFAULT_DATA.sec1` 使用獨立 LINE URL，與本次指定的八德共用目的地不同。這是門市資料欄位的目的地設定差異；UTM 分流及按鈕渲染不需修改。

## 4. 修改內容

- commit `ae3913ecfc05b534d82242f341e68ac6599116e2` 只將榮華門市 LINE URL 從 `https://line.me/ti/g2/bwTXKC1zb84zCy86O_v9EE1FxePEL7CzdwSPUQ` 更新為 `https://line.me/ti/g2/Op9gU_Jp1O0452mwLTlcklV03TegLNy9Q9df2w`。
- 八德原有 URL 保持原值；其他門市資料、UTM routes 及展示程式未包含在該提交變更中。
- GitHub Pages workflow `38589918223` 完成，狀態為 success。

## 5. 測試方式

- 正式站根網址 HTTP 回讀，並將首頁 HTML 與本機正式來源逐 byte 比較。
- 使用 Playwright Chromium 開啟正式站首頁及 `https://baby03.tw/?utm_campaign=ronghua`，實際檢查首頁榮華門市入口、路由頁主入口與詳情入口的 LINE 目的地。
- 瀏覽器未使用 Chrome remote debugging port 9222。

## 6. 測試結果

- `https://baby03.tw/` 回傳 HTTP 200；首頁 HTML 與本機正式來源 byte-equal。
- Playwright Chromium 首頁點選榮華門市後，以及 `utm_campaign=ronghua` 路由頁的主入口與詳情入口，均指向八德共用 URL：`https://line.me/ti/g2/Op9gU_Jp1O0452mwLTlcklV03TegLNy9Q9df2w`。
- 八德資料的原 URL 未變；瀏覽器測試未記錄 `pageerror`。

## 7. 回歸風險

- 本次確認的是正式頁面中 URL 的設定與連結行為；未實際加入 LINE 社群，也未獨立驗證該目的地社群的身份、管理者或成員人數。
- 正式站回讀證明部署內容與本機來源一致，不代表 LINE 端目的地持續可用或符合社群營運需求。

## 8. 後續追蹤

本次程式與正式站回讀已完成。若日後需確認社群身份或入群流程，須另以 LINE 端實際頁面查驗；本紀錄不將該項未驗證事項視為通過。

## 9. 本次結論

榮華門市 LINE URL 已在正式站改為與八德共用的目的地，GitHub Pages workflow 成功，正式首頁與榮華 UTM 路由的瀏覽器檢查均確認目標 URL 正確。八德既有 URL 保持不變；LINE 社群身份、成員人數及實際入群未驗證。
