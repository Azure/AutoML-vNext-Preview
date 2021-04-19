# Getting Started: Create/Get an AutoMLJob using REST APIs

Follow the next steps to get started with AutoML by using the REST APIs:

1. **Create an Machine Learning Workspace** from here: https://ms.portal.azure.com/#create/Microsoft.MachineLearningServices (This is one time thing, if you need postman request for this as well, check out this complementary info on other [AML REST APIs](docs/rest-apis/aml-rest-apis.MD)
2. **Go to your Machine Learning Workspace** from https://ml.azure.com
3. **Create/Upload a Tabular Dataset** for train and validation data using the UI by following this link - https://docs.microsoft.com/en-us/azure/machine-learning/how-to-create-register-datasets#create-a-tabulardataset
    a.	Use regression_machinedata_train.csv and regression_machinedata_valid.csv from [this folder with dataset files](/datasets/regression/regression_machinedata_sample), for train/validation data.
4. **Create a compute cluster** to use for your training job in your workspace, select the appropriate configuration for virtual machine size, for testing purposes STANDARD_DS3_V2 should suffice, and you can have for instance 4 nodes in cluster.
    ![image](https://user-images.githubusercontent.com/1712635/115306947-65dc6c00-a11d-11eb-8455-867c85e5e82c.png)
