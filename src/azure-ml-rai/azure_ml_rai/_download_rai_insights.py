# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
import os
import tempfile

import mlflow
from mlflow.tracking import MlflowClient

from azure.ml import MLClient

from ._constants import OutputPortNames
from ._utilities import _get_v1_workspace_client


def download_rai_insights(
    ml_client: MLClient,
    rai_insight_id: str,
    path: str
) -> None:
    v1_ws = _get_v1_workspace_client(ml_client)

    mlflow.set_tracking_uri(v1_ws.get_mlflow_tracking_uri())

    mlflow_client = MlflowClient()

    with tempfile.TemporaryDirectory() as temp_dir:
        mlflow_client.download_artifacts(
            rai_insight_id, 
            OutputPortNames.RAI_INSIGHTS_CONSTRUCTOR_OUTPUT_PORT, 
            temp_dir)

        json_filename = os.path.join(temp_dir, OutputPortNames.RAI_INSIGHTS_CONSTRUCTOR_OUTPUT_PORT)

        with open(json_filename, 'r') as json_file:
            constructor_location_info = json.load(json_file)

        print(constructor_location_info)