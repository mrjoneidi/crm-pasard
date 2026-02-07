import unittest
from app import create_app
from modules.db import db
from modules.models import Case, Person, LeaseContract, Invoice, AuditLog
import io
from datetime import datetime, timedelta

class TestConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'tests/uploads'
    TESTING = True

class TestSystem(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_full_workflow(self):
        # 1. Create Case
        print("1. Creating Case...")
        case_data = {
            "شماره_پرونده": "FULL-001",
            "شماره_کلاسه": "CLS-001",
            "وضعیت": "active",
            "آدرس": "Tehran",
            "توضیحات": "Mother Case"
        }
        res = self.client.post('/api/cases/', json=case_data)
        self.assertEqual(res.status_code, 201)
        case_id = res.get_json()['شناسه']

        # 2. Add Owner
        print("2. Adding Owner...")
        owner_data = {
            "نام_و_نام_خانوادگی": "Reza Shah",
            "کد_ملی": "9998887776",
            "تلفن_همراه": "09120000000"
        }
        res = self.client.post(f'/api/cases/{case_id}/owners', json=owner_data)
        self.assertEqual(res.status_code, 200)

        # 3. Upload Document
        print("3. Uploading Document...")
        doc_data = {
            'file': (io.BytesIO(b"Important deed"), 'deed.txt'),
            'case_id': case_id,
            'title': 'Title Deed',
            'category': 'Deed'
        }
        res = self.client.post('/api/documents/', data=doc_data, content_type='multipart/form-data')
        self.assertEqual(res.status_code, 201)
        doc_id = res.get_json()['شناسه']

        # 4. Subdivide
        print("4. Subdividing...")
        subdivide_data = {
            "reason": "Development",
            "children": [
                {
                    "شماره_پرونده": "FULL-001-A",
                    "شماره_کلاسه": "CLS-001-A",
                    "توضیحات": "Child A",
                    "docs_to_transfer": [doc_id]
                }
            ]
        }
        res = self.client.post(f'/api/cases/{case_id}/subdivide', json=subdivide_data)
        self.assertEqual(res.status_code, 201)
        child_id = res.get_json()[0]['شناسه']

        # Verify document transfer
        child_docs = self.client.get(f'/api/cases/{child_id}').get_json()['اسناد']
        self.assertEqual(len(child_docs), 1)
        self.assertEqual(child_docs[0]['عنوان'], 'Title Deed')

        # 5. Create Contract for Child
        print("5. Creating Contract...")
        # Create tenant manually in DB
        tenant = Person(full_name="Tenant Man", national_id="1112223334")
        db.session.add(tenant)
        db.session.commit()
        tenant_id = tenant.id

        contract_data = {
            "شناسه_پرونده": child_id,
            "شناسه_مستاجر": tenant_id,
            "تاریخ_شروع": datetime.utcnow().date().isoformat(),
            "تاریخ_پایان": (datetime.utcnow() + timedelta(days=365)).date().isoformat(),
            "مبلغ_اجاره_پایه": 5000000,
            "دوره_پرداخت": "monthly"
        }
        res = self.client.post('/api/contracts/', json=contract_data)
        self.assertEqual(res.status_code, 201)

        # 6. Generate Invoice
        print("6. Generating Invoice...")
        res = self.client.post('/api/invoices/generate')
        self.assertEqual(res.status_code, 201)

        # 7. Check Financial Report
        print("7. Checking Report...")
        res = self.client.get('/api/invoices/reports/financial')
        data = res.get_json()
        self.assertEqual(data['تعداد_بدهکاران'], 1)
        self.assertEqual(data['مجموع_بدهی'], 5000000)

        # 8. Check Audit Log
        print("8. Checking Audit Log...")
        # Check for Child creation
        # We need to query using mapped column names or filter by target_id
        logs = AuditLog.query.filter_by(target_id=child_id).all()
        # Filter for Case creation
        case_creation_log = [l for l in logs if l.target_model == 'Case' and l.action == 'create']
        self.assertTrue(len(case_creation_log) > 0)

if __name__ == '__main__':
    unittest.main()
