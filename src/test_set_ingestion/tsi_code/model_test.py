import argparse
import os

from azureml.core import Run
from azureml.core.dataset import Dataset
import mlflow

from azureml.train.automl.runtime._remote_script import model_test_wrapper_v2

script_directory = None


def model_test_run():
    global script_directory

    parser = argparse.ArgumentParser()
    parser.add_argument('--model-uri', type=str, dest="model_uri")
    parser.add_argument('--target-column-name', type=str, dest="label_column_name")
    parser.add_argument('--automl-run-id', type=str, dest="automl_run_id")
    parser.add_argument('--automl-experiment', type=str, dest="automl_experiment")
    parser.add_argument('--task-type', type=str, dest="task")
    parser.add_argument('--test-dataset', type=str, dest="test_dataset")
    parser.add_argument('--train-dataset', type=str, dest="train_dataset")
    args = parser.parse_args()

    print("Starting the model test run....")
    print(args)

    run = Run.get_context()

    """
    Use this code if data_bindings get added back in

    data_path = os.environ.get('AZURE_ML_INPUT_test_data')
    if not data_path:
        raise Exception("No input binding for test_data found.")
    """
    test_data = Dataset.from_delimited_files(args.test_dataset)
    print(f'test data: {test_data}')

    train_data = None
    if args.train_dataset:
        train_data = Dataset.from_delimited_files(args.train_dataset)

    print(f"model_uri: {args.model_uri}")
    mlflow.set_tracking_uri(run.experiment.workspace.get_mlflow_tracking_uri())
    kwargs = {}

    # We want the default value from model_test_wrapper_v2
    if args.task:
        kwargs["task"] = args.task
    if args.train_dataset:
        kwargs["train-dataset"] = args.train_dataset

    model_test_wrapper_v2(
        script_directory=script_directory,
        train_dataset=train_data,
        test_dataset=test_data,
        model_id=args.model_uri,
        label_column_name=args.label_column_name,
        entry_point="test_run",
        automl_run_id=args.automl_run_id,
        **kwargs
        )


if __name__ == '__main__':
    model_test_run()
