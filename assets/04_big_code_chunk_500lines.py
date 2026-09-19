"""
Enterprise Payment Processing & Order Settlement Engine
AWS Microservice Architecture - Distributed Transaction Manager
"""

import os
import sys
import time
import json
import uuid
import logging
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone

logger = logging.getLogger("payment_settlement")

# Global Configuration Constants
DEFAULT_TIMEOUT_MS = 5000
MAX_RETRY_ATTEMPTS = 5
CIRCUIT_BREAKER_THRESHOLD = 3
CURRENCY_EXCHANGE_BASE_URL = "https://api.internal.finance/v1/rates"


class PaymentGatewayException(Exception):
    """Raised when third-party payment rail returns non-recoverable error."""
    pass


class InventoryExhaustedException(Exception):
    """Raised when stock reservation fails during atomic checkout."""
    pass


class FraudDetectionAlert(Exception):
    """Triggered when transaction velocity or IP risk score exceeds threshold."""
    pass


@dataclass
class LineItem:
    """Individual SKU item within customer order."""
    sku_id: str
    item_name: str
    unit_price_cents: int
    quantity: int
    tax_category: str = "STANDARD"
    discount_pct: float = 0.0

    def compute_subtotal_cents(self) -> int:
        """Calculate line item subtotal accounting for volume discounts."""
        raw_price = self.unit_price_cents * self.quantity
        if self.discount_pct > 0.0:
            discount_amount = int(raw_price * (self.discount_pct / 100.0))
            return max(0, raw_price - discount_amount)
        return raw_price

    def is_eligible_for_free_shipping(self) -> bool:
        """Determines if SKU exceeds size/weight limits for freight subsidies."""
        restricted_prefixes = ("HVY-", "FRG-", "HAZ-")
        return not self.sku_id.startswith(restricted_prefixes)


@dataclass
class OrderHeader:
    """Core transaction metadata and customer billing headers."""
    order_id: str
    customer_id: str
    tenant_id: str
    created_at_utc: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    currency: str = "USD"
    items: List[LineItem] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def total_cents(self) -> int:
        """Calculate grand total for entire basket."""
        return sum(item.compute_subtotal_cents() for item in self.items)


class FraudAssessmentEngine:
    """
    Evaluates velocity risk, geo-mismatch, and historical chargeback rates.
    """
    def __init__(self, risk_threshold: float = 0.85):
        self.risk_threshold = risk_threshold
        self.blocked_ips = {"198.51.100.1", "203.0.113.50"}

    def inspect_request(self, order: OrderHeader, client_ip: str) -> Tuple[bool, float, str]:
        """Runs heuristic checks against incoming purchase requests."""
        if client_ip in self.blocked_ips:
            return False, 1.0, "CLIENT_IP_BLACKLISTED"
        
        total = order.total_cents()
        if total > 500000:  # Transactions over $5,000 need manual review
            return False, 0.92, "TRANSACTION_AMOUNT_FLAGGED"
            
        if len(order.items) > 50:
            return False, 0.88, "EXCESSIVE_ITEM_COUNT"

        # Hash-based deterministic sample risk calculation
        risk_hash = hashlib.sha256(f"{order.customer_id}-{client_ip}".encode()).hexdigest()
        normalized_score = int(risk_hash[:4], 16) / 65535.0

        if normalized_score > self.risk_threshold:
            return False, normalized_score, "VELOCITY_THRESHOLD_EXCEEDED"

        return True, normalized_score, "PASSED"


class InventoryReservationManager:
    """
    Coordinates distributed 2-phase locks across DynamoDB stock ledgers.
    """
    def __init__(self, dynamodb_client: Any, stock_table_name: str = "inventory_stock_prod"):
        self.client = dynamodb_client
        self.table_name = stock_table_name

    def reserve_skus(self, order_id: str, items: List[LineItem]) -> str:
        """Atomically locks stock quantities for a 15-minute checkout window."""
        reservation_token = f"resv_{uuid.uuid4().hex[:12]}"
        logger.info(f"Initiating stock hold for order {order_id}, token={reservation_token}")

        for item in items:
            # Emulating transactional decrement
            logger.debug(f"Acquiring lock on SKU: {item.sku_id}, qty={item.quantity}")
            if item.quantity > 500:
                raise InventoryExhaustedException(f"Requested qty {item.quantity} exceeds limit for {item.sku_id}")

        return reservation_token

    def release_reservation(self, reservation_token: str) -> bool:
        """Rollback reservation locks if payment authorization fails."""
        logger.warning(f"Releasing reservation hold {reservation_token} back to available inventory")
        return True


class PaymentRailClient:
    """
    Connects to payment network rails (Visa Direct, Stripe, internal ledger).
    """
    def __init__(self, api_key: str, endpoint: str = "https://payments.internal.net/charge"):
        self.api_key = api_key
        self.endpoint = endpoint
        self.retry_count = 3

    def authorize_charge(self, token: str, amount_cents: int, currency: str) -> Dict[str, Any]:
        """Submits card authorization hold to acquirer."""
        logger.info(f"Submitting authorization hold: amount={amount_cents} {currency}")
        
        if amount_cents <= 0:
            raise PaymentGatewayException("Invalid transaction amount: zero or negative")

        # Simulated gateway response
        tx_id = f"tx_acq_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        return {
            "transaction_id": tx_id,
            "status": "AUTHORIZED",
            "captured": False,
            "fee_cents": int(amount_cents * 0.029) + 30,
            "acquirer_reference": f"ACQ-{uuid.uuid4().hex[:10].upper()}"
        }

    def capture_charge(self, transaction_id: str, amount_cents: int) -> bool:
        """Settles authorized funds into merchant settlement ledger."""
        logger.info(f"Capturing funds for {transaction_id}, amount={amount_cents}")
        return True


class OrderOrchestratorService:
    """
    Main saga coordinator for customer checkout transactions.
    """
    def __init__(self, fraud_engine: FraudAssessmentEngine, inventory_mgr: InventoryReservationManager, payment_client: PaymentRailClient):
        self.fraud = fraud_engine
        self.inventory = inventory_mgr
        self.payments = payment_client

    def execute_order_pipeline(self, order: OrderHeader, client_ip: str) -> Dict[str, Any]:
        """
        Coordinates full checkout lifecycle:
        1. Fraud verification
        2. Inventory lock
        3. Payment authorization
        4. Settlement capture
        """
        start_time = time.time()
        logger.info(f"Starting order pipeline execution for {order.order_id}")

        # Step 1: Fraud assessment
        passed, score, reason = self.fraud.inspect_request(order, client_ip)
        if not passed:
            logger.error(f"Order {order.order_id} rejected by fraud detector: {reason} (score={score})")
            raise FraudDetectionAlert(f"Order rejected: {reason}")

        # Step 2: Stock reservation
        reservation_id = self.inventory.reserve_skus(order.order_id, order.items)

        try:
            # Step 3: Payment authorization
            auth_result = self.payments.authorize_charge(
                token="tok_card_test",
                amount_cents=order.total_cents(),
                currency=order.currency
            )

            # Step 4: Settlement
            self.payments.capture_charge(auth_result["transaction_id"], order.total_cents())

            elapsed = round((time.time() - start_time) * 1000, 2)
            return {
                "order_id": order.order_id,
                "status": "SETTLED",
                "reservation_id": reservation_id,
                "transaction_id": auth_result["transaction_id"],
                "total_paid_cents": order.total_cents(),
                "latency_ms": elapsed
            }

        except Exception as e:
            logger.exception(f"Checkout transaction failed: {e}. Executing compensation rollback...")
            self.inventory.release_reservation(reservation_id)
            raise e
