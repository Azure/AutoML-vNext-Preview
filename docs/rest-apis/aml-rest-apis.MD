# Azure ML REST APIs

In addition to REST APIs for AutoML you might need to use other REST APIs for implementing an end-to-end scenario.

In v2.0 Preview, you can:

1.Create Datastore and 'file Dataset': Use this new postman collection: https://www.getpostman.com/collections/cd0c5a9f5836b675918c
 

Most AML REST APIs for v2.0 are still in development, but if you need to implement pre-requisites in order to setup your AutoML scenario, the following information with existing REST APIS (not 2.0) can help you:

1. Authentication for storage/machine learning resource 
     o	[Azure API Management REST API Authentication | Microsoft Docs](https://docs.microsoft.com/en-us/rest/api/apimanagement/apimanagementrest/azure-api-management-rest-api-authentication)
     o	[Use REST to manage ML resources - Azure Machine Learning | Microsoft Docs](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-manage-rest)
2. Create/Update workspace Workspaces - Create Or Update (Azure Machine Learning) | Microsoft Docs
   o	Create storage account: - [Create an Azure Storage account using the REST APIs | Microsoft Docs](https://docs.microsoft.com/en-us/rest/api/storagerp/storage-sample-create-account)
   o	Key vault  - [Vaults - Create Or Update (Azure Key Vault) | Microsoft Docs](https://docs.microsoft.com/en-us/rest/api/keyvault/vaults/createorupdate)
   o	Application insights – For now create it using UI with this doc - [Create a new Azure Monitor Application Insights workspace-based resource - Azure Monitor | Microsoft Docs](https://docs.microsoft.com/en-us/azure/azure-monitor/app/create-workspace-resource)
   o	Container registry - [Registries - Create (Azure Container Registry) | Microsoft Docs](https://docs.microsoft.com/en-us/rest/api/containerregistry/registries/create)
   o	Resource Group- Resource Groups - [Create Or Update (Azure Resource Management) | Microsoft Docs](https://docs.microsoft.com/en-us/rest/api/resources/resourcegroups/createorupdate)
3. Create/Update Compute  - [Machine Learning Compute - Create Or Update (Azure Machine Learning) | Microsoft Docs](https://docs.microsoft.com/en-us/rest/api/azureml/workspacesandcomputes/machinelearningcompute/createorupdate)
4. Upload new data to datasource — Blob Storage to use the same storage account - [Blob service REST API - Azure Storage | Microsoft Docs](https://docs.microsoft.com/en-us/rest/api/storageservices/blob-service-rest-api)


