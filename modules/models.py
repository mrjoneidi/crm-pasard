from modules.db import db
from datetime import datetime
import json
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(256))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Case(db.Model):
    __tablename__ = 'cases'
    id = db.Column('شناسه', db.Integer, primary_key=True)
    case_number = db.Column('شماره_پرونده', db.String(50), unique=True, nullable=False, index=True)
    classification_number = db.Column('شماره_کلاسه', db.String(50), index=True)
    status = db.Column('وضعیت', db.String(20), default='active')
    address = db.Column('آدرس', db.Text)
    description = db.Column('توضیحات', db.Text)
    created_at = db.Column('تاریخ_ایجاد', db.DateTime, default=datetime.utcnow)
    parent_id = db.Column('شناسه_والد', db.Integer, db.ForeignKey('cases.شناسه'), nullable=True)

    # Relationships
    children = db.relationship('Case', backref=db.backref('parent', remote_side=[id]))
    documents = db.relationship('Document', backref='case', lazy=True)
    ownerships = db.relationship('Ownership', backref='case', lazy=True)
    contracts = db.relationship('LeaseContract', backref='case', lazy=True)

    def __repr__(self):
        return f'<Case {self.case_number}>'

class Person(db.Model):
    __tablename__ = 'people'
    id = db.Column('شناسه', db.Integer, primary_key=True)
    full_name = db.Column('نام_و_نام_خانوادگی', db.String(100), nullable=False, index=True)
    national_id = db.Column('کد_ملی', db.String(20), unique=True, nullable=False, index=True)
    phone = db.Column('تلفن_همراه', db.String(20))
    alt_phone = db.Column('تلفن_ثابت', db.String(20))

    # Relationships
    ownerships = db.relationship('Ownership', backref='person', lazy=True)
    contracts = db.relationship('LeaseContract', backref='tenant', lazy=True)

    def __repr__(self):
        return f'<Person {self.full_name}>'

class Ownership(db.Model):
    __tablename__ = 'ownerships'
    id = db.Column('شناسه', db.Integer, primary_key=True)
    case_id = db.Column('شناسه_پرونده', db.Integer, db.ForeignKey('cases.شناسه'), nullable=False)
    person_id = db.Column('شناسه_شخص', db.Integer, db.ForeignKey('people.شناسه'), nullable=False)
    start_date = db.Column('تاریخ_شروع', db.Date, nullable=False)
    end_date = db.Column('تاریخ_پایان', db.Date, nullable=True)
    is_current = db.Column('فعال', db.Boolean, default=True)

class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column('شناسه', db.Integer, primary_key=True)
    case_id = db.Column('شناسه_پرونده', db.Integer, db.ForeignKey('cases.شناسه'), nullable=False)
    title = db.Column('عنوان', db.String(100), nullable=False, index=True)
    description = db.Column('توضیحات', db.Text)
    file_path = db.Column('مسیر_فایل', db.String(255), nullable=False)
    category = db.Column('دسته_بندی', db.String(50))
    created_at = db.Column('تاریخ_ثبت', db.DateTime, default=datetime.utcnow)
    document_date = db.Column('تاریخ_سند', db.Date, nullable=True)

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column('شناسه', db.Integer, primary_key=True)
    user = db.Column('کاربر', db.String(50)) # Placeholder for user system
    action = db.Column('عملیات', db.String(50))
    target_model = db.Column('بخش', db.String(50))
    target_id = db.Column('شناسه_هدف', db.Integer)
    timestamp = db.Column('زمان', db.DateTime, default=datetime.utcnow)
    details = db.Column('جزئیات', db.Text) # JSON string

    def set_details(self, details_dict):
        self.details = json.dumps(details_dict, ensure_ascii=False)

    def get_details(self):
        return json.loads(self.details) if self.details else {}

class LeaseContract(db.Model):
    __tablename__ = 'lease_contracts'
    id = db.Column('شناسه', db.Integer, primary_key=True)
    case_id = db.Column('شناسه_پرونده', db.Integer, db.ForeignKey('cases.شناسه'), nullable=False)
    tenant_id = db.Column('شناسه_مستاجر', db.Integer, db.ForeignKey('people.شناسه'), nullable=False)
    start_date = db.Column('تاریخ_شروع', db.Date, nullable=False)
    end_date = db.Column('تاریخ_پایان', db.Date, nullable=False)
    base_rent = db.Column('مبلغ_اجاره_پایه', db.Float, nullable=False)
    payment_period = db.Column('دوره_پرداخت', db.String(20)) # monthly, quarterly, yearly
    annual_increase_percent = db.Column('درصد_افزایش_سالانه', db.Float, default=0.0)

    invoices = db.relationship('Invoice', backref='contract', lazy=True)

class Invoice(db.Model):
    __tablename__ = 'invoices'
    id = db.Column('شناسه', db.Integer, primary_key=True)
    contract_id = db.Column('شناسه_قرارداد', db.Integer, db.ForeignKey('lease_contracts.شناسه'), nullable=False)
    invoice_number = db.Column('شماره_صورتحساب', db.String(50), unique=True, nullable=False)
    amount = db.Column('مبلغ', db.Float, nullable=False)
    due_date = db.Column('تاریخ_سررسید', db.Date, nullable=False)
    status = db.Column('وضعیت', db.String(20), default='unpaid')
    created_at = db.Column('تاریخ_صدور', db.DateTime, default=datetime.utcnow)
