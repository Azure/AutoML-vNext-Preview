# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# This is copied from the component constants.py


class RAIToolType:
    CAUSAL = "causal"
    COUNTERFACTUAL = "counterfactual"
    ERROR_ANALYSIS = "error_analysis"
    EXPLANATION = "explanation"


class PropertyKeyValues:
    # The property to indicate the type of Run
    RAI_INSIGHTS_TYPE_KEY = "_azureml.responsibleai.rai_insights.type"
    RAI_INSIGHTS_TYPE_GATHER = "gather"

    # Property to point at the model under examination
    RAI_INSIGHTS_MODEL_ID_KEY = "_azureml.responsibleai.rai_insights.model_id"

    # Property to record responsibleai version
    RAI_INSIGHTS_RESPONSIBLEAI_VERSION_KEY = (
        "_azureml.responsibleai.rai_insights.responsibleai_version"
    )


# This comes from the component definitions
class OutputPortNames:
    RAI_INSIGHTS_GATHER_RAIINSIGHTS_PORT = "dashboard"
    RAI_INSIGHTS_GATHER_RAIINSIGHTS_UX_PORT = "ux_json"
