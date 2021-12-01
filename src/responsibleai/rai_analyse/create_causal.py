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
from arg_helpers import (
    float_or_json_parser,
    boolean_parser,
    str_or_list_parser,
    int_or_none_parser,
)

_logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.INFO)


def parse_args():
    # setup arg parser
    parser = argparse.ArgumentParser()

    parser.add_argument("--model_analysis_dashboard", type=str, required=True)

    parser.add_argument("--treatment_features", type=json.loads, help="List[str]")
    parser.add_argument(
        "--heterogeneity_features",
        type=json.loads,
        help="Optional[List[str]] use 'null' to skip",
    )
    parser.add_argument("--nuisance_model", type=str)
    parser.add_argument("--heterogeneity_model", type=str)
    parser.add_argument("--alpha", type=float)
    parser.add_argument("--upper_bound_on_cat_expansion", type=int)
    parser.add_argument(
        "--treatment_cost",
        type=float_or_json_parser,
        help="Union[float, List[Union[float, np.ndarray]]]",
    )
    parser.add_argument("--min_tree_leaf_samples", type=int)
    parser.add_argument("--max_tree_depth", type=int)
    parser.add_argument("--skip_cat_limit_checks", type=boolean_parser)
    parser.add_argument("--categories", type=str_or_list_parser)
    parser.add_argument("--n_jobs", type=int)
    parser.add_argument("--verbose", type=int)
    parser.add_argument("--random_state", type=int_or_none_parser)

    parser.add_argument("--causal_path", type=str)

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
    model_analysis_parent_file = os.path.join(
        args.model_analysis_dashboard, Constants.RAI_INSIGHTS_PARENT_FILENAME
    )
    with open(model_analysis_parent_file, "r") as si:
        model_analysis_parent = json.load(si)
    _logger.info("Model_analysis_parent info: {0}".format(model_analysis_parent))

    # Load the Model Analysis
    with tempfile.TemporaryDirectory() as incoming_temp_dir:
        incoming_dir = pathlib.Path(incoming_temp_dir)
        shutil.copytree(args.model_analysis_dashboard, incoming_dir, dirs_exist_ok=True)

        os.makedirs(incoming_dir / "causal", exist_ok=True)
        os.makedirs(incoming_dir / "counterfactual", exist_ok=True)
        os.makedirs(incoming_dir / "error_analysis", exist_ok=True)
        os.makedirs(incoming_dir / "explainer", exist_ok=True)

        print_dir_tree(incoming_dir)

        ma = ModelAnalysis.load(incoming_dir)
        _logger.info("Loaded ModelAnalysis object")

        # Add the causal analysis
        ma.causal.add(
            treatment_features=args.treatment_features,
            heterogeneity_features=args.heterogeneity_features,
            nuisance_model=args.nuisance_model,
            heterogeneity_model=args.heterogeneity_model,
            alpha=args.alpha,
            upper_bound_on_cat_expansion=args.upper_bound_on_cat_expansion,
            treatment_cost=args.treatment_cost,
            min_tree_leaf_samples=args.min_tree_leaf_samples,
            max_tree_depth=args.max_tree_depth,
            skip_cat_limit_checks=args.skip_cat_limit_checks,
            categories=args.categories,
            n_jobs=args.n_jobs,
            verbose=args.verbose,
            random_state=args.random_state,
        )
        _logger.info("Added explanation")

        # Compute
        ma.compute()
        _logger.info("Computation complete")

        # Save
        with tempfile.TemporaryDirectory() as tmpdirname:
            ma.save(tmpdirname)
            _logger.info(f"Saved to {tmpdirname}")

            print_dir_tree(tmpdirname)

            shutil.copytree(
                pathlib.Path(tmpdirname) / "causal",
                args.causal_path,
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
