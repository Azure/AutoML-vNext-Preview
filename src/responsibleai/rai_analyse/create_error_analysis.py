# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import argparse
import json
import logging

from responsibleai import RAIInsights


from constants import DashboardInfo, RAIToolType
from rai_component_utilities import (
    load_dashboard_info_file,
    load_rai_insights_from_input_port,
    save_to_output_port,
    add_properties_to_tool_run,
)

_logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.INFO)


def parse_args():
    # setup arg parser
    parser = argparse.ArgumentParser()

    parser.add_argument("--rai_insights_dashboard", type=str, required=True)
    parser.add_argument("--comment", type=str, required=True)
    parser.add_argument("--max_depth", type=int)
    parser.add_argument("--num_leaves", type=int)
    parser.add_argument("--filter_features", type=json.loads, help="List")
    parser.add_argument("--error_analysis_path", type=str)

    # parse args
    args = parser.parse_args()

    # Patch issue with argument passing
    if isinstance(args.filter_features, list) and len(args.filter_features) == 0:
        args.filter_features = None

    # return args
    return args


def main(args):
    # Load the model_analysis_parent info
    dashboard_info = load_dashboard_info_file(args.rai_insights_dashboard)

    # Load the RAI Insights object
    rai_i: RAIInsights = load_rai_insights_from_input_port(
        args.rai_insights_dashboard)

    # Add the error analysis
    rai_i.error_analysis.add(
        max_depth=args.max_depth,
        num_leaves=args.num_leaves,
        filter_features=args.filter_features,
    )
    _logger.info("Added error analysis")

    # Compute
    rai_i.compute()
    _logger.info("Computation complete")

    # Save
    save_to_output_port(rai_i, args.error_analysis_path,
                        RAIToolType.ERROR_ANALYSIS)

    # Add the necessary properties
    add_properties_to_tool_run(
        RAIToolType.ERROR_ANALYSIS, dashboard_info[DashboardInfo.RAI_INSIGHTS_RUN_ID_KEY]
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
