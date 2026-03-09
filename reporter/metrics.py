import os
from datetime import datetime, timezone
from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v2.api.metrics_api import MetricsApi
from datadog_api_client.v2.model.metric_intake_type import MetricIntakeType
from datadog_api_client.v2.model.metric_payload import MetricPayload
from datadog_api_client.v2.model.metric_series import MetricSeries
from datadog_api_client.v2.model.metric_point import MetricPoint

def push_metrics(report):
    api_key = os.getenv("DD_API_KEY")
    site = os.getenv("DD_SITE", "us5.datadoghq.com")

    if not api_key:
        print("No DD_API_KEY found, skipping Datadog metrics.")
        return

    configuration = Configuration()
    configuration.api_key["apiKeyAuth"] = api_key
    configuration.server_variables["site"] = site

    now = int(datetime.now(timezone.utc).timestamp())

    total = report["deployment"]["total_boards"]
    success = report["deployment"]["successful"]
    failed = report["deployment"]["failed"]
    severity_map = {"LOW": 0, "HIGH": 1, "CRITICAL": 2}
    severity_score = severity_map.get(report["severity"], 0)

    series = [
        MetricSeries(
            metric="deploymate.boards.total",
            type=MetricIntakeType.GAUGE,
            points=[MetricPoint(timestamp=now, value=float(total))],
            tags=["project:deploymate"]
        ),
        MetricSeries(
            metric="deploymate.boards.success",
            type=MetricIntakeType.GAUGE,
            points=[MetricPoint(timestamp=now, value=float(success))],
            tags=["project:deploymate"]
        ),
        MetricSeries(
            metric="deploymate.boards.failed",
            type=MetricIntakeType.GAUGE,
            points=[MetricPoint(timestamp=now, value=float(failed))],
            tags=["project:deploymate"]
        ),
        MetricSeries(
            metric="deploymate.severity.score",
            type=MetricIntakeType.GAUGE,
            points=[MetricPoint(timestamp=now, value=float(severity_score))],
            tags=["project:deploymate", f"severity:{report['severity'].lower()}"]
        ),
    ]

    with ApiClient(configuration) as api_client:
        api = MetricsApi(api_client)
        response = api.submit_metrics(body=MetricPayload(series=series))
        print(f"Metrics pushed to Datadog: {response['errors'] or 'OK'}")