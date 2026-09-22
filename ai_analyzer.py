import os
import json

from dotenv import load_dotenv
from openai import OpenAI

from alerts import get_alert_summary


# =========================================================
# Load Environment Variables
# =========================================================

load_dotenv()


# =========================================================
# OpenAI Configuration
# =========================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

OPENAI_MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-4o-mini"
)


# =========================================================
# Validate API Key
# =========================================================

if not OPENAI_API_KEY:

    raise ValueError(
        "OPENAI_API_KEY is not configured in .env"
    )


# =========================================================
# OpenAI Client
# =========================================================

client = OpenAI(
    api_key=OPENAI_API_KEY
)


# =========================================================
# System Prompt
# =========================================================

SYSTEM_PROMPT = """
You are a PostgreSQL DBA Expert and Database Reliability Assistant.

Analyze the PostgreSQL alert JSON provided by the monitoring
system.

The monitoring system has already detected the alert.
Your responsibility is to explain the alert and provide
safe, actionable DBA guidance.

Do not invent facts that are not present in the input.

For a long-running transaction, consider:

- transaction duration
- configured threshold
- transaction state
- query
- wait event
- application
- possible lock retention
- possible impact on vacuum
- possible table bloat

Do not claim that a transaction is blocking another session
unless the input contains evidence of blocking.

Do not assume that an idle transaction is currently
executing a query.

SAFETY RULES:

- Do not execute commands.
- Do not invent database information.
- Prefer investigation before remediation.
- Do not recommend destructive actions as the first step.
- Before recommending pg_terminate_backend(), require
  confirmation that the session is safe to terminate.

Return ONLY valid JSON.

The JSON must have exactly these fields:

{
    "summary": "One sentence summary",
    "root_cause": "Simple explanation of why the alert triggered",
    "impact": "Potential consequences if ignored",
    "suggested_action": [
        "Step 1",
        "Step 2",
        "Step 3"
    ]
}

Rules for the response:

- summary must be exactly one sentence.
- suggested_action must contain 2 or 3 steps.
- Keep all explanations concise.
- No markdown.
- No greetings.
- No additional fields.
"""


# =========================================================
# Analyze Single Alert
# =========================================================

def analyze_alert(alert):
    """
    Send a single PostgreSQL alert to GPT-4o-mini
    and return structured DBA analysis.
    """

    response = client.chat.completions.create(

        model=OPENAI_MODEL,

        temperature=0,

        response_format={
            "type": "json_object"
        },

        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": json.dumps(
                    alert,
                    indent=2,
                    default=str
                )
            }
        ]
    )

    content = response.choices[0].message.content

    return json.loads(content)


# =========================================================
# Analyze All Alerts
# =========================================================

def analyze_alerts(alert_summary):
    """
    Analyze all detected PostgreSQL alerts.
    """

    results = []

    for alert in alert_summary.get("alerts", []):

        analysis = analyze_alert(alert)

        results.append(
            {
                "alert": alert,
                "analysis": analysis
            }
        )

    return results


# =========================================================
# Test
# =========================================================

if __name__ == "__main__":

    print("=" * 70)

    print(
        "POSTGRESQL AI DBA ANALYZER"
    )

    print("=" * 70)

    alert_summary = get_alert_summary()

    print(
        f"\nAlerts detected: "
        f"{alert_summary['alert_count']}"
    )

    if alert_summary["alert_count"] == 0:

        print(
            "\n✅ No alerts found."
        )

        print(
            "Create a long-running transaction "
            "to test the AI analyzer."
        )

    else:

        results = analyze_alerts(
            alert_summary
        )

        for result in results:

            print("\n" + "-" * 70)

            print("AI DBA ANALYSIS")

            print("-" * 70)

            print(
                json.dumps(
                    result["analysis"],
                    indent=4
                )
            )

    print("\n" + "=" * 70)