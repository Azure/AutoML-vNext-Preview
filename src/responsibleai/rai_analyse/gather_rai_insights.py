# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import argparse
import json
import logging
from pathlib import Path
import shutil
import tempfile

from responsibleai import RAIInsights

from rai_component_utilities import create_rai_tool_directories, copy_insight_to_raiinsights, print_dir_tree

_logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.INFO)


def parse_args():
    # setup arg parser
    parser = argparse.ArgumentParser()

    parser.add_argument("--constructor", type=str, required=True)
    parser.add_argument("--insight_1", type=str, required=True)
    parser.add_argument("--insight_2", type=str, required=True)
    parser.add_argument("--insight_3", type=str, required=True)
    parser.add_argument("--insight_4", type=str, required=True)
    parser.add_argument("--dashboard", type=str, required=True)
    parser.add_argument("--ux_json", type=str, required=True)

    # parse args
    args = parser.parse_args()

    # return args
    return args


def main(args):
    with tempfile.TemporaryDirectory() as incoming_temp_dir:
        incoming_dir = Path(incoming_temp_dir)
        shutil.copytree(args.constructor, incoming_dir, dirs_exist_ok=True)
        _logger.info("Copied RAI Insights input to temporary directory")

        create_rai_tool_directories(incoming_dir)
        _logger.info("Copied empty RAIInsights")

        print_dir_tree(incoming_dir)
        print("\n==================\n")

        copy_insight_to_raiinsights(incoming_dir, Path(args.insight_1))
        _logger.info("All copies complete")

        print_dir_tree(incoming_dir)
        print("\n==================\n")

        rai_i = RAIInsights.load(incoming_dir)
        _logger.info("Object loaded")

        # rai_i.save(args.dashboard)
        _logger.info("Saved dashboard to oputput")

        rai_data = rai_i.get_data()
        json_filename = 'dashboard.json'
        output_path = Path(args.ux_json) / json_filename
        with open(output_path, 'w') as json_file:
            json.dump(rai_data, json_file)
        _logger.info("Dashboard JSON written")


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
