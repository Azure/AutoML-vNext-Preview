# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ml import MLClient
from azureml.core import Workspace


def _get_v1_workspace_client(ml_client: MLClient) -> Workspace:
    subscription = ml_client._workspace_scope.subscription_id
    rg_name = ml_client._workspace_scope.resource_group_name
    ws_name = ml_client._workspace_scope.workspace_name

    v1_workspace = Workspace(subscription, rg_name, ws_name, auth=None)

    return v1_workspace
