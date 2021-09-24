$baseName="amlisdkv2"

function Get-ExistingWorkspaces
{
    # Would be nice to do this server-side
    $all_workspaces = az ml workspace list | ConvertFrom-Json
    return Where-Object {$_.friendly_name -contains $baseName}
}

Write-Host Get-ExistingWorkspaces()