# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

param (
    [ValidateSet("LatestRelease", "LatestDev")]        
    [string]
    $sdkVersionSelect
)

# Instructions from:
# https://docs.microsoft.com/en-us/azure/machine-learning/how-to-configure-cli

# Remove old extensions
az extension remove -n azure-cli-ml
az extension remove -n ml

# Add the new one
if( $sdkVersionSelect -eq "LatestRelease")
{
    az extension add -n ml -y
}
else
{
    az extension add --source https://azuremlsdktestpypi.blob.core.windows.net/wheels/sdk-cli-v2/ml-latest-py3-none-any.whl --yes
}

# Upgrade to latest version
az extension update -n ml

# Enable all the commands
$Env:AZURE_ML_CLI_PRIVATE_FEATURES_ENABLED=$true

# Check the commands
az ml -h
