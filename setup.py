from distutils.core import setup
import setuptools


setup(
  name = 'aomame',
  packages = ['aomame'],
  version = '0.0.6',
  description = 'Aomame',
  long_description = 'Pythonic SDK for Translation APIs',
  author = '',
  url = 'https://github.com/alvations/aomame',
  keywords = [],
  classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
  ],
  install_requires = ['requests', 'tqdm'],
)
