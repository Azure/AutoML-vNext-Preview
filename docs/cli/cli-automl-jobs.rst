Train AutoML Models (Create AutoML Job) with the CLI
====================================================

A Job is a resource that specifies all aspects of a computation job. It aggregates 3 things:

1. What to run
2. How to run it
3. Where to run it

A user can execute a job via the CLI by executing an `az ml job create` command. 

Create your first AutoML job with the CLI
-----------------------------------------

The below example uses the command job using a specific .YAML configuration specially made for AutoML jobs. 
The .YAML config below will train multiple models until it finds the best model based on the configuration settings (.YAML config file) provided to AutoML.

``Example .YAML: /examples/cli/classification/01-portoseguro-classif-job-single-dataset.yaml``

.. code-block:: yaml

   type: automl_job
   name: 01-portoseguro-cli-classif-job-single-dataset-1
   experiment_name: Portoseguro-Classification-CLI-Tests
   compute:
     target: azureml:cpu-cluster
   general:
     task: classification
     primary_metric: AUC_weighted
     enable_model_explainability: true
   limits:
     job_timeout_minutes: 2400
     max_total_trials: 100
     max_concurrent_trials: 5
     enable_early_termination: true
   data:
     training:
       dataset: azureml:porto_seguro_safe_driver_single_dataset:1
       target_column_name: target
     validation:
       n_cross_validations: 5
   featurization:
     featurization_config: auto

In the above .YAML config there are three parameters/assets that you'll need to prepare in advanced:

- 1. job name: Initially it'll be as example "01-portoseguro-cli-classif-job-single-dataset-1", but every new job needs to have a different name provided/updated by you.
- 2. target compute: You need to create a cluster in AML named "cpu-cluster" or similar name and then update the .YAML config.
- 3. dataset: Such as "azureml:porto_seguro_safe_driver_single_dataset:1" - In this PRIVATE PREVIEW you need to manualy upload a dataset thorugh the AML UI, in advanced.

How to upload a dataset to AML
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order to reference the input dataset above ("azureml:porto_seguro_safe_driver_single_dataset:1"), for this PRIVATE PREVIEW only, you first need to upload the dataset into your Azure ML Workspace, then reference to it from the .YAML as done above. In next previews, you will also be able to directly provide a local path to a dataset filename (i.e. a local .csv file) and it'll be uploaded automatically to Azure ML Workspace.

For the above example, you can [download the dataset .csv file from this HTTP URL](https://automluipublicstorage.blob.core.windows.net/automl-devplat2-sample-datasets/classification/porto_seguro_safe_driver_prediction/porto_seguro_safe_driver_prediction_single_dataset.csv) and then manually upload it as an AML Dataset in your workspace with the name "porto_seguro_safe_driver_single_dataset": 

.. image :: https://user-images.githubusercontent.com/1712635/115085742-e1d97880-9ebf-11eb-9dfd-272741dcd588.png
    :alt: AML Dataset already uploaded into a Workspace

Then, the AutoML job can be executed by running the following CLI command (after setting your specific compute name, such as "cpu-cluster" in the YAML above):

.. code-block:: console

    az ml job create --file 01-portoseguro-classif-job-single-dataset.yaml

.. image :: https://user-images.githubusercontent.com/1712635/115087101-6af1af00-9ec2-11eb-9ebb-33f7302c8b4b.png
    :alt: AutoML Job creation from CLI

The above command is the simplest way you can do it, but note it will be using your "CLI AML defaults": 
   - Default Azure Subscription
   - Default Azure Resource Group
   - Default AML Workspace.

If you want to specify those "defaults" in the very same CLI command, then you can also do it like in the following command:

.. code-block:: console

    az ml job create --file 01-portoseguro-classif-job-single-dataset.yaml --workspace-name <your_workspace_name> --resource-group <your_resource_group_name> --subscription <XXXXXXXX-YOUR-SUBSCRIPTION-ID-XXXXXXXXXXX>

You can also specify the Job's name as a CLI parameter so it'll override any job name specified in the .YAML config file, so you don't need to change the .YAML every time you create another run with the same .YAML (Since each Job's name need to be unique and cannot be repeated):

.. code-block:: console

    az ml job create --file 01-portoseguro-classif-job-single-dataset.yaml --name <my-specific-job-name-02>

Once the AutoML Job is created from the CLI, you can navigate to the Azure ML Workspace and check how the AutoML job is running.

.. image :: https://user-images.githubusercontent.com/1712635/115088200-8362c900-9ec4-11eb-986d-4aa7262125bb.png
    :alt: Checking out the AutoML Job/Run in AML Studio

If you don't know where to find it in the AML UI, you can simply type the following and it'll open a browser and navigate to the specific AutoML job because of the parameter ``--web``:

.. code-block:: bash

    az ml job show --name 01-portoseguro-cli-classif-job-single-dataset-1 --web
    


Useful az commands
~~~~~~~~~~~~~~~~~~

Login from CLI:

``az login --tenant <your_tenant_name_such_us_microsoft.onmicrosoft.com>``

List account's subscriptions with access:

``az account list --output table``

Show current selected by default subscription:

``az account show --output table``

Set by default subscription:

``az account set -s <XXXXXXXX-YOUR-SUBSCRIPTION-ID-XXXXXXXXXXX>``

Check defaults (resoruce group, location/region and workspace):

``az configure``

Set by default Resource Group:

``az configure --defaults group=<your_resource_group_name> location=<your_azure_region>``

Set by default AML Workspace:

``az configure --defaults workspace=<your_workspace_name>``


Understanding the AutoML Job specification
-----------------------------------------

The following is the AutoMLJob specification YAML file for CLI version 0.0.65:

https://github.com/Azure/automl-devplat2-preview/blob/main/schemas/0.0.65/AutoMLCommon.yaml

In reality, "AutoMLCommon.yaml" is the core/shared parameters, and the AutoMLJob specification YAML file is the following file named "AutoMLJob.yaml" which "derives" from the above:

https://github.com/Azure/automl-devplat2-preview/blob/main/schemas/0.0.65/AutoMLJob.yaml

But most AutoML settings are in "AutoMLCommon.yaml" since "AutoMLJob.yaml" only add the 'compute' parameter.
The reson for having "AutoMLCommon.yaml" as shared parameters file is because there's another derived schema named "AutoMLComponent" which will be used for integration into Azure ML Pipelines. 
        

Other AutoML training examples
------------------------------

- Classification task with train/validation split by size/%

.. code-block:: bash

    az ml job create --file examples/TBD ******************

- Classification task with specific train AML dataset and validation AML dataset

.. code-block:: bash

    az ml job create --file examples/TBD ******************
    
- Classification task allowing only certain algorithms (whitelisting algos)

.. code-block:: bash

    az ml job create --file examples/TBD ******************

Monitor a job
-------------

To show the details for a job, run:

.. code-block:: bash

    az ml job show --name <job name>
    
Add the ``--web`` option to open the job's run details in the Studio UI in a web browser:

.. code-block:: bash

    az ml job show --name <job name> --web
    
To stream the job's logs to the console, run:

.. code-block:: bash

    az ml job stream --name <job name>

Download job files
------------------

To download all the job-related files (including system logs), run:

.. code-block:: bash

    az ml job download --name <job name>

The above example will download the job files to the current directory by default. To specify a download location, provide the ``--download-path`` argument.

During training, the folder ``./outputs`` receives special treatment from Azure ML. When you write files to the ``./outputs`` folder from your training script, the files will get automatically uploaded to your job's run history, so that you have access to them once your run is finished. You can also download those artifacts via ``az ml job download`` by including the ``--outputs`` flag:

.. code-block:: bash

    az ml job download --name <job name> --outputs
