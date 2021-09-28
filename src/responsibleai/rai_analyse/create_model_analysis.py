import argparse
import json
import logging
import os
import uuid


import pandas as pd

from azureml._common._error_definition import AzureMLError
from azureml.core import Dataset, Datastore, Model, Run, Workspace
from azureml.exceptions import AzureMLException


import azureml.responsibleai

from azureml.responsibleai.tools.model_analysis._aml_init_dto import AMLInitDTO
from azureml.responsibleai.tools.model_analysis._model_analysis_settings import ModelAnalysisSettings
from azureml.responsibleai.common.pickle_model_loader import PickleModelLoader

from azureml.responsibleai.tools.model_analysis._init_utilities import (
    _check_dataframe_size,
    create_analysis_asset,
)
from azureml.responsibleai.tools.model_analysis._constants import (
    AnalysisTypes,
    PropertyKeys,
)

from azureml.responsibleai.common.model_loader import ModelLoader

from constants import Constants
from arg_helpers import get_from_args

_logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.INFO)


class ReplacementDataset:
    def __init__(self, path):
        self.path = path
        self.id = uuid.UUID("00000000-00000000-00000000-00000000")


def parse_args():
    # setup arg parser
    parser = argparse.ArgumentParser()

    parser.add_argument("--title", type=str, required=True)

    parser.add_argument("--task_type", type=str, required=True, choices=["classification", "regression"])

    parser.add_argument("--model_info_path", type=str, help="name:version", required=True)

    parser.add_argument("--train_dataset", type=str, required=True)
    parser.add_argument("--test_dataset", type=str, required=True)

    parser.add_argument("--target_column_name", type=str, required=True)
    parser.add_argument("--X_column_names", type=str, required=True, help="List[str]")

    parser.add_argument("--datastore_name", type=str, required=True)

    parser.add_argument("--maximum_rows_for_test_dataset", type=int, default=5000)
    parser.add_argument("--categorical_column_names", type=str, help="Optional[List[str]]")

    parser.add_argument("--output_path", type=str, help="Path to output JSON")

    # parse args
    args = parser.parse_args()

    # return args
    return args


def fetch_model_id(args):
    model_info_path = os.path.join(args.model_info_path, Constants.MODEL_INFO_FILENAME)
    with open(model_info_path, "r") as json_file:
        model_info = json.load(json_file)
    return model_info[Constants.MODEL_ID_KEY]


def create_amlinitdto(args):
    my_run = Run.get_context()
    my_workspace = my_run.experiment.workspace

    model_id = fetch_model_id(args)
    my_model = Model(workspace=my_workspace, id=model_id)
    loader = "mlflow"

    train_ds = ReplacementDataset(args.train_dataset)
    # train_dataset = Dataset.get_by_name(my_workspace, train_ds_name)
    test_ds = ReplacementDataset(args.test_dataset)
    # test_dataset = Dataset.get_by_name(my_workspace, test_ds_name)

    target_column_name = args.target_column_name
    X_column_names = get_from_args(args, "X_column_names", custom_parser=json.loads, allow_none=False)
    ds_name = args.datastore_name
    cat_col_names = get_from_args(args, "categorical_column_names", custom_parser=json.loads, allow_none=True)

    mas = ModelAnalysisSettings(
        workspace=my_run.experiment.workspace,
        title=args.title,
        model=my_model,
        model_loader=loader,
        model_type=args.task_type,
        train_dataset=train_ds,  # Use some relaxed typing ...
        test_dataset=test_ds,  # Use some relaxed typing ...
        X_column_names=X_column_names,
        target_column_name=target_column_name,
        confidential_datastore_name=ds_name,
        run_configuration=None,
        maximum_rows_for_test_dataset=args.maximum_rows_for_test_dataset,
        categorical_column_names=cat_col_names,
    )

    result = AMLInitDTO(mas)

    return result


def load_dataset(parquet_path: str):
    _logger.info("Loading parquet file: {0}".format(parquet_path))
    df = pd.read_parquet(parquet_path)
    print(df.dtypes)
    print(df.head(10))
    return df


def main(args):
    settings = create_amlinitdto(args)

    _logger.info("Model analysis ID: {0}".format(settings.analysis_id))
    my_run = Run.get_context()
    my_run.add_properties(
        {
            PropertyKeys.ANALYSIS_ID: settings.analysis_id,
            PropertyKeys.MODEL_ID: settings.model_id,
            PropertyKeys.MODEL_TYPE: settings.model_type,
            PropertyKeys.TRAIN_SNAPSHOT_ID: settings.train_snapshot_id,
            PropertyKeys.TEST_SNAPSHOT_ID: settings.test_snapshot_id,
            PropertyKeys.ANALYSIS_TYPE: AnalysisTypes.MODEL_ANALYSIS_TYPE,
        }
    )

    _logger.info("Dealing with initialization dataset")
    train_df = load_dataset(args.train_dataset)

    _logger.info("Dealing with evaluation dataset")
    test_df = load_dataset(args.test_dataset)
    _check_dataframe_size(test_df, settings.maximum_rows_for_test_dataset, "test", "maximum_rows_for_test_dataset")

    _logger.info("Loading model: {0}".format(settings.model_loader))
    model_estimator = ModelLoader.load_model_from_workspace(
        my_run.experiment.workspace, settings.model_loader, settings.model_id
    )

    _logger.info("Starting create_analysis_asset")
    create_analysis_asset(my_run, model_estimator, train_df, test_df, settings)

    _logger.info("Saving JSON for tool components")
    output_dict = {Constants.MA_RUN_ID_KEY: str(my_run.id)}
    output_file = os.path.join(args.output_path, Constants.MODEL_ANALYSIS_PARENT_FILENAME)
    with open(output_file, "w") as of:
        json.dump(output_dict, of)


# run script
if __name__ == "__main__":
    # add space in logs
    print("*" * 60)
    print("\n\n")

    print("azureml-responsibleai version:", azureml.responsibleai.__version__)

    # parse args
    args = parse_args()

    # run main function
    main(args)

    # add space in logs
    print("*" * 60)
    print("\n\n")
