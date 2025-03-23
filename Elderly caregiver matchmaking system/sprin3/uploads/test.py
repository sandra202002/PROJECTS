from app import db
from models import Payment

pending_payouts = Payment.query.filter_by(status="pending").all()
print(pending_payouts)
