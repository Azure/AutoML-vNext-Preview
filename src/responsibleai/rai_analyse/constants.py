# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


class Constants:
    MODEL_ID_KEY = "id"  # To match Model schema
    MODEL_INFO_FILENAME = "model_info.json"
    RAI_INSIGHTS_RUN_ID_KEY = "rai_insights_parent_run_id"
    RAI_INSIGHTS_PARENT_FILENAME = "rai_insights.json"


class PropertyKeyValues:
    # The property to indicate the type of Run
    RAI_INSIGHTS_TYPE_KEY = '_azureml.responsibleai.rai_insights.type'
    RAI_INSIGHTS_TYPE_CONSTRUCT = 'construction'
    RAI_INSIGHTS_TYPE_CAUSAL = 'causal'
    RAI_INSIGHTS_TYPE_COUNTERFACTUAL = 'counterfactual'
    RAI_INSIGHTS_TYPE_EXPLANATION = 'explanation'
    RAI_INSIGHTS_TYPE_ERROR_ANALYSIS = 'error_analysis'

    # Property for tool runs to point at their constructor run
    RAI_INSIGHTS_CONSTRUCTOR_RUN_ID_KEY = '_azureml.responsibleai.rai_insights.constructor_run'

    # Property to record responsibleai version
    RAI_INSIGHTS_RESPONSIBLEAI_VERSION_KEY = '_azureml.responsibleai.rai_insights.responsibleai_version'

    # Properties for the constructor run to point at tool runs
    RAI_INSIGHTS_EXPLANATION_POINTER_KEY_FORMAT = '_azureml.responsibleai.rai_insights.has_explanation_{0}'