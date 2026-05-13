import html

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from app.core.cache import is_redis_available
from app.core.metrics import get_metrics


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/metrics")
def read_metrics():
    return get_metrics()


@router.get("/health")
def health_check():
    redis_status = "connected" if is_redis_available() else "unavailable"
    return {
        "status": "healthy",
        "redis": redis_status,
    }


@router.get("/", response_class=HTMLResponse)
def dashboard_page():
    metrics = get_metrics()
    redis_status = "connected" if is_redis_available() else "unavailable"
    endpoints = html.escape(str(metrics["endpoints"]))
    status_codes = html.escape(str(metrics["status_codes"]))
    cache_metrics = html.escape(str(metrics["cache"]))
    recent_errors = html.escape(str(metrics["recent_errors"]))

    html_content = f"""
    <html>
        <head>
            <title>Monitoring Dashboard</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 40px;
                    background-color: #f4f4f4;
                }}
                .card {{
                    background: white;
                    padding: 20px;
                    margin-bottom: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }}
                h1 {{
                    color: #333;
                }}
                h2 {{
                    color: #555;
                }}
                .grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                    gap: 16px;
                }}
                pre {{
                    background: #eee;
                    padding: 10px;
                    border-radius: 8px;
                }}
            </style>
        </head>
        <body>
            <h1>Blog Monitoring Dashboard</h1>

            <div class="grid">
                <div class="card">
                    <h2>Total Requests</h2>
                    <p>{metrics["total_requests"]}</p>
                </div>

                <div class="card">
                    <h2>Total Errors</h2>
                    <p>{metrics["total_errors"]}</p>
                </div>

                <div class="card">
                    <h2>Average Response Time</h2>
                    <p>{metrics["average_response_time_ms"]} ms</p>
                </div>

                <div class="card">
                    <h2>System Health</h2>
                    <p>API healthy, Redis {redis_status}</p>
                </div>
            </div>

            <div class="card">
                <h2>Cache Hits and Misses</h2>
                <pre>{cache_metrics}</pre>
            </div>

            <div class="card">
                <h2>Requests Per Endpoint</h2>
                <pre>{endpoints}</pre>
            </div>

            <div class="card">
                <h2>Status Codes</h2>
                <pre>{status_codes}</pre>
            </div>

            <div class="card">
                <h2>Recent Error Logs</h2>
                <pre>{recent_errors}</pre>
            </div>
        </body>
    </html>
    """

    return html_content
