# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
import logging
import time
import sys

from azure.ml import MLClient
from azure.ml.entities import Job

_logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.INFO)


def get_component_config():
    config_file = 'component_config.json'

    with open(config_file, 'r') as cf:
        result = json.load(cf)

    return result

def get_workspace_config():
    ws_config_file = 'config.json'

    with open(ws_config_file) as cf:
        result = json.load(cf)

    return result

def test_pipeline_from_yaml():
    pipeline_file = "test/rai/pipeline_analyse.yaml"
    pipeline_processed_file = "pipeline_analyse.processed.yaml"

    component_config = get_component_config()

    replacements = {
        'VERSION_REPLACEMENT_STRING': str(component_config['version'])
    }
    with open(pipeline_file, 'r') as infile, open(pipeline_processed_file, 'w')as outfile:
        for line in infile:
            for f, r in replacements.items():
                line = line.replace(f, r)
            outfile.write(line)

    # Now get the client
    ws_config = get_workspace_config()

    client = MLClient(
        ws_config['subscription_id'],
        ws_config['resource_group'],
        ws_config['workspace_name'],
        logging_enable=True
    )

    pipeline_job = Job.load(
        path=pipeline_processed_file
    )

    created_job = client.jobs.create_or_update(pipeline_job)
    assert created_job is not None

    while created_job.status not in ['Completed', 'Failed', 'Canceled', 'NotResponding']:
        time.sleep(30)
        created_job = client.jobs.get(created_job.name)
        print("Latest status : {0}".format(created_job.status))
        _logger.info("Latest status : {0}".format(created_job.status))
        
    assert created_job.status == 'Completed'