from flask import Blueprint, request, jsonify, send_from_directory, current_app
from modules.db import db
from modules.models import Document, Case
from modules.schemas import DocumentSchema
from modules.utils import save_file
import os

documents_bp = Blueprint('documents', __name__)
document_schema = DocumentSchema()

@documents_bp.route('/', methods=['POST'])
def upload_document():
    """
    Upload a document for a case
    ---
    tags:
      - Documents
    parameters:
      - name: file
        in: formData
        type: file
        required: true
      - name: case_id
        in: formData
        type: integer
        required: true
      - name: title
        in: formData
        type: string
    responses:
      201:
        description: Document uploaded
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    case_id = request.form.get('case_id')
    if not case_id:
        return jsonify({'error': 'case_id required'}), 400

    case = Case.query.get(case_id)
    if not case:
        return jsonify({'error': 'Case not found'}), 404

    file_path = save_file(file)
    if not file_path:
         return jsonify({'error': 'File save failed'}), 500

    title = request.form.get('title', file.filename)
    description = request.form.get('description')
    category = request.form.get('category')

    new_doc = Document(
        case_id=case_id,
        title=title,
        description=description,
        file_path=file_path,
        category=category
    )

    db.session.add(new_doc)
    db.session.commit()

    return document_schema.dump(new_doc), 201

@documents_bp.route('/<int:doc_id>', methods=['GET'])
def get_document(doc_id):
    doc = Document.query.get_or_404(doc_id)
    return document_schema.dump(doc)

@documents_bp.route('/<int:doc_id>/download', methods=['GET'])
def download_document(doc_id):
    doc = Document.query.get_or_404(doc_id)
    # Ensure absolute path or safe join
    upload_folder = os.path.abspath(current_app.config['UPLOAD_FOLDER'])
    return send_from_directory(upload_folder, doc.file_path, as_attachment=True)
