# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import argparse
import json
import logging

from responsibleai import RAIInsights


from constants import RAIToolType
from rai_component_utilities import (
    load_rai_insights_from_input_port,
    save_to_output_port,
    copy_dashboard_info_file,
)

_logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.INFO)


def parse_args():
    # setup arg parser
    parser = argparse.ArgumentParser()

    parser.add_argument("--rai_insights_dashboard", type=str, required=True)
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
    # Load the RAI Insights object
    rai_i: RAIInsights = load_rai_insights_from_input_port(args.rai_insights_dashboard)

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
    save_to_output_port(rai_i, args.error_analysis_path, RAIToolType.ERROR_ANALYSIS)
    _logger.info("Saved to output port")

    # Copy the dashboard info file
    copy_dashboard_info_file(args.rai_insights_dashboard, args.error_analysis_path)

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
