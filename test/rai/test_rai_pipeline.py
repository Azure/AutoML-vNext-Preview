# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
import pathlib
import time

from azure.ml.entities import JobInput
from azure.ml.entities import ComponentJob, Job, PipelineJob

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

    def test_classification_pipeline(self, ml_client, component_config):
        # This only configures an explanation for simplicity
        version_string = component_config['version']

        # Configure the global pipeline inputs:
        pipeline_inputs = {
            'target_column_name': 'income',
            'my_training_data': JobInput(dataset=f"Adult_Train_PQ:{version_string}"),
            'my_test_data': JobInput(dataset=f"Adult_Test_PQ:{version_string}")
        }

        # Specify the training job
        train_job_inputs = {
            'target_column_name': '${{inputs.target_column_name}}',
            'training_data': '${{inputs.my_training_data}}',
        }
        train_job_outputs = {
            'model_output': None
        }
        train_job = ComponentJob(
            component=f"TrainLogisticRegressionForRAI:{version_string}",
            inputs=train_job_inputs,
            outputs=train_job_outputs
        )

        # The model registration job
        register_job_inputs = {
            'model_input_path': '${{jobs.train-model-job.outputs.model_output}}',
            'model_base_name': 'notebook_registered_logreg',
        }
        register_job_outputs = {
            'model_info_output_path': None
        }
        register_job = ComponentJob(
            component=f"RegisterModel:{version_string}",
            inputs=register_job_inputs,
            outputs=register_job_outputs
        )

        # Top level Model Analysis component
        create_ma_inputs = {
            'title': 'Run built from Python',
            'task_type': 'classification',
            'model_info_path': '${{jobs.register-model-job.outputs.model_info_output_path}}',
            'train_dataset': '${{inputs.my_training_data}}',
            'test_dataset': '${{inputs.my_test_data}}',
            'target_column_name': '${{inputs.target_column_name}}',
            # 'X_column_names': '["Age", "Workclass", "Education-Num", "Marital Status", "Occupation", "Relationship", "Race", "Sex", "Capital Gain", "Capital Loss", "Hours per week", "Country"]',
            # 'datastore_name': 'workspaceblobstore',
            'categorical_column_names': '["Race", "Sex", "Workclass", "Marital Status", "Country", "Occupation"]',
        }
        create_ma_outputs = {
            'model_analysis_dashboard': None
        }
        create_ma_job = ComponentJob(
            component=f"ModelAnalysisConstructor:{version_string}",
            inputs=create_ma_inputs,
            outputs=create_ma_outputs
        )

        # Setup the explanation
        explain_inputs = {
            'comment': 'Insert text here',
            'model_analysis_dashboard': '${{jobs.create-ma-job.outputs.model_analysis_dashboard}}'
        }
        explain_outputs = {
            'explanation': None
        }
        explain_job = ComponentJob(
            component=f"ModelAnalysisExplanation:{version_string}",
            inputs=explain_inputs,
            outputs=explain_outputs
        )

        # Setup causal
        causal_inputs = {
            'comment': 'Insert something',
            'model_analysis_dashboard': '${{jobs.create-ma-job.outputs.model_analysis_dashboard}}',
            'treatment_features': '["Age", "Sex"]',
            'heterogeneity_features': '["Marital Status"]'
        }
        causal_outputs = {
            'causal': None
        }
        causal_job = ComponentJob(
            component=f"ModelAnalysisCausal:{version_string}",
            inputs=causal_inputs,
            outputs=causal_outputs
        )

        # Setup counterfactual
        counterfactual_inputs = {
            'comment': "Something witty",
            'model_analysis_dashboard': '${{jobs.create-ma-job.outputs.model_analysis_dashboard}}',
            'treatment_features': '["Age", "Sex"]',
            'heterogeneity_features': '["Marital Status"]',
        }
        counterfactual_outputs = {
            'counterfactual': None
        }
        counterfactual_job = ComponentJob(
            component=f"ModelAnalysisCounterfactual:{version_string}",
            inputs=counterfactual_inputs,
            outputs=counterfactual_outputs
        )

        # Assemble into a pipeline
        pipeline_job = PipelineJob(
            experiment_name=f"Classification_from_Python_{version_string}",
            description="Python submitted Adult",
            jobs={
                'train-model-job': train_job,
                'register-model-job': register_job,
                'create-ma-job': create_ma_job,
                'explain-ma-job': explain_job,
                'causal-ma-job': causal_job,
                'counterfactual-ma-job': counterfactual_job
            },
            inputs=pipeline_inputs,
            outputs=train_job_outputs,
            compute="cpucluster"
        )

        # Send it
        submit_and_wait(ml_client, pipeline_job)
