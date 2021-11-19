# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import argparse
import json
import logging
import os
import pathlib
import tempfile
import shutil

from responsibleai import ModelAnalysis

from constants import Constants

_logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.INFO)


def parse_args():
    # setup arg parser
    parser = argparse.ArgumentParser()

    parser.add_argument("--model_analysis_dashboard", type=str, required=True)
    parser.add_argument("--comment", type=str, required=True)
    parser.add_argument("--explanation_path", type=str, required=True)

    # parse args
    args = parser.parse_args()

    # return args
    return args


def print_dir_tree(base_dir):
    for current_dir, subdirs, files in os.walk(base_dir):
        # Current Iteration Directory
        print(current_dir)

        # Directories
        for dirname in subdirs:
            print('\t' + dirname)

        # Files
        for filename in files:
            print('\t' + filename)


def main(args):
    # Load the model_analysis_parent info
    model_analysis_parent_file = os.path.join(
        args.model_analysis_dashboard, Constants.MODEL_ANALYSIS_PARENT_FILENAME)
    with open(model_analysis_parent_file, "r") as si:
        model_analysis_parent = json.load(si)
    _logger.info("Model_analysis_parent info: {0}".format(
        model_analysis_parent))

    # Load the Model Analysis
    with tempfile.TemporaryDirectory() as incoming_temp_dir:
        incoming_dir = pathlib.Path(incoming_temp_dir)
        shutil.copytree(args.model_analysis_dashboard,
                        incoming_dir, dirs_exist_ok=True)

        os.makedirs(incoming_dir / 'causal', exist_ok=True)
        os.makedirs(incoming_dir / 'counterfactual', exist_ok=True)
        os.makedirs(incoming_dir / 'error_analysis', exist_ok=True)
        os.makedirs(incoming_dir / 'explainer', exist_ok=True)

        print_dir_tree(incoming_dir)

        ma = ModelAnalysis.load(incoming_dir)
        _logger.info("Loaded ModelAnalysis object")

        # Add the explanation
        ma.explainer.add()
        _logger.info("Added explanation")

        # Compute
        ma.compute()
        _logger.info("Computation complete")

        # Save
        with tempfile.TemporaryDirectory() as tmpdirname:
            ma.save(tmpdirname)
            print_dir_tree(tmpdirname)


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
