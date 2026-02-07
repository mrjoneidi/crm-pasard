from flask import Blueprint, request, jsonify
from modules.db import db
from modules.models import LeaseContract, Case, Person
from modules.schemas import LeaseContractSchema
from datetime import datetime

contracts_bp = Blueprint('contracts', __name__)
contract_schema = LeaseContractSchema()
contracts_schema = LeaseContractSchema(many=True)

@contracts_bp.route('/', methods=['POST'])
def create_contract():
    data = request.get_json()
    try:
        new_contract = contract_schema.load(data, session=db.session)
        db.session.add(new_contract)
        db.session.commit()
        return contract_schema.dump(new_contract), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@contracts_bp.route('/<int:contract_id>', methods=['GET'])
def get_contract(contract_id):
    contract = LeaseContract.query.get_or_404(contract_id)
    return contract_schema.dump(contract)
