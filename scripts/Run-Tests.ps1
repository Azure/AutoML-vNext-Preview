# Enable all the commands
$Env:AZURE_ML_CLI_PRIVATE_FEATURES_ENABLED=$true

python -m pytest tests --timeout=1200 -o junit_family=xunit2 --junitxml=junit.xml