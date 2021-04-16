Installation of Azure ML CLI 
============================

You can install *azure.ml* on Linux, MacOS, and Windows for several interfaces.

Command Line Interface (CLI)
----------------------------

The ``az ml`` CLI provides access to AutoML actions plus many more actions for Azure ML.

Terminal
~~~~~~~~

Launch any terminal. 

.. warning::
    A cloud shell (https://shell.azure.com) is recommended for private preview to avoid conflicting installations.

Azure CLI Install
~~~~~~~~~~~~~~~~~

If you do not have the Azure CLI installed, follow the installation instructions at https://docs.microsoft.com/cli/azure/install-azure-cli.

Verify installation:

.. code-block:: console

    az version

The Azure ML extension requires CLI version **>=2.15.0**. To upgrade your CLI installation, please run the below command.
 
 
.. code-block:: console

    az upgrade

ML Extension Install
~~~~~~~~~~~~~~~~~~~~

Remove any previous extension installations:

.. code-block:: console

    az extension remove -n ml; az extension remove -n azure-cli-ml

Install the Azure CLI extension for ML:

.. tip:: 
    This will be simplified to "``az extension add -n ml``" for public preview.

.. code-block:: console

    az extension add --source https://azuremlsdktestpypi.blob.core.windows.net/wheels/sdk-cli-v2/ml-0.0.64-py3-none-any.whl --pip-extra-index-urls https://azuremlsdktestpypi.azureedge.net/sdk-cli-v2 -y


.. code-block:: console

    az ml -h

Verify installation:

.. code-block:: console

    az ml -h

You should see the following output:

.. code-block:: console

    Group
        az ml
            This command group is experimental and under development. Reference and support levels:
            https://aka.ms/CLI_refstatus
    Subgroups:
        code        : Manage Azure ML code assets.
        compute     : Manage Azure ML compute resources.
        data        : Manage Azure ML data assets.
        datastore   : Manage Azure ML datastores.
        endpoint    : Manage Azure ML endpoints.
        environment : Manage Azure ML environments.
        job         : Manage Azure ML jobs.
        model       : Manage Azure ML models.
        workspace   : Manage Azure ML workspaces.
