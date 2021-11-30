# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import argparse
import json
import logging
import os
from typing import Any

import mlflow
import pandas as pd

from azureml.core import Model, Run, Workspace

from responsibleai import ModelAnalysis

from constants import Constants
from arg_helpers import get_from_args

_logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.INFO)


def parse_args():
    # setup arg parser
    parser = argparse.ArgumentParser()

    parser.add_argument("--title", type=str, required=True)

    parser.add_argument(
        "--task_type", type=str, required=True, choices=["classification", "regression"]
    )

    parser.add_argument(
        "--model_info_path", type=str, help="name:version", required=True
    )

    parser.add_argument("--train_dataset", type=str, required=True)
    parser.add_argument("--test_dataset", type=str, required=True)

    parser.add_argument("--target_column_name", type=str, required=True)

    parser.add_argument("--maximum_rows_for_test_dataset", type=int, default=5000)
    parser.add_argument(
        "--categorical_column_names", type=str, help="Optional[List[str]]"
    )

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


def load_mlflow_model(workspace: Workspace, model_id: str) -> Any:
    mlflow.set_tracking_uri(workspace.get_mlflow_tracking_uri())

    model = Model._get(workspace, id=model_id)
    model_uri = "models:/{}/{}".format(model.name, model.version)
    return mlflow.pyfunc.load_model(model_uri)._model_impl


def load_dataset(parquet_path: str):
    _logger.info("Loading parquet file: {0}".format(parquet_path))
    df = pd.read_parquet(parquet_path)
    print(df.dtypes)
    print(df.head(10))
    return df


def main(args):

    my_run = Run.get_context()

    _logger.info("Dealing with initialization dataset")
    train_df = load_dataset(args.train_dataset)

    _logger.info("Dealing with evaluation dataset")
    test_df = load_dataset(args.test_dataset)

    model_id = fetch_model_id(args)
    _logger.info("Loading model: {0}".format(model_id))
    model_estimator = load_mlflow_model(my_run.experiment.workspace, model_id)

    _logger.info("Getting categorical columns")
    cat_col_names = get_from_args(
        args, "categorical_column_names", custom_parser=json.loads, allow_none=True
    )

    _logger.info("Creating ModelAnalysis object")
    model_analysis = ModelAnalysis(
        model=model_estimator,
        train=train_df,
        test=test_df,
        target_column=args.target_column_name,
        task_type=args.task_type,
        categorical_features=cat_col_names,
        maximum_rows_for_test=args.maximum_rows_for_test_dataset,
    )

    _logger.info("Saving ModelAnalysis object")
    model_analysis.save(args.output_path)

    _logger.info("Saving JSON for tool components")
    output_dict = {Constants.MA_RUN_ID_KEY: str(my_run.id)}
    output_file = os.path.join(
        args.output_path, Constants.MODEL_ANALYSIS_PARENT_FILENAME
    )
    with open(output_file, "w") as of:
        json.dump(output_dict, of)

    _logger.info("Adding properties to Run")
    my_run.add_properties({"TBD": "TBD"})


# run script
if __name__ == "__main__":
    # add space in logs
    print("*" * 60)
    print("\n\n")

    # parse args
    args = parse_args()

    # run main function
    main(args)

    # add space in logs
    print("*" * 60)
    print("\n\n")
