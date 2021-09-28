import argparse
import json
import logging
import os

from azureml.core import Run
import azureml.responsibleai
from azureml.responsibleai.tools.model_analysis._requests import CausalRequest, RequestDTO
from azureml.responsibleai.tools.model_analysis._compute_dto import ComputeDTO
from azureml.responsibleai.tools.model_analysis._utilities import _run_all_and_upload

from constants import Constants
from arg_helpers import float_or_json_parser, boolean_parser, str_or_list_parser, int_or_none_parser

_logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.INFO)


def parse_args():
    # setup arg parser
    parser = argparse.ArgumentParser()

    parser.add_argument("--model_analysis_info", type=str, required=True)
    parser.add_argument("--comment", type=str, required=True)

    parser.add_argument("--treatment_features", type=json.loads, help="List[str]")
    parser.add_argument("--heterogeneity_features", type=json.loads, help="Optional[List[str]] use 'null' to skip")
    parser.add_argument("--nuisance_model", type=str)
    parser.add_argument("--heterogeneity_model", type=str)
    parser.add_argument("--alpha", type=float)
    parser.add_argument("--upper_bound_on_cat_expansion", type=int)
    parser.add_argument(
        "--treatment_cost", type=float_or_json_parser, help="Union[float, List[Union[float, np.ndarray]]]"
    )
    parser.add_argument("--min_tree_leaf_samples", type=int)
    parser.add_argument("--max_tree_depth", type=int)
    parser.add_argument("--skip_cat_limit_checks", type=boolean_parser)
    parser.add_argument("--categories", type=str_or_list_parser)
    parser.add_argument("--n_jobs", type=int)
    parser.add_argument("--verbose", type=int)
    parser.add_argument("--random_state", type=int_or_none_parser)

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

    causal_request = CausalRequest(
        treatment_features=args.treatment_features,
        heterogeneity_features=args.heterogeneity_features,
        nuisance_model=args.nuisance_model,
        heterogeneity_model=args.heterogeneity_model,
        alpha=args.alpha,
        upper_bound_on_cat_expansion=args.upper_bound_on_cat_expansion,
        treatment_cost=args.treatment_cost,
        min_tree_leaf_samples=args.min_tree_leaf_samples,
        max_tree_depth=args.max_tree_depth,
        skip_cat_limit_checks=args.skip_cat_limit_checks,
        categories=args.categories,
        comment=args.comment,
        n_jobs=args.n_jobs,
        verbose=args.verbose,
        random_state=args.random_state,
    )

    req_dto = RequestDTO(causal_requests=[causal_request])
    compute_dto = ComputeDTO(
        model_analysis_run.experiment.name, model_analysis_run_id=model_analysis_run.id, requests=req_dto
    )
    _logger.info("compute_dto created")

    causal_run = model_analysis_run.child_run()
    _run_all_and_upload(compute_dto, causal_run)
    causal_run.complete()


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
