# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import argparse
import json
import logging
import os

from azureml.core import Run
import azureml.responsibleai
from azureml.responsibleai.tools.model_analysis._requests.explain_request import ExplainRequest
from azureml.responsibleai.tools.model_analysis._requests.request_dto import RequestDTO
from azureml.responsibleai.tools.model_analysis._compute_dto import ComputeDTO
from azureml.responsibleai.tools.model_analysis._utilities import _run_all_and_upload

from constants import Constants

_logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.INFO)


def parse_args():
    # setup arg parser
    parser = argparse.ArgumentParser()

    parser.add_argument("--model_analysis_info", type=str, required=True)
    parser.add_argument("--comment", type=str, required=True)

    # parse args
    args = parser.parse_args()

    # return args
    return args


def main(args):
    # Load the model_analysis_parent info
    model_analysis_parent_file = os.path.join(args.model_analysis_info, Constants.MODEL_ANALYSIS_PARENT_FILENAME)
    with open(model_analysis_parent_file, "r") as si:
        model_analysis_parent = json.load(si)
    _logger.info("Model_analysis_parent info: {0}".format(model_analysis_parent))

    ws = Run.get_context().experiment.workspace
    model_analysis_run = Run.get(ws, model_analysis_parent[Constants.MA_RUN_ID_KEY])

    explain_request = ExplainRequest(args.comment)

    req_dto = RequestDTO(explanation_requests=[explain_request])
    compute_dto = ComputeDTO(
        model_analysis_run.experiment.name, model_analysis_run_id=model_analysis_run.id, requests=req_dto
    )
    _logger.info("compute_dto created")

    explain_run = model_analysis_run.child_run()
    _run_all_and_upload(compute_dto, explain_run)
    explain_run.complete()


# run script
if __name__ == "__main__":
    # add space in logs
    print("*" * 60)
    print("\n\n")

    print("azureml-responsibleai version:", azureml.responsibleai.__version__)

    # parse args
    args = parse_args()

    # run main function
    main(args)

    # add space in logs
    print("*" * 60)
    print("\n\n")
