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


from constants import DashboardInfo, RAIToolType
from rai_component_utilities import (
    load_dashboard_info_file,
    load_rai_insights_from_input_port,
    save_to_output_port,
    add_properties_to_tool_run,
)
from arg_helpers import boolean_parser, str_or_int_parser, str_or_list_parser

_logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.INFO)


def parse_args():
    # setup arg parser
    parser = argparse.ArgumentParser()

    parser.add_argument("--rai_insights_dashboard", type=str, required=True)
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
            print("\t" + dirname)

        # Files
        for filename in files:
            print("\t" + filename)


def main(args):
    # Load the model_analysis_parent info
    dashboard_info = load_dashboard_info_file(args.rai_insights_dashboard)

    # Load the RAI Insights object
    rai_i: RAIInsights = load_rai_insights_from_input_port(
        args.rai_insights_dashboard)

    # Add the counterfactual
    rai_i.counterfactual.add(
            total_CFs=args.total_CFs,
            method=args.method,
            desired_class=args.desired_class,
            desired_range=args.desired_range,
            permitted_range=args.permitted_range,
            features_to_vary=args.features_to_vary,
            feature_importance=args.feature_importance,
        )
    _logger.info("Added counterfactual")

    # Compute
    rai_i.compute()
    _logger.info("Computation complete")

    # Save
    save_to_output_port(rai_i, args.causal_path, RAIToolType.COUNTERFACTUAL)

    # Add the necessary properties
    add_properties_to_tool_run(
        RAIToolType.COUNTERFACTUAL, dashboard_info[DashboardInfo.RAI_INSIGHTS_RUN_ID_KEY]
    )

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
