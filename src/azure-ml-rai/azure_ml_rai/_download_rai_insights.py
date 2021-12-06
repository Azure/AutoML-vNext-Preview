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

from azure.identity import ChainedTokenCredential
from azure.storage.blob import BlobServiceClient

from azure.ml import MLClient

from ._constants import OutputPortNames, RAIToolType
from ._list_rai_runs import list_components_for_rai_insight
from ._utilities import _get_v1_workspace_client


# Directory names saved by RAIInsights might not match tool names
_tool_directory_mapping: Dict[str, str] = {
    RAIToolType.CAUSAL: "causal",
    RAIToolType.COUNTERFACTUAL: "counterfactual",
    RAIToolType.ERROR_ANALYSIS: "error_analysis",
    RAIToolType.EXPLANATION: "explainer",
}

_tool_output_port_mapping: Dict[str, str] = {
    RAIToolType.CAUSAL: "causal",
    RAIToolType.COUNTERFACTUAL: "counterfactual",
    RAIToolType.ERROR_ANALYSIS: "error_analysis",
    RAIToolType.EXPLANATION: "explanation"
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

    return port_info


def _download_port_files(
    mlflow_client: MlflowClient,
    run_id: str,
    port_name: str,
    target_directory: pathlib.Path,
    credential: ChainedTokenCredential
) -> None:
    port_info = _get_output_port_info(mlflow_client, run_id, port_name)

    _, storage_account, _, account_dns_suffix = AzureBlobArtifactRepository.parse_wasbs_uri(
        port_info['Uri']
    )
    account_url = "https://{account}.{suffix}".format(
        account=storage_account,
        suffix=account_dns_suffix
    )

    bsc = BlobServiceClient(account_url=account_url,
                            credential=credential)
    abar = AzureBlobArtifactRepository(
        port_info['Uri'], client=bsc)

    # Download everything
    abar.download_artifacts('', target_directory)


def download_rai_insights(
    ml_client: MLClient,
    rai_insight_id: str,
    path: str
) -> None:
    v1_ws = _get_v1_workspace_client(ml_client)

    mlflow.set_tracking_uri(v1_ws.get_mlflow_tracking_uri())

    mlflow_client = MlflowClient()

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = pathlib.Path(temp_dir)

        # Get the empty RAIInsights
        _download_port_files(
            mlflow_client,
            rai_insight_id,
            OutputPortNames.RAI_INSIGHTS_CONSTRUCTOR_OUTPUT_PORT,
            temp_dir_path,
            ml_client._credential
        )

        # Need to ensure all the tool directories exist
        for v in _tool_directory_mapping.values():
            os.makedirs(temp_dir_path / v, exist_ok=True)

        # Start working through the insights
        tool_runs = list_components_for_rai_insight(
            ml_client,
            v1_ws.get_run(rai_insight_id).experiment.name,
            rai_insight_id=rai_insight_id
        )
        for t in tool_runs:
            run_id = t[0]
            tool = t[1]

            insight_directory = temp_dir_path/_tool_directory_mapping[tool]/run_id
            insight_directory.mkdir(parents=True, exist_ok=False)

            _download_port_files(
                mlflow_client,
                run_id,
                _tool_output_port_mapping[tool],
                insight_directory,
                ml_client._credential
            )

        shutil.copytree(temp_dir, path)
