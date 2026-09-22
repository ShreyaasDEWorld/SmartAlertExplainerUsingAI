import streamlit as st

from alerts import get_alert_summary
from ai_analyzer import analyze_alerts


# =========================================================
# Page Configuration
# =========================================================

st.set_page_config(
    page_title="PostgreSQL AI DBA Assistant",
    page_icon="🛢️",
    layout="wide"
)


# =========================================================
# Header
# =========================================================

st.title("🛢️ PostgreSQL AI DBA Assistant")

st.caption(
    "MVP - Long-Running Transaction Monitoring"
)


# =========================================================
# Refresh Button
# =========================================================

if st.button("🔄 Check Database"):

    with st.spinner("Checking PostgreSQL..."):

        # ---------------------------------------------
        # Step 1: Get alerts
        # ---------------------------------------------

        alert_summary = get_alert_summary()

        # ---------------------------------------------
        # Store in session state
        # ---------------------------------------------

        st.session_state["alert_summary"] = alert_summary

        # ---------------------------------------------
        # Step 2: Analyze alerts with AI
        # ---------------------------------------------

        if alert_summary["alert_count"] > 0:

            with st.spinner(
                "Analyzing alerts with GPT-4o-mini..."
            ):

                ai_results = analyze_alerts(
                    alert_summary
                )

                st.session_state["ai_results"] = ai_results

        else:

            st.session_state["ai_results"] = []


# =========================================================
# Default State
# =========================================================

alert_summary = st.session_state.get(
    "alert_summary",
    None
)

ai_results = st.session_state.get(
    "ai_results",
    []
)


# =========================================================
# No Check Yet
# =========================================================

if alert_summary is None:

    st.info(
        "Click **Check Database** to run the PostgreSQL health check."
    )

    st.stop()


# =========================================================
# KPI Section
# =========================================================

alert_count = alert_summary["alert_count"]

col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Database",
        "PostgreSQL"
    )


with col2:

    st.metric(
        "Alert Type",
        "Long Running Transaction"
    )


with col3:

    st.metric(
        "Alerts",
        alert_count
    )


st.divider()


# =========================================================
# No Alerts
# =========================================================

if alert_count == 0:

    st.success(
        "✅ No long-running transactions detected."
    )

    st.stop()


# =========================================================
# Alert Details
# =========================================================

st.subheader("🚨 Database Alert")


for index, alert in enumerate(
    alert_summary["alerts"]
):

    details = alert["details"]

    st.warning(
        f"{alert['severity']} - "
        f"Long-running transaction detected"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "PID",
            details["pid"]
        )

    with col2:

        st.metric(
            "Duration",
            f"{details['transaction_duration_seconds']} sec"
        )

    with col3:

        st.metric(
            "Threshold",
            f"{details['threshold_seconds']} sec"
        )

    with col4:

        st.metric(
            "State",
            details["state"]
        )

    st.write(
        f"**Database:** {alert['database']}"
    )

    st.write(
        f"**User:** {details['username']}"
    )

    st.write(
        f"**Application:** "
        f"{details['application_name']}"
    )

    st.write(
        f"**Wait Event:** "
        f"{details['wait_event']}"
    )

    st.write("**Query:**")

    st.code(
        details["query"],
        language="sql"
    )

    st.divider()


# =========================================================
# AI Analysis
# =========================================================

st.subheader("🤖 AI DBA Analysis")


for result in ai_results:

    analysis = result["analysis"]

    # -----------------------------------------------------
    # Summary
    # -----------------------------------------------------

    st.markdown("### Summary")

    st.write(
        analysis["summary"]
    )

    # -----------------------------------------------------
    # Root Cause
    # -----------------------------------------------------

    st.markdown("### Root Cause")

    st.write(
        analysis["root_cause"]
    )

    # -----------------------------------------------------
    # Impact
    # -----------------------------------------------------

    st.markdown("### Impact")

    st.write(
        analysis["impact"]
    )

    # -----------------------------------------------------
    # Suggested Action
    # -----------------------------------------------------

    st.markdown("### Suggested Action")

    for step in analysis["suggested_action"]:

        st.write(
            f"➡️ {step}"
        )