#!/usr/bin/env python
import codecs
import os
import re

from setuptools import find_packages
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))


def fread(filename):
    with codecs.open(os.path.join(here, filename), "r", encoding="utf-8") as f:
        return f.read()


def meta(category, fpath="src/kaomojin/__init__.py"):
    package_root_file = fread(fpath)
    matched = re.search(
        r"^__{}__\s+=\s+['\"]([^'\"]*)['\"]".format(category), package_root_file, re.M
    )
    if matched:
        return matched.group(1)
    raise Exception("Meta info string for {} undefined".format(category))


author = meta("author")
author_email = meta("author_email")
license = meta("license")
version = meta("version")
readme = fread("README.rst")


requires = ["emoji", "regex", "termcolor"]

setup_requires = ["pytest-runner>=5.2"]

dev_requires = [
    "black>=19.10b0",
    "flake8>=3.7.9",
    "isort[pyproject]>=4.3.21",
    "pre-commit>=2.2.0",
    "seed-isort-config>=2.1.1",
]

tests_require = ["coverage[toml]>=5.0.4", "pytest>=5.4.1", "pytest-cov>=2.8.1"]


setup(
    name="kaomojin",
    version=version,
    description="A kaomoji extractor for Python",
    long_description=readme,
    long_description_content_type="text/x-rst",
    author=author,
    author_email=author_email,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Utilities",
    ],
    entry_points={"console_scripts": ["kaodump=kaomojin.dumpers:cli"]},
    extras_require={"dev": dev_requires + tests_require, "tests": tests_require},
    include_package_data=True,
    install_requires=requires,
    license=license,
    package_data={"": ["LICENSE.txt"], "kaomojin.data": ["kaomoji/*.tsv"]},
    package_dir={"": "src"},
    packages=find_packages("src"),
    platforms=["Linux"],
    python_requires=">=3.7",
    scripts=[],
    setup_requires=setup_requires,
    tests_require=tests_require,
    url="https://github.com/okomestudio/kaomojin",
)
