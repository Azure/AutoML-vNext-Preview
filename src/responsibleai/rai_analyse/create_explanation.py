# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import argparse
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
    parser.add_argument("--comment", type=str, required=True)
    parser.add_argument("--explanation_path", type=str, required=True)

    # parse args
    args = parser.parse_args()

    # return args
    return args


def main(args):
    # Load the RAI Insights object
    rai_i: RAIInsights = load_rai_insights_from_input_port(args.rai_insights_dashboard)

    # Add the explanation
    rai_i.explainer.add()
    _logger.info("Added explanation")

    # Compute
    rai_i.compute()
    _logger.info("Computation complete")

    # Save
    save_to_output_port(rai_i, args.explanation_path, RAIToolType.EXPLANATION)
    _logger.info("Saved to output port")

    # Copy the dashboard info file
    copy_dashboard_info_file(args.rai_insights_dashboard, args.explanation_path)

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
