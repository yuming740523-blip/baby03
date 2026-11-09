# 2026-11-09 — 楊梅環東店上架（官網 baby03.tw）

## A. 基本資訊

| 項目 | 內容 |
|---|---|
| 日期 | 2026-11-09 |
| 專案 | baby03.tw 落地頁（GitHub Pages + Cloudflare） |
| 嚴重度 | P3 |
| 結案類型 | Feature / Store onboarding / Production verification |
| 正式程式 | index.html 的 DEFAULT_DATA.sec1、STORE_ROUTES、STORE_LAYOUT |

## B. 背景

楊梅環東店（取代舊展示名「楊梅環中」準備中）開幕廣告 URL：
`?utm_source=fb&utm_medium=cpc&utm_campaign=yangmei_1151120_opening&utm_content=yangmei_opening_flyer_v1`，進站需置頂楊梅環東店。

## C. 資料（依 docs/STORE_ONBOARDING_SOP.md）

| 欄位 | 值 |
|---|---|
| label | 🍴【楊梅環東店】美食團購LINE下單 |
| LINE | https://line.me/ti/g2/cpcwiucYsileAIXdSR-4MuqdU7AeDKEuhDHPNg?utm_source=invitation&utm_medium=link_copy&utm_campaign=default |
| addr | 桃園市楊梅區環東路454號(宜康美藥局) |
| lat / lng | 24.9100688 / 121.1571186 |
| 座標來源 | Google Maps 2026-11-09 門牌查核：「326桃園市楊梅區中山里環東路454號」place 頁 !3d24.9100688!4d121.1571186 |
| 營業時間（傳單，不上網頁） | 週二至週六 12:00~20:00；開幕 11/20 |

## D. 修改內容

1. DEFAULT_DATA.sec1 在大甲育英店後新增楊梅環東店。
2. STORE_ROUTES 在大甲後新增 `{ rx: /yangmei|楊梅|環東/i, key: '楊梅環東' }`（既有 utm 值不含這些字，不誤命中）。
3. STORE_LAYOUT 的「楊梅環中／準備中」改為 `{ key:'楊梅環東', name:'楊梅環東店', region:'北區', color:'orange' }`；註解「四間準備中」改「三間準備中」（台南東區／高雄三民／雲林北港）。
4. 一併 commit 先前已補登的 11-02 兩份與 09-06 內湖 repair log 及 INDEX 列。

## E. 驗證

見 commit 後回報（本機 http.server + Playwright；正式站 Playwright + Pixel）。
