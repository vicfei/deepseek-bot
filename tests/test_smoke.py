import deepseek_bot as dsb


def test_package_importable():
    assert dsb.__name__ == "deepseek_bot"
    assert dsb.__version__
