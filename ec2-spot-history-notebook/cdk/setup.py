import setuptools


with open("../README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="spot-historic-price-notebook",
    version="1.0.0",

    description="CDK Project to deploy spot-historic-price-notebook",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="Carlos Manzanedo Rueda <ruecarlo@amazon.com>",

    package_dir={"": "spot_historic_notebook"},
    packages=setuptools.find_packages(where="spot_historic_notebook"),

    install_requires=[
        "aws-cdk.core",
        "aws-cdk.aws-iam",
        "aws-cdk.aws-sagemaker",
        "boto3"
    ],

    python_requires=">=3.6",

    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",

        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",

        "Typing :: Typed",
    ],
)
