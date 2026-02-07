from flask import Blueprint, request, jsonify
from modules.db import db
from modules.models import Invoice, LeaseContract
from modules.schemas import InvoiceSchema
from datetime import datetime, timedelta
import uuid

invoices_bp = Blueprint('invoices', __name__)
invoice_schema = InvoiceSchema()
invoices_schema = InvoiceSchema(many=True)

@invoices_bp.route('/generate', methods=['POST'])
def generate_invoices():
    # Simplified logic to create invoices for due contracts
    generated = []
    today = datetime.utcnow().date()

    # Get active contracts
    contracts = LeaseContract.query.filter(LeaseContract.end_date >= today).all()

    for contract in contracts:
        # Check last invoice
        last_invoice = Invoice.query.filter_by(contract_id=contract.id).order_by(Invoice.created_at.desc()).first()

        # Determine next due date
        # If no previous invoice, use contract start date
        if not last_invoice:
            next_due_date = contract.start_date
        else:
            # Simple assumption: periods are days
            if contract.payment_period == 'monthly':
                next_due_date = last_invoice.due_date + timedelta(days=30)
            elif contract.payment_period == 'yearly':
                next_due_date = last_invoice.due_date + timedelta(days=365)
            else:
                 # Default monthly
                 next_due_date = last_invoice.due_date + timedelta(days=30)

        # If due date is passed or today, generate invoice
        if next_due_date <= today:
            # Calculate amount (apply increase if > 1 year)
            years_passed = (today - contract.start_date).days // 365
            amount = contract.base_rent

            # Simple compounding
            if years_passed > 0 and contract.annual_increase_percent > 0:
                amount = amount * ((1 + contract.annual_increase_percent/100) ** years_passed)

            new_invoice = Invoice(
                contract_id=contract.id,
                invoice_number=str(uuid.uuid4()), # Unique
                amount=amount,
                due_date=next_due_date,
                status='unpaid',
                created_at=datetime.utcnow()
            )
            db.session.add(new_invoice)
            generated.append(new_invoice)

    if generated:
        db.session.commit()

    return jsonify(invoices_schema.dump(generated)), 201

@invoices_bp.route('/', methods=['GET'])
def get_invoices():
    invoices = Invoice.query.all()
    return jsonify(invoices_schema.dump(invoices))

@invoices_bp.route('/reports/financial', methods=['GET'])
def financial_report():
    total_unpaid = Invoice.query.filter_by(status='unpaid').count()
    total_amount_due = db.session.query(db.func.sum(Invoice.amount)).filter_by(status='unpaid').scalar() or 0

    return jsonify({
        'تعداد_بدهکاران': total_unpaid,
        'مجموع_بدهی': total_amount_due
    })
