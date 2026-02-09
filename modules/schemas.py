from modules.db import ma
from modules.models import Case, Person, Ownership, Document, AuditLog, LeaseContract, Invoice
from marshmallow import fields, pre_load, post_dump
from modules.utils import gregorian_to_jalali, jalali_to_gregorian

class JalaliDateField(fields.Field):
    """Custom field to handle Jalali dates."""
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return gregorian_to_jalali(value)

    def _deserialize(self, value, attr, data, **kwargs):
        if value is None:
            return None
        return jalali_to_gregorian(value)

class PersonSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Person
        load_instance = True
        include_fk = True

    id = fields.Int(data_key='شناسه')
    full_name = fields.Str(data_key='نام_و_نام_خانوادگی')
    national_id = fields.Str(data_key='کد_ملی')
    phone = fields.Str(data_key='تلفن_همراه', allow_none=True)
    alt_phone = fields.Str(data_key='تلفن_ثابت', allow_none=True)

class OwnershipSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Ownership
        load_instance = True
        include_fk = True

    id = fields.Int(data_key='شناسه')
    case_id = fields.Int(data_key='شناسه_پرونده')
    person_id = fields.Int(data_key='شناسه_شخص')
    start_date = JalaliDateField(data_key='تاریخ_شروع')
    end_date = JalaliDateField(data_key='تاریخ_پایان', allow_none=True)
    is_current = fields.Bool(data_key='فعال')

    person = fields.Nested(PersonSchema, dump_only=True, data_key='مالک')

class DocumentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Document
        load_instance = True
        include_fk = True

    id = fields.Int(data_key='شناسه')
    case_id = fields.Int(data_key='شناسه_پرونده')
    title = fields.Str(data_key='عنوان')
    description = fields.Str(data_key='توضیحات')
    file_path = fields.Str(data_key='مسیر_فایل')
    category = fields.Str(data_key='دسته_بندی')
    created_at = fields.DateTime(data_key='تاریخ_ثبت')
    document_date = JalaliDateField(data_key='تاریخ_سند', allow_none=True)

class CaseSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Case
        load_instance = True
        include_fk = True

    id = fields.Int(data_key='شناسه')
    case_number = fields.Str(data_key='شماره_پرونده')
    classification_number = fields.Str(data_key='شماره_کلاسه')
    status = fields.Str(data_key='وضعیت')
    address = fields.Str(data_key='آدرس')
    description = fields.Str(data_key='توضیحات')
    created_at = fields.DateTime(data_key='تاریخ_ایجاد')
    parent_id = fields.Int(data_key='شناسه_والد', allow_none=True)

    documents = fields.Nested(DocumentSchema, many=True, dump_only=True, data_key='اسناد')
    ownerships = fields.Nested(OwnershipSchema, many=True, dump_only=True, data_key='سوابق_مالکیت')
    children = fields.Nested('CaseSchema', many=True, dump_only=True, data_key='زیر_پرونده_ها')
    contracts = fields.Nested('LeaseContractSchema', many=True, dump_only=True, data_key='قراردادها')

class AuditLogSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = AuditLog
        load_instance = True

    id = fields.Int(data_key='شناسه')
    user = fields.Str(data_key='کاربر')
    action = fields.Str(data_key='عملیات')
    target_model = fields.Str(data_key='بخش')
    target_id = fields.Int(data_key='شناسه_هدف')
    timestamp = fields.DateTime(data_key='زمان')
    details = fields.Str(data_key='جزئیات')

class InvoiceSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Invoice
        load_instance = True
        include_fk = True

    id = fields.Int(data_key='شناسه')
    contract_id = fields.Int(data_key='شناسه_قرارداد')
    invoice_number = fields.Str(data_key='شماره_صورتحساب')
    amount = fields.Float(data_key='مبلغ')
    due_date = JalaliDateField(data_key='تاریخ_سررسید')
    status = fields.Str(data_key='وضعیت')
    created_at = fields.DateTime(data_key='تاریخ_صدور')

class LeaseContractSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LeaseContract
        load_instance = True
        include_fk = True

    id = fields.Int(data_key='شناسه')
    case_id = fields.Int(data_key='شناسه_پرونده')
    tenant_id = fields.Int(data_key='شناسه_مستاجر')
    start_date = JalaliDateField(data_key='تاریخ_شروع')
    end_date = JalaliDateField(data_key='تاریخ_پایان')
    base_rent = fields.Float(data_key='مبلغ_اجاره_پایه')
    payment_period = fields.Str(data_key='دوره_پرداخت')
    annual_increase_percent = fields.Float(data_key='درصد_افزایش_سالانه')

    tenant = fields.Nested(PersonSchema, dump_only=True, data_key='مستاجر')
    invoices = fields.Nested(InvoiceSchema, many=True, dump_only=True, data_key='صورتحساب_ها')
