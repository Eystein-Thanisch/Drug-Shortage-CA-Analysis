from setuptools import setup, find_packages

VERSION = '0.0.1' 
DESCRIPTION = 'Helper functions for working with the DSCA data.'
LONG_DESCRIPTION = 'Helper functions for working with the DSCA data.'

setup(
        name="drug_shortage_ca_helpers", 
        version=VERSION,
        author="Eystein Thanisch",
        author_email="epthanisch@gmail.com",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=["requests"],
        keywords=['python', 'first package'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)