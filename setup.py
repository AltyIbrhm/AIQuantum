from setuptools import setup, find_packages

setup(
    name="AIQuantum",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "pytest>=7.4.0",
        "PyYAML>=6.0.1",
        "python-dotenv>=1.0.0",
        "scikit-learn>=1.3.0",
        "ta>=0.10.2",
        "pandas-ta>=0.3.14b",
        "rich>=13.7.0",
        "loguru>=0.7.2",
        "pytest-cov>=4.1.0",
        "mypy>=1.7.0",
        "types-python-dateutil>=2.8.19.14",
        "requests>=2.26.0",
        "aiohttp>=3.8.0",
    ],
    python_requires=">=3.8",
) 