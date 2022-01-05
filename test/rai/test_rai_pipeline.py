# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
import pathlib
import time

from azure.ml import MLClient
from azure.ml.entities import JobInput
from azure.ml.entities import ComponentJob, Job, PipelineJob

_logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.INFO)


def process_file(input_file, output_file, replacements):
    with open(input_file, "r") as infile, open(output_file, "w") as outfile:
        for line in infile:
            for f, r in replacements.items():
                line = line.replace(f, r)
            outfile.write(line)


def submit_and_wait(
    ml_client: MLClient, pipeline_job: PipelineJob, expected_state: str = "Completed"
) -> PipelineJob:
    created_job = ml_client.jobs.create_or_update(pipeline_job)
    terminal_states = ["Completed", "Failed", "Canceled", "NotResponding"]
    assert created_job is not None
    assert expected_state in terminal_states

    while created_job.status not in terminal_states:
        time.sleep(30)
        created_job = ml_client.jobs.get(created_job.name)
        print("Latest status : {0}".format(created_job.status))
        _logger.info("Latest status : {0}".format(created_job.status))
    if created_job.status != expected_state:
        _logger.error(str(created_job))
    assert created_job.status == expected_state
    return created_job


class TestRAI:
    def test_classification_pipeline_from_yaml(self, ml_client, component_config):
        current_dir = pathlib.Path(__file__).parent.absolute()
        pipeline_file = current_dir / "pipeline_adult_analyse.yaml"
        pipeline_processed_file = "pipeline_adult_analyse.processed.yaml"

        replacements = {"VERSION_REPLACEMENT_STRING": str(component_config["version"])}
        process_file(pipeline_file, pipeline_processed_file, replacements)

        pipeline_job = Job.load(path=pipeline_processed_file)

        submit_and_wait(ml_client, pipeline_job)

    def test_boston_pipeline_from_yaml(self, ml_client, component_config):
        current_dir = pathlib.Path(__file__).parent.absolute()
        pipeline_file = current_dir / "pipeline_boston_analyse.yaml"
        pipeline_processed_file = "pipeline_boston_analyse.processed.yaml"

        replacements = {"VERSION_REPLACEMENT_STRING": str(component_config["version"])}
        process_file(pipeline_file, pipeline_processed_file, replacements)

        pipeline_job = Job.load(path=pipeline_processed_file)

        submit_and_wait(ml_client, pipeline_job)

    def test_classification_pipeline_from_python(
        self, ml_client: MLClient, component_config
    ):
        # This is for the Adult dataset
        version_string = component_config["version"]

        # Configure the global pipeline inputs:
        pipeline_inputs = {
            "target_column_name": "income",
            "my_training_data": JobInput(dataset=f"Adult_Train_PQ:{version_string}"),
            "my_test_data": JobInput(dataset=f"Adult_Test_PQ:{version_string}"),
        }

        # Specify the training job
        train_job_inputs = {
            "target_column_name": "${{inputs.target_column_name}}",
            "training_data": "${{inputs.my_training_data}}",
        }
        train_job_outputs = {"model_output": None}
        train_job = ComponentJob(
            component=f"TrainLogisticRegressionForRAI:{version_string}",
            inputs=train_job_inputs,
            outputs=train_job_outputs,
        )

        # The model registration job
        register_job_inputs = {
            "model_input_path": "${{jobs.train-model-job.outputs.model_output}}",
            "model_base_name": "notebook_registered_logreg",
        }
        register_job_outputs = {"model_info_output_path": None}
        register_job = ComponentJob(
            component=f"RegisterModel:{version_string}",
            inputs=register_job_inputs,
            outputs=register_job_outputs,
        )

        # Top level RAI Insights component
        create_rai_inputs = {
            "title": "Run built from Python",
            "task_type": "classification",
            "model_info_path": "${{jobs.register-model-job.outputs.model_info_output_path}}",
            "train_dataset": "${{inputs.my_training_data}}",
            "test_dataset": "${{inputs.my_test_data}}",
            "target_column_name": "${{inputs.target_column_name}}",
            "categorical_column_names": '["Race", "Sex", "Workclass", "Marital Status", "Country", "Occupation"]',
        }
        create_rai_outputs = {"rai_insights_dashboard": None}
        create_rai_job = ComponentJob(
            component=f"RAIInsightsConstructor:{version_string}",
            inputs=create_rai_inputs,
            outputs=create_rai_outputs,
        )

        # Setup the explanation
        explain_inputs = {
            "comment": "Insert text here",
            "rai_insights_dashboard": "${{jobs.create-rai-job.outputs.rai_insights_dashboard}}",
        }
        explain_outputs = {"explanation": None}
        explain_job = ComponentJob(
            component=f"RAIInsightsExplanation:{version_string}",
            inputs=explain_inputs,
            outputs=explain_outputs,
        )

        # Setup causal
        causal_inputs = {
            "rai_insights_dashboard": "${{jobs.create-rai-job.outputs.rai_insights_dashboard}}",
            "treatment_features": '["Age", "Sex"]',
            "heterogeneity_features": '["Marital Status"]',
        }
        causal_outputs = {"causal": None}
        causal_job = ComponentJob(
            component=f"RAIInsightsCausal:{version_string}",
            inputs=causal_inputs,
            outputs=causal_outputs,
        )

        # Setup counterfactual
        counterfactual_inputs = {
            "rai_insights_dashboard": "${{jobs.create-rai-job.outputs.rai_insights_dashboard}}",
            "total_CFs": "10",
            "desired_class": "opposite",
        }
        counterfactual_outputs = {"counterfactual": None}
        counterfactual_job = ComponentJob(
            component=f"RAIInsightsCounterfactual:{version_string}",
            inputs=counterfactual_inputs,
            outputs=counterfactual_outputs,
        )

        # Setup error analysis
        error_analysis_inputs = {
            "rai_insights_dashboard": "${{jobs.create-rai-job.outputs.rai_insights_dashboard}}",
            "filter_features": '["Race", "Sex", "Workclass", "Marital Status", "Country", "Occupation"]',
        }
        error_analysis_outputs = {"error_analysis": None}
        error_analysis_job = ComponentJob(
            component=f"RAIInsightsErrorAnalysis:{version_string}",
            inputs=error_analysis_inputs,
            outputs=error_analysis_outputs,
        )

        # Configure the gather component
        gather_inputs = {
            "constructor": "${{jobs.create-rai-job.outputs.rai_insights_dashboard}}",
            "insight_1": "${{jobs.explain-rai-job.outputs.explanation}}",
            "insight_2": "${{jobs.causal-rai-job.outputs.causal}}",
            "insight_3": "${{jobs.counterfactual-rai-job.outputs.counterfactual}}",
            "insight_4": "${{jobs.error-analysis-rai-job.outputs.error_analysis}}",
        }
        gather_outputs = {"dashboard": None, "ux_json": None}
        gather_job = ComponentJob(
            component=f"RAIInsightsGather:{version_string}",
            inputs=gather_inputs,
            outputs=gather_outputs,
        )

        # Assemble into a pipeline
        pipeline_job = PipelineJob(
            experiment_name=f"classification_pipeline_from_python_{version_string}",
            description="Python submitted Adult",
            jobs={
                "train-model-job": train_job,
                "register-model-job": register_job,
                "create-rai-job": create_rai_job,
                "explain-rai-job": explain_job,
                "causal-rai-job": causal_job,
                "counterfactual-rai-job": counterfactual_job,
                "error-analysis-rai-job": error_analysis_job,
                "gather-job": gather_job,
            },
            inputs=pipeline_inputs,
            outputs=train_job_outputs,
            compute="cpucluster",
        )

        # Send it
        pipeline_job = submit_and_wait(ml_client, pipeline_job)
        assert pipeline_job is not None

    def test_tool_component_mismatch(self, ml_client: MLClient, component_config):
        # Checks that components from different constructors can't be mixed
        # This is for the Adult dataset
        version_string = component_config["version"]

        # Configure the global pipeline inputs:
        pipeline_inputs = {
            "target_column_name": "income",
            "my_training_data": JobInput(dataset=f"Adult_Train_PQ:{version_string}"),
            "my_test_data": JobInput(dataset=f"Adult_Test_PQ:{version_string}"),
        }

        # Specify the training job
        train_job_inputs = {
            "target_column_name": "${{inputs.target_column_name}}",
            "training_data": "${{inputs.my_training_data}}",
        }
        train_job_outputs = {"model_output": None}
        train_job = ComponentJob(
            component=f"TrainLogisticRegressionForRAI:{version_string}",
            inputs=train_job_inputs,
            outputs=train_job_outputs,
        )

        # The model registration job
        register_job_inputs = {
            "model_input_path": "${{jobs.train-model-job.outputs.model_output}}",
            "model_base_name": "notebook_registered_logreg",
        }
        register_job_outputs = {"model_info_output_path": None}
        # Register twice (the component is non-deterministic so we can be
        # sure output won't be reused)
        register_job_1 = ComponentJob(
            component=f"RegisterModel:{version_string}",
            inputs=register_job_inputs,
            outputs=register_job_outputs,
        )
        register_job_2 = ComponentJob(
            component=f"RegisterModel:{version_string}",
            inputs=register_job_inputs,
            outputs=register_job_outputs,
        )

        # Top level RAI Insights component
        create_rai_inputs = {
            "title": "Run built from Python",
            "task_type": "classification",
            "model_info_path": "${{jobs.register-model-job-1.outputs.model_info_output_path}}",
            "train_dataset": "${{inputs.my_training_data}}",
            "test_dataset": "${{inputs.my_test_data}}",
            "target_column_name": "${{inputs.target_column_name}}",
            "categorical_column_names": '["Race", "Sex", "Workclass", "Marital Status", "Country", "Occupation"]',
        }
        create_rai_outputs = {"rai_insights_dashboard": None}

        # Have TWO dashboard constructors
        create_rai_1 = ComponentJob(
            component=f"RAIInsightsConstructor:{version_string}",
            inputs=create_rai_inputs,
            outputs=create_rai_outputs,
        )
        create_rai_inputs[
            "model_info_path"
        ] = "${{jobs.register-model-job-2.outputs.model_info_output_path}}"
        create_rai_2 = ComponentJob(
            component=f"RAIInsightsConstructor:{version_string}",
            inputs=create_rai_inputs,
            outputs=create_rai_outputs,
        )

        # Setup causal on constructor 1
        causal_inputs = {
            "rai_insights_dashboard": "${{jobs.create-rai-job-1.outputs.rai_insights_dashboard}}",
            "treatment_features": '["Age", "Sex"]',
            "heterogeneity_features": '["Marital Status"]',
        }
        causal_outputs = {"causal": None}
        causal_job = ComponentJob(
            component=f"RAIInsightsCausal:{version_string}",
            inputs=causal_inputs,
            outputs=causal_outputs,
        )

        # Setup counterfactual on constructor 2
        counterfactual_inputs = {
            "rai_insights_dashboard": "${{jobs.create-rai-job-2.outputs.rai_insights_dashboard}}",
            "total_CFs": "10",
            "desired_class": "opposite",
        }
        counterfactual_outputs = {"counterfactual": None}
        counterfactual_job = ComponentJob(
            component=f"RAIInsightsCounterfactual:{version_string}",
            inputs=counterfactual_inputs,
            outputs=counterfactual_outputs,
        )

        # Configure the gather component
        gather_inputs = {
            "constructor": "${{jobs.create-rai-job-1.outputs.rai_insights_dashboard}}",
            "insight_2": "${{jobs.causal-rai-job.outputs.causal}}",
            "insight_3": "${{jobs.counterfactual-rai-job.outputs.counterfactual}}",
        }
        gather_outputs = {"dashboard": None, "ux_json": None}
        gather_job = ComponentJob(
            component=f"RAIInsightsGather:{version_string}",
            inputs=gather_inputs,
            outputs=gather_outputs,
        )

        # Assemble into a pipeline
        pipeline_job = PipelineJob(
            experiment_name=f"XFAIL_tool_component_mismatch_{version_string}",
            description="Python submitted Adult",
            jobs={
                "train-model-job": train_job,
                "register-model-job-1": register_job_1,
                "register-model-job-2": register_job_2,
                "create-rai-job-1": create_rai_1,
                "create-rai-job-2": create_rai_2,
                "causal-rai-job": causal_job,
                "counterfactual-rai-job": counterfactual_job,
                "gather-job": gather_job,
            },
            inputs=pipeline_inputs,
            outputs=train_job_outputs,
            compute="cpucluster",
        )

        # Send it
        pipeline_job = submit_and_wait(ml_client, pipeline_job, "Failed")
        # Want to do more here, but there isn't anything useful in the returned job
        # Problem is, the job might have failed for some other reason
        assert pipeline_job is not None

    def test_fetch_registered_model_component(self, ml_client, component_config):
        # Actually does two pipelines. One to register, then one to use
        version_string = component_config["version"]

        model_name_suffix = int(time.time())
        model_name = "fetch_model"

        # Configure the global pipeline inputs:
        pipeline_inputs = {
            "target_column_name": "income",
            "my_training_data": JobInput(dataset=f"Adult_Train_PQ:{version_string}"),
            "my_test_data": JobInput(dataset=f"Adult_Test_PQ:{version_string}"),
        }

        # Specify the training job
        train_job_inputs = {
            "target_column_name": "${{inputs.target_column_name}}",
            "training_data": "${{inputs.my_training_data}}",
        }
        train_job_outputs = {"model_output": None}
        train_job = ComponentJob(
            component=f"TrainLogisticRegressionForRAI:{version_string}",
            inputs=train_job_inputs,
            outputs=train_job_outputs,
        )

        # The model registration job
        register_job_inputs = {
            "model_input_path": "${{jobs.train-model-job.outputs.model_output}}",
            "model_base_name": model_name,
            "model_name_suffix": model_name_suffix,
        }
        register_job_outputs = {"model_info_output_path": None}
        register_job = ComponentJob(
            component=f"RegisterModel:{version_string}",
            inputs=register_job_inputs,
            outputs=register_job_outputs,
        )

        # Assemble into a pipeline
        register_pipeline = PipelineJob(
            experiment_name=f"Register_Model_{version_string}",
            description="Python submitted Adult model registration",
            jobs={
                "train-model-job": train_job,
                "register-model-job": register_job,
            },
            inputs=pipeline_inputs,
            outputs=register_job_outputs,
            compute="cpucluster",
        )

        # Send it
        register_pipeline_job = submit_and_wait(ml_client, register_pipeline)
        assert register_pipeline_job is not None

        # Now the pipeline to consume the model

        # The job to fetch the model (this is the one under test)
        expected_model_id = f"{model_name}_{model_name_suffix}:1"
        fetch_job_inputs = {"model_id": expected_model_id}
        fetch_job_outputs = {"model_info_output_path": None}
        fetch_job = ComponentJob(
            component=f"FetchRegisteredModel:{version_string}",
            inputs=fetch_job_inputs,
            outputs=fetch_job_outputs,
        )

        # Top level RAI Insights component
        create_rai_inputs = {
            "title": "Run built from Python",
            "task_type": "classification",
            "model_info_path": "${{jobs.fetch-model-job.outputs.model_info_output_path}}",
            "train_dataset": "${{inputs.my_training_data}}",
            "test_dataset": "${{inputs.my_test_data}}",
            "target_column_name": "${{inputs.target_column_name}}",
            "categorical_column_names": '["Race", "Sex", "Workclass", "Marital Status", "Country", "Occupation"]',
        }
        create_rai_outputs = {"rai_insights_dashboard": None}
        create_rai_job = ComponentJob(
            component=f"RAIInsightsConstructor:{version_string}",
            inputs=create_rai_inputs,
            outputs=create_rai_outputs,
        )

        # Setup the explanation
        explain_inputs = {
            "comment": "Insert text here",
            "rai_insights_dashboard": "${{jobs.create-rai-job.outputs.rai_insights_dashboard}}",
        }
        explain_outputs = {"explanation": None}
        explain_job = ComponentJob(
            component=f"RAIInsightsExplanation:{version_string}",
            inputs=explain_inputs,
            outputs=explain_outputs,
        )

        # Pipeline to construct the RAI Insights
        insights_pipeline_job = PipelineJob(
            experiment_name=f"fetch_registered_model_component_{version_string}",
            description="Python submitted Adult insights using fetched model",
            jobs={
                "fetch-model-job": fetch_job,
                "create-rai-job": create_rai_job,
                "explain-job": explain_job,
            },
            inputs=pipeline_inputs,
            outputs=None,
            compute="cpucluster",
        )

        # Send it
        insights_pipeline_job = submit_and_wait(ml_client, insights_pipeline_job)
        assert insights_pipeline_job is not None
