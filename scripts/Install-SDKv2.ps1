# Instructions from:
# https://docs.microsoft.com/en-us/azure/machine-learning/how-to-configure-cli

# Remove old extensions
az extension remove -n azure-cli-ml
az extension remove -n ml

# Add the new one
az extension add -n ml -y

# Upgrade to latest version
az extension update -n ml

# Check the commands
az ml -h
