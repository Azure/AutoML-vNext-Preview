# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

param (
    [ValidateSet("LatestRelease", "LatestDev")]        
    [string]
    $sdkVersionSelect
)

# Add the new one
Write-Host "Now installing $sdkVersionSelect"
if( $sdkVersionSelect -eq "LatestRelease")
{
    pip install -r requirements-dev-releasepackage.txt
}
else
{
    pip install -r requirements-dev.txt
}