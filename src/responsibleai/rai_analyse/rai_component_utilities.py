# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
import os
import pathlib
import shutil
import tempfile
import uuid

from responsibleai import RAIInsights


_logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.INFO)


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


def load_rai_insights_from_input_port(input_port_path: str) -> RAIInsights:
    with tempfile.TemporaryDirectory() as incoming_temp_dir:
        incoming_dir = pathlib.Path(incoming_temp_dir)
        shutil.copytree(input_port_path, incoming_dir, dirs_exist_ok=True)
        _logger.info("Copied RAI Insights input to temporary directory")

        # Have to create empty subdirectories for the managers
        # THe RAI Insights object expect these to be present, but
        # since directories don't actually exist in Azure Blob store
        # they may not be present (some of the tools always have
        # a file present, even if no tool instances have been added)
        os.makedirs(incoming_dir / "causal", exist_ok=True)
        os.makedirs(incoming_dir / "counterfactual", exist_ok=True)
        os.makedirs(incoming_dir / "error_analysis", exist_ok=True)
        os.makedirs(incoming_dir / "explainer", exist_ok=True)
        _logger.info("Added empty directories")

        result = RAIInsights.load(incoming_dir)
        _logger.info("Loaded RAIInsights object")
    return result


def save_to_output_port(rai_i: RAIInsights, output_port_path: str, tool_dir_name: str):
    with tempfile.TemporaryDirectory() as tmpdirname:
        rai_i.save(tmpdirname)
        _logger.info(f"Saved to {tmpdirname}")

        tool_dirs = os.listdir(pathlib.Path(tmpdirname) / tool_dir_name)
        assert len(tool_dirs) == 1, "Checking for exactly one tool output"
        _logger.info("Checking dirname is GUID")
        uuid.UUID(tool_dirs[0])

        shutil.copytree(
            pathlib.Path(tmpdirname) / tool_dir_name / tool_dir_name[0],
            output_port_path,
            dirs_exist_ok=True,
        )
    _logger.info("Copied to output")
