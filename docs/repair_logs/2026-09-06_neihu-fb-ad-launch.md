# 2026-09-06 — 內湖 landing 上線與 FB 廣告開投驗證

## A. 基本資訊

| 項目 | 內容 |
|---|---|
| 日期 | 2026-09-05 到 2026-09-06 |
| 專案 | baby03.tw 落地頁 + Meta Ads |
| 影響範圍 | Production：內湖 UTM landing route、Meta 廣告帳號 `act_460927117258880` |
| 嚴重度 | P2（新店開幕投放，需正式驗證與追蹤補記） |
| 結案類型 | Feature / Platform Launch + Process Follow-up |
| 相關網站 commit | GitHub web commit `a5cba35`；本地 landing commit `0282262` |
| Meta 廣告物件 | campaign `52574105685336`、adset `52574105688936`、ad `52574106207736`、creative `2547548165672024` |
| 授權 | 使用者明確指示「開始動並開投」；完成後追加「寫維修紀錄 commit 再存檔」 |

## B. 任務描述

內湖店開幕需要從網站到 Meta 廣告完成同一條投放鏈：

1. `baby03.tw` 依內湖 UTM 命中內湖店內容。
2. 內湖 FB 廣告導向正式 landing URL。
3. 廣告使用指定開幕圖與內湖文案。
4. Meta 的 AI/Advantage+ creative automation 不得留下自動強化或多媒體變體。
5. 開投後用 Graph/API 或 Ads Manager readback 驗證，不用未讀回的 UI 印象結案。

## C. 處理紀錄

### C-1 Landing

- 套用已 dry-run 驗證通過的內湖 landing patch。
- 內湖不是另做一頁，而是同一個 `baby03.tw` 依 UTM route 切到內湖內容。
- 正式投放 URL：
  `https://baby03.tw/?utm_campaign=neihu_1150912&utm_content=neihu_page`
- live 驗證通過：
  - DOM 含「內湖店」
  - DOM 含 `內湖路一段629巷36弄2號`
  - DOM 含 LINE/社群入口

### C-2 Meta Campaign / Adset / Ad

| 層級 | 名稱 | ID | 最終狀態 |
|---|---|---:|---|
| Campaign | `1150912-台北內湖` | `52574105685336` | `ACTIVE / ACTIVE` |
| Adset | `1150912(台北內湖)-開幕入群-LAL2%-5km adset` | `52574105688936` | `ACTIVE / ACTIVE` |
| Ad | `1150912(台北內湖)-開幕入群-LAL2%-5km ad` | `52574106207736` | `ACTIVE / ACTIVE` |

Adset 設定 readback：

| 項目 | 值 |
|---|---|
| Daily budget | `200`（TWD/day） |
| Optimization goal | `LANDING_PAGE_VIEWS` |
| Billing event | `IMPRESSIONS` |
| Audience | LAL 2%：`52572657425136` |
| Excludes | `6989502128332`, `52514523464136`, `52514523494136`, `52561778484536`, `52562394138936` |
| Gender / age | Female, 25-65 |
| Geo | `25.0812678, 121.5746635`，5 km，TW，home/recent |
| Placement | Facebook feed only |
| Device | mobile + desktop |

### C-3 Creative

| 項目 | 值 |
|---|---|
| Creative ID | `2547548165672024` |
| Page ID | `1420308921574349` |
| Effective object story ID | `1420308921574349_1138025838550026` |
| Image hash | `050aaf3a99031b81f944419fcbb90ff8` |
| CTA | `SEE_DETAILS` |
| Caption | `baby03.tw` |
| Headline | `台北內湖店開幕優惠` |
| Description | `加入 LINE 接收內湖店最新優惠` |
| Link | `https://baby03.tw/?utm_campaign=neihu_1150912&utm_content=neihu_page` |

Primary text：

```text
台北內湖店開幕倒數。

9/12 試營運、9/19 正式開幕，內湖朋友先加入 LINE 社群，開幕優惠、每日團購、生鮮食品與零售批發資訊會直接在社群公告。

地址：台北市內湖區內湖路一段629巷36弄2號。
```

Creative automation readback：

| 欄位 | 狀態 |
|---|---|
| `contextual_multi_ads` | `OPT_OUT` |
| `advantage_plus_creative` | `OPT_OUT` |
| `standard_enhancements` | `OPT_OUT` |
| `product_browsing` | `OPT_OUT` |
| `image_brightness_and_contrast` | `OPT_OUT` |
| `inline_comment` | `OPT_OUT` |
| `site_extensions` | `OPT_OUT` |
| `text_optimizations` | `OPT_OUT` |
| 其他 `creative_features_spec` enroll status | 全部 `OPT_OUT` |

## D. 驗證方式

1. Meta Graph readback：
   - `/{campaign_id}?fields=id,name,status,effective_status,configured_status,objective,buying_type`
   - `/{adset_id}?fields=id,name,status,effective_status,configured_status,daily_budget,optimization_goal,billing_event,targeting`
   - `/{ad_id}?fields=id,name,status,effective_status,configured_status,campaign_id,adset_id,creative{id}`
   - `/{creative_id}?fields=id,name,object_story_spec,contextual_multi_ads,degrees_of_freedom_spec`
2. Ads Manager UI readback：
   - 內湖廣告列出現在 Ads table。
   - 狀態由處理中進入 Graph `ACTIVE / ACTIVE`。
3. Live landing readback：
   - 以 Chrome 9222 開啟正式投放 URL。
   - 讀 DOM 驗證內湖店、地址與 LINE/社群入口存在。

## E. 已知未閉環

### E-1 `ad_change_events.csv` 補記失敗

應依 fb 廣告專案規則補記：

`D:\程式設計\fb廣告\data\ad_change_events.csv`

但本次 Codex session 對 D 槽寫入被 sandbox 擋下，`Add-Content` 回 `拒絕存取`，且已用 tail 驗證 rows 沒追加。

待補記事件：

| event_id | event_type | 物件 |
|---|---|---|
| `EVT_20260906_new_ad_52574106207736_neihu_opening` | `new_ad` | ad `52574106207736` / creative `2547548165672024` |
| `EVT_20260906_launch_52574105688936_neihu_opening` | `resume_adset` | campaign `52574105685336` / adset `52574105688936` |

### E-2 全域維修索引未更新

repair-log 規則要求同步全域索引：

`D:\程式設計\_GLOBAL_REPAIR_INDEX\GLOBAL_REPAIR_INDEX.md`

目前同樣受 D 槽寫入權限限制，本次只更新專案內 `docs/repair_logs/REPAIR_INDEX.md`。

## F. 結論

內湖 landing 與 FB 廣告開投已完成，Meta Graph 最終讀回 campaign/adset/ad 均為 `ACTIVE / ACTIVE`，creative 指向正確 URL、素材、文案與 CTA，且 creative automation 全部關閉。

未完成事項只剩流程紀錄補登：`ad_change_events.csv` 與全域 repair index 需在可寫入 D 槽的 session 補上。
