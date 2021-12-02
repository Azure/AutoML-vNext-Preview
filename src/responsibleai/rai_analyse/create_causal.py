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
import uuid

from responsibleai import RAIInsights, __version__ as responsibleai_version


from azureml.core import Run


from constants import Constants, PropertyKeyValues
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

    parser.add_argument("--rai_insights_dashboard", type=str, required=True)

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
    rai_insights_parent_file = os.path.join(
        args.rai_insights_dashboard, Constants.RAI_INSIGHTS_PARENT_FILENAME
    )
    with open(rai_insights_parent_file, "r") as si:
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

        rai_i = RAIInsights.load(incoming_dir)
        _logger.info("Loaded RAI Insights object")

        # Add the causal analysis
        rai_i.causal.add(
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
        _logger.info("Added causal")

        # Compute
        rai_i.compute()
        _logger.info("Computation complete")

        # Save
        with tempfile.TemporaryDirectory() as tmpdirname:
            rai_i.save(tmpdirname)
            _logger.info(f"Saved to {tmpdirname}")

            causal_dirs = os.listdir(pathlib.Path(tmpdirname) / "causal")
            assert len(causal_dirs) == 1, "Checking for exactly one causal"
            _logger.info("Checking dirname is GUID")
            uuid.UUID(causal_dirs[0])

            shutil.copytree(
                pathlib.Path(tmpdirname) / "causal" / causal_dirs[0],
                args.causal_path,
                dirs_exist_ok=True,
            )
            _logger.info("Copied to output")

    _logger.info("Adding properties to Run")
    run_properties = {
        PropertyKeyValues.RAI_INSIGHTS_TYPE_KEY: PropertyKeyValues.RAI_INSIGHTS_TYPE_CAUSAL,
        PropertyKeyValues.RAI_INSIGHTS_RESPONSIBLEAI_VERSION_KEY: responsibleai_version,
        PropertyKeyValues.RAI_INSIGHTS_CONSTRUCTOR_RUN_ID_KEY: rai_insights_parent[
            Constants.RAI_INSIGHTS_RUN_ID_KEY
        ],
    }
    my_run = Run.get_context()
    my_run.add_properties(run_properties)

    _logger.info("Adding explanation property to constructor run")
    extra_props = {
        PropertyKeyValues.RAI_INSIGHTS_CAUSAL_POINTER_KEY_FORMAT.format(my_run.id): True
    }
    constructor_run = Run.get(
        my_run.experiment.workspace,
        rai_insights_parent[Constants.RAI_INSIGHTS_RUN_ID_KEY],
    )
    constructor_run.add_properties(extra_props)
    _logger.info("Completing")


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
