$baseName="amlisdkv2"
$location="WestUS"
$createdTag="createdAt"
$ownerTeamTagKey="owningTeam"
$ownerTeamTagValue="AML Intelligence"
$purposeTagKey="workspacePurpose"
$purposeTagValue="Automated Tests for DPv2"
$workspaceYAML="workspace.yaml"

function Get-RecentWorkspaces(
    [int]$min_epoch
)
{
    Write-Host "Minimum Epoch: $min_epoch"
    # Would be nice to do this server-side
    $all_workspaces = az ml workspace list | ConvertFrom-Json


    $filtered_workspaces = $all_workspaces | Where-Object {$_.name.contains($baseName) -and $_.tags.$createdTag -gt $min_epoch}

    return $filtered_workspaces
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

    $ws_data = @{}
    $ws_data['name']=$ws_name
    $ws_data['tags'] = @{}
    $ws_data['tags'][$createdTag]="$epoch_secs"
    $ws_data['tags'][$ownerTeamTagKey]=$ownerTeamTagValue
    $ws_data['tags'][$purposeTagKey]=$purposeTagValue

    ConvertTo-Yaml $ws_data | Out-File -FilePath $workspaceYAML -Encoding ascii

    az group create --location $location --name $rg_name --tags $createdTag=$epoch_secs
    az ml workspace create --resource-group $rg_name --file $workspaceYAML
    az configure --defaults group=$rg_name workspace=$ws_name
}

# Install-Module powershell-yaml -Scope CurrentUser

$epoch_secs = Get-EpochSecs

# Create-EpochWorkspace -epoch_secs $epoch_secs

$ws_list = Get-RecentWorkspaces($epoch_secs-24*3600)
Write-Host $ws_list

