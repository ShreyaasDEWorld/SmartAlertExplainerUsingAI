import os
import json
from datetime import datetime, timezone

from dotenv import load_dotenv

from db import get_long_running_transactions


# =========================================================
# Load Environment Variables
# =========================================================

load_dotenv()


# =========================================================
# Configuration
# =========================================================

LONG_RUNNING_THRESHOLD_SECONDS = int(
    os.getenv("LONG_RUNNING_THRESHOLD_SECONDS", "300")
)


# =========================================================
# Long-Running Transaction Detection
# =========================================================

def check_long_running_transactions():
    """
    Detect PostgreSQL transactions that have exceeded
    the configured duration threshold.
    """

    transactions = get_long_running_transactions(
        threshold_seconds=LONG_RUNNING_THRESHOLD_SECONDS
    )

    alerts = []

    for transaction in transactions:

        # -------------------------------------------------
        # Calculate transaction duration
        # -------------------------------------------------

        duration = transaction["transaction_duration"]

        duration_seconds = int(
            duration.total_seconds()
        )

        # -------------------------------------------------
        # Determine severity
        # -------------------------------------------------

        if duration_seconds >= 900:
            severity = "CRITICAL"

        elif duration_seconds >= 300:
            severity = "HIGH"

        else:
            severity = "MEDIUM"

        # -------------------------------------------------
        # Create standardized alert
        # -------------------------------------------------

        alert = {
            "alert_type": "long_running_transaction",

            "severity": severity,

            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),

            "database": transaction["database"],

            "details": {

                "pid": transaction["pid"],

                "username": transaction["username"],

                "state": transaction["state"],

                "application_name": (
                    transaction["application_name"]
                ),

                "client_addr": (
                    str(transaction["client_addr"])
                    if transaction["client_addr"]
                    else None
                ),

                "transaction_start": (
                    transaction["transaction_start"].isoformat()
                    if transaction["transaction_start"]
                    else None
                ),

                "query_start": (
                    transaction["query_start"].isoformat()
                    if transaction["query_start"]
                    else None
                ),

                "transaction_duration_seconds": (
                    duration_seconds
                ),

                "threshold_seconds": (
                    LONG_RUNNING_THRESHOLD_SECONDS
                ),

                "wait_event_type": (
                    transaction["wait_event_type"]
                ),

                "wait_event": (
                    transaction["wait_event"]
                ),

                "query": transaction["query"]
            }
        }

        alerts.append(alert)

    return alerts


# =========================================================
# Alert Summary
# =========================================================

def get_alert_summary():
    """
    Return a standardized alert payload.

    This object will later be sent to GPT-4o-mini.
    """

    alerts = check_long_running_transactions()

    return {
        "alert_count": len(alerts),
        "alerts": alerts
    }


# =========================================================
# Test
# =========================================================

if __name__ == "__main__":

    print("=" * 70)

    print(
        "POSTGRESQL LONG-RUNNING TRANSACTION ALERT ENGINE"
    )

    print("=" * 70)

    print(
        f"\nConfigured threshold: "
        f"{LONG_RUNNING_THRESHOLD_SECONDS} seconds"
    )

    result = get_alert_summary()

    print("\nAlert Summary:")

    print(
        json.dumps(
            result,
            indent=4,
            default=str
        )
    )

    print("\n" + "=" * 70)