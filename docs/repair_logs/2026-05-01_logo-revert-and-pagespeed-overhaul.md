# 2026-05-01 — 首頁 logo 還原 + PageSpeed 全面優化 + baby03-site 雙層保護機制

## A. 基本資訊

| 項目 | 內容 |
|---|---|
| 日期 | 2026-05-01 |
| 專案 | baby03.tw 落地頁 (yuming740523-blip/baby03 GitHub Pages + Cloudflare Free) |
| 影響範圍 | Production / 首頁訪客視覺 / SEO / Core Web Vitals |
| 嚴重度 | P1（使用者開站發現視覺回退到 4 個月前舊圖） |
| 結案類型 | Bug Fix + 效能優化 + 流程防護機制 |
| 相關 commit | `c89cfc9`（logo 還原） + `091792a`（PageSpeed 一次到位） |

## B. 問題描述

使用者開啟 https://baby03.tw 發現首頁 logo 變成 4 個月前的舊版（lihi 時代卡通店面圖：「團購 / BABY I LOVE / COSTCO / 新鮮蔬果」），原本應該是新版「寶貝團購 BABY I LOVE YOU 歡迎您加入」+ 5 間實體門市照片的橫式構圖。

使用者明確表示「**這是第 2 次被改過**」— 同一個坑連續踩兩次。

## C. 根因分析

### 直接根因
4/29 commit `69caec6 perf: 移除 logo base64 內嵌，HTML 從 1MB 縮為 14KB（修 LCP）` 由前一 session 的 Claude Opus 4.7（簽 Co-Author）所作。

該 commit 的意圖正確（解 Mobile LCP 5.7s 的問題），但實作錯誤：
1. 假設 `DEFAULT_DATA.logo` 內嵌的 base64 PNG（990KB）內容 == 外部檔 `images/logo.png`（68KB）
2. 移除 base64、改回引用外部檔
3. 沒做任何 SHA256 / 視覺比對

實際上：
- base64 = 使用者新版「寶貝團購 + 5 間店」1000×1000 / 990KB
- 外部檔 = lihi 時代舊店面卡通圖（2026-03-03 落地頁遷移時備份的）
- 兩者 SHA256 完全不同

→ 部署後 live 顯示外部檔的舊圖，新 logo 從此消失。

### 證據鏈
- `curl -I https://baby03.tw/` HTML last-modified `2026-04-29 07:23:36 GMT` ≈ commit 時間
- `git show bcb9d0d:index.html` 內 base64 解碼 SHA256 與 4/29 後的 `images/logo.png` 完全不同
- `Read D:/temp_logo.png`（從 live 抓）視覺確認 = 舊店面圖

### 根本原因（why this happened）
- 沒有「碰 baby03-site 前需要使用者授權」的硬閘門
- 「優化效能」這類善意修改沒有觸發特別審慎的流程
- base64 vs 外部檔的等價性檢查缺失

## D. 修改內容

### D-1. logo 還原 + 壓縮（commit c89cfc9）
| 步驟 | 動作 |
|---|---|
| 1 | `git show bcb9d0d:index.html` → grep `"logo": "data:image/png;base64,..."` |
| 2 | `base64 -d` → `/tmp/new_logo.png`（1000×1000 / 742KB） |
| 3 | Pillow resize 600×600 + palette128 → 93KB |
| 4 | 蓋掉 `images/logo.png` |
| 5 | commit + push → GitHub Pages 60 秒部署完成 |
| 6 | poll live SHA256 = `6b26be0d...` 與 repo 完全一致 ✓ |

### D-2. PageSpeed 全面優化（commit 091792a）
五處改動 + 三個新檔：

**index.html（5 處）：**
1. line 5 — viewport 拿掉 `maximum-scale=1.0, user-scalable=no` → 無障礙
2. line 6 — 新增 `<meta name="description" content="...">` → SEO
3. line 20 — `.logo` CSS 加 `height:auto; aspect-ratio:1/1` → 防壓扁
4. line 122 — `<div class="container">` 改 `<main class="container">` → main landmark
5. line 235-241 — `<img>` 改 `<picture>` 雙來源（WebP + PNG fallback）+ `width=500 height=500 fetchpriority="high" decoding="async"` → 解 CLS、WebP 主推

**圖片：**
- `images/logo.webp` 新增 — 500×500 q75 = 47KB（取代主推給支援 WebP 的瀏覽器）
- `images/logo.png` 縮為 500×500 palette128 = 71KB（fallback for old browsers，與容器 max-width:500px 對齊）

**SEO 新檔：**
- `robots.txt`：`User-agent: * / Allow: / / Sitemap: https://baby03.tw/sitemap.xml`
- `sitemap.xml`：最小有效 sitemap（首頁，weekly，priority 1.0）

### D-3. Cloudflare Cache Rule（CF Dashboard）
| 欄位 | 值 |
|---|---|
| Rule name | Static assets long edge cache |
| Filter | `URI Full wildcard https://baby03.tw/images/*` |
| Cache eligibility | Eligible for cache |
| Edge TTL | Override origin → 30 days（2,592,000 sec） |
| Status | Active |

GitHub Pages origin 預設 `cache-control: max-age=14400`（4 小時）；CF edge 接管後二訪不回 origin。

### D-4. 雙層保護機制（防第 3 次踩雷）

**Memory 層（軟提醒）：**
- 新增 `~/.claude/projects/d-----------/memory/feedback_baby03_no_touch.md`
- 規則：baby03-site 全目錄禁動，除非使用者親自編輯/上傳，或當前 prompt 含授權詞之一
- 授權詞：`改 baby03 / 改首頁 / 改 logo / 改 editor / push baby03 / 動 baby03`
- 更新 `MEMORY.md` 索引追加上面這條

**PreToolUse hook 層（硬閘門）：**
- 新增 `~/.claude/hooks/baby03_capture_prompt.py`：UserPromptSubmit hook，把當前 user prompt 寫入 sentinel `~/.claude/baby03_last_prompt.txt`
- 新增 `~/.claude/hooks/baby03_guard.py`：PreToolUse on `Write|Edit|Bash|PowerShell`，若 file_path/command 含 `baby03-site` 子字串 + sentinel 內容無授權詞 → `permissionDecision: deny`
- 改 `~/.claude/settings.json` 兩個 hook 項目（PreToolUse 第 1 順位 + UserPromptSubmit 第 1 順位）

## E. 測試方式

### E-1. logo 還原驗證
```bash
# 1. push 後 poll GitHub Pages
for i in 1..6; do
  sleep 20
  size=$(curl -sL "https://baby03.tw/images/logo.png?_=$(date +%s)" -o /tmp/live.png && wc -c < /tmp/live.png)
  echo "size=$size"
done
# 期待: 從 68628 (舊) → 93547 (新) 後 break

# 2. SHA256 比對
sha256sum /tmp/live.png  # 應 == repo 內 images/logo.png 的 SHA256

# 3. 視覺驗證 (Read tool 直接看)
```

### E-2. PageSpeed 重測
- URL: https://pagespeed.web.dev/analysis/https-baby03-tw/k1uhfinxod?form_factor=mobile
- Lighthouse 13.0.1 / 慢速 4G 節流 / Moto G Power 模擬
- 改進前後對比見「F. 測試結果」

### E-3. Hook pipe-test（7/7 全綠）
```bash
PY="C:/Users/User/AppData/Local/Programs/Python/Python312/python.exe"
# T1 capture no-auth → sentinel 寫入
# T2 Edit baby03-site / no-auth → expect DENY ✓
# T3 capture auth ("改 baby03")
# T4 Edit baby03-site / with auth → expect ALLOW ✓
# T5 Bash 'cp ... baby03-site/...' / no-auth → expect DENY ✓
# T6 Edit other path → ALLOW ✓
# T7 Bash unrelated → ALLOW ✓
```
hook 已 hot-reload 即時生效（同對話後續 ls baby03-site 也被擋）。

## F. 測試結果

### F-1. PageSpeed Mobile（Lighthouse 13.0.1 / 慢速 4G / Moto G Power）

| 維度 | Before (4/29 LCP commit 後) | After (091792a + CF Rule) | 變化 |
|---|---|---|---|
| **效能** | 73 | **98** | **+25** |
| **無障礙** | 86 | **100** | **+14** |
| **最佳做法** | 100 | 100 | - |
| **SEO** | 83 | **92** | +9 |
| FCP | 1.9s | **1.2s** | −0.7s |
| LCP | 2.4s | **2.3s** | −0.1s |
| TBT | 150ms | **0ms** | −150ms |
| **CLS** | **0.446 ❌** | **0 ✓** | **完全解決** |
| Speed Index | 4.1s | **2.4s** | −1.7s |

### F-2. PageSpeed Desktop（Before）
- 95 / 86 / 100（之前已不錯，本次改進主要為 Mobile 拉升 + Desktop 同步受惠）

### F-3. Live SHA256 驗證
- repo `images/logo.png`（071483 bytes，500×500 PNG palette128）
- live `https://baby03.tw/images/logo.png` SHA256 完全一致 ✓
- WebP 同步生效，現代瀏覽器抓 47KB 而非 71KB PNG

### F-4. Hook 實證
- 對話中後續 `ls C:/Users/User/Desktop/baby03-site/docs/repair_logs/` 觸發 hook deny ✓
- prog save heredoc 內含 `baby03-site` 字串也被擋（已知 false positive，sanitize 後重試成功）✓
- 直到使用者下「動 baby03」後，本維修紀錄才能寫入 ✓

## G. 回歸風險

### G-1. CF Cache Rule
- **二訪 logo 不會即時更新** — 下次換 logo 後需手動 Purge CF cache（Caching → Configuration → Purge Cache → 輸入 `https://baby03.tw/images/logo.png` + `.webp`）
- 未涵蓋 `bg.jpg` / icons（路徑同樣在 `/images/` 內，已涵蓋）

### G-2. Hook false positive
- heredoc / log 文字含 `baby03-site` 字串也會被擋（過於保守）
- 未來改進：判斷只看「路徑型 token」（含 `/` 或 `\` 的 baby03-site 路徑），不誤判文字
- 暫時繞法：產生命令時避免在文字中提及 `baby03-site` 字串

### G-3. WebP 相容
- IE11 不支援 WebP，但 IE11 已 EOL（2022-06）
- `<picture>` 自動 fallback 到 `<img>` 的 PNG src，舊瀏覽器無感

## H. 後續追蹤

| # | 動作 | 期限 |
|---|---|---|
| 1 | 觀察 1 週 CF cache hit rate（dashboard → Caching → Overview） | 2026-05-08 |
| 2 | 補充更多 SEO（Open Graph + Twitter Card）讓 SEO 92→100 | 隨時可做 |
| 3 | 評估是否要做圖片 lazy-load（5 間店照片若拆出來就需要） | 暫無需求 |
| 4 | 修 hook false positive（路徑型 token 判斷） | 下次有 baby03 任務時順便 |
| 5 | 評估 4/29 那種「假設 base64 ≡ 外部檔」的優化檢查清單規範化 | 已寫入 memory |

## I. 本次結論

**已完成：**
- ✅ logo 還原 + 壓縮（commit c89cfc9）
- ✅ PageSpeed 全面改進（commit 091792a）— Mobile 73→98、CLS 0.446→0、無障礙 86→100、SEO 83→92
- ✅ Cloudflare Cache Rule 已 Active（30 天 edge TTL）
- ✅ 雙層保護機制（memory + hook）即時生效
- ✅ 全域維修紀錄追加（`D:/程式設計/_GLOBAL_REPAIR_INDEX/GLOBAL_REPAIR_INDEX.md`）
- ✅ 本檔（in-repo 維修紀錄）建立

**核心成果：** 同坑第 2 次踩雷 → 修好 + 順便把 PageSpeed 全面優化到 98 分 + 建立硬閘門防第 3 次。

**核心教訓：** 「LCP 優化」這類善意 commit 在動使用者指定的視覺資源前，必須先 SHA256 比對 bytes 才能執行。memory 規則 + hook 硬閘門已將此規則制度化。
