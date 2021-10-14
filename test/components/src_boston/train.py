# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Sample train script for azureml-responisbleai notebooks."""

import argparse
import json
import os
import shutil
import tempfile

import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder

import mlflow
import mlflow.sklearn

from azureml.core.run import Run


def parse_args():
    # setup arg parser
    parser = argparse.ArgumentParser()

    # add arguments
    parser.add_argument("--training_data", type=str,
                        help="Path to training data")
    parser.add_argument("--target_column_name", type=str,
                        help="Name of target column")
    parser.add_argument("--continuous_features", type=json.loads)
    parser.add_argument("--categorical_features", type=json.loads)
    parser.add_argument("--model_output", type=str,
                        help="Path of output model")

    # parse args
    args = parser.parse_args()

    # return args
    return args


def get_regression_model_pipeline(continuous_features, categorical_features):
    # We create the preprocessing pipelines for both numeric and
    # categorical data.
    numeric_transformer = Pipeline(steps=[
        ('scaler', StandardScaler())])

    categorical_transformer = Pipeline(steps=[
        ('onehot', OneHotEncoder(handle_unknown='ignore'))])

    transformations = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, continuous_features),
            ('cat', categorical_transformer, categorical_features)])

    # Append classifier to preprocessing pipeline.
    # Now we have a full prediction pipeline.
    pipeline = Pipeline(steps=[('preprocessor', transformations),
                               ('regressor', RandomForestRegressor())])
    return pipeline


def main(args):
    current_experiment = Run.get_context().experiment
    tracking_uri = current_experiment.workspace.get_mlflow_tracking_uri()
    print("tracking_uri: {0}".format(tracking_uri))
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(current_experiment.name)

    # Read in data
    print("Reading data")
    train_dataset = pd.read_parquet(args.training_data)

    # Drop the labeled column to get the training set.
    X_train = train_dataset.drop_columns(
        columns=[args.target_column_name]).to_pandas_dataframe()
    y_train = train_dataset.keep_columns(
        columns=[args.target_column_name], validate=True).to_pandas_dataframe().values

    continuous_features = args.continuous_features
 #       ['CRIM', 'ZN', 'INDUS', 'CHAS', 'NOX', 'RM', 'AGE',
 #        'DIS', 'RAD', 'TAX', 'PTRATIO', 'B', 'LSTAT']
    categorical_features = args.categorical_features

    pipeline = get_regression_model_pipeline(
        continuous_features=continuous_features,
        categorical_features=categorical_features)
    model = pipeline.fit(X_train, y_train)

    # Saving model with mlflow
    with tempfile.TemporaryDirectory() as td:
        print("Saving model with MLFlow to temporary directory")
        tmp_output_dir = os.path.join(td, "my_model_dir")
        mlflow.sklearn.save_model(sk_model=model, path=tmp_output_dir)

        print("Copying MLFlow model to output path")
        for file_name in os.listdir(tmp_output_dir):
            print("  Copying: ", file_name)
            # As of Python 3.8, copytree will acquire dirs_exist_ok as
            # an option, removing the need for listdir
            shutil.copy2(src=os.path.join(tmp_output_dir, file_name),
                         dst=os.path.join(args.model_output, file_name))


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
