from os import path
from flask import (render_template, Blueprint, redirect, url_for, flash, current_app, session)

from flask_login import login_required, current_user
from app.extensions import admin_permission

admin_bp = Blueprint('admin_bp', __name__, template_folder=path.join(path.pardir, 'templates', 'admin'),
                     url_prefix="/admin")


@admin_bp.route('/')
@login_required
@admin_permission.require(http_exception=403)
def index_admin():
    return render_template('index-admin.html')