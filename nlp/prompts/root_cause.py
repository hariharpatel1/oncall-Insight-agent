from langchain_core.prompts import PromptTemplate

root_cause_template = """
Analyze the following incident and determine the most likely root cause:

Incident Details:
{incident_details}

Logs:
{logs}

Code References:
{code_references}

Root Cause:
"""

root_cause_prompt = PromptTemplate(
    input_variables=["incident_details", "logs", "code_references"],
    template=root_cause_template,
)