# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import setuptools

version = "0.0.1"
name = "azure_ml_rai"

long_description = "Figuring out client side operations for RAI components"

install_requires = ["azure-ml", "azureml-core", "azureml-mlflow"]

setuptools.setup(
    name=name,  # noqa: F821
    version=version,  # noqa: F821
    author="Richard Edgar",
    author_email="@microsoft.com",
    description="Package for downloading RAI component output",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    package_data={},
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=install_requires,
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
)
