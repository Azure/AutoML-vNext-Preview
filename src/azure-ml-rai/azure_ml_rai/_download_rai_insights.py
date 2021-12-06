# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


import mlflow
from mlflow.tracking import MlflowClient

from azure.ml import MLClient

from ._utilities import _get_v1_workspace_client

def download_rai_insights(
    ml_client: MLClient,
    rai_insight_id: str,
    path: str
) -> None:
    v1_ws = _get_v1_workspace_client(ml_client)

    mlflow.set_tracking_uri(v1_ws.get_mlflow_tracking_uri())

    mlflow_client = MlflowClient()

    