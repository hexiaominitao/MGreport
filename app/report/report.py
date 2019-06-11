from os import path

from flask import (render_template, Blueprint, redirect, url_for)

report_bp = Blueprint('report_bp', __name__, template_folder=path.join(path.pardir, 'templates', 'report'),
                      url_prefix="/report")

@report_bp.route('/')
def index():
    return render_template('index.html')