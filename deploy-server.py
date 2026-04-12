"""
baby03 本地部署伺服器
- 提供靜態檔案服務（http://localhost:7788）
- POST /deploy → 寫入 index.html + git add commit push
使用方式：雙擊 start-editor.bat 即可
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json, os, subprocess, threading, sys

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
PORT = 7788

class Handler(BaseHTTPRequestHandler):

    # ── CORS preflight ──────────────────────────────────
    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    # ── 靜態檔案 ────────────────────────────────────────
    def do_GET(self):
        path = self.path.split('?')[0]
        if path == '/':
            path = '/index.html'
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
            html   = body.get('html', '')
            if not html:
                self._json(400, False, '內容為空')
                return
        except Exception as e:
            self._json(400, False, f'解析失敗：{e}')
            return

        # 1. 寫入 index.html
        index_path = os.path.join(REPO_DIR, 'index.html')
        try:
            with open(index_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(html)
        except Exception as e:
            self._json(500, False, f'寫檔失敗：{e}')
            return

        # 2. git add
        r = subprocess.run(
            ['git', 'add', 'index.html'],
            cwd=REPO_DIR, capture_output=True, text=True, encoding='utf-8'
        )
        if r.returncode != 0:
            self._json(500, False, f'git add 失敗：{r.stderr}')
            return

        # 3. 確認是否有變更
        diff = subprocess.run(
            ['git', 'diff', '--cached', '--name-only'],
            cwd=REPO_DIR, capture_output=True, text=True, encoding='utf-8'
        )
        if not diff.stdout.strip():
            self._json(200, True, '內容未變更，已是最新版本')
            return

        # 4. git commit
        r = subprocess.run(
            ['git', 'commit', '-m', 'update: content via editor'],
            cwd=REPO_DIR, capture_output=True, text=True, encoding='utf-8'
        )
        if r.returncode != 0:
            self._json(500, False, f'git commit 失敗：{r.stderr}')
            return

        # 5. git push
        r = subprocess.run(
            ['git', 'push'],
            cwd=REPO_DIR, capture_output=True, text=True, encoding='utf-8'
        )
        if r.returncode != 0:
            self._json(500, False, f'git push 失敗：{r.stderr}')
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
        pass  # 不輸出 HTTP log，避免編碼問題


if __name__ == '__main__':
    import io
    # 強制 stdout 使用 UTF-8
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

    server = HTTPServer(('127.0.0.1', PORT), Handler)
    print(f'[OK] 編輯伺服器已啟動 -> http://localhost:{PORT}')
    print(f'[  ] 請在瀏覽器開啟以上網址進行編輯')
    print(f'[  ] 關閉此視窗將停止伺服器\n', flush=True)

    # 啟動後 1 秒自動開瀏覽器
    def open_browser():
        import webbrowser
        webbrowser.open(f'http://localhost:{PORT}')
    threading.Timer(1.0, open_browser).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n已停止')
        sys.exit(0)
