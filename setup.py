from setuptools import setup
import os
from pathlib import Path
from platform import platform


install_requires = [
    "requests",
    "requests-toolbelt",
    "liftover",
    "markdown",
    "aiohttp<4.0.0",
    "chardet>=3.0.4",
    "aiosqlite",
    "oyaml",
    "nest-asyncio",
    "psutil",
    "python-dateutil",
    "download",
    "gdown",
    "split-file-reader",
    "packaging",
    "Pillow",
    "duckdb",
    "rich",
    "aiohttp-cors",
    "pyjwt",
    "polars>=1.9.0",
    "connectorx",
    "pyarrow",
    "multiprocess",
    "PySimpleGUI",
    "ujson",
    "numpy",
    # below are module-specific. move them to module's yml.
    "mpmath",
    "twobitreader",
    # ok to delete the below?
    "intervaltree",
]
if platform().startswith("Windows"):
    install_requires.append("PySimpleGUI")


def walk_and_add(d, pkg_files):
    folders = [
        "api",
        "cli",
        "gui",
        "lib",
    ]
    for root, _, files in os.walk(d):
        root_spl = root.split(os.sep)
        if len(root_spl) <= 1:
            continue
        root_f = root_spl[1]
        root_l = root_spl[-1]
        if root_f in folders and root_l != "__pycache__":
            root_files = [os.path.join("..", root, f) for f in files]
            pkg_files.extend(root_files)


this_directory = Path(__file__).parent
long_description = (this_directory / "README.rst").read_text()
oakvar_files = []
cravat_files = []
walk_and_add("oakvar", oakvar_files)
walk_and_add("cravat", cravat_files)
setup(
    name="oakvar",
    version="2.12.19",
    description="A genomic variant analysis platform",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/rkimoakbioinformatics/oakvar",
    author="Ryangguk Kim",
    author_email="rkim@oakbioinformatics.com",
    license="",
    classifiers=[""],
    keywords="genomic variant analysis interpretation genome",
    project_urls={
        "Documentation": "https://oakvar.readthedocs.io",
        "Source": "https://github.com/rkimoakbioinformatics/oakvar",
        "Tracker": "https://github.com/rkimoakbioinformatics/oakvar/issues",
    },
    packages=["oakvar", "cravat"],
    install_requires=install_requires,
    py_modules=[],
    python_requires=">=3.8",
    package_data={"oakvar": oakvar_files, "cravat": cravat_files},
    data_files=[],
    scripts=[],
    entry_points={
        "console_scripts": [
            "ov=oakvar.__main__:main",
        ]
    },
)
