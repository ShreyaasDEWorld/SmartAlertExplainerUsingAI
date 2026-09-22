import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


# ---------------------------------------------------------
# Database Connection
# ---------------------------------------------------------

def get_connection():
    """
    Create and return a PostgreSQL database connection.
    """

    connection = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

    return connection


# ---------------------------------------------------------
# Test Database Connection
# ---------------------------------------------------------

def test_connection():
    """
    Test PostgreSQL connectivity and return basic DB details.
    """

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                current_database(),
                current_user,
                version();
        """)

        result = cursor.fetchone()

        return {
            "status": "UP",
            "database": result[0],
            "user": result[1],
            "version": result[2]
        }

    except Exception as e:

        return {
            "status": "DOWN",
            "error": str(e)
        }

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ---------------------------------------------------------
# Get Active PostgreSQL Sessions
# ---------------------------------------------------------

def get_active_sessions():
    """
    Return currently active PostgreSQL sessions.

    pg_stat_activity is the main PostgreSQL monitoring view
    we will use for our DBA monitoring MVP.
    """

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor()

        query = """
            SELECT
                pid,
                usename,
                datname,
                state,
                application_name,
                client_addr,
                backend_start,
                xact_start,
                query_start,
                wait_event_type,
                wait_event,
                query
            FROM pg_stat_activity
            WHERE pid <> pg_backend_pid()
            ORDER BY query_start;
        """

        cursor.execute(query)

        rows = cursor.fetchall()

        columns = [
            "pid",
            "username",
            "database",
            "state",
            "application_name",
            "client_addr",
            "backend_start",
            "transaction_start",
            "query_start",
            "wait_event_type",
            "wait_event",
            "query"
        ]

        sessions = []

        for row in rows:

            session = dict(zip(columns, row))

            sessions.append(session)

        return sessions

    except Exception as e:

        print("Error while collecting active sessions:", e)

        return []

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ---------------------------------------------------------
# Get Long Running Transactions
# ---------------------------------------------------------

def get_long_running_transactions(threshold_seconds=300):
    """
    Find transactions that have been open longer than
    the configured threshold.

    Default:
        300 seconds = 5 minutes
    """

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor()

        query = """
            SELECT
                pid,
                usename,
                datname,
                state,
                application_name,
                client_addr,
                xact_start,
                query_start,
                NOW() - xact_start AS transaction_duration,
                wait_event_type,
                wait_event,
                query
            FROM pg_stat_activity
            WHERE
                xact_start IS NOT NULL
                AND pid <> pg_backend_pid()
                AND NOW() - xact_start >
                    (%s * INTERVAL '1 second')
            ORDER BY xact_start;
        """

        cursor.execute(query, (threshold_seconds,))

        rows = cursor.fetchall()

        columns = [
            "pid",
            "username",
            "database",
            "state",
            "application_name",
            "client_addr",
            "transaction_start",
            "query_start",
            "transaction_duration",
            "wait_event_type",
            "wait_event",
            "query"
        ]

        transactions = []

        for row in rows:

            transaction = dict(zip(columns, row))

            transactions.append(transaction)

        return transactions

    except Exception as e:

        print("Error while collecting long-running transactions:", e)

        return []

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ---------------------------------------------------------
# Main Test
# ---------------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("POSTGRESQL DBA MONITOR")
    print("=" * 60)

    # -----------------------------------------------------
    # Test 1: Database Connection
    # -----------------------------------------------------

    print("\n1. Testing database connection...")

    db_status = test_connection()

    print(db_status)

    # -----------------------------------------------------
    # Test 2: Active Sessions
    # -----------------------------------------------------

    print("\n2. Getting active PostgreSQL sessions...")

    sessions = get_active_sessions()

    print(f"Total sessions found: {len(sessions)}")

    for session in sessions:

        print("-" * 60)

        print("PID:", session["pid"])
        print("User:", session["username"])
        print("Database:", session["database"])
        print("State:", session["state"])
        print("Application:", session["application_name"])
        print("Transaction Start:", session["transaction_start"])
        print("Query Start:", session["query_start"])
        print("Wait Event:", session["wait_event"])
        print("Query:", session["query"])

    # -----------------------------------------------------
    # Test 3: Long Running Transactions
    # -----------------------------------------------------

    print("\n3. Checking long-running transactions...")

    #threshold = 300
    threshold = 30     # this is testing case #

    transactions = get_long_running_transactions(
        threshold_seconds=threshold
    )

    print(
        f"Transactions running longer than "
        f"{threshold} seconds: {len(transactions)}"
    )

    for transaction in transactions:

        print("-" * 60)

        print("PID:", transaction["pid"])
        print("User:", transaction["username"])
        print("Database:", transaction["database"])
        print("State:", transaction["state"])
        print(
            "Transaction Duration:",
            transaction["transaction_duration"]
        )
        print("Wait Event:", transaction["wait_event"])
        print("Query:", transaction["query"])

    print("\n" + "=" * 60)
    print("MONITORING TEST COMPLETED")
    print("=" * 60)