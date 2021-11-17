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

$ws = az ml workspace show --resource-group $ws_info.resource_group --name $ws_info.workspace_name | ConvertFrom-Json

Write-Host
Write-Host "Storage Account: $($ws.storage_account)"
Write-Host

# Install the command we need
Install-Module -Name Az -Scope CurrentUser -Repository PSGallery -Force

# Set the permissions
Write-Host 
Write-Host $env:servicePrincipalId
New-AzRoleAssignment -ObjectID $env:servicePrincipalId -RoleDefinitionName "Storage Blob Data Reader" -Scope $ws.storage_account