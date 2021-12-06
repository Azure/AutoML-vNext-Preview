# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import List, Optional

from azureml.core import Workspace, Run
from azure.ml import MLClient

from ._constants import PropertyKeyValues


def list_rai_insights(
    ml_client: MLClient,
    experiment_name: str,
    model_id: Optional[str] = None
) -> List[str]:
    # Return the Run ids for runs having RAI insights

    filter_properties = {
        PropertyKeyValues.RAI_INSIGHTS_TYPE_KEY: PropertyKeyValues.RAI_INSIGHTS_TYPE_CONSTRUCT
    }
    if model_id is not None:
        filter_properties[PropertyKeyValues.RAI_INSIGHTS_MODEL_ID_KEY] = model_id

    # Have to use V1 client for now
    creds = ml_client._credential

    subscription = ml_client._workspace_scope.subscription_id
    rg_name = ml_client._workspace_scope.resource_group_name
    ws_name = ml_client._workspace_scope.workspace_name

    v1_workspace = Workspace(subscription, rg_name, ws_name, auth=None)
    experiment = v1_workspace.experiments[experiment_name]

    all_runs = Run.list(experiment, properties=filter_properties, include_children=True)

    return [r.id for r in all_runs]
