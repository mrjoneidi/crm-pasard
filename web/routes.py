from flask import Blueprint, render_template

web_bp = Blueprint('web', __name__, template_folder='../templates', static_folder='../static')

@web_bp.route('/')
def dashboard():
    return render_template('dashboard.html')

@web_bp.route('/cases')
def cases_list():
    return render_template('cases/list.html')

@web_bp.route('/cases/create')
def cases_create():
    return render_template('cases/create.html')

@web_bp.route('/cases/<int:case_id>')
def cases_detail(case_id):
    return render_template('cases/detail.html', case_id=case_id)

@web_bp.route('/financial')
def financial_index():
    return render_template('financial/index.html')
