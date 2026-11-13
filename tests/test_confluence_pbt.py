"""汇流性首属性(INV-1 / M0 出口标准①的最小切片)。

种子 T4 单例的泛化:对四件套插件宇宙(logger / counter / greeter / announcer,
依赖链 announcer→greeter→counter),任意 load/unload 操作序列的静止态
(observable_state)恒等于"终集一次性装配"的结果。

WS3 将扩展完整属性集(apply/revert 契约、LIFO 回放、授权代数、重放幂等);
本文件只落首属性。
"""

import asyncio

from hypothesis import given, settings
from hypothesis import strategies as st

from deepseek_bot import kernel

PLUGINS = {
    "announcer": kernel.announcer_plugin,
    "counter": kernel.counter_plugin,
    "greeter": kernel.greeter_plugin,
    "logger": kernel.logger_plugin,
}
NAMES = sorted(PLUGINS)

ops_strategy = st.lists(
    st.tuples(st.sampled_from(["load", "unload"]), st.sampled_from(NAMES)),
    min_size=0,
    max_size=12,
)


async def _drive(ops):
    """按序列操作内核;非法操作(load 已在载/卸载不在载)跳过。返回终集。"""
    k = kernel.Kernel()
    loaded: dict[str, object] = {}
    for op, name in ops:
        if op == "load" and name not in loaded:
            loaded[name] = await k.load(kernel.Plugin(PLUGINS[name]))
        elif op == "unload" and name in loaded:
            await k.unload(loaded.pop(name))
    return k, set(loaded)


async def _compose(final):
    """终集一次性装配(顺序取字典序——汇流性保证装配序无关)。"""
    k = kernel.Kernel()
    for name in sorted(final):
        await k.load(kernel.Plugin(PLUGINS[name]))
    return k


# 历史注记:本属性曾用"零计数视同缺席"的归一化规避空列表键残留
# (hypothesis 缩小出 load counter → load greeter → unload counter 后
# {'app/ready': 0} 的键)。#106 已在内核 on()/off 效应中清理空键,
# 归一化随之移除——观测现在严格全等,INV-1 不再依赖归一化约定。


class TestConfluenceInv1:
    @settings(deadline=None)  # asyncio.run 每例重建事件循环,免 deadline 误报
    @given(ops=ops_strategy)
    def test_random_sequence_matches_one_shot_composition(self, ops):
        async def compare():
            k_seq, final = await _drive(ops)
            k_ref = await _compose(final)
            return kernel.observable_state(k_seq), kernel.observable_state(k_ref)

        state_seq, state_ref = asyncio.run(compare())
        assert state_seq == state_ref, f"INV-1 broken: seq {state_seq} != ref {state_ref}"
