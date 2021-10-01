# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# Instructions from:
# https://docs.microsoft.com/en-us/azure/machine-learning/how-to-configure-cli

# Remove old extensions
az extension remove -n azure-cli-ml
az extension remove -n ml

# Add the new one
# az extension add -n ml -y
az extension add --source https://azuremlsdktestpypi.blob.core.windows.net/wheels/sdk-cli-v2/ml-0.0.17_october_cand-py3-none-any.whl --yes

# Upgrade to latest version
az extension update -n ml

# Enable all the commands
$Env:AZURE_ML_CLI_PRIVATE_FEATURES_ENABLED=$true

# Check the commands
az ml -h

# Show the version
az version
