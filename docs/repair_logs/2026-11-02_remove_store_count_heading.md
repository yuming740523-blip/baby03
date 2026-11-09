# 2026-11-02 — 移除首頁營運與準備中數量標語

## 1. 基本資訊

- 專案：`C:/Users/User/Desktop/baby03-site`；正式站：https://baby03.tw/；嚴重度：P3。
- 類型：使用者指定 UI 文案移除與正式站驗收。
- 使用者明確要求「11 間營運門市 · 4 間準備中 這一行不需要」，之後要求維修紀錄、commit、存檔。
- 正式程式提交：`a2fc242887246856a4023ca4e7781a46fd64f229`；Pages run：`41463022985`。

## 2. 問題描述

南區新增兩間準備中門市的前一版 `1f13ecf` 將樣本的數量標語重新放入正式首頁。使用者要求移除整行，門市清單與各門市準備中狀態仍須保留。

## 3. 根因分析

`index.html::render()` 於定位操作區與北區門市清單之間輸出 `.region-count`，固定文字為「11 間營運門市 · 4 間準備中」。這一行在先前 `2026-10-15_remove_store_count_heading.md` 已有移除紀錄，本次新增門市時重新加入，與既有移除決定不一致。刪除這個展示節點即可，無須修改資料或渲染門市的函式。

## 4. 修改內容

- 正式程式提交只修改 `index.html::render()`，刪除一行 `.region-count` 標語，沒有其他程式 diff。
- 原專案 `C:/Users/User/Desktop/baby03-site/index.html` 與本機樣本 `D:/程式設計/網頁專案/baby03-region-grid-sample.html` 同步移除該行。
- `STORE_LAYOUT`、`DEFAULT_DATA`、15 個門市展示項目及四筆準備中狀態保留；沒有修改定位、追蹤或廣告分流。
- 使用獨立發布 worktree `C:/Users/User/AppData/Local/Temp/baby03-remove-count-20261102`，分支 `codex/remove-store-count-20261102`，從當時 `origin/master` 建立，避免帶入前次尚未 push 的文件提交及原專案其他未提交內容。

## 5. 測試方式

```text
git diff --check
git diff -- index.html
gh api repos/yuming740523-blip/baby03/actions/runs/41463022985
gh api repos/yuming740523-blip/baby03/pages/builds/latest
```

發布前透過 Playwright 載入修改後正式 HTML，確認 `.region-count` 不存在，門市總數與準備中狀態保留。發布後等待 Pages 成功，再使用新瀏覽器 context 直接開啟不帶查詢參數的 `https://baby03.tw/`，回讀相同欄位及南區各門市。

## 6. 測試結果

- `git diff --check` 通過；正式程式 commit 為 1 個檔案、1 行刪除。
- 發布前 HTML 瀏覽器回讀：標語節點 0、門市 15、準備中 disabled 4；南區三筆狀態均保留。
- Pages run `41463022985` 最終 `completed/success`，head SHA 為 `a2fc242887246856a4023ca4e7781a46fd64f229`；latest build 為 `built`。
- 部署尚在 building／queued 時，一般首頁曾回讀到標語節點 1，此次沒有將該結果視為完成。
- 部署成功後，新 context 一般首頁回讀標語節點 0、門市 15、準備中 disabled 4；南區台南東區、高雄三民、雲林北港均顯示準備中且 disabled。

## 7. 回歸風險

- 本次只驗證數量標語移除與門市展示保留，沒有重跑全部 UTM、定位、追蹤入帳或各裝置流程；程式未改的功能不得視為全部重驗。
- 舊分頁可能保留快取；最終證據使用新 context 的一般首頁，沒有依賴版本查詢參數。
- 正式原專案保留既有本地提交與未提交變更；前次文件提交 `76595cb` 位於另一分支，尚未 push，不應為了本次建檔而覆蓋、強推或混入提交。

## 8. 後續追蹤

前次紀錄 `2026-11-02_south_preparing_stores_publish.md` 所列「重新加入標語」差異，已由本次移除解決；原紀錄保留作歷史證據，不改寫成當時沒有發生。

接續以原專案 `PROGRESS.md`、`claude_task_log.txt` 與最新 `progress_history` 快照為準。本次文件 commit 只包含本紀錄與發布分支的專案索引，留在本機，不另外 push。全域索引獨立更新，不在此專案 Git 提交範圍內。沒有新增網站待辦。

## 9. 本次結論

`a2fc242` 已正式部署；首頁不再顯示營運／準備中數量標語，15 個門市項目及四筆準備中保留。Pages 部署成功與新 context 一般首頁回讀均有證據。本輪僅補紀錄、索引、commit 與存檔，不再改網站。
