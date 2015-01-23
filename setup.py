# -*- encoding: utf-8 -*-
import io
import sys
import re
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext

from setuptools import find_packages
from setuptools import setup
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest

        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


def read(*names, **kwargs):
    return io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get("encoding", "utf8")
    ).read()


setup(
    name="pdfpapersaver",
    version="0.1.0",
    license="BSD",
    description="An example package. Replace this with a proper project description. Generated with https://github.com/ionelmc/cookiecutter-pylibrary",
    long_description="%s\n%s" % (read("README.rst"), re.sub(":obj:`~?(.*?)`", r"``\1``", read("CHANGELOG.rst"))),
    author="Joern Paessler",
    author_email="mail@beyond-content.de",
    url="https://github.com/beyond-content/python-pdf-paper-saver",
    packages=find_packages("src"),
    package_dir={"": "src"},
    py_modules=[splitext(basename(path))[0] for path in glob("src/*.py")],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
    ],
    keywords=[
        # eg: "keyword1", "keyword2", "keyword3",
    ],
    install_requires=[
        # eg: "aspectlib==1.1.1", "six>=1.7",
        "Rect", "PyPDF2", "reportlab", "sphinx", "sphinx_py3doc_enhanced_theme", "PyHamcrest", "pytest", "jinja2"
    ],
    extras_require={
        # eg: "rst": ["docutils>=0.11"],
    },
    entry_points={
        "console_scripts": [
            "pdfpapersaver = pdfpapersaver.__main__:main"
        ]
    },
    cmdclass={
        "test": PyTest,
    },
)
