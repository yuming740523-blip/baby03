"""
baby03 本地部署伺服器
- 提供靜態檔案服務（http://localhost:7788）
- 根路徑 / 自動導向 editor.html（本地編輯器）
- POST /deploy → 更新 index.html 的 DEFAULT_DATA + git add commit push
使用方式：雙擊 start-editor.bat 即可
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json, os, subprocess, threading, sys

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
PORT = 7788

START = '// @@DATA_START@@\n'
END   = '\n// @@DATA_END@@'


def extract_data(template):
    """從 index.html 取出目前線上的 DEFAULT_DATA。抓不到就拋例外，不回 None 讓呼叫端誤放行。"""
    s = template.find(START)
    e = template.find(END)
    if s < 0 or e < 0 or e < s:
        raise ValueError('找不到 DATA 標記')
    blk = template[s + len(START):e]
    a = blk.find('{')
    b = blk.rfind('}')
    if a < 0 or b < 0:
        raise ValueError('DATA 區塊格式異常')
    return json.loads(blk[a:b + 1])


def store_key(btn):
    """門市識別：優先用 URL（排序可合法改變，位置不能當 identity），URL 缺失才退回 label。"""
    url = (btn.get('url') or '').strip()
    if url:
        return ('url', url)
    return ('label', (btn.get('label') or '').strip())


def missing_stores(current, incoming):
    """回傳 current 有、incoming 沒有的門市 label 清單。"""
    have = {store_key(b) for b in (incoming.get('sec1') or [])}
    return [
        (b.get('label') or '(無名稱)')
        for b in (current.get('sec1') or [])
        if store_key(b) not in have
    ]

class Handler(BaseHTTPRequestHandler):

    # ── CORS preflight ──────────────────────────────────
    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    # ── 靜態檔案 ────────────────────────────────────────
    def do_GET(self):
        path = self.path.split('?')[0]
        # 根路徑導向本地編輯器（不對外公開）
        if path == '/':
            path = '/editor.html'
        fp = os.path.join(REPO_DIR, path.lstrip('/').replace('/', os.sep))
        if os.path.isfile(fp):
            ext = fp.rsplit('.', 1)[-1].lower() if '.' in fp else ''
            mime = {
                'html': 'text/html;charset=utf-8',
                'css':  'text/css',
                'js':   'application/javascript',
                'png':  'image/png',
                'jpg':  'image/jpeg',
                'jpeg': 'image/jpeg',
                'gif':  'image/gif',
                'svg':  'image/svg+xml',
                'ico':  'image/x-icon',
            }.get(ext, 'text/plain')
            with open(fp, 'rb') as f:
                data = f.read()
            self.send_response(200)
            self.send_header('Content-Type', mime)
            self.send_header('Content-Length', len(data))
            self._cors()
            self.end_headers()
            self.wfile.write(data)
        else:
            self.send_response(404)
            self.end_headers()

    # ── 部署 API ────────────────────────────────────────
    def do_POST(self):
        if self.path != '/deploy':
            self.send_response(404)
            self.end_headers()
            return

        try:
            length = int(self.headers.get('Content-Length', 0))
            body   = json.loads(self.rfile.read(length).decode('utf-8'))
            data   = body.get('data')
            if not data:
                self._json(400, False, '內容為空')
                return
        except Exception as e:
            self._json(400, False, f'解析失敗：{e}')
            return

        # 1. 讀取 index.html 模板
        index_path = os.path.join(REPO_DIR, 'index.html')
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                template = f.read()
        except Exception as e:
            self._json(500, False, f'讀取模板失敗：{e}')
            return

        # 2. 安全閘門：不准讓既有門市無聲消失
        #    2026-08-09 事故背景：editor 內建的 DEFAULT_DATA 過期（少了桃園榮華、士林葫東），
        #    在沒有 localStorage 的機器上開編輯器按部署，會把線上 8 家直接洗成 6 家並自動 push。
        try:
            current = extract_data(template)
        except Exception as ex:
            self._json(500, False, f'讀不到 index.html 現況（{ex}），為安全起見不部署')
            return

        gone = missing_stores(current, data)
        if gone:
            self._json(409, False,
                       '拒絕部署：這次會讓現有門市消失 → ' + '、'.join(gone) +
                       '。請先在編輯器載入正式站目前資料，確認後再部署。')
            return

        # 3. 替換 DEFAULT_DATA 區塊
        s = template.find(START)
        e = template.find(END)
        if s < 0 or e < 0:
            self._json(500, False, '找不到資料標記，請確認 index.html 格式')
            return
        data_json = json.dumps(data, ensure_ascii=False, indent=4)
        new_html = (template[:s + len(START)]
                    + f'const DEFAULT_DATA = {data_json};'
                    + template[e:])

        # 4. 寫入 index.html
        try:
            with open(index_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(new_html)
        except Exception as e:
            self._json(500, False, f'寫檔失敗：{e}')
            return

        # 5. git add
        r = subprocess.run(
            ['git', 'add', 'index.html'],
            cwd=REPO_DIR, capture_output=True, text=True, encoding='utf-8',
            stdin=subprocess.DEVNULL
        )
        if r.returncode != 0:
            self._json(500, False, f'git add 失敗：{r.stderr}')
            return

        # 6. 確認是否有變更
        diff = subprocess.run(
            ['git', 'diff', '--cached', '--name-only'],
            cwd=REPO_DIR, capture_output=True, text=True, encoding='utf-8',
            stdin=subprocess.DEVNULL
        )
        if not diff.stdout.strip():
            self._json(200, True, '內容未變更，已是最新版本')
            return

        # 7. git commit
        r = subprocess.run(
            ['git', 'commit', '-m', 'update: content via editor'],
            cwd=REPO_DIR, capture_output=True, text=True, encoding='utf-8',
            stdin=subprocess.DEVNULL
        )
        if r.returncode != 0:
            self._json(500, False, f'git commit 失敗：{r.stderr}')
            return

        # 8. git push
        r = subprocess.run(
            ['git', 'push', 'origin', 'master'],
            cwd=REPO_DIR, capture_output=True, text=True, encoding='utf-8',
            stdin=subprocess.DEVNULL
        )
        if r.returncode != 0:
            self._json(500, False, f'git push 失敗：{r.stderr.strip()}')
            return

        self._json(200, True, '已成功部署到 GitHub Pages！')

    # ── 工具方法 ────────────────────────────────────────
    def _cors(self):
        self.send_header('Access-Control-Allow-Origin',  '*')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')

    def _json(self, code, ok, msg):
        data = json.dumps({'ok': ok, 'msg': msg}, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json;charset=utf-8')
        self.send_header('Content-Length', len(data))
        self._cors()
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt, *args):
        pass  # 不輸出 HTTP log


if __name__ == '__main__':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

    server = HTTPServer(('127.0.0.1', PORT), Handler)
    print(f'[OK] 編輯伺服器已啟動 -> http://localhost:{PORT}')
    print(f'[  ] 請在瀏覽器開啟以上網址進行編輯')
    print(f'[  ] 關閉此視窗將停止伺服器\n', flush=True)

    def open_browser():
        import webbrowser
        webbrowser.open(f'http://localhost:{PORT}')
    threading.Timer(1.0, open_browser).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n已停止')
        sys.exit(0)
