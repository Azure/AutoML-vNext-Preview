Train AutoML Models (Create AutoML Job)
=======================================

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

In order to reference the input dataset above ("azureml:porto_seguro_safe_driver_single_dataset:1"), for this PRIVATE PREVIEW only, you first need to upload the dataset into your Azure ML Workspace, then reference to it from the .YAML as done above. In next previews, you will also be able to directly provide a local path to a dataset filename (i.e. a local .csv file) and it'll be uploaded automatically to Azure ML Workspace.

For the above example, you can download the dataset .csv file from this HTTP URL and then manually upload it as an AML Dataset in your workspace with the name "porto_seguro_safe_driver_single_dataset": 

https://azmlworkshopdata.blob.core.windows.net/safedriverdata/porto_seguro_safe_driver_prediction_train.csv


This AutoML job can be executed by running the following CLI command (after setting your compute name in the YAML above):

.. code-block:: console

    az ml job create --file 01-portoseguro-classif-job-single-dataset.yaml







XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

Understanding a job specification
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following is a fully fleshed out job specification YAML file:

.. literalinclude:: ../../examples/iris/iris_job.yml
   :language: yaml

        
``code / local_path`` is the path to your code directory relative to where the YAML file lives. 

- This directory is uploaded as a snapshot to Azure ML and mounted to your job for execution. 
- All of the files from 'local_path' are uploaded as a snapshot before the job is created and can be viewed in the Snapshot tab of the run from Studio UI.
     
``command`` defines the command that gets run on the remote compute. 

- ``command`` executes from the root of the code directory defined above.
- This is a typical command, for example: ``python train.py`` or ``Rscript train.R`` and can include as many arguments as you desire.

``environment`` defines the environment you want to run your job in.

- ``azureml:`` is a special moniker used to refer to an existing entity within the workspace. 
- ``azureml:AzureML-Minimal:1`` specifies version 1 of an environment called AzureML-Minimal (one of the Azure ML curated environments) that exists in the current workspace. 
- You can also specify an environment definition inline using the syntax in the hello world example above.

``compute`` defines where you want to run your job and compute-specific information

- ``target`` indicates the compute you want to run your job against. For example, ``azureml:goazurego`` refers to a compute cluster called 'goazurego' in the current workspace.
- You can override the compute (or any field in the YAML file) by using the ``--set`` parameter for ``az ml job create``, e.g. ``--set compute.target=azureml:cpu-cluster``

``inputs`` defines data you want mounted or downloaded for your job.
    
- ``data`` is either the 1) reference an existing data asset in your workspace you want to use (using the ``azureml:<name>:<version>`` notation) or 2) an inline definition of the data
- ``mode`` indicates how you want the data made available on the compute for the job. 'mount' and 'download' are the two supported options.

``name`` is the (optional) user-defined identifier of the job's run, which needs to be *unique*. If you do not provide a name a GUID name will be generated for you. To find the generated GUID, you can either look at the job object returned by ``az ml job create`` in the ``name`` property, or you can look under the "Experiments" tab of the Studio UI. The job name corresponds to the "Run ID" in the UI.

``experiment_name`` is the (optional) experiment name you want to track your job runs under. Your runs will be tagged with this experiment name, and in the Studio UI the runs will be organized under that experiment in the "Experiments" tab. If this field is not provided, your runs will be tagged with the experiment name "Default". We recommend that you provide a custom experiment_name for each of your jobs to more easily manage your jobs' run details.

Real training examples
~~~~~~~~~~~~~~~~~~~~~~

Here's an example that runs  **Python code.**

.. code-block:: bash

    az ml environment create --file examples/train/tensorflow/tf_env.yml
    az ml job create --file examples/train/tensorflow/mnist/tf_mnist_job.yml


.. literalinclude:: ../../examples/train/tensorflow/mnist/tf_mnist_job.yml
   :language: yaml

Here's an example that runs **R code:**

.. code-block:: bash

    az ml job create --file examples/train/r/accident-prediction/r_job.yml

.. literalinclude:: ../../examples/train/r/accident-prediction/r_job.yml
   :language: yaml


Train an XGBoost model
-----------------------

Next, let's train an xgboost model on an IRIS dataset.

Let's navigate to the examples/iris directory in the repository and see what we should do next.

.. code-block:: bash

    cd ./examples/iris/
    
Define your environment
~~~~~~~~~~~~~~~~~~~~~~~~

First we are going to define the xgboost environment we want to use for the job:

.. literalinclude:: ../../examples/iris/xgboost_env.yml
   :language: yaml

Now create the environment:

.. code-block:: bash

    az ml environment create --file xgboost_env.yml
    
    
Create your data asset
~~~~~~~~~~~~~~~~~~~~~~

Next create a data asset for your training data:

.. literalinclude:: ../../examples/iris/iris_data.yml
   :language: yaml

.. code-block:: bash

    az ml data create --file iris_data.yml


The above example will upload the data from the local folder `.data/` to the workspace's default Blob storage (`workspaceblobstore`). It creates a data asset under the name `irisdata` in your workspace.

Create your xgboost training job
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../examples/iris/iris_job.yml
   :language: yaml
   
To submit the job:

.. code-block:: bash

    az ml job create --file iris_job.yml


Defining environment and data inline
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The above example for configuring the job assumes that you have existing registered assets for environment and data in your workspace that you are referencing for the job.

However, you may not need to or want to explicitly version and track the environment or data for your job. In that case, you can simply define those specifications inline within your job configuration YAML file, e.g. iris_job_inline.yml:

.. code-block:: yaml

    experiment_name: xgboost-iris
    code: 
        local_path: train
    command: >-
        python train.py --data {inputs.training_data} 
    environment:
        conda_file: file:xgboost_conda.yml
        docker: 
            image: mcr.microsoft.com/azureml/openmpi3.1.2-ubuntu18.04
    compute:
        target: azureml:goazurego
    inputs:
        training_data:
            data: azureml:irisdata:1
            mode: mount
            
Submit the job:

.. code-block:: bash

    az ml job create --file iris_job_inline.yml

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
