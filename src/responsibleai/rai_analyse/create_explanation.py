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
from rai_component_utilities import load_rai_insights_from_input_port, save_to_output_port

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
    # Load the model_analysis_parent info
    rai_insights_dashboard_file = os.path.join(
        args.rai_insights_dashboard, Constants.RAI_INSIGHTS_PARENT_FILENAME
    )
    with open(rai_insights_dashboard_file, "r") as si:
        rai_insights_parent = json.load(si)
    _logger.info("rai_insights_parent info: {0}".format(rai_insights_parent))

    # Load the RAI Insights object
    rai_i = load_rai_insights_from_input_port(args.rai_insights.dashboard)
    
    # Add the explanation
    rai_i.explainer.add()
    _logger.info("Added explanation")

    # Compute
    rai_i.compute()
    _logger.info("Computation complete")

    # Save
    save_to_output_port(rai_i, args.explanation_path, 'explainer')

    _logger.info("Adding properties to Run")
    run_properties = {
        PropertyKeyValues.RAI_INSIGHTS_TYPE_KEY: PropertyKeyValues.RAI_INSIGHTS_TYPE_EXPLANATION,
        PropertyKeyValues.RAI_INSIGHTS_RESPONSIBLEAI_VERSION_KEY: responsibleai_version,
        PropertyKeyValues.RAI_INSIGHTS_CONSTRUCTOR_RUN_ID_KEY: rai_insights_parent[
            Constants.RAI_INSIGHTS_RUN_ID_KEY]
    }
    my_run = Run.get_context()
    my_run.add_properties(run_properties)

    _logger.info("Adding explanation property to constructor run")
    extra_props = {
        PropertyKeyValues.RAI_INSIGHTS_EXPLANATION_POINTER_KEY_FORMAT.format(my_run.id): True
    }
    constructor_run = Run.get(my_run.experiment.workspace,
                              rai_insights_parent[Constants.RAI_INSIGHTS_RUN_ID_KEY])
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
