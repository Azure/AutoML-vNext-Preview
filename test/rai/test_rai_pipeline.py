# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
import pathlib
import time

from azure.ml.entities import Job

_logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.INFO)

class TestRAI:
    def test_pipeline_from_yaml(self, ml_client, component_config):
        current_dir = pathlib.Path(__file__).parent.absolute()
        pipeline_file = current_dir / "pipeline_analyse.yaml"
        pipeline_processed_file = "pipeline_analyse.processed.yaml"

        replacements = {
            'VERSION_REPLACEMENT_STRING': str(component_config['version'])
        }
        with open(pipeline_file, 'r') as infile, open(pipeline_processed_file, 'w') as outfile:
            for line in infile:
                for f, r in replacements.items():
                    line = line.replace(f, r)
                outfile.write(line)

        pipeline_job = Job.load(
            path=pipeline_processed_file
        )

        created_job = ml_client.jobs.create_or_update(pipeline_job)
        assert created_job is not None

        while created_job.status not in ['Completed', 'Failed', 'Canceled', 'NotResponding']:
            time.sleep(30)
            created_job = ml_client.jobs.get(created_job.name)
            print("Latest status : {0}".format(created_job.status))
            _logger.info("Latest status : {0}".format(created_job.status))
            
        assert created_job.status == 'Completed'