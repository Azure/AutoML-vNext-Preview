# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import List, Optional, Tuple

from azureml.core import Run
from azure.ml import MLClient

from ._constants import PropertyKeyValues
from ._utilities import _get_v1_workspace_client


def list_rai_insights(
    ml_client: MLClient,
    experiment_name: str,
    model_id: Optional[str] = None
) -> List[str]:
    # Return the Run ids for runs having RAI insights

    filter_properties = {
        PropertyKeyValues.RAI_INSIGHTS_TYPE_KEY: PropertyKeyValues.RAI_INSIGHTS_TYPE_GATHER
    }
    if model_id is not None:
        filter_properties[PropertyKeyValues.RAI_INSIGHTS_MODEL_ID_KEY] = model_id

    # Have to use V1 client for now
    v1_workspace = _get_v1_workspace_client(ml_client)
    v1_experiment = v1_workspace.experiments[experiment_name]

    all_runs = Run.list(
        v1_experiment, properties=filter_properties, include_children=True)

    return [r.id for r in all_runs]
