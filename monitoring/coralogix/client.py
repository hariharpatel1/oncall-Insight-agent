import json
from typing import List
from langchain_core.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI
from contracts.settings import settings
from contracts.monitoring import LogMessage, MonitoringQuery
import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

class CoralogixClient:
    def __init__(self):
        self.base_url = settings.coralogix.api_url
        self.api_key = settings.coralogix.api_key

        self.llm = AzureChatOpenAI(
            azure_deployment=settings.azure_openai.deployment_name,
            api_version=settings.azure_openai.api_version,
            azure_endpoint=settings.azure_openai.api_base,
            api_key=settings.azure_openai.api_key,
            temperature=settings.azure_openai.temperature,
        )

        self.query_logs_prompt = PromptTemplate.from_template("""
            Generate Coralogix logs based on the following query parameters:
            Query: {query}
            
            Return logs as a list of JSON objects with format:
            [
                {
                    "timestamp": "2024-02-23T13:14:18Z",
                    "level": "error",
                    "message": "Detailed error message",
                    "attributes": {
                        "service": "api",
                        "trace_id": "abc123"
                    }
                }
            ]
            
            Include relevant error and warning logs that might indicate system issues.
        """)

    async def query_logs(self, query: MonitoringQuery) -> List[LogMessage]:
        """Query logs using the new LangChain syntax"""
        try:
            query_params = {
                "query": f"severity:{query.log_level}" if query.log_level else "*",
                "from": query.date_range.start if query.date_range else "",
                "to": query.date_range.end if query.date_range else "",
            }
            query_string = " ".join(f"{k}={v}" for k, v in query_params.items())

            # Create chain using the new pipe syntax
            #chain = self.query_logs_prompt | self.llm
            _ = self.query_logs_prompt | self.llm
            
            logger.info(f"[Coralogix Client] Querying Coralogix logs: {query_string}")

            # Run the chain
            #logs_json = await chain.ainvoke({"query": query_string})

            logs_json = parse_logs(mock_logs_json)

            logger.info(f"[Coralogix Client] Retrieved logs: {logs_json}")
            
           
            # Determine the actual logs data
            # if isinstance(logs_json, str):
            #     logs_data = json.loads(logs_json)
            # elif isinstance(logs_json, list):
            #     logs_data = logs_json  # If it's already a list, use it directly
            # elif hasattr(logs_json, 'content'):
            #     logs_data = logs_json.content  # For chat models
            #     if isinstance(logs_data, str):
            #         logs_data = json.loads(logs_data)
            # else:
            #     logs_data = []
            #     logger.warning("Unexpected logs format received")
                
            #     return [LogMessage(**log) for log in logs_data]

            return logs_json
        except Exception as e:
            logger.error(f"Error querying Coralogix logs: {str(e)}")
            return []
        
# Function to parse logs
def parse_logs(logs_json: str) -> List[LogMessage]:
    try:
        # Parse JSON string to list of dictionaries
        logs_data = json.loads(logs_json)
        
        # Convert numeric values in attributes to strings
        processed_logs = []
        for log in logs_data:
            if log.get('attributes'):
                log['attributes'] = {
                    k: str(v) for k, v in log['attributes'].items()
                }
            processed_logs.append(log)
        
        # Parse using Pydantic model
        return [LogMessage.model_validate(log) for log in processed_logs]
    except Exception as e:
        logger.error(f"Error parsing logs: {str(e)}")
        return []
        
# Mock data for testing
mock_logs_json = """[
    {
        "timestamp": "2024-02-23T13:14:18Z",
        "level": "warn",
        "message": "High database query execution time detected",
        "attributes": {
            "service": "api",
            "trace_id": "abc123def456",
            "query_time_ms": 1890,
            "query_type": "select"
        }
    },
    {
        "timestamp": "2024-02-23T13:14:19Z",
        "level": "error",
        "message": "Connection pool reached 95% capacity",
        "attributes": {
            "service": "api",
            "trace_id": "abc124def457",
            "pool_size": 200,
            "active_connections": 190
        }
    },
    {
        "timestamp": "2024-02-23T13:14:20Z",
        "level": "warn",
        "message": "High memory usage detected",
        "attributes": {
            "service": "api",
            "trace_id": "abc125def458",
            "memory_usage_mb": 2847,
            "threshold_mb": 2500
        }
    },
    {
        "timestamp": "2024-02-23T13:14:21Z",
        "level": "error",
        "message": "Request timeout for /users/profile endpoint",
        "attributes": {
            "service": "api",
            "trace_id": "abc126def459",
            "endpoint": "/users/profile",
            "timeout_ms": 5000
        }
    },
    {
        "timestamp": "2024-02-23T13:14:22Z",
        "level": "warn",
        "message": "Cache miss rate exceeding threshold",
        "attributes": {
            "service": "api",
            "trace_id": "abc127def460",
            "cache_miss_rate": 0.55,
            "threshold": 0.40
        }
    },
    {
        "timestamp": "2024-02-23T13:14:23Z",
        "level": "error",
        "message": "Database connection timeout",
        "attributes": {
            "service": "api",
            "trace_id": "abc128def461",
            "database": "postgres-main",
            "connection_timeout_ms": 3000
        }
    },
    {
        "timestamp": "2024-02-23T13:14:24Z",
        "level": "warn",
        "message": "High CPU utilization on api-server-pod-1",
        "attributes": {
            "service": "api",
            "trace_id": "abc129def462",
            "cpu_usage": 89.5,
            "pod": "api-server-pod-1"
        }
    },
    {
        "timestamp": "2024-02-23T13:14:25Z",
        "level": "error",
        "message": "Redis command execution exceeded timeout",
        "attributes": {
            "service": "api",
            "trace_id": "abc130def463",
            "command": "GET",
            "execution_time_ms": 890
        }
    },
    {
        "timestamp": "2024-02-23T13:14:26Z",
        "level": "warn",
        "message": "Increased error rate detected for /users/profile",
        "attributes": {
            "service": "api",
            "trace_id": "abc131def464",
            "error_rate": 0.08,
            "threshold": 0.05
        }
    },
    {
        "timestamp": "2024-02-23T13:14:27Z",
        "level": "error",
        "message": "Thread pool saturation detected",
        "attributes": {
            "service": "api",
            "trace_id": "abc132def465",
            "active_threads": 48,
            "max_threads": 50
        }
    },
    {
        "timestamp": "2024-02-23T13:14:28Z",
        "level": "warn",
        "message": "Kafka consumer lag increasing",
        "attributes": {
            "service": "api",
            "trace_id": "abc133def466",
            "lag": 2456,
            "topic": "user-events"
        }
    },
    {
        "timestamp": "2024-02-23T13:14:29Z",
        "level": "error",
        "message": "Circuit breaker opened for payment-service",
        "attributes": {
            "service": "api",
            "trace_id": "abc134def467",
            "failure_rate": 0.25,
            "threshold": 0.20
        }
    },
    {
        "timestamp": "2024-02-23T13:14:30Z",
        "level": "warn",
        "message": "High network I/O detected",
        "attributes": {
            "service": "api",
            "trace_id": "abc135def468",
            "bytes_transferred": 1458963,
            "direction": "ingress"
        }
    },
    {
        "timestamp": "2024-02-23T13:14:31Z",
        "level": "error",
        "message": "Garbage collection duration exceeded threshold",
        "attributes": {
            "service": "api",
            "trace_id": "abc136def469",
            "gc_duration_ms": 350,
            "threshold_ms": 250
        }
    },
    {
        "timestamp": "2024-02-23T13:14:32Z",
        "level": "warn",
        "message": "System load average exceeding threshold",
        "attributes": {
            "service": "api",
            "trace_id": "abc137def470",
            "load_average": 4.25,
            "threshold": 3.0
        }
    },
    {
        "timestamp": "2024-02-23T13:14:33Z",
        "level": "error",
        "message": "HTTP request queue building up",
        "attributes": {
            "service": "api",
            "trace_id": "abc138def471",
            "queue_size": 145,
            "threshold": 100
        }
    },
    {
        "timestamp": "2024-02-23T13:14:34Z",
        "level": "warn",
        "message": "Slow gRPC request processing",
        "attributes": {
            "service": "api",
            "trace_id": "abc139def472",
            "method": "GetUserProfile",
            "duration_ms": 1750
        }
    },
    {
        "timestamp": "2024-02-23T13:14:35Z",
        "level": "error",
        "message": "Database connection pool exhaustion imminent",
        "attributes": {
            "service": "api",
            "trace_id": "abc140def473",
            "available_connections": 5,
            "total_connections": 200
        }
    },
    {
        "timestamp": "2024-02-23T13:14:36Z",
        "level": "warn",
        "message": "High number of open file descriptors",
        "attributes": {
            "service": "api",
            "trace_id": "abc141def474",
            "open_fds": 856,
            "max_fds": 1024
        }
    },
    {
        "timestamp": "2024-02-23T13:14:37Z",
        "level": "error",
        "message": "Cache eviction rate spike detected",
        "attributes": {
            "service": "api",
            "trace_id": "abc142def475",
            "eviction_rate": 256,
            "threshold": 200
        }
    },
    {
        "timestamp": "2024-02-23T13:14:38Z",
        "level": "warn",
        "message": "Increased latency in payment service integration",
        "attributes": {
            "service": "api",
            "trace_id": "abc143def476",
            "latency_ms": 1230,
            "threshold_ms": 1000
        }
    },
    {
        "timestamp": "2024-02-23T13:14:39Z",
        "level": "error",
        "message": "Deadlock detected in thread pool",
        "attributes": {
            "service": "api",
            "trace_id": "abc144def477",
            "thread_pool": "request-processor",
            "blocked_threads": 12
        }
    },
    {
        "timestamp": "2024-02-23T13:14:40Z",
        "level": "warn",
        "message": "Unusual spike in authentication failures",
        "attributes": {
            "service": "api",
            "trace_id": "abc145def478",
            "failure_count": 45,
            "time_window_minutes": 5
        }
    },
    {
        "timestamp": "2024-02-23T13:14:41Z",
        "level": "error",
        "message": "Redis cluster node disconnection",
        "attributes": {
            "service": "api",
            "trace_id": "abc146def479",
            "node_id": "redis-node-3",
            "disconnection_duration_s": 25
        }
    },
    {
        "timestamp": "2024-02-23T13:14:42Z",
        "level": "warn",
        "message": "API rate limit approaching threshold",
        "attributes": {
            "service": "api",
            "trace_id": "abc147def480",
            "current_rate": 950,
            "limit": 1000
        }
    },
    {
        "timestamp": "2024-02-23T13:14:43Z",
        "level": "error",
        "message": "Elasticsearch query timeout",
        "attributes": {
            "service": "api",
            "trace_id": "abc148def481",
            "query_type": "complex_aggregation",
            "timeout_ms": 5000
        }
    },
    {
        "timestamp": "2024-02-23T13:14:44Z",
        "level": "warn",
        "message": "JWT token validation delays",
        "attributes": {
            "service": "api",
            "trace_id": "abc149def482",
            "validation_time_ms": 250,
            "threshold_ms": 200
        }
    },
    {
        "timestamp": "2024-02-23T13:14:45Z",
        "level": "error",
        "message": "Connection reset by external payment gateway",
        "attributes": {
            "service": "api",
            "trace_id": "abc150def483",
            "gateway": "stripe-api",
            "retry_attempt": 2
        }
    }
]"""