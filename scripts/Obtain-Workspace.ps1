$baseName="amlisdkv2"
$location="WestUS"
$createdTag="createdAt"
$workspaceYAML="workspace.yaml"

function Get-ExistingWorkspaces
{
    # Would be nice to do this server-side
    $all_workspaces = az ml workspace list | ConvertFrom-Json
    return Where-Object {$_.friendly_name -contains $baseName}
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
    $ws_data['tags'] = @{ $createdTag="$epoch_secs"}
    $ws_data['name']=$ws_name

    ConvertTo-Yaml $ws_data | Out-File -FilePath $workspaceYAML -Encoding ascii

    az group create --location $location --name $rg_name --tags $createdTag=$epoch_secs
    az ml workspace create --resource-group $rg_name --file $workspaceYAML
    az configure --defaults group=$rg_name workspace=$ws_name
}

$epoch_secs = Get-EpochSecs

Create-EpochWorkspace -epoch_secs $epoch_secs


