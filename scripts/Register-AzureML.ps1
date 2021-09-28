param (
        [string]$path_to_registration_json
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
        python $data_info.script

        foreach($data_yaml in $data_info.data_yamls)
        {
            $full_path = Join-Path -Path $base_directory -ChildPath $data_yaml
            $temp_file = Join-Path -Path $base_directory -ChildPath "$data_yaml.updated"

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

# Enable all the commands
$Env:AZURE_ML_CLI_PRIVATE_FEATURES_ENABLED=$true

# Read in the configuration files
$ws = Read-JsonConfig('config.json')
$component_config = Read-JsonConfig('component_config.json')
$reg_config = Read-JsonConfig($path_to_registration_json)

# Figure out the target directory
$component_directory = [System.IO.Path]::GetDirectoryName($path_to_registration_json)
Write-Host "Directory containing components: $component_directory"
Write-Host

# Register the environments
foreach ($env_file in $reg_config.environments) {
    Write-Host "Registering environment $env_file"
    Register-Environment -workspace_config $ws -component_config $component_config  -base_directory $component_directory -environment_file $env_file
    Write-Host
}
Write-Host
Write-Host "Environment registration complete"

# Register the components
foreach ($component_file in $reg_config.components){
    Write-Host "Registering component $component_file"
    Register-Component -workspace_config $ws -component_config $component_config  -base_directory $component_directory -component_file $component_file
    Write-Host
}
Write-Host
Write-Host "Component registration complete"

# Register the datasets
foreach ($data_item in $reg_config.data){
    Register-Dataset -workspace_config $ws -component_config $component_config  -base_directory $component_directory -data_info $data_item
}