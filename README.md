# Dino Auto Player

自动游玩 Chrome 内置的 `chrome://dino` 恐龙游戏。程序根据障碍物位置自动跳跃；遇到飞鸟时，根据高度选择跳跃或下蹲。启用无敌兜底后，即使碰撞也不会触发游戏结束。

## 运行

需要 Windows、Google Chrome、Python 3 和 `websocket-client`：

```powershell
python -m pip install -r requirements.txt
python dino_autoplay.py
```

程序会打开一个使用独立临时配置目录的 Chrome 窗口。保持游戏标签页打开即可观看；关闭窗口即可停止。重新加载游戏页面后，需要重新运行程序。

## 工作原理与限制

程序通过本机 Chrome DevTools 接口连接游戏页面，读取游戏状态并控制恐龙，同时替换游戏结束函数作为兜底。它依赖 Chrome 游戏的内部实现；Chrome 更新可能使程序失效。页面切到后台时 Chrome 可能暂停或降低游戏速度。本项目是独立作品，与 Google 没有隶属关系，不包含 Chrome 游戏资源。

## 许可证

MIT，详见 [LICENSE](LICENSE)。
