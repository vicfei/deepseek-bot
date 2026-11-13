"""#106 回归:off 效应移除 handler 后清理 _listeners 空列表键(源自 #11)。

零计数=缺席:load counter → load greeter → unload counter 后,
observable_state 不再出现 {'app/ready': []};emit/aemit 行为不变。
"""

import asyncio

from deepseek_bot import kernel


async def _cascade_unloaded() -> kernel.Kernel:
    k = kernel.Kernel()
    c = await k.load(kernel.Plugin(kernel.counter_plugin))
    await k.load(kernel.Plugin(kernel.greeter_plugin))
    assert k._listeners.get("app/ready")   # 激活期 handler 在册
    await k.unload(c)                      # 级联停用 greeter → off 效应移除 handler
    return k


def test_empty_listener_key_removed_after_cascade_unload():
    k = asyncio.run(_cascade_unloaded())
    assert "app/ready" not in k._listeners, f"残留空键: {k._listeners}"
    assert kernel.observable_state(k)["listeners"] == {}


def test_reactivation_resubscribes_normally():
    """清理键不改变行为:重载 counter 后 greeter 重新订阅。"""
    async def drive():
        k = await _cascade_unloaded()
        await k.load(kernel.Plugin(kernel.counter_plugin))
        return k

    k = asyncio.run(drive())
    assert k._listeners.get("app/ready"), "重载后 handler 应重新在册"


def test_double_unload_is_safe():
    """边界:重复卸载不抛(off 效应幂等)。"""
    async def drive():
        k = kernel.Kernel()
        c = await k.load(kernel.Plugin(kernel.counter_plugin))
        await k.load(kernel.Plugin(kernel.greeter_plugin))
        await k.unload(c)
        await k.unload(c)
        return k

    k = asyncio.run(drive())
    assert "app/ready" not in k._listeners
