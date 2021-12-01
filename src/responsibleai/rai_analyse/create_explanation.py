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

from responsibleai import RAIInsights

from constants import Constants

_logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.INFO)


def parse_args():
    # setup arg parser
    parser = argparse.ArgumentParser()

    parser.add_argument("--rai_insights_dashboard", type=str, required=True)
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
            print("\t" + dirname)

        # Files
        for filename in files:
            print("\t" + filename)


def main(args):
    # Load the model_analysis_parent info
    rai_insights_dashboard_file = os.path.join(
        args.rai_insights_dashboard, Constants.RAI_INSIGHTS_PARENT_FILENAME
    )
    with open(rai_insights_dashboard_file, "r") as si:
        rai_insights_parent = json.load(si)
    _logger.info("Model_analysis_parent info: {0}".format(rai_insights_parent))

    # Load the Model Analysis
    with tempfile.TemporaryDirectory() as incoming_temp_dir:
        incoming_dir = pathlib.Path(incoming_temp_dir)
        shutil.copytree(args.rai_insights_dashboard, incoming_dir, dirs_exist_ok=True)

        os.makedirs(incoming_dir / "causal", exist_ok=True)
        os.makedirs(incoming_dir / "counterfactual", exist_ok=True)
        os.makedirs(incoming_dir / "error_analysis", exist_ok=True)
        os.makedirs(incoming_dir / "explainer", exist_ok=True)

        print_dir_tree(incoming_dir)

        rai_i = RAIInsights.load(incoming_dir)
        _logger.info("Loaded RAI Insights object")

        # Add the explanation
        rai_i.explainer.add()
        _logger.info("Added explanation")

        # Compute
        rai_i.compute()
        _logger.info("Computation complete")

        # Save
        with tempfile.TemporaryDirectory() as tmpdirname:
            rai_i.save(tmpdirname)
            _logger.info(f"Saved to {tmpdirname}")

            shutil.copytree(
                pathlib.Path(tmpdirname) / "explainer",
                args.explanation_path,
                dirs_exist_ok=True,
            )
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
