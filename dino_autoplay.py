\"\"\"Use an existing debuggable Chrome window, or open a normal window if none exists.\"\"\"
import ctypes
import json
import os
import socket
import subprocess
import tempfile
import time
import urllib.request
import urllib.error
from ctypes import wintypes
import websocket

DEBUG_PORT = 9222
CHROME_CANDIDATES = (
    os.path.join(os.environ.get('PROGRAMFILES', ''), 'Google', 'Chrome', 'Application', 'chrome.exe'),
    os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'Google', 'Chrome', 'Application', 'chrome.exe'),
    os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google', 'Chrome', 'Application', 'chrome.exe'),
)
CHROME = next((path for path in CHROME_CANDIDATES if os.path.isfile(path)), None)
if not CHROME:
    raise RuntimeError('找不到 Google Chrome，请先安装。')


def chrome_window_exists():
    user32 = ctypes.windll.user32
    found = []
    callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

    def visit(hwnd, _):
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            if length:
                title = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, title, length + 1)
                if 'Google Chrome' in title.value:
                    found.append(True)
                    return False
        return True

    user32.EnumWindows(callback_type(visit), 0)
    return bool(found)


def get_tabs():
    try:
        with urllib.request.urlopen(f'http://127.0.0.1:{DEBUG_PORT}/json', timeout=1) as response:
            return json.load(response)
    except (OSError, urllib.error.URLError):
        return None


if not chrome_window_exists():
    # Chrome 136+ requires a non-default user-data directory for remote debugging.
    profile = tempfile.mkdtemp(prefix='dino-autoplay-')
    subprocess.Popen([
        CHROME, '--new-window', '--no-first-run', '--no-default-browser-check',
        '--user-data-dir=' + profile,
        f'--remote-debugging-port={DEBUG_PORT}', '--remote-allow-origins=*',
        'chrome://dino/',
    ])
    for _ in range(100):
        tabs = get_tabs()
        if tabs is not None:
            break
        time.sleep(.2)
else:
    tabs = get_tabs()
    if tabs is None:
        raise RuntimeError(
            '检测到已有 Chrome 窗口，但它未开启远程调试，Chrome 不允许脚本接管该窗口。\\n'
            '请先完全退出 Chrome，再用下面命令启动普通窗口，然后运行本脚本：\\n'
            '"C:\\\\Program Files\\\\Google\\\\Chrome\\\\Application\\\\chrome.exe" '
            '--remote-debugging-port=9222 --remote-allow-origins=* chrome://dino'
        )

if not tabs:
    raise RuntimeError('没有找到可控制的 Chrome 标签页。')
tab = next((item for item in tabs if item.get('url', '').startswith('chrome://dino')), None)
if tab is None:
    tab = next((item for item in tabs if item.get('type') == 'page'), None)
if tab is None:
    raise RuntimeError('没有可用的 Chrome 页面标签页。')

ws = websocket.create_connection(tab['webSocketDebuggerUrl'], timeout=10, suppress_origin=True)
if not tab.get('url', '').startswith('chrome://dino'):
    ws.send(json.dumps({'id': 99, 'method': 'Page.navigate', 'params': {'url': 'chrome://dino/'}}))
    time.sleep(1.5)
ws.send(json.dumps({'id': 98, 'method': 'Page.bringToFront'}))
code = r'''(() => {
  if (typeof Runner === 'undefined') return 'not ready';
  let r; try { r = Runner.getInstance(); } catch (_) { return 'not ready'; }
  if (!r.tRex || !r.horizon) return 'not ready';
  if (window.__dinoBot) clearInterval(window.__dinoBot);
  const key = (type, keyCode, code) => new KeyboardEvent(type, {keyCode, which: keyCode, code, bubbles: true});
  if (!r.playing) { r.onKeyDown(key('keydown', 32, 'Space')); r.onKeyUp(key('keyup', 32, 'Space')); }
  window.__dinoBot = setInterval(() => {
    if (!r.playing || !r.tRex || !r.horizon) return;
    const obstacle = r.horizon.obstacles && r.horizon.obstacles[0];
    const trex = r.tRex;
    if (!obstacle) { if (trex.ducking) trex.setDuck(false); return; }
    const distance = obstacle.xPos - trex.xPos;
    const speed = r.currentSpeed || 6;
    const bird = obstacle.typeConfig && obstacle.typeConfig.type === 'pterodactyl';
    const duck = bird && obstacle.yPos >= trex.groundYPos - 23 && obstacle.yPos < trex.groundYPos - 5;
    const near = distance > -obstacle.width - 30 && distance < Math.max(90, speed * 15);
    if (duck && near && !trex.jumping) {
      if (!trex.ducking) trex.setDuck(true);
    } else {
      if (trex.ducking) trex.setDuck(false);
      if (!duck && near && distance > 0 && !trex.jumping) trex.startJump(speed);
    }
  }, 20);
  return 'started';
})()'''
for _ in range(50):
    ws.send(json.dumps({'id': 1, 'method': 'Runtime.evaluate', 'params': {'expression': code, 'returnByValue': True}}))
    while True:
        result = json.loads(ws.recv())
        if result.get('id') == 1:
            break
    if result.get('result', {}).get('result', {}).get('value') == 'started':
        print('新版自动避障已在 Chrome 中运行。按 Ctrl+C 停止脚本。')
        break
    time.sleep(.2)
else:
    raise RuntimeError('恐龙游戏尚未准备好：' + str(result))

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    ws.close()
