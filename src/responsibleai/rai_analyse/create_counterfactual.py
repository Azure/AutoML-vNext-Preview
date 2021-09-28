import argparse
import json
import logging
import os

from azureml.core import Run
import azureml.responsibleai
from azureml.responsibleai.tools.model_analysis._requests import CounterfactualRequest, RequestDTO
from azureml.responsibleai.tools.model_analysis._compute_dto import ComputeDTO
from azureml.responsibleai.tools.model_analysis._utilities import _run_all_and_upload

from constants import Constants
from arg_helpers import boolean_parser, str_or_int_parser, str_or_list_parser

_logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.INFO)


def parse_args():
    # setup arg parser
    parser = argparse.ArgumentParser()

    parser.add_argument("--model_analysis_info", type=str, required=True)
    parser.add_argument("--comment", type=str, required=True)
    parser.add_argument("--total_CFs", type=int, required=True)
    parser.add_argument("--method", type=str)
    parser.add_argument("--desired_class", type=str_or_int_parser)
    parser.add_argument("--desired_range", type=json.loads, help="List")
    parser.add_argument("--permitted_range", type=json.loads, help="Dict")
    parser.add_argument("--features_to_vary", type=str_or_list_parser)
    parser.add_argument("--feature_importance", type=boolean_parser)

    # parse args
    args = parser.parse_args()

    # return args
    return args


def main(args):
    # Load the surrogacy info
    surrogacy_file = os.path.join(args.model_analysis_info, Constants.MODEL_ANALYSIS_PARENT_FILENAME)
    with open(surrogacy_file, "r") as si:
        model_analysis_parent = json.load(si)
    _logger.info("Model_analysis_parent info: {0}".format(model_analysis_parent))

    ws = Run.get_context().experiment.workspace
    model_analysis_run = Run.get(ws, model_analysis_parent[Constants.MA_RUN_ID_KEY])

    counterfactual_request = CounterfactualRequest(
        total_CFs=args.total_CFs,
        method=args.method,
        desired_class=args.desired_class,
        desired_range=args.desired_range,
        permitted_range=args.permitted_range,
        features_to_vary=args.features_to_vary,
        feature_importance=args.feature_importance,
        comment=args.comment,
    )

    req_dto = RequestDTO(counterfactual_requests=[counterfactual_request])
    compute_dto = ComputeDTO(
        model_analysis_run.experiment.name, model_analysis_run_id=model_analysis_run.id, requests=req_dto
    )
    _logger.info("compute_dto created")

    child_run = model_analysis_run.child_run()
    _run_all_and_upload(compute_dto, child_run)
    child_run.complete()


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
