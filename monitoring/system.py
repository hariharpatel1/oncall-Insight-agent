from typing import Dict, List
from contracts.monitoring import MonitoringQuery, MonitoringData
from monitoring.coralogix.client import CoralogixClient
from monitoring.prometheus.client import PrometheusClient

import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

class MonitoringSystem:
    def __init__(self):
        self.coralogix_client = CoralogixClient()
        self.prometheus_client = PrometheusClient()

    async def query_monitoring_data(self, query: MonitoringQuery) -> MonitoringData:
        """
        Query both metrics and logs data and return combined monitoring data
        
        Args:
            query: MonitoringQuery object containing query parameters
            
        Returns:
            MonitoringData object containing both metrics and logs
        """
        try:
            metrics_data = await self.prometheus_client.query_metrics(query)

            logger.info(f"[Monitoring System] Retrieved metrics data: {metrics_data}")

            logs_data = await self.coralogix_client.query_logs(query)

            logger.info(f"[Monitoring System] Retrieved logs data: {logs_data}")  

            # Return combined data as MonitoringData object
            return MonitoringData(
                metrics=metrics_data,
                logs=logs_data
            )
        except Exception as e:
                logger.info(f"[Monitoring System] Error querying monitoring data: {str(e)}")
                # Return empty monitoring data on error
                return MonitoringData(metrics=[], logs=[])