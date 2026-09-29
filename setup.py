from setuptools import setup, find_packages

def parse_requirements(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="naviq-maritime-ml",
    version="1.0.0",
    description="NAVIQ Maritime - Global Ocean Freight Intelligence & Master Super ML",
    author="NAVIQ Data Science Team",
    packages=find_packages(),
    include_package_data=True,
    install_requires=parse_requirements("requirements.txt"),
    python_requires=">=3.8",
)
