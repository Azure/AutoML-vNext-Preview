# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
import os
import pathlib
import shutil
import tempfile

from typing import Any, Dict

import mlflow
from mlflow.store.artifact.azure_blob_artifact_repo import AzureBlobArtifactRepository
from mlflow.tracking import MlflowClient

from azure.storage.blob import BlobServiceClient

from azure.ml import MLClient

from ._constants import OutputPortNames, RAIToolType
from ._utilities import _get_v1_workspace_client


# Directory names saved by RAIInsights might not match tool names
_tool_directory_mapping: Dict[str, str] = {
    RAIToolType.CAUSAL: "causal",
    RAIToolType.COUNTERFACTUAL: "counterfactual",
    RAIToolType.ERROR_ANALYSIS: "error_analysis",
    RAIToolType.EXPLANATION: "explainer",
}


def _get_output_port_info(
        mlflow_client: MlflowClient,
        run_id: str,
        port_name: str) -> Any:
    with tempfile.TemporaryDirectory() as temp_dir:
        mlflow_client.download_artifacts(
            run_id,
            port_name,
            temp_dir)

        json_filename = os.path.join(
            temp_dir, port_name)

        with open(json_filename, 'r') as json_file:
            port_info = json.load(json_file)

    print(port_info)
    return port_info


def download_rai_insights(
    ml_client: MLClient,
    rai_insight_id: str,
    path: str
) -> None:
    v1_ws = _get_v1_workspace_client(ml_client)

    mlflow.set_tracking_uri(v1_ws.get_mlflow_tracking_uri())

    mlflow_client = MlflowClient()

    constructor_location_info = _get_output_port_info(
        mlflow_client,
        rai_insight_id,
        OutputPortNames.RAI_INSIGHTS_CONSTRUCTOR_OUTPUT_PORT)

    print(AzureBlobArtifactRepository.parse_wasbs_uri(
        constructor_location_info['Uri']), sep=' ---  ')

    container, storage_account, blob_path, account_dns_suffix = AzureBlobArtifactRepository.parse_wasbs_uri(
        constructor_location_info['Uri'])
    account_url = "https://{account}.{suffix}".format(
        account=storage_account, suffix=account_dns_suffix)

    bsc = BlobServiceClient(account_url=account_url, credential=ml_client._credential)
    abar = AzureBlobArtifactRepository(constructor_location_info['Uri'], client=bsc)

    print(abar.list_artifacts(''))

    with tempfile.TemporaryDirectory() as temp_dir:
        abar.download_artifacts('', temp_dir)

        temp_dir_path = pathlib.Path(temp_dir)

        for v in _tool_directory_mapping.values():
            os.makedirs(temp_dir_path / v, exist_ok=True)

        shutil.copytree(temp_dir, path)