"""M0 存储拓扑骨架。

数据模型设计文档 §2 的目录布局与 home 解析。本模块只负责布局存在性与
权限;head.log 追加、segments 封存、快照、CAS 读写逻辑属 WS2,不在此实现。
"""

from __future__ import annotations

import os

# 数据模型 §2 拓扑的目录部分(相对 home;ledger/ 父目录随子目录自动创建)
LAYOUT_DIRS = (
    "ledger/segments",
    "ledger/snapshots",
    "assets/blobs",
    "assets/sidecar",
    "assets/refs",
    "memory/episodic",
    "memory/semantic",
    "traces",
    "shadow",
    "credentials",
    "keys",
    "keys/escrow",
)

# 凭据与密钥库属敏感目录(数据模型 §2:credentials 独立权限 0600 级)
PRIVATE_DIRS = frozenset({"credentials", "keys", "keys/escrow"})


def env_opt(name: str) -> str | None:
    """读 DEEPSEEK_BOT_<name>,回退 NAGA_<name>(2026-11 改名批兼容窗口)。"""
    for prefix in ("DEEPSEEK_BOT_", "NAGA_"):
        value = os.environ.get(prefix + name)
        if value:
            return value
    return None


def _default_home() -> str:
    """默认 home:~/.naga(与代号对齐)。存量 ~/.deepseek-bot 存在且新名不存在
    则沿用(soak 时钟/账本/凭据/密钥连续性优先;目录迁移属显式动作,不静默搬家)。"""
    modern = os.path.expanduser("~/.naga")
    legacy = os.path.expanduser("~/.deepseek-bot")
    if not os.path.exists(modern) and os.path.isdir(legacy):
        return legacy
    return modern


def resolve_home(explicit: str | None = None) -> str:
    """home 解析优先级:显式参数 > DEEPSEEK_BOT_HOME > NAGA_HOME >
    SAMSARA_HOME(兼容别名)> 默认 ~/.naga。"""
    if explicit:
        return explicit
    for env in ("DEEPSEEK_BOT_HOME", "NAGA_HOME", "SAMSARA_HOME"):
        value = os.environ.get(env)
        if value:
            return value
    return _default_home()


def init_home(home: str | None = None) -> str:
    """幂等创建完整布局,返回 home 绝对路径;私有目录权限 0700。"""
    h = resolve_home(home)
    for d in LAYOUT_DIRS:
        path = os.path.join(h, d)
        os.makedirs(path, exist_ok=True)
        if d in PRIVATE_DIRS:
            os.chmod(path, 0o700)
    return h
