# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
import pathlib
import time

from azure.ml.entities import Job

_logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.INFO)


def process_file(input_file, output_file, replacements):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            for f, r in replacements.items():
                line = line.replace(f, r)
            outfile.write(line)


def submit_and_wait(ml_client, pipeline_job):
    created_job = ml_client.jobs.create_or_update(pipeline_job)
    assert created_job is not None

    while created_job.status not in ['Completed', 'Failed', 'Canceled', 'NotResponding']:
        time.sleep(30)
        created_job = ml_client.jobs.get(created_job.name)
        print("Latest status : {0}".format(created_job.status))
        _logger.info("Latest status : {0}".format(created_job.status))
    assert created_job.status == 'Completed'


class TestRAI:
    def test_classification_pipeline_from_yaml(self, ml_client, component_config):
        current_dir = pathlib.Path(__file__).parent.absolute()
        pipeline_file = current_dir / "pipeline_adult_analyse.yaml"
        pipeline_processed_file = "pipeline_adult_analyse.processed.yaml"

        replacements = {
            'VERSION_REPLACEMENT_STRING': str(component_config['version'])
        }
        process_file(pipeline_file, pipeline_processed_file, replacements)

        pipeline_job = Job.load(
            path=pipeline_processed_file
        )

        submit_and_wait(ml_client, pipeline_job)

    def test_boston_pipeline_from_yaml(self, ml_client, component_config):
        current_dir = pathlib.Path(__file__).parent.absolute()
        pipeline_file = current_dir / "pipeline_boston_analyse.yaml"
        pipeline_processed_file = "pipeline_boston_analyse.processed.yaml"

        replacements = {
            'VERSION_REPLACEMENT_STRING': str(component_config['version'])
        }
        process_file(pipeline_file, pipeline_processed_file, replacements)

        pipeline_job = Job.load(
            path=pipeline_processed_file
        )

        submit_and_wait(ml_client, pipeline_job)
