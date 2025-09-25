import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from models import DonHang, PaymentTransaction, PaymentStatus


def generate_txn_ref() -> str:
    return "VNP" + datetime.utcnow().strftime("%y%m%d%H%M%S") + uuid.uuid4().hex[:6].upper()


def get_order_amount(db: Session, order_id: int) -> Optional[float]:
    order = db.query(DonHang).filter(DonHang.id == order_id).first()
    if not order:
        return None
    return float(order.tong_tien or 0.0)


def create_transaction(db: Session, order_id: int, amount: float, method: str = "vnpay") -> PaymentTransaction:
    txn = PaymentTransaction(
        transaction_id=uuid.uuid4().hex,
        don_hang_id=order_id,
        payment_method=method,
        amount=amount,
        currency="VND",
        status=PaymentStatus.PENDING,
        gateway_reference=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(txn)
    db.commit()
    db.refresh(txn)
    return txn


def set_txn_gateway_ref(db: Session, txn_id: str, gateway_ref: str) -> None:
    txn = db.query(PaymentTransaction).filter(PaymentTransaction.transaction_id == txn_id).first()
    if not txn:
        return
    txn.gateway_reference = gateway_ref
    txn.updated_at = datetime.utcnow()
    db.commit()


def update_status_by_ref(db: Session, gateway_ref: str, status: PaymentStatus) -> Optional[PaymentTransaction]:
    txn = db.query(PaymentTransaction).filter(PaymentTransaction.gateway_reference == gateway_ref).first()
    if not txn:
        return None
    # idempotent: if already final success/failed/refunded, do not downgrade
    if txn.status == status:
        return txn
    txn.status = status
    txn.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(txn)
    return txn