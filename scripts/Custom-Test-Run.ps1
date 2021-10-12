# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

function Read-JsonConfig(
    [string]$json_filepath
)
{
    Write-Host "Reading $json_filepath"
    $config = Get-Content $json_filepath | ConvertFrom-Json
    return $config
}

# Enable all the commands
$Env:AZURE_ML_CLI_PRIVATE_FEATURES_ENABLED=$true

# Get the workspace configuration
$ws = Read-JsonConfig('config.json')

az ml job create --file ./pipeline_analyse.processed.yaml --resource-group $ws.resource_group --workspace $ws.workspace_name