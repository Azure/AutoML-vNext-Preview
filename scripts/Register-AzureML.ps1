# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# Registers environments, components and datasets
#
# The AzureML objects to be registered are specified in a
# JSON file passed on the command line
#
# {
#     "environments": [env_file.yaml],
#     "components": [component_file.yaml],
#     "data": [
#         {
#             "script" : "data_fetch.py",
#             "data_yamls": [
#                 "data_1.yaml",
#                 "data_2.yaml"
#             ]
#         }
#     ]
# }
#
# The 'environments' and 'components' keys are for lists of filenames
# to be registered as each. Before registration, these will have the
# VERSION_REPLACEMENT_STRING replaced by the value specified in the
# top level component_config.json (created by Obtain-Workspace.ps1)
#
# Datasets are slightly more involved. First, the specified script is run in the
# same directory as the JSON file from the command line.
# Then the YAMLs are processed for VERSION_REPLACEMENT_STRING, and
# registered as datasets

param (
        [string]$initial_directory
)

function Read-JsonConfig(
    [string]$json_filepath
)
{
    Write-Host "Reading $json_filepath"
    $config = Get-Content $json_filepath | ConvertFrom-Json
    return $config
}

function Replace-StringInFile(
    [string]$input_file,
    [string]$output_file,
    [string]$target_string,
    [string]$replace_string
)
{
    $text = Get-Content $input_file
    $updated_text = $text -replace $target_string, $replace_string
    $updated_text | Out-File -FilePath $output_file -Encoding ascii
}

function Register-Environment(
    $workspace_config,
    $component_config,
    [string]$base_directory,
    [string]$environment_file
)
{
    $full_path = Join-Path -Path $base_directory -ChildPath $environment_file
    $temp_file = Join-Path -Path $base_directory -ChildPath "$environment_file.updated"

    Write-Host "Updating version in $environment_file"
    Replace-StringInFile -input_file $full_path -output_file $temp_file -target_string 'VERSION_REPLACEMENT_STRING' -replace_string $component_config.version
    
    Write-Host "Registering $temp_file"
    az ml environment create --resource-group $workspace_config.resource_group --workspace $workspace_config.workspace_name --file $temp_file
}

function Register-Component(
    $workspace_config,
    $component_config,
    [string]$base_directory,
    [string]$component_file
)
{
    $full_path = Join-Path -Path $base_directory -ChildPath $component_file
    $temp_file = Join-Path -Path $base_directory -ChildPath "$component_file.updated"

    Write-Host "Updating version in $component_file"
    Replace-StringInFile -input_file $full_path -output_file $temp_file -target_string 'VERSION_REPLACEMENT_STRING' -replace_string $component_config.version

    Write-Host "Registering $temp_file"
    az ml component create --resource-group $workspace_config.resource_group --workspace $workspace_config.workspace_name --file $temp_file
}

function Register-Dataset(
    $workspace_config,
    $component_config,
    [string]$base_directory,
    $data_info
)
{
    Push-Location $base_directory
    try {
        Write-Host "Running script $($data_info.script)"
        python $data_info.script
        Write-Host "Script completed"

        foreach($data_yaml in $data_info.data_yamls)
        {
            $full_path = $data_yaml
            $temp_file = "$data_yaml.updated"

            Write-Host "Updating version in $data_yaml"
            Replace-StringInFile -input_file $full_path -output_file $temp_file -target_string 'VERSION_REPLACEMENT_STRING' -replace_string $component_config.version

            Write-Host "Registering $temp_file"
            az ml data create --resource-group $workspace_config.resource_group --workspace $workspace_config.workspace_name --file $temp_file
        }
    }
    finally {
        Pop-Location
    }
}


function Process-Directory(
    $workspace_config,
    $component_config,
    [string]$base_directory
)
{
    Write-Host "Processing directory: $base_directory"
    $reg_config_file = [System.IO.Path]::Join($base_directory, 'registration_config.json')
    $reg_config = Read-JsonConfig($reg_config_file)

    # Register the environments
    foreach ($env_file in $reg_config.environments) {
        Write-Host "Registering environment $env_file"
        Register-Environment -workspace_config $workspace_config `
                            -component_config $component_config `
                            -base_directory $base_directory `
                            -environment_file $env_file
        Write-Host
    }
    Write-Host
    Write-Host "Environment registration complete"
    Write-Host

    
    # Register the components
    foreach ($component_file in $reg_config.components){
        Write-Host "Registering component $component_file"
        Register-Component -workspace_config $ws `
                        -component_config $component_config `
                        -base_directory $component_directory `
                        -component_file $component_file
        Write-Host
    }
    Write-Host
    Write-Host "Component registration complete"
    Write-Host

    # Register the datasets
    foreach ($data_item in $reg_config.data){
        Register-Dataset -workspace_config $ws `
                        -component_config $component_config `
                        -base_directory $component_directory `
                        -data_info $data_item
    }
    Write-Host
    Write-Host "Dataset registration complete"
    Write-Host
}

# Enable all the commands
$Env:AZURE_ML_CLI_PRIVATE_FEATURES_ENABLED=$true

# Read in the configuration files
$ws = Read-JsonConfig('config.json')
$component_config = Read-JsonConfig('component_config.json')

Write-Host
Write-Host "Starting in directory $initial_directory"
Write-Host

Process-Directory($ws, $reg_config, $initial_directory)