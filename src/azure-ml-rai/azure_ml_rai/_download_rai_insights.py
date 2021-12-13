# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
import os
from pathlib import Path
import tempfile

from typing import Any

import mlflow
from mlflow.store.artifact.azure_blob_artifact_repo import AzureBlobArtifactRepository
from mlflow.tracking import MlflowClient

from azure.identity import ChainedTokenCredential
from azure.storage.blob import BlobServiceClient

from azure.ml import MLClient

from ._constants import OutputPortNames
from ._utilities import _get_v1_workspace_client


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
    target_directory: Path,
    credential: ChainedTokenCredential
) -> None:
    port_info = _get_output_port_info(mlflow_client, run_id, port_name)

    wasbs_tuple = AzureBlobArtifactRepository.parse_wasbs_uri(
        port_info['Uri']
    )
    storage_account = wasbs_tuple[1]
    if len(wasbs_tuple) == 4:
        account_dns_suffix = wasbs_tuple[3]
    else:
        account_dns_suffix = 'blob.core.windows.net'

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

    output_directory = Path(path)
    output_directory.mkdir(parents=True, exist_ok=False)

    _download_port_files(
        mlflow_client,
        rai_insight_id,
        OutputPortNames.RAI_INSIGHTS_GATHER_RAIINSIGHTS_PORT,
        output_directory,
        ml_client._credential
    )

    # Ensure empty directories are present
    tool_dirs = ['causal', 'counterfactual', 'error_analysis', 'explainer']
    for t in tool_dirs:
        os.makedirs(Path(path) / t, exist_ok=True)
