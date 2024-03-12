import codecs
import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

setup(
    name='pyside6-svg-widgets',
    version='0.2.16',
    author='SHADRIN',
    author_email='none@gmail.com',
    license='MIT',
    packages=find_packages(),
    description='PySide6 svg widgets',
    url='https://github.com/SHADR1N/pyside6-svg-widgets.git',
    long_description_content_type='text/markdown',
    long_description=long_description,
    install_requires=[
        'PySide6>=6.4.0',
    ]
)