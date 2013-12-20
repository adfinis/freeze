from setuptools import setup, find_packages

setup(
    name = "freeze",
    version = "0.8.0",
    package_dir = {'': 'lib'},
    py_modules=['freeze'],

    install_requires = ['six'],

    author = "Jean-Louis Fuchs",
    author_email = "ganwell@fangorn.ch",
    description = "Freeze - hash / sort / compare / diff anything",
    license = "Modified BSD",
    long_description = """
ATTENTION: I now have enough experience to design clean interface for freeze.
So if there is no bugfix version, the next version will break things.

* freeze_fast will become freeze (because only cycle free datastructures can
  truely be frozen
* freeze becomes dump, freeze_stable becomes dump_stable
-> Their purpose is unit-testing or dumping for analysis
-> There will be an option to select unit-test or dump mode

Freeze the state of data-structures and objects for data-analysis or testing
(diffing data-structures). Frozen data-structures consist of only tuples
and these are comparable/sortable/hashable. The freeze method can be used
for many purposes for example implement __hash__ for your complex object
very fast. freeze_stable and flatten are usable for testing and analysis.""",
    keywords = "freeze state hash sort compare unittest",
    url = "https://github.com/adfinis-sygroup/freeze",
    #download_url = "https://github.com/adfinis-sygroup/freeze/archive/freeze-0.1.0.tar.gz",
    #bugtrack_url = "https://github.com/adfinis-sygroup/freeze/issues",
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Topic :: Software Development :: Libraries",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Testing",
    ]
)
