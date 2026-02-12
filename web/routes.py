from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from modules.models import User

web_bp = Blueprint('web', __name__, template_folder='../templates', static_folder='../static')

@web_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('web.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('web.dashboard'))
        else:
            flash('نام کاربری یا رمز عبور اشتباه است.', 'danger')
    return render_template('login.html')

@web_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('web.login'))

@web_bp.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html')

@web_bp.route('/cases')
@login_required
def cases_list():
    return render_template('cases/list.html')

@web_bp.route('/cases/create')
@login_required
def cases_create():
    return render_template('cases/create.html')

@web_bp.route('/cases/<int:case_id>')
@login_required
def cases_detail(case_id):
    return render_template('cases/detail.html', case_id=case_id)

@web_bp.route('/financial')
@login_required
def financial_index():
    return render_template('financial/index.html')
