import json
from typing import List
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import AzureChatOpenAI
from contracts.settings import settings
from contracts.monitoring import Metric, MonitoringQuery
import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

class PrometheusClient:
    def __init__(self):
        self.base_url = settings.prometheus.url

        self.llm = AzureChatOpenAI(
            azure_deployment=settings.azure_openai.deployment_name,
            api_version=settings.azure_openai.api_version,
            azure_endpoint=settings.azure_openai.api_base,
            api_key=settings.azure_openai.api_key,
            temperature=settings.azure_openai.temperature,
        )

        self.query_metrics_prompt = PromptTemplate.from_template("""
            Generate Prometheus metrics based on the following query parameters:
            Query: {query}
            
            Return metrics as a list of JSON objects with format:
            [
                {
                    "name": "metric_name",
                    "value": 123.45,
                    "timestamp": "2024-02-23T13:14:18Z",
                    "type": "counter",
                    "labels": {
                        "service": "api",
                        "endpoint": "/users"
                    }
                }
            ]
            
            Include relevant metrics that might indicate system issues.
        """)

    async def query_metrics(self, query: MonitoringQuery) -> List[Metric]:
        """Query metrics using the new LangChain syntax"""
        try:
            # Prepare query parameters
            query_params = {
                "query": query.metric_name or ".*",
                "start": query.date_range.start if query.date_range else "",
                "end": query.date_range.end if query.date_range else "",
                "step": "5m",
            }
            query_string = " ".join(f"{k}={v}" for k, v in query_params.items())

            logger.info(f"[Prometheus Client] Querying Prometheus metrics: {query_string}")

            # Create chain using the new pipe syntax with JSON parsing
            #chain = self.query_metrics_prompt | self.llm | JsonOutputParser()
            _ = self.query_metrics_prompt | self.llm | JsonOutputParser()
            
            # Run the chain
            #metrics_data = await chain.ainvoke({"query": query_string})

            metrics_data = json.loads(mock_metrics_json)

            logger.info(f"[Prometheus Client] Retrieved Prometheus metrics: {metrics_data}")
            
            # Handle potential string response from chat models
            if isinstance(metrics_data, str):
                metrics_data = json.loads(metrics_data)
            
            # Convert to Metric objects
            return [Metric.model_validate(metric) for metric in metrics_data]
            
        except Exception as e:
            # Add proper error handling
            logger.error(f"Error querying Prometheus metrics: {str(e)}")
            # Return empty list instead of failing
            return []

# Mock Prometheus metrics data for testing
mock_metrics_json = """
[
    {
        "name": "http_request_duration_seconds",
        "value": 2.45,
        "timestamp": "2024-02-23T13:14:18Z",
        "type": "histogram",
        "labels": {
            "service": "api",
            "endpoint": "/users/profile",
            "method": "GET"
        }
    },
    {
        "name": "database_query_duration_seconds",
        "value": 1.89,
        "timestamp": "2024-02-23T13:14:19Z",
        "type": "histogram",
        "labels": {
            "service": "api",
            "query_type": "select",
            "table": "user_profiles"
        }
    },
    {
        "name": "memory_usage_bytes",
        "value": 2847632445,
        "timestamp": "2024-02-23T13:14:20Z",
        "type": "gauge",
        "labels": {
            "service": "api",
            "pod": "api-server-pod-1"
        }
    },
    {
        "name": "cpu_usage_percent",
        "value": 89.5,
        "timestamp": "2024-02-23T13:14:20Z",
        "type": "gauge",
        "labels": {
            "service": "api",
            "pod": "api-server-pod-1"
        }
    },
    {
        "name": "connection_pool_usage",
        "value": 95,
        "timestamp": "2024-02-23T13:14:21Z",
        "type": "gauge",
        "labels": {
            "service": "api",
            "database": "postgres-main"
        }
    },
    {
        "name": "http_requests_total",
        "value": 15234,
        "timestamp": "2024-02-23T13:14:22Z",
        "type": "counter",
        "labels": {
            "service": "api",
            "endpoint": "/users/profile",
            "status": "200"
        }
    },
    {
        "name": "http_request_duration_seconds",
        "value": 3.12,
        "timestamp": "2024-02-23T13:14:23Z",
        "type": "histogram",
        "labels": {
            "service": "api",
            "endpoint": "/users/preferences",
            "method": "GET"
        }
    },
    {
        "name": "cache_hit_ratio",
        "value": 0.45,
        "timestamp": "2024-02-23T13:14:24Z",
        "type": "gauge",
        "labels": {
            "service": "api",
            "cache": "redis-user-cache"
        }
    },
    {
        "name": "network_io_bytes",
        "value": 1458963,
        "timestamp": "2024-02-23T13:14:25Z",
        "type": "counter",
        "labels": {
            "service": "api",
            "direction": "ingress"
        }
    },
    {
        "name": "database_connections",
        "value": 195,
        "timestamp": "2024-02-23T13:14:26Z",
        "type": "gauge",
        "labels": {
            "service": "api",
            "database": "postgres-main"
        }
    },
    {
        "name": "http_error_rate",
        "value": 0.08,
        "timestamp": "2024-02-23T13:14:27Z",
        "type": "gauge",
        "labels": {
            "service": "api",
            "endpoint": "/users/profile"
        }
    },
    {
        "name": "grpc_request_duration_seconds",
        "value": 1.75,
        "timestamp": "2024-02-23T13:14:28Z",
        "type": "histogram",
        "labels": {
            "service": "api",
            "method": "GetUserProfile"
        }
    },
    {
        "name": "thread_pool_active_threads",
        "value": 48,
        "timestamp": "2024-02-23T13:14:29Z",
        "type": "gauge",
        "labels": {
            "service": "api",
            "pool": "request-processor"
        }
    },
    {
        "name": "kafka_consumer_lag",
        "value": 2456,
        "timestamp": "2024-02-23T13:14:30Z",
        "type": "gauge",
        "labels": {
            "service": "api",
            "topic": "user-events"
        }
    },
    {
        "name": "http_request_queue_size",
        "value": 145,
        "timestamp": "2024-02-23T13:14:31Z",
        "type": "gauge",
        "labels": {
            "service": "api",
            "endpoint": "/users/profile"
        }
    },
    {
        "name": "system_load_average_1m",
        "value": 4.25,
        "timestamp": "2024-02-23T13:14:32Z",
        "type": "gauge",
        "labels": {
            "service": "api",
            "node": "node-1"
        }
    },
    {
        "name": "redis_command_duration_seconds",
        "value": 0.89,
        "timestamp": "2024-02-23T13:14:33Z",
        "type": "histogram",
        "labels": {
            "service": "api",
            "command": "GET"
        }
    },
    {
        "name": "jvm_gc_collection_seconds",
        "value": 0.35,
        "timestamp": "2024-02-23T13:14:34Z",
        "type": "histogram",
        "labels": {
            "service": "api",
            "gc": "G1 Young Generation"
        }
    },
    {
        "name": "process_open_fds",
        "value": 856,
        "timestamp": "2024-02-23T13:14:35Z",
        "type": "gauge",
        "labels": {
            "service": "api",
            "pod": "api-server-pod-1"
        }
    },
    {
        "name": "http_client_duration_seconds",
        "value": 1.23,
        "timestamp": "2024-02-23T13:14:36Z",
        "type": "histogram",
        "labels": {
            "service": "api",
            "client": "payment-service"
        }
    }
]
"""
              