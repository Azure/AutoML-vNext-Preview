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
from arg_helpers import boolean_parser, str_or_int_parser, str_or_list_parser

_logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.INFO)


def parse_args():
    # setup arg parser
    parser = argparse.ArgumentParser()

    parser.add_argument("--model_analysis_info", type=str, required=True)
    parser.add_argument("--comment", type=str, required=True)
    parser.add_argument("--total_CFs", type=int, required=True)
    parser.add_argument("--method", type=str)
    parser.add_argument("--desired_class", type=str_or_int_parser)
    parser.add_argument("--desired_range", type=json.loads, help="List")
    parser.add_argument("--permitted_range", type=json.loads, help="Dict")
    parser.add_argument("--features_to_vary", type=str_or_list_parser)
    parser.add_argument("--feature_importance", type=boolean_parser)
    parser.add_argument("--counterfactual_path", type=str)

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

        # Add the counterfactual
        ma.counterfactual.add(
            total_CFs=args.total_CFs,
            method=args.method,
            desired_class=args.desired_class,
            desired_range=args.desired_range,
            permitted_range=args.permitted_range,
            features_to_vary=args.features_to_vary,
            feature_importance=args.feature_importance,
            comment=args.comment
        )
        _logger.info("Added counterfactual")

        # Compute
        ma.compute()
        _logger.info("Computation complete")

        # Save
        with tempfile.TemporaryDirectory() as tmpdirname:
            ma.save(tmpdirname)
            _logger.info(f"Saved to {tmpdirname}")

            print_dir_tree(tmpdirname)

            shutil.copytree(
                pathlib.Path(tmpdirname)/'counterfactual', args.explanation_path, dirs_exist_ok=True)
            _logger.info("Copied to output")


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
