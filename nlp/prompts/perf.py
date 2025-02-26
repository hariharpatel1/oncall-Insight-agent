from langchain_core.prompts import PromptTemplate

performance_analysis_template = """
Analyze the following incident and monitoring data to identify performance bottlenecks:

Incident Details:
{incident_details}

Metrics:
{metrics}

Logs:
{logs}

Performance Bottlenecks:
"""

performance_analysis_prompt = PromptTemplate(
    input_variables=["incident_details", "metrics", "logs"],
    template=performance_analysis_template,
)