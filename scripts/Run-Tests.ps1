# Enable all the commands
$Env:AZURE_ML_CLI_PRIVATE_FEATURES_ENABLED=$true

python -m pytest ./tests/ -o junit_family=xunit2 --junitxml=junit.xml