import sys
from argparse import ArgumentParser
from html import unescape

import emoji
import regex as re
from termcolor import colored

from .kaomojin import extract_and_replace


_valid_emojis = set(emoji.EMOJI_UNICODE.keys())


def remove_emojis(text):
    text = emoji.demojize(text)
    ijs = []
    for m in re.finditer(r":\w+:", text):
        if m.group() in _valid_emojis:
            ijs.append((m.start(), m.end()))
    pieces = []
    pos = 0
    for i, j in ijs:
        pieces.append(text[pos:i])
        pos = j
    pieces.append(text[pos:])
    return "".join(pieces)


def remove_japanese(text):
    text = re.sub(
        r"(([！]{0,})([\p{Hiragana}\p{Katakana}\p{Han}a-zA-Z0-9.,&:;/＆０-９ー、](?<![ｧ-ﾝ])){2,}([…。！？]{0,}))",
        "\n",
        text,
    )
    return text


class Format:
    def __call__(self, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def factory(cls, format):
        subcls = {cls.__name__: cls for cls in Format.__subclasses__()}.get(format)
        return subcls() if subcls else default()


class tweet(Format):
    def __call__(self, text):
        text = text.replace("\u200b", "")
        text = unescape(text)

        kaomojis, text = extract_and_replace(text, "")

        # Remove @username
        text = re.sub(r"\.?@[a-zA-Z0-9_]+[:;]?", "", text)

        # Remove tag
        text = re.sub(r"#(\w+)", r"\1", text)

        # Remove URL
        text = re.sub(r"https?://[\w./]+", r"", text)

        text = re.sub(r"【[\w！？]+】", "", text)

        text = remove_emojis(text)
        text = text.replace("\u200b", "")
        text = remove_japanese(text)
        return [(0, obj.text) for obj in kaomojis] + [
            (1, s.strip()) for s in text.split("\n") if s.strip() != ""
        ]


class default(Format):
    def __call__(self, text):
        text = remove_emojis(text)
        text = text.replace("\u200b", "")
        text = remove_japanese(text)
        return [s.strip() for s in text.split("\n") if s.strip() != ""]


def main(filenames, format=None, show_source=False):
    format = Format.factory(format)

    def gen_texts(filenames):
        if not filenames:
            for text in sys.stdin:
                yield text
        else:
            for filename in filenames:
                with open(filename) as f:
                    for text in f:
                        yield text

    for idx, text in enumerate(gen_texts(filenames)):
        result = format(text)
        lines = []
        if show_source:
            lines.append(colored(text, "blue"))
        for each in result:
            lines.append("%d\t%s" % each)

        if lines:
            for line in lines:
                print(line)
            print()


def cli():
    p = ArgumentParser()
    p.add_argument("filename", nargs="*")
    p.add_argument("--format", "-f", choices=("tweet",), default=None)
    p.add_argument("--show-source", "-s", action="store_true", default=False)
    args = p.parse_args()
    main(args.filename, format=args.format, show_source=args.show_source)
