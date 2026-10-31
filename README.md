# Dino Auto Player

自动游玩 Chrome 内置的 `chrome://dino` 恐龙游戏。程序根据障碍物位置自动跳跃；遇到飞鸟时，根据高度选择跳跃或下蹲。程序会尝试躲避障碍，碰撞后游戏仍会正常结束。

## 运行

需要 Windows、Google Chrome、Python 3 和 `websocket-client`：

```powershell
python -m pip install -r requirements.txt
python dino_autoplay.py
```

程序优先连接已开启远程调试的 Chrome 窗口；没有 Chrome 窗口时才会打开普通窗口（非无痕）。保持终端运行，按 Ctrl+C 停止。若 Chrome 已打开但未启用远程调试，请先完全退出 Chrome，再运行：

```powershell
& "$env:ProgramFiles\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --remote-allow-origins=* chrome://dino
```

## 工作原理与限制

程序通过本机 Chrome DevTools 接口连接游戏页面，读取游戏状态并控制恐龙，不会屏蔽游戏碰撞判定，失误时游戏会正常结束。它依赖 Chrome 游戏的内部实现；Chrome 更新可能使程序失效。页面切到后台时 Chrome 可能暂停或降低游戏速度。本项目是独立作品，与 Google 没有隶属关系，不包含 Chrome 游戏资源。

## 许可证

MIT，详见 [LICENSE](LICENSE)。
