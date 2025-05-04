from setuptools import setup, find_packages

setup(
    name="AIQuantum",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pytest>=7.4.0",
        "pytest-cov>=4.1.0",
    ],
    python_requires=">=3.8",
) 