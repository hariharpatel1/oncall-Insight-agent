from typing import Dict, List, Optional
from langchain_openai import AzureChatOpenAI
from contracts.settings import settings

class AzureOpenAIClient:
    def __init__(self):
        self.llm = AzureChatOpenAI(
            azure_deployment=settings.azure_openai.deployment_name,
            api_version=settings.azure_openai.api_version,
            azure_endpoint=settings.azure_openai.api_base,
            api_key=settings.azure_openai.api_key,
            temperature=settings.azure_openai.temperature,
        )

    async def complete(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """
        Complete a prompt using the Azure OpenAI model.
        """
        messages = [{"role": "user", "content": prompt}]
        response = await self.llm.ainvoke(messages, stop=stop)
        return response.content


# Create a singleton instance
azure_openai_client = AzureOpenAIClient()