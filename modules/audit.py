from sqlalchemy import event, inspect
from modules.db import db
from modules.models import Case, Person, Ownership, Document, AuditLog, LeaseContract, Invoice
import json
from datetime import datetime

# Helper to serialize details
def get_details(target):
    data = {}
    # Use inspector to get attribute names mapping to columns
    insp = inspect(target)
    if not insp:
        return {}

    for attr in insp.mapper.column_attrs:
        key = attr.key # The python attribute name (e.g., 'case_number')
        # We want to store using the DB column name (Persian)
        # attr.columns[0].name should be the DB name
        col_name = attr.columns[0].name

        # Get value
        val = getattr(target, key)

        # Handle datetime serialization if needed, though str(val) covers most
        if val is not None:
             data[col_name] = str(val)

    return data

def _log(connection, target, action):
    # Determine user
    user = "system"

    details = get_details(target)

    audit_table = AuditLog.__table__

    # Map to Persian column names
    values = {
        'کاربر': user,
        'عملیات': action,
        'بخش': target.__class__.__name__,
        'شناسه_هدف': target.id,
        'زمان': datetime.utcnow(),
        'جزئیات': json.dumps(details, ensure_ascii=False)
    }

    connection.execute(
        audit_table.insert().values(**values)
    )

def after_insert_listener(mapper, connection, target):
    _log(connection, target, 'create')

def after_update_listener(mapper, connection, target):
    _log(connection, target, 'update')

def after_delete_listener(mapper, connection, target):
    _log(connection, target, 'delete')

def register_audit_listeners():
    models = [Case, Person, Ownership, Document, LeaseContract, Invoice]
    for model in models:
        event.listen(model, 'after_insert', after_insert_listener)
        event.listen(model, 'after_update', after_update_listener)
        event.listen(model, 'after_delete', after_delete_listener)
