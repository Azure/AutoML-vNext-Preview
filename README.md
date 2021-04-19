# Private Preview: AutoML in Azure ML 2.0 developer experience (DevPlat 2.0)

> Welcome to the PRIVATE PREVIEW of **Azure Machine Learning Automated ML for the Azure ML 2.0 developer experience (DevPlat 2.0)**
> AutoML in the 2.0 developer platform will provide first class API/CLI/SDK support for automated model training.
> This is an early PREVIEW, still not announced and not supported publicly so it's defined as PRIVATE from that point of view, although anyone can access to it.

Automated Machine Learning, also referred to as Automated ML or AutoML, is the process of automating the time consuming, iterative tasks of machine learning model development. It allows data scientists, analysts, and developers to quickly and easily build ML models with high scale, efficiency, and productivity all while sustaining model quality.

Apply automated ML when you want Azure Machine Learning to train and tune a model for you using the target metric you specify. Automated ML democratizes the machine learning model development process.

Azure AutoML CLI currently supports these three ML tasks:

- Classification (Binary classification and multi-class classification)
- Regression
- Time Series Forecasting 

## Scope for AutoML in 2.0 versions

Azure AutoML in DevPlat 2.0 provides the following main feature areas:

- **CLI (Common-Line Interface)** support for AutoML
- **REST APIs** for AutoML
- **AML Python SDK 2.0** for AutoML (will be available in next previews)

## Prerequisites

- An Azure subscription. If you don't have an Azure subscription, [create a free account](https://aka.ms/AMLFree) before you begin.


# CLI support for AutoML

## Install Azure CLI and setup the Azure ML extension:

Follow this quick start doc for the setup:

- [How to install the CLI and setup the Azure ML extension](/docs/cli/cli-installation.rst)

AutoML job/run creationg with the CLI is also based on .YAML config files that you as a user can create by specifying the multiple AutoML settings in that config file.

## Train AutoML Models (Create AutoML Job) with the CLI

In order to learn how to use the CLI to create AutoML jobs, follow this quick start doc:

- [Train AutoML Models (Create AutoML Job) with the CLI](/docs/cli/cli-automl-jobs.rst)



# REST API support for AutoML

The Azure Machine Learning REST APIs allow you to develop client applications developed on any platform and language that use REST calls to work with the service. 
These APIs are in v2.0 the same REST APIs consumed by the CLI and Python SDK clients.

- [Getting Started: Create and Get an AutoMLJob using REST APIs](/docs/rest-apis/automl-rest-apis.MD)

- [Other Azure ML REST APIS to complement your end-to-end scenarios](/docs/rest-apis/aml-rest-apis.MD)


# Python SDK 2.0 support for AutoML

(TBD) - Will be available in next previews, not in the 1st Private Preview (April/May 2021) for AutomML but later.


## Contributing

We welcome contributions and suggestions! 

### Issues and feedback

All forms of feedback are welcome through this repo's issues: 
https://github.com/Azure/automl-devplat2-preview/issues

Please see the [contributing guidelines](CONTRIBUTING.md) for further details.

## Code of Conduct

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). Please see the [code of conduct](CODE_OF_CONDUCT.md) for details.
