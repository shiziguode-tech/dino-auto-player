import json, os, socket, subprocess, tempfile, time, urllib.request
import websocket

CHROME = next((p for p in (os.path.join(os.environ.get('PROGRAMFILES', ''), 'Google', 'Chrome', 'Application', 'chrome.exe'), os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'Google', 'Chrome', 'Application', 'chrome.exe'), os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google', 'Chrome', 'Application', 'chrome.exe')) if os.path.isfile(p)), None)
if not CHROME:
    raise RuntimeError('找不到 Google Chrome，请先安装。')
with socket.socket() as sock:
    sock.bind(('127.0.0.1', 0))
    PORT = sock.getsockname()[1]
profile = tempfile.mkdtemp(prefix='dino-autoplay-')
subprocess.Popen([CHROME, '--new-window', '--no-first-run', '--no-default-browser-check', '--user-data-dir=' + profile,
                  '--remote-debugging-port=' + str(PORT), '--remote-allow-origins=*',
                  'chrome://dino/'])
for attempt in range(100):
    try:
        with urllib.request.urlopen(f'http://127.0.0.1:{PORT}/json', timeout=1) as response:
            tabs = json.load(response)
        tab = next((t for t in tabs if t.get('url', '').startswith('chrome://dino')), None) or next((t for t in tabs if t.get('type') == 'page' and t.get('url', '').startswith('chrome://newtab')), None)
        if tab:
            break
    except Exception:
        pass
    time.sleep(.2)
else:
    raise RuntimeError('无法连接 Chrome 恐龙游戏。')
ws = websocket.create_connection(tab['webSocketDebuggerUrl'], timeout=10, suppress_origin=True)
if not tab.get('url', '').startswith('chrome://dino'):
    ws.send(json.dumps({'id': 99, 'method': 'Page.navigate', 'params': {'url': 'chrome://dino/'}}))
    time.sleep(2)
ws.send(json.dumps({'id': 98, 'method': 'Page.bringToFront'}))
code = r'''(() => {
  if (typeof Runner === 'undefined') return 'not ready';
  let r; try { r = Runner.getInstance(); } catch (_) { return 'not ready'; }
  if (!r.tRex || !r.horizon) return 'not ready';
  if (window.__dinoBot) clearInterval(window.__dinoBot);
  r.gameOver = function() {};
  const key = (type, code, name) => new KeyboardEvent(type, {keyCode: code, which: code, code: name, bubbles: true});
  if (!r.playing) { r.onKeyDown(key('keydown', 32, 'Space')); r.onKeyUp(key('keyup', 32, 'Space')); }
  window.__dinoBot = setInterval(() => {
    if (!r.playing || !r.tRex || !r.horizon) return;
    const o = r.horizon.obstacles && r.horizon.obstacles[0];
    const t = r.tRex;
    if (!o) { if (t.ducking) t.setDuck(false); return; }
    const distance = o.xPos - t.xPos;
    const speed = r.currentSpeed || 6;
    const bird = (o.typeConfig && o.typeConfig.type === 'pterodactyl');
    const duck = bird && o.yPos < t.groundYPos - 5;
    const near = distance > -o.width - 30 && distance < Math.max(90, speed * 15);
    if (duck && near && !t.jumping) {
      if (!t.ducking) t.setDuck(true);
    } else {
      if (t.ducking) t.setDuck(false);
      if (!duck && near && distance > 0 && !t.jumping) t.startJump(speed);
    }
  }, 20);
  return 'started';
})()'''
for attempt in range(50):
    ws.send(json.dumps({'id': 1, 'method': 'Runtime.evaluate', 'params': {'expression': code, 'returnByValue': True}}))
    while True:
        result = json.loads(ws.recv())
        if result.get('id') == 1: break
    if result.get('result', {}).get('result', {}).get('value') == 'started':
        print('恐龙游戏已启动，自动跳跃和无敌模式已开启。')
        break
    time.sleep(.2)
else:
    raise RuntimeError('游戏加载失败：' + str(result))
ws.close()





