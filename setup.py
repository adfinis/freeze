from setuptools import setup
import os
import six


def do_setup(cython=False):
    if 'USE_CYTHON' in os.environ:
        if os.environ['USE_CYTHON'] == "false":
            cython = False
    packages = ['freeze']
    if cython:
        print("Installing with cython\n")
        from Cython.Build import cythonize
        if six.PY3:
            ext_modules = cythonize([
                "lib/freeze/xfreeze.py",
                "lib/freeze/fpprint.py",
            ])
        else:
            ext_modules = cythonize([
                "lib/freeze/xfreeze.py",
            ])
    else:
        print("Installing without cython\n")
        ext_modules = []

    setup(
        name = "freeze",
        version = "1.0.8",
        package_dir = {'': 'lib'},
        packages    = packages,
        ext_modules = ext_modules,

        install_requires = ['six'],

        author = "Jean-Louis Fuchs",
        author_email = "ganwell@fangorn.ch",
        description = "Freeze - dump / hash / sort / compare / diff anything",
        license = "Modified BSD",
        long_description = """
Freeze the state of data-structures and objects for data-analysis or testing
(diffing data-structures). Frozen data-structures consist of only tuples
and these are comparable/sortable/hashable. The freeze() function can be used
for many purposes for example implement __hash__() for your complex object
very fast. dump() is intended for testing and analysis.""",
        keywords = "freeze state hash sort compare unittest",
        url = "https://github.com/adfinis-sygroup/freeze",
        classifiers = [
            "Development Status :: 5 - Production/Stable",
            "Environment :: Console",
            "Intended Audience :: Developers",
            "Intended Audience :: Education",
            "Intended Audience :: Information Technology",
            "License :: OSI Approved :: BSD License",
            "Natural Language :: English",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 2.6",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3.3",
            "Programming Language :: Python :: 3.4",
            "Topic :: Software Development :: Libraries",
            "Topic :: Scientific/Engineering :: Information Analysis",
            "Topic :: Software Development :: Testing",
        ]
    )

try:
    do_setup(True)
except:
    do_setup(False)
