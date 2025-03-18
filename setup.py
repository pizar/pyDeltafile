from setuptools import setup, find_packages

setup(
    name='pyDeltafile',
    version='1.1.0',
    packages=find_packages(),
    install_requires=[
        'pandas',
    ],
)