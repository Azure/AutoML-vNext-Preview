# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
import pytest

from azure.ml import MLClient


@pytest.fixture(scope='session')
def component_config():
    config_file = 'component_config.json'

    with open(config_file, 'r') as cf:
        result = json.load(cf)

    return result

@pytest.fixture(scope='session')
def workspace_config():
    ws_config_file = 'config.json'

    with open(ws_config_file) as cf:
        result = json.load(cf)

    return result

@pytest.fixture(scope='function')
def ml_client(workspace_config):
    client = MLClient(
        workspace_config['subscription_id'],
        workspace_config['resource_group'],
        workspace_config['workspace_name'],
        logging_enable=True
    )

    return client