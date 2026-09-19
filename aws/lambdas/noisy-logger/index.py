#!/usr/bin/env python3
"""
Squeeze Demo Noisy Logger
Emits realistic high-cardinality repetitive error logs, stack traces,
and simulated test credential leaks into CloudWatch.
Used to demonstrate Squeeze's 85-95% compression and DLP masking.
"""

import sys
import time
import uuid

def lambda_handler(event, context):
    print("=== START OF RUNAWAY MICROSERVICE TRANSACTION LOGS ===")
    
    # 1. Health check heartbeat spam
    for i in range(15):
        t_id = uuid.uuid4()
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        print(f"{now} [INFO] [pool-{i%3}] ConnectionPool.heartbeat: Ping ok to replica-db-primary (latency=1.2ms) txn={t_id}")

    # 2. Leaked test credentials in debug trace (for DLP Secret Shield demonstration)
    print("2026-09-19T14:32:01.102Z [DEBUG] AuthContext initialized with AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE and secret=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY")
    print("2026-09-19T14:32:01.105Z [DEBUG] External gateway initialized with OpenAI API key: sk-proj-abCDefGhIjKlMnOpQrStUvWxYz1234567890")

    # 3. Cascading database failure with repetitive stack traces
    print("2026-09-19T14:32:01.200Z [ERROR] [thread-8841] DatabaseConnectionException: Failed to acquire JDBC connection from hikari-pool-1")
    for attempt in range(1, 12):
        err_id = uuid.uuid4()
        ts = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
        print(f"{ts}.{attempt:03d}Z [WARN]  [thread-{8840+attempt}] Retrying connection to aurora-cluster.internal:5432 (attempt {attempt}/15) reqId={err_id}")
        print(f"Traceback (most recent call last):")
        print(f'  File "/var/task/app/db/pool.py", line 142, in get_connection')
        print(f'    conn = self.driver.connect(host="aurora-cluster.internal", port=5432, timeout=5)')
        print(f'  File "/var/task/vendor/pg_driver/engine.py", line 89, in connect')
        print(f'    raise ConnectionTimeoutError("Timed out waiting for socket ready: 5000ms")')
        print(f'pg_driver.errors.ConnectionTimeoutError: Timed out waiting for socket ready: 5000ms (cluster failover in progress)')

    print("2026-09-19T14:32:03.990Z [FATAL] [thread-8850] CircuitBreaker OPEN for service 'payment-ledger' after 12 consecutive timeouts.")
    print("=== END OF LOG SEQUENCE ===")

    return {
        "statusCode": 200,
        "message": "Emitted 75 noisy, repetitive log lines with stack traces and test credentials to CloudWatch."
    }

if __name__ == "__main__":
    lambda_handler({}, None)
