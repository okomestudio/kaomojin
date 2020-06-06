import pytest
from kaomojin.kaomojin import Kaomoji
from kaomojin.kaomojin import NonKaomoji
from kaomojin.kaomojin import analyze
from kaomojin.kaomojin import extract
from kaomojin.kaomojin import extract_and_replace
from kaomojin.kaomojin import replace


class TestAnalyze:
    def test(self):
        s = "今日もいい天気！(=^▽^=) 海に行こう！"
        assert list(analyze(s)) == [
            NonKaomoji(0, "今日もいい天気！"),
            Kaomoji(8, "(=^▽^=)"),
            NonKaomoji(15, " 海に行こう！"),
        ]


class TestExtract:
    def test(self):
        s = "今日もいい天気！(=^▽^=) 海に行こう！"
        assert extract(s) == [Kaomoji(8, "(=^▽^=)")]


class TestExtractAndReplace:
    @pytest.mark.parametrize("text", [("今日もいい天気！(=^▽^=) 海に行こう！(*ﾟ▽ﾟ)ﾉ")])
    def test(self, text):
        new = "<<{num}>>"
        kaomojis, modified = extract_and_replace(text, new)
        assert text != modified

        recovered = modified
        for num, kaomoji in enumerate(kaomojis):
            recovered = recovered.replace(new.format(num=num), kaomoji.text)
        assert text == recovered


class TestReplace:
    @pytest.mark.parametrize("text, count", [("今日もいい天気！(=^▽^=) 海に行こう！", 1)])
    def test(self, text, count):
        replaced = replace(text, "<<{num}>>")
        for num in range(count):
            assert "<<{num}>>".format(num=num) in replaced
