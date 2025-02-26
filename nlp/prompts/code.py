from langchain_core.prompts import PromptTemplate

code_analysis_template = """
Analyze the following code snippets and identify potential bugs or issues:

Code References:
{code_references}

Potential Bugs:
"""

code_analysis_prompt = PromptTemplate(
    input_variables=["code_references"],
    template=code_analysis_template,
)