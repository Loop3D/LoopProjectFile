from setuptools import setup
import os

package_root = os.path.abspath(os.path.dirname(__file__))

version = {}
with open(os.path.join(package_root, "LoopProjectFile/version.py")) as fp:
    exec(fp.read(), version)
version = version["__version__"]

setup()
