from setuptools import setup, find_packages

setup(
    name="rdflib-simulator",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'rdflib>=6.3.2',
        'SPARQLWrapper>=2.0.0',
        'pandas>=2.0.0',
        'networkx>=3.0',
        'matplotlib>=3.7.0',
        'tqdm>=4.65.0',
        'pytest>=7.3.1'
    ]
) 