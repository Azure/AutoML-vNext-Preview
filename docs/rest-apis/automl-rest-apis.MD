# Getting Started: Create/Get an AutoMLJob using REST APIs

Follow the next steps to get started with AutoML by using the REST APIs:

1. **Create an Machine Learning Workspace** from here: https://ms.portal.azure.com/#create/Microsoft.MachineLearningServices (This is one time thing, if you need postman request for this as well, check out this complementary info on other [AML REST APIs](docs/rest-apis/aml-rest-apis.MD)
2. **Go to your Machine Learning Workspace** from https://ml.azure.com
3. **Create/Upload a Tabular Dataset** for train and validation data using the UI by following this link - https://docs.microsoft.com/en-us/azure/machine-learning/how-to-create-register-datasets#create-a-tabulardataset
    a.	Use regression_machinedata_train.csv and regression_machinedata_valid.csv from [this folder with dataset files](/datasets/regression/regression_machinedata_sample), for train/validation data.
4. **Create a compute cluster** to use for your training job in your workspace, select the appropriate configuration for virtual machine size, for testing purposes STANDARD_DS3_V2 should suffice, and you can have for instance 4 nodes in cluster.
    ![image](https://user-images.githubusercontent.com/1712635/115306947-65dc6c00-a11d-11eb-8455-867c85e5e82c.png)
5.	**Use Postman webclient** or desktop client and import this collection: https://www.getpostman.com/collections/cd0c5a9f5836b675918c
    ![image](https://user-images.githubusercontent.com/1712635/115307303-db483c80-a11d-11eb-98a3-758e6518ab64.png)
6. **Import the file “EnvironmentVariables.postman_globals”** file from the same folder where this .MD document is placed. Note that you might need to either clone this repo or download the files needed.
    ![image](https://user-images.githubusercontent.com/1712635/115307786-95d83f00-a11e-11eb-825d-60e65186264d.png)
7. **Ensure you edit the global values** and populate respective values in each field appropriately including the values for subscriptionId, resourceGroup, workspaceName, compute, region etc. related to your environment.
    ![image](https://user-images.githubusercontent.com/1712635/115308156-244cc080-a11f-11eb-893a-429ceead759f.png)
8.	Now you need to have Azure CLI installed in order to get the auth token.- [Install the Azure CLI | Microsoft Docs](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
9.	Once you have installed Azure CLI, you can use command like this to get the auth token:

    `az account get-access-token`
    
    ![image](https://user-images.githubusercontent.com/1712635/115308735-09c71700-a120-11eb-9153-db47406ffa07.png)
    
10.	**Get this token and set it in “authToken” global variable.**
11.	Now **update the dataset name in the Body of Create AutoML job** (Use the same name that you used while creating the tabular dataset in step 3 above).
     ![image](https://user-images.githubusercontent.com/1712635/115308900-59a5de00-a120-11eb-847f-93a6502959ed.png)
13.	12.	Now you can click on Create AutoML job and hit send.
