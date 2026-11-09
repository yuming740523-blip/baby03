# 2026-11-02 — 南區新增高雄三民、雲林北港準備中與發布驗收

## 1. 基本資訊

- 專案：`C:/Users/User/Desktop/baby03-site`；正式站：https://baby03.tw/。
- 類型：使用者指定門市內容更新、發布與驗收流程紀錄；P3。
- 使用者先要求南區新增高雄三民、雲林北港並寫「準備中」，其後明確授權發布，再要求維修紀錄、commit 與存檔。
- 正式程式提交：`1f13ecf51c2e1a715732546f2e66d8047d1acd58`；GitHub Pages run：`41454300211`。
- 協調／驗收模型：`gpt-6.1-sol`，thread `01a19c72-4394-7632-874a-138f5a85fa52`；執行模型：`gpt-6-luna`，thread `01a19c75-f2ec-7512-8354-d3b28abf6338`。模型由本機 rollout／prog 回讀確認。

## 2. 問題描述

本機樣本先加入兩間門市，正式站仍只有楊梅環中、台南東區兩筆準備中。發布時須補入兩筆南區展示項目，保留既有 11 間營運門市及正式版的定位、廣告分流與追蹤功能。

部署後，帶版本查詢參數的正式網址已顯示新資料，但既有瀏覽器 context 的一般首頁仍顯示 13 格、2 筆準備中。第一次完成判定過早，已在 task log 明確撤回並重新驗收。

## 3. 根因分析

正式首頁的展示項目來自 `STORE_LAYOUT`，實際營運資料來自 `DEFAULT_DATA.sec1`；樣本的新增內容不會自動進入正式版。正式版另有最近門市跨區置頂等後續改善，直接覆蓋樣本會遺失既有功能。

驗收流程問題是將帶版本參數的回讀成功直接擴大為一般首頁也完成。新瀏覽器 context 不帶查詢參數回讀正常，而舊 context 曾持續取得舊版；證據支持瀏覽器 context 快取差異，未另行證明每一層 CDN 快取狀態。

## 4. 修改內容

- 樣本：`D:/程式設計/網頁專案/baby03-region-grid-sample.html` 加入兩間南區準備中，樣本標題同步為 11 間營運、4 間準備中。
- 正式 `index.html::STORE_LAYOUT` 加入高雄三民、雲林北港，只有名稱、區域、顏色及 `status:'準備中'`；沒有虛構 URL、地址或座標，也未寫入 `DEFAULT_DATA.sec1`。
- 正式 `index.html::render()` 新增 `region-count` 文案「11 間營運門市 · 4 間準備中」，相關註解改為四間準備中。
- 程式提交只含 `index.html`，5 行新增、2 行刪除；未修改定位函式、Pixel／Lead listener、UTM 路由、SEO、編輯器或 `go` 頁。
- 發布採用從 `origin/master` 建立的獨立 worktree：`C:/Users/User/AppData/Local/Temp/baby03-publish-20261102-2135`，分支 `codex/publish-south-20261102`，避免帶入原專案既有文件及未提交變更。

## 5. 測試方式

```text
git diff --check -- index.html
git diff -- index.html
gh api repos/yuming740523-blip/baby03/actions/runs/41454300211
gh api repos/yuming740523-blip/baby03/pages/builds/latest
```

透過 Playwright 載入正式 HTML 做發布前驗證，再於部署後以新瀏覽器 context 直接開啟 `https://baby03.tw/`，不帶版本查詢參數，分別檢查 320、390、500px 的門市數、準備中狀態及水平溢位。另檢查內湖門市點選及 LINE 目的網址、舊 `utm_campaign=sanchong_1150701` 導向士林葫東，以及 JavaScript pageerror。

## 6. 測試結果

- 靜態檢查通過：展示 15 筆，營運資料 11 筆；11 間營運店皆有來源對應，新增兩筆無 URL／座標／地址；資料標記各保留一處；差異及空白檢查通過。
- Pages run `41454300211` 為 `completed/success`，部署 commit 為 `1f13ecf51c2e1a715732546f2e66d8047d1acd58`；latest build 為 `built`。
- 最終新 context 一般首頁於三種寬度均有 15 格、4 筆 disabled 準備中；南區依序為台南東區、高雄三民、雲林北港，三筆皆顯示準備中且不可點選；水平溢位為 false。
- 內湖 LINE 目的網址及士林 UTM 預選符合既有資料；指定操作的 pageerror 為 0。
- 過早 DONE、撤回 review、舊 context 13 格回讀、最終新 context 15 格驗收都保留於正式專案 `claude_task_log.txt`，沒有把舊版回讀計為成功。

## 7. 回歸風險

- `2026-10-15_remove_store_count_heading.md` 記錄曾依需求移除數量標語；本次發布重新加入該標語。這是已發生的差異，不能說原有文案全部未變。本輪建檔不再修改網站；若需維持舊版移除決定，須另行確認是否移除此標語。
- 原專案 `master` 留有既有本地文件提交及未提交內容，與此次發布分支分開；後續接續須先檢查兩邊歷史，不可直接覆蓋或強推。
- 既有瀏覽器可能需要重新整理。未驗證所有裝置快取、所有 UTM、真實 GPS 感測器、或 Meta 後台轉換入帳；追蹤程式未改不等於已做轉換端完整驗收。
- 本次未宣稱兩間門市已營運，也沒有查證未提供的地址、座標或社群連結。

## 8. 後續追蹤

兩間新增門市維持準備中；取得正式營運資料後才能另外上架連結與地址。發布與指定瀏覽器驗證完成。數量標語與既有移除紀錄的差異保留為接續注意事項，不自動另改網站。

紀錄與專案索引 commit 位於上述發布 worktree；全域索引位於 `D:/程式設計/_GLOBAL_REPAIR_INDEX/GLOBAL_REPAIR_INDEX.md`。正式存檔以 `C:/Users/User/Desktop/baby03-site` 的 `PROGRESS.md`、`claude_task_log.txt`、`progress_history` 快照與 `INDEX.md` 為接續依據；實際文件 commit 與快照名稱由 task log 記錄。

## 9. 本次結論

兩間南區門市已隨 `1f13ecf` 正式發布，均顯示準備中且不可點選。Pages 部署與新 context 一般首頁三種寬度回讀通過。驗收曾過早完成，已撤回並補足一般首頁證據；標語重新加入及未驗範圍如實列入風險。
