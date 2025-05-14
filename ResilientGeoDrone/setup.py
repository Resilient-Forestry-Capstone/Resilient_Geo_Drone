from setuptools import setup, find_packages

setup(
    name="resilient-geodrone",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        line.strip()
        for line in open(r"C:\Users\bensp\OneDrive\Desktop\Code Box Two\Python\GeoDrone\ResilientGeoDrone\ResilientGeoDrone\ResilientGeoDrone\requirements.txt").readlines()
        if not line.startswith("#")
    ],
    entry_points={
        "console_scripts": [
            "drone-pipeline=src.main:main",
        ],
    },
    python_requires='>=3.9',
)