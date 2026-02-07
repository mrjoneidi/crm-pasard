from flask import Blueprint, request, jsonify
from modules.db import db
from modules.models import Case, Person, Ownership, Document
from modules.schemas import CaseSchema, PersonSchema, OwnershipSchema
from sqlalchemy import or_
from datetime import datetime

cases_bp = Blueprint('cases', __name__)

case_schema = CaseSchema()
cases_schema = CaseSchema(many=True)
person_schema = PersonSchema()

@cases_bp.route('/', methods=['POST'])
def create_case():
    """
    Create a new Case (Parvandeh)
    ---
    tags:
      - Cases
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            شماره_پرونده:
              type: string
              example: "1001"
            شماره_کلاسه:
              type: string
              example: "C1001"
            وضعیت:
              type: string
              example: "active"
            آدرس:
              type: string
              example: "Tehran, Valiasr St"
            توضیحات:
              type: string
              example: "New case description"
    responses:
      201:
        description: Case created successfully
      400:
        description: Error creating case
    """
    data = request.get_json()

    # Extract owner data before validation as it's not part of Case model
    owner_name = data.pop('owner_name', None)
    owner_national_id = data.pop('owner_national_id', None)
    owner_phone = data.pop('owner_phone', None)
    owner_alt_phone = data.pop('owner_alt_phone', None)

    try:
        new_case = case_schema.load(data, session=db.session)
        db.session.add(new_case)
        db.session.flush()

        # Handle initial owner if provided
        if owner_national_id:
            person = Person.query.filter_by(national_id=owner_national_id).first()
            if not person:
                person = Person(
                    full_name=owner_name,
                    national_id=owner_national_id,
                    phone=owner_phone,
                    alt_phone=owner_alt_phone
                )
                db.session.add(person)
                db.session.flush()

            ownership = Ownership(
                case_id=new_case.id,
                person_id=person.id,
                start_date=datetime.utcnow().date(),
                is_current=True
            )
            db.session.add(ownership)

        db.session.commit()
        return case_schema.dump(new_case), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@cases_bp.route('/', methods=['GET'])
def get_cases():
    """
    List all Cases with optional search
    ---
    tags:
      - Cases
    parameters:
      - name: search
        in: query
        type: string
        description: Search term for case number, owner name, address, etc.
    responses:
      200:
        description: List of cases
    """
    search_term = request.args.get('search')
    query = Case.query

    if search_term:
        search = f"%{search_term}%"
        query = query.outerjoin(Case.ownerships).outerjoin(Ownership.person).outerjoin(Case.documents).filter(
            or_(
                Case.case_number.like(search),
                Case.classification_number.like(search),
                Case.description.like(search),
                Case.address.like(search),
                Person.full_name.like(search),
                Person.national_id.like(search),
                Document.title.like(search),
                Document.description.like(search)
            )
        ).distinct()

    cases = query.all()
    return jsonify(cases_schema.dump(cases))

@cases_bp.route('/<int:case_id>', methods=['GET'])
def get_case(case_id):
    case = Case.query.get_or_404(case_id)
    return case_schema.dump(case)

@cases_bp.route('/<int:case_id>', methods=['PUT'])
def update_case(case_id):
    case = Case.query.get_or_404(case_id)
    data = request.get_json()

    try:
        updated_case = case_schema.load(data, session=db.session, instance=case, partial=True)
        db.session.commit()
        return case_schema.dump(updated_case)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@cases_bp.route('/<int:case_id>/owners', methods=['POST'])
def add_owner(case_id):
    """
    Add a new owner to a case, archiving the previous one
    ---
    tags:
      - Cases
    parameters:
      - name: case_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            نام_و_نام_خانوادگی:
              type: string
            کد_ملی:
              type: string
            تلفن_همراه:
              type: string
    responses:
      200:
        description: Owner added successfully
      400:
        description: Error
    """
    case = Case.query.get_or_404(case_id)
    data = request.get_json()

    national_id = data.get('کد_ملی')
    if not national_id:
         return jsonify({'error': 'کد_ملی required'}), 400

    person = Person.query.filter_by(national_id=national_id).first()

    # If person doesn't exist, create them
    if not person:
        # Check if we have enough info to create person
        if not data.get('نام_و_نام_خانوادگی'):
             return jsonify({'error': 'Person not found and name not provided'}), 400

        # Extract person data from request (assuming flat structure or nested? let's assume flat for simplicity or use schema)
        # Using schema would be cleaner but might fail if extra fields.
        # Let's construct dict.
        person_data = {
            'نام_و_نام_خانوادگی': data.get('نام_و_نام_خانوادگی'),
            'کد_ملی': national_id,
            'تلفن_همراه': data.get('تلفن_همراه'),
            'تلفن_ثابت': data.get('تلفن_ثابت')
        }
        try:
            person = person_schema.load(person_data, session=db.session)
            db.session.add(person)
            db.session.commit()
        except Exception as e:
            return jsonify({'error': f"Error creating person: {str(e)}"}), 400

    # End current ownerships
    current_ownerships = Ownership.query.filter_by(case_id=case.id, is_current=True).all()
    for o in current_ownerships:
        o.is_current = False
        o.end_date = datetime.utcnow().date()

    # Add new ownership
    new_ownership = Ownership(
        case_id=case.id,
        person_id=person.id,
        start_date=datetime.utcnow().date(),
        is_current=True
    )
    db.session.add(new_ownership)
    db.session.commit()

    # Return updated case
    return case_schema.dump(case)

@cases_bp.route('/<int:case_id>/subdivide', methods=['POST'])
def subdivide_case(case_id):
    """
    Subdivide a case into multiple child cases
    ---
    tags:
      - Cases
    parameters:
      - name: case_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            reason:
              type: string
            children:
              type: array
              items:
                type: object
                properties:
                  شماره_پرونده:
                    type: string
                  شماره_کلاسه:
                    type: string
                  docs_to_transfer:
                    type: array
                    items:
                      type: integer
    responses:
      201:
        description: Sub-cases created successfully
    """
    parent_case = Case.query.get_or_404(case_id)
    data = request.get_json()

    children_data = data.get('children', [])
    reason = data.get('reason', 'Subdivision')

    created_children = []

    try:
        for child_info in children_data:
            # Create child case
            child = Case(
                parent_id=parent_case.id,
                case_number=child_info.get('شماره_پرونده'),
                classification_number=child_info.get('شماره_کلاسه'),
                status='active',
                address=child_info.get('آدرس', parent_case.address),
                description=f"Subdivided from {parent_case.case_number}. Reason: {reason}. {child_info.get('توضیحات', '')}"
            )
            db.session.add(child)
            # Flush to get ID if needed immediately, but loop is fine

            # Transfer docs? Need explicit IDs or logic.
            # Assuming simple copy of metadata pointing to same file
            transfer_docs = child_info.get('docs_to_transfer', [])
            for doc_id in transfer_docs:
                original_doc = Document.query.get(doc_id)
                if original_doc and original_doc.case_id == parent_case.id:
                    new_doc = Document(
                        case_id=None, # Will be set after flush
                        title=original_doc.title,
                        description=original_doc.description,
                        file_path=original_doc.file_path,
                        category=original_doc.category
                    )
                    child.documents.append(new_doc)

            created_children.append(child)

        db.session.commit()
        return cases_schema.dump(created_children), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
