# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# Uses a config.json to get the workspace information

Write-Host
Write-Host "Reading config.json"
Write-Host

$ws_info = Get-Content -Path "config.json" | ConvertFrom-Json

Write-Host "Resource Group: $($ws_info.resource_group)"
Write-Host "Workspace: $($ws_info.workspace_name)"

Write-Host
Write-Host "Creating Compute"
Write-Host

az ml compute create --resource-group $ws_info.resource_group --workspace $ws_info.workspace_name --file scripts/compute_config.yaml