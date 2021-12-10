# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
import logging
import os
import pathlib
import shutil
import tempfile
import uuid

from typing import Dict

from azureml.core import Run

from responsibleai import RAIInsights, __version__ as responsibleai_version

from constants import DashboardInfo, PropertyKeyValues, RAIToolType


_logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.INFO)


# Directory names saved by RAIInsights might not match tool names
_tool_directory_mapping: Dict[str, str] = {
    RAIToolType.CAUSAL: "causal",
    RAIToolType.COUNTERFACTUAL: "counterfactual",
    RAIToolType.ERROR_ANALYSIS: "error_analysis",
    RAIToolType.EXPLANATION: "explainer",
}


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


def load_dashboard_info_file(input_port_path: str) -> Dict[str, str]:
    # Load the rai_insights_dashboard file info
    rai_insights_dashboard_file = os.path.join(
        input_port_path, DashboardInfo.RAI_INSIGHTS_PARENT_FILENAME
    )
    with open(rai_insights_dashboard_file, "r") as si:
        dashboard_info = json.load(si)
    _logger.info("rai_insights_parent info: {0}".format(dashboard_info))
    return dashboard_info


def create_rai_tool_directories(rai_insights_dir: pathlib.Path)->None:
    # Have to create empty subdirectories for the managers
    # THe RAI Insights object expect these to be present, but
    # since directories don't actually exist in Azure Blob store
    # they may not be present (some of the tools always have
    # a file present, even if no tool instances have been added)
    for v in _tool_directory_mapping.values():
        os.makedirs(rai_insights_dir / v, exist_ok=True)
    _logger.info("Added empty directories")

def load_rai_insights_from_input_port(input_port_path: str) -> RAIInsights:
    with tempfile.TemporaryDirectory() as incoming_temp_dir:
        incoming_dir = pathlib.Path(incoming_temp_dir)
        shutil.copytree(input_port_path, incoming_dir, dirs_exist_ok=True)
        _logger.info("Copied RAI Insights input to temporary directory")

        create_rai_tool_directories(incoming_dir)

        result = RAIInsights.load(incoming_dir)
        _logger.info("Loaded RAIInsights object")
    return result

def copy_insight_to_raiinsights(rai_insights_dir: pathlib.Path, insight_dir: pathlib.Path) -> None:
    print("Starting copy")
    dir_items = list(insight_dir.iterdir())
    print("Directory contents: {0}".format(dir_items))
    assert len(dir_items) == 1

    tool_dir_name = dir_items[0]
    _logger.info("Detected tool: {0}".format(tool_dir_name))
    assert tool_dir_name in _tool_directory_mapping.values()


    shutil.copytree(
        insight_dir/tool_dir_name,
        pathlib.Path(rai_insights_dir) / tool_dir_name
    )
    _logger.info("Copy complete")



def save_to_output_port(rai_i: RAIInsights, output_port_path: str, tool_type: str):
    with tempfile.TemporaryDirectory() as tmpdirname:
        rai_i.save(tmpdirname)
        _logger.info(f"Saved to {tmpdirname}")

        tool_dir_name = _tool_directory_mapping[tool_type]
        insight_dirs = os.listdir(pathlib.Path(tmpdirname) / tool_dir_name)
        assert len(insight_dirs) == 1, "Checking for exactly one tool output"
        _logger.info("Checking dirname is GUID")
        uuid.UUID(insight_dirs[0])

        target_path = pathlib.Path(output_port_path) / tool_dir_name
        target_path.mkdir()
        _logger.info("Created output directory")

        _logger.info("Starting copy")
        shutil.copytree(
            pathlib.Path(tmpdirname) / tool_dir_name,
            target_path,
            dirs_exist_ok=True,
        )
    _logger.info("Copied to output")


def add_properties_to_tool_run(tool_type: str, constructor_run_id: str):
    target_run = Run.get_context()
    if tool_type == RAIToolType.CAUSAL:
        type_key = PropertyKeyValues.RAI_INSIGHTS_TYPE_CAUSAL
        pointer_format = PropertyKeyValues.RAI_INSIGHTS_CAUSAL_POINTER_KEY_FORMAT
    elif tool_type == RAIToolType.COUNTERFACTUAL:
        type_key = PropertyKeyValues.RAI_INSIGHTS_TYPE_COUNTERFACTUAL
        pointer_format = (
            PropertyKeyValues.RAI_INSIGHTS_COUNTERFACTUAL_POINTER_KEY_FORMAT
        )
    elif tool_type == RAIToolType.ERROR_ANALYSIS:
        type_key = RAIToolType.ERROR_ANALYSIS
        pointer_format = (
            PropertyKeyValues.RAI_INSIGHTS_ERROR_ANALYSIS_POINTER_KEY_FORMAT
        )
    elif tool_type == RAIToolType.EXPLANATION:
        type_key = PropertyKeyValues.RAI_INSIGHTS_TYPE_EXPLANATION
        pointer_format = PropertyKeyValues.RAI_INSIGHTS_EXPLANATION_POINTER_KEY_FORMAT
    else:
        raise ValueError("Unrecognised tool_type: {0}".format(tool_type))

    _logger.info("Adding properties to Run")
    run_properties = {
        PropertyKeyValues.RAI_INSIGHTS_TYPE_KEY: type_key,
        PropertyKeyValues.RAI_INSIGHTS_RESPONSIBLEAI_VERSION_KEY: responsibleai_version,
        PropertyKeyValues.RAI_INSIGHTS_CONSTRUCTOR_RUN_ID_KEY: constructor_run_id,
    }
    target_run.add_properties(run_properties)

    _logger.info("Adding tool property to constructor run")
    extra_props = {pointer_format.format(target_run.id): target_run.id}
    constructor_run = Run.get(target_run.experiment.workspace, constructor_run_id)
    constructor_run.add_properties(extra_props)
