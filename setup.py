from setuptools import setup, find_packages
import os

package_root = os.path.abspath(os.path.dirname(__file__))

version = {}
with open(os.path.join(package_root, "LoopProjectFile/Version.py")) as fp:
    exec(fp.read(), version)
version = version["__version__"]

setup(
    name="LoopProjectFile",
    install_requires=["netCDF4>=1.5.4", "numpy", "pandas"],
    description="Open source structural geology data storage for Loop Projects",
    author="Roy Thomson",
    author_email="roy.thomson@monash.edu",
    url="https://github.com/Loop3D/LoopProjectFile",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Other Audience",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "License :: Free for non-commercial use",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Multimedia :: Graphics :: 3D Modeling",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: GIS",
    ],
    version=version,
    packages=find_packages(),
)
