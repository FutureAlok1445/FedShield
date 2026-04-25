from setuptools import setup, find_packages

setup(
    name="fedshield-sdk",
    version="0.1.0",
    description="FedShield bank-side Python SDK",
    packages=find_packages(where="."),
    package_dir={"": "."},
    install_requires=[
        "numpy==2.4.4",
        "requests>=2.31.0",
        "scipy==1.17.1",
        "scikit-learn==1.8.0",
        "lightgbm>=4.0.0",
        "ipfshttpclient==0.7.0"
    ],
    python_requires=">=3.12",
)
