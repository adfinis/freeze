import os
import sys
import warnings

from setuptools import setup

warnings.warn(
    """
pretty_dump has been deprecated
""".strip(),
    DeprecationWarning,
)

version = sys.version_info[0]

__version__ = None
version_file = "freeze/version.py"
with open(version_file) as f:
    code = compile(f.read(), version_file, "exec")
    exec(code)


def do_setup(cython=False):
    if "USE_CYTHON" in os.environ:
        if os.environ["USE_CYTHON"] == "false":
            cython = False
    packages = ["freeze"]
    if cython:
        print("Installing with cython\n")
        from Cython.Build import cythonize

        if version > 2:
            ext_modules = cythonize(["freeze/xfreeze.py", "freeze/fpprint.py",])
        else:
            ext_modules = cythonize(["freeze/xfreeze.py",])
    else:
        print("Installing without cython\n")
        ext_modules = []

    setup(
        name="pretty_dump",
        version=__version__,
        packages=packages,
        ext_modules=ext_modules,
        install_requires=["six"],
        author="Adfinis-SyGroup",
        author_email="jean-louis.fuchs@adfinis-sygroup.ch",
        description="Diff and dump anything",
        long_description="""This package is deprecated.

NOTE: This is a long dead project a lot of people are installing for some reason. You
don't need it, trust me.
""",
        keywords="freeze state hash sort compare unittest",
        url="https://github.com/adfinis-sygroup/freeze",
        classifiers=[
            "Development Status :: 5 - Production/Stable",
            "Environment :: Console",
            "Intended Audience :: Developers",
            "Intended Audience :: Education",
            "Intended Audience :: Information Technology",
            "License :: OSI Approved :: " "GNU Affero General Public License v3",
            "Natural Language :: English",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 2.6",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3.3",
            "Programming Language :: Python :: 3.4",
            "Programming Language :: Python :: 3.5",
            "Topic :: Software Development :: Libraries",
            "Topic :: Scientific/Engineering :: Information Analysis",
            "Topic :: Software Development :: Testing",
        ],
    )


try:
    do_setup(True)
except:
    do_setup(False)
