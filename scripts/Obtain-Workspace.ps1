$baseName="amlisdkv2"
$location="WestUS"
$createdTag="createdAt"
$ownerTeamTagKey="owningTeam"
$ownerTeamTagValue="AML Intelligence"
$purposeTagKey="workspacePurpose"
$purposeTagValue="Automated Tests for DPv2"
$workspaceYAML="workspace.yaml"
$window_seconds = 1*1800

function Get-RecentResourceGroups(
    [int]$min_epoch
)
{
    Write-Host "Searching for recent resource groups"
    Write-Host "Minimum Epoch: $min_epoch"
    # Would be nice to do this server-side
    $all_groups = az group list | ConvertFrom-Json


    $filtered_groups = $all_groups.Where({$_.name.contains($baseName) -and $_.tags.$createdTag -gt $min_epoch})

    return $filtered_groups
}


function Get-OldResourceGroups(
    [int]$max_epoch
)
{
    Write-Host "Searching for older resource groups"
    Write-Host "Maximum Epoch: $max_epoch"
    # Would be nice to do this server-side
    $all_groups = az group list | ConvertFrom-Json


    $filtered_groups = $all_groups.Where({$_.name.contains($baseName) -and $_.tags.$createdTag -lt $max_epoch})

    return $filtered_groups
}

function Get-WorkspaceFromResourceGroup(
    [string]$resource_group_name
)
{
    Write-Host "Checking resource group $resource_group_name"
    $workspaces = az ml workspace list --resource-group $resource_group_name | ConvertFrom-Json

    $filtered_workspaces = $workspaces.Where({$_.name.contains($baseName)})

    if($filtered_workspaces.count -gt 0)
    {
        $workspace = $workspaces[0]
    } else {
        throw "Resource Group did not contain workspace with name starting with $baseName"
    }

    return $workspace
}

function Get-EpochSecs
{
    # Get time to nearest second
    $epoch_time =  Get-Date (Get-Date).ToUniversalTime() -UFormat %s
    $epoch_secs = [Math]::Truncate($epoch_time)
    return $epoch_secs
}

function Create-EpochWorkspace(
    [int]$epoch_secs
)
{
    $rg_name = "$basename-rg-$epoch_secs"
    $ws_name = "$basename$epoch_secs"

    Write-Host "Creating workspace $ws_name in resource group $rg_name"

    $ws_data = @{}
    $ws_data['name']=$ws_name
    $ws_data['tags'] = @{}
    $ws_data['tags'][$createdTag]="$epoch_secs"
    $ws_data['tags'][$ownerTeamTagKey]=$ownerTeamTagValue
    $ws_data['tags'][$purposeTagKey]=$purposeTagValue

    ConvertTo-Yaml $ws_data | Out-File -FilePath $workspaceYAML -Encoding ascii

    az group create --location $location --name $rg_name --tags $createdTag=$epoch_secs
    $ws = az ml workspace create --resource-group $rg_name --file $workspaceYAML | ConvertFrom-Json
    return $ws
}

# Install-Module powershell-yaml -Scope CurrentUser

$epoch_secs = Get-EpochSecs

$rg_list = Get-RecentResourceGroups($epoch_secs-$window_seconds)
if($rg_list.count -gt 0)
{
    Write-Host "Found $($rg_list.count) suitable resource groups"
    $target_rg = $rg_list[0].name

    $workspace = Get-WorkspaceFromResourceGroup($target_rg)
} else {
    Write-Host "No recent workspace"
    $workspace = Create-EpochWorkspace($epoch_secs)
}

Write-Host $workspace

Write-Host "Checking for old resource groups"
$old_rg_list =Get-OldResourceGroups($epoch_secs-2*$window_seconds)
if( $old_rg_list.count -gt 0)
{
    Write-Host "Found $($old_rg_list.count) resource groups to clean up"
    foreach( $rg in $old_rg_list)
    {
        Write-Host "Cleaning up $($rg.name)"
        az group delete --name $rg.name --yes
    }
} else {
    Write-Host "No old resource groups found"
}