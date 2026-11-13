# DeepSeek Bot（Naga）—— 窗口接入（项目层）

> 全局协同协议见 https://github.com/vicfei/protocol 的 `COORDINATION.md`（唯一真相源）。
> 本文件只做**本项目映射**，不复制全局准则。

- 节点名：`singapore`
- 会话登记：`~/sessionlog/sessions/YYYY-MM/YYYY-MM-DD-singapore.md`
- 任务条目：`~/worklog/log/YYYY-MM/YYYY-MM-DD-singapore.md`
- `.context` 快照去向：`brainvault/naga/context/`（批次收尾跑 `~/brainvault/sync.sh`）
- 本项目边界令：
  - 三门全绿（pytest / ruff / pyright strict）才 push；PR 合并走 `.context/merge_gate.sh`（显式红绿判定，不靠 shell 链）
  - 运行时 home 默认 `~/.deepseek-bot`（存量 `~/.naga` 自动沿用）；凭据只进 `<home>/credentials/`（0600），永不入仓
  - `docs/design/` 为冻结基线（R3 资产，改动走 RFC）；种子内核 `src/deepseek_bot/kernel.py` 在 ruff/pyright 排除清单内（#106 等内核修复仅动 src 侧）
  - 微信多渠道绑定仓 `<home>/credentials/wechat-ilinks.json`（0600）；事件可见性/信任档位为宪法锚点，勿改值
