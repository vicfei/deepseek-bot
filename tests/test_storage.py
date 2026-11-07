import os
import stat

from deepseek_bot.storage import LAYOUT_DIRS, PRIVATE_DIRS, init_home, resolve_home


def test_layout_created_idempotent(tmp_path):
    home = init_home(str(tmp_path / "home"))
    for d in LAYOUT_DIRS:
        assert os.path.isdir(os.path.join(home, d)), d
    # 幂等:重复初始化不报错、布局不变
    assert init_home(home) == home
    assert os.path.isdir(os.path.join(home, "ledger/segments"))


def test_private_dirs_are_0700(tmp_path):
    home = init_home(str(tmp_path / "home"))
    for d in PRIVATE_DIRS:
        mode = stat.S_IMODE(os.stat(os.path.join(home, d)).st_mode)
        assert mode == 0o700, d


def test_home_priority(tmp_path, monkeypatch):
    explicit = str(tmp_path / "explicit")
    dsb_home = str(tmp_path / "dsbhome")
    naga_home = str(tmp_path / "nagahome")
    samsara_home = str(tmp_path / "samsarahome")
    monkeypatch.setenv("DEEPSEEK_BOT_HOME", dsb_home)
    monkeypatch.setenv("NAGA_HOME", naga_home)
    monkeypatch.setenv("SAMSARA_HOME", samsara_home)
    assert resolve_home(explicit) == explicit
    assert resolve_home() == dsb_home           # DEEPSEEK_BOT_HOME 优先
    monkeypatch.delenv("DEEPSEEK_BOT_HOME")
    assert resolve_home() == naga_home          # NAGA_HOME 兼容回退
    monkeypatch.delenv("NAGA_HOME")
    assert resolve_home() == samsara_home       # SAMSARA_HOME 兼容别名
    monkeypatch.delenv("SAMSARA_HOME")
    monkeypatch.setenv("HOME", str(tmp_path))   # 隔离真实 home,默认值可测
    assert resolve_home().endswith(".deepseek-bot")   # 新装默认
    (tmp_path / ".naga").mkdir()                # 存量部署:沿用旧 home(连续性)
    assert resolve_home().endswith(".naga")
    (tmp_path / ".deepseek-bot").mkdir()        # 新名一旦出现即切换
    assert resolve_home().endswith(".deepseek-bot")
