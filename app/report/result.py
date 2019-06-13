import os
import json
from os import path

from flask import (render_template, Blueprint, redirect, url_for, request,
                   current_app, send_from_directory)
from flask_login import login_required
from sqlalchemy import func, or_, and_

from app.extensions import (file_result, admin_permission, default_permission,
                            ResultToSql, get_name, dict_to_json, save_in_sql,
                            SaveInSql, dict_to_sql, export_to_excel)
from app.forms import ResultUpForm, CountReForm, StartCheck
from app.models import (db, Stat, Snv, Cnv, Sv_no, Germline_total, Germline_filter, Chem, SampleStat)

result_bp = Blueprint('result_bp', __name__,
                      template_folder=path.join(path.pardir, 'templates', 'result'),
                      url_prefix="/result")


@result_bp.route('/', methods=['POST', 'GET'])
@login_required
def index_re():
    form = CountReForm()
    check_form = StartCheck()
    path_result = current_app.config['UPLOADED_FILERESULT_DEST']
    class_name = [Stat, Snv, Cnv, Chem]
    # if form.validate_on_submit():
    #     for filename in os.listdir(path_result):
    #         file_count = os.path.join(os.getcwd(), count_dir, '{}_count.json'.format(filename.split('.')[0]))
    #         if not os.path.exists(file_count):
    #             res = ResultToSql(os.path.join(os.getcwd(), path_result, filename))
    #             save_in_sql(class_name,res,filename,db.session)
    #             dict_to_json(res, file_count)
    #
    # dic_res = {}
    # for json_f in os.listdir(count_dir):
    #     with open(os.path.join(os.getcwd(), count_dir, json_f), 'r')as f_json:
    #         dic = json.load(f_json)
    #         sample_name = (json_f.split('_')[0])
    #         dic_res[sample_name] = dic

    if form.validate_on_submit():
        for filename in os.listdir(path_result):
            sam_stat = SampleStat.query.filter(SampleStat.Sample_name == filename.split('.')[0]).first()
            if not sam_stat:
                sample_stat = SampleStat(Sample_name=filename.split('.')[0])
                res = ResultToSql(os.path.join(os.getcwd(), path_result, filename))
                dict_to_sql(res, sample_stat, db.session)
                save_in_sql(class_name, res, filename, db.session)
    if 'pass' in request.form:
        mut_id = request.form.getlist('check')
        for id in mut_id:
            sta = SampleStat.query.filter(and_(SampleStat.id == id, SampleStat.status == '未审核'))
            if sta.first():
                sample_name = sta.first().Sample_name
                sta.update({
                    'status': '开始审核',
                })
                db.session.commit()
                for sam in Snv.query.filter(Snv.Sample_name == sample_name).all():
                    sam.status = '开始审核'
                    db.session.commit()
    if 'npass' in request.form:
        mut_id = request.form.getlist('check')
        for id in mut_id:
            sta = SampleStat.query.filter(and_(SampleStat.id == id, SampleStat.status == '未审核')).first()
            if sta:
                sample_name = sta.Sample_name
                for sam in Snv.query.filter(Snv.Sample_name == sample_name).all():
                    db.session.delete(sam)
                    db.session.commit()
                db.session.delete(sta)
                db.session.commit()

    report_id = (request.url).split('=')[-1] if '=' in request.url else ''
    if report_id:
        df = {
            'status': SampleStat.query.filter(
                or_(SampleStat.Sample_name == report_id,
                    SampleStat.Sample_name.endswith(report_id))).order_by(SampleStat.id.desc()).all()
        }
    else:
        df = {
            'status': SampleStat.query.order_by(SampleStat.id.desc()).all()
        }
    print(report_id)

    return render_template('index_re.html', form=form, **df, stat=0)


@result_bp.route('/review/first/', methods=['GET', 'POST'])
@login_required
def review_first():
    df = {
        'status': SampleStat.query.filter(SampleStat.status == '开始审核').all()
    }
    if 'pass' in request.form:
        mut_id = request.form.getlist('check')
        for id in mut_id:
            SampleStat.query.filter(SampleStat.id == id).update({
                'status': '开始二审',
            })
            db.session.commit()
    if 'npass' in request.form:
        mut_id = request.form.getlist('check')
        for id in mut_id:
            sta = SampleStat.query.filter(SampleStat.id == id)
            if sta.first():
                sample_name = sta.first().Sample_name
                sta.update({
                    'status': '未审核',
                })
                db.session.commit()
                for sam in Snv.query.filter(and_(Snv.Sample_name == sample_name, Snv.status == '开始审核')).all():
                    sam.status = ''
                    db.session.commit()

    return render_template('review_first.html', **df, stat=1, title='一审',
                           button_name='发送二审', button_name_n='退回上一步', url_detail='result_bp.review_first')


@result_bp.route('/review/second/', methods=['GET', 'POST'])
@login_required
def review_second():
    df = {
        'status': SampleStat.query.filter(SampleStat.status == '开始二审').all()
    }
    if 'pass' in request.form:
        mut_id = request.form.getlist('check')
        for id in mut_id:
            SampleStat.query.filter(SampleStat.id == id).update({
                'status': '开始三审',
            })
            db.session.commit()
    if 'npass' in request.form:
        mut_id = request.form.getlist('check')
        for id in mut_id:
            sta = SampleStat.query.filter(SampleStat.id == id)
            if sta.first():
                sample_name = sta.first().Sample_name
                sta.update({
                    'status': '开始审核',
                })
                db.session.commit()
                for sam in Snv.query.filter(and_(Snv.Sample_name == sample_name, Snv.status == '一审通过')).all():
                    sam.status = '开始审核'
                    db.session.commit()

    return render_template('review_first.html', **df, stat=2, title='二审',
                           button_name='发送三审', button_name_n='退回上一步', url_detail='result_bp.review_second')


@result_bp.route('/review/third/', methods=['GET', 'POST'])
@login_required
def review_third():
    df = {
        'status': SampleStat.query.filter(SampleStat.status == '开始三审').all()
    }
    if 'pass' in request.form:
        mut_id = request.form.getlist('check')
        for id in mut_id:
            SampleStat.query.filter(SampleStat.id == id).update({
                'status': '审核完成',
            })
            db.session.commit()
    if 'npass' in request.form:
        mut_id = request.form.getlist('check')
        for id in mut_id:
            sta = SampleStat.query.filter(SampleStat.id == id)
            if sta.first():
                sample_name = sta.first().Sample_name
                sta.update({
                    'status': '开始二审',
                })
                db.session.commit()
                for sam in Snv.query.filter(and_(Snv.Sample_name == sample_name, Snv.status == '二审通过')).all():
                    sam.status = '一审通过'
                    db.session.commit()

    return render_template('review_first.html', **df, stat=3, title='三审',
                           button_name='完成审核', button_name_n='退回上一步', url_detail='result_bp.review_third')


@result_bp.route('/result_export/', methods=['GET', 'POST'])
@login_required
def result_export():
    df = {
        'status': SampleStat.query.filter(SampleStat.status == '审核完成').order_by(SampleStat.id.desc()).all()
    }
    filepath = current_app.config['EXPORT_DEST']
    if 'pass' in request.form:
        mut_id = request.form.getlist('check')
        class_names = [Stat, Snv, Cnv, Chem]
        for id in mut_id:
            sam = SampleStat.query.filter(SampleStat.id == id).first()
            filename = sam.Sample_name
            export_to_excel(class_names, filename, filepath)
    if 'npass' in request.form:
        mut_id = request.form.getlist('check')
        for id in mut_id:
            sta = SampleStat.query.filter(SampleStat.id == id)
            if sta.first():
                sample_name = sta.first().Sample_name
                sta.update({
                    'status': '开始三审',
                })
                db.session.commit()
                for sam in Snv.query.filter(and_(Snv.Sample_name == sample_name, Snv.status == '审核完成')).all():
                    sam.status = '二审通过'
                    db.session.commit()

    return render_template('result_export.html', **df, stat=4)


# 结果上传
@result_bp.route('/upload/', methods=['GET', 'POST'])
@login_required
def upload_re():
    form = ResultUpForm()
    if form.validate_on_submit():
        for filename in request.files.getlist('file'):
            file_result.save(filename)
    return render_template('upload_result.html', form=form)


@result_bp.route('/file_manager/index/')
@login_required
def file_index():
    return render_template('file-manager.html')


@result_bp.route('/file_manager/upload/')
@login_required
def file_manager():
    path_result = current_app.config['UPLOADED_FILERESULT_DEST']
    filelist = os.listdir(path_result)
    return render_template('file-manager.html', filelist=filelist)


@result_bp.route('/download/upload/<filename>/', methods=['POST', 'GET'])
@login_required
def download(filename):
    path_result = os.path.join(os.getcwd(), current_app.config['UPLOADED_FILERESULT_DEST'])
    return send_from_directory(path_result, filename, as_attachment=True)


# 结果文件管理和下载
@result_bp.route('/file_manager/result/')
@login_required
def file_manager_re():
    path_result = current_app.config['EXPORT_DEST']
    filelist = os.listdir(path_result)
    return render_template('file-manager-re.html', filelist=filelist)


@result_bp.route('/download/result/<filename>/', methods=['POST', 'GET'])
@login_required
def download_re(filename):
    path_result = os.path.join(os.getcwd(), current_app.config['EXPORT_DEST'])
    return send_from_directory(path_result, filename, as_attachment=True)


@result_bp.route('/delate/result/<filename>', methods=['GET', 'POST'])
@login_required
@admin_permission.require(http_exception=403)
def delate_re(filename):
    path_file = os.path.join(os.getcwd(), current_app.config['EXPORT_DEST'], filename)
    os.remove(path_file)
    return redirect(url_for('.file_manager_re'))


@result_bp.route('/delate/upload/<filename>', methods=['GET', 'POST'])
@login_required
@admin_permission.require(http_exception=403)
def delate(filename):
    path_file = file_result.path(filename)
    os.remove(path_file)
    return redirect(url_for('.file_manager'))


@result_bp.route('/detail/stat/<filename>/', methods=['GET', 'POST'])
@login_required
def stat_detail(filename):
    count_dir = current_app.config['UPLOADED_FILERESULT_DEST']
    file_name = os.path.join(os.getcwd(), count_dir, '{}.xlsx'.format(filename))
    res = ResultToSql(file_name)
    dic = res.result_dic('stat')
    val = dic.values()
    kkey = dic.keys()
    keys = (dic[list(kkey)[0]].keys())

    def get_val(dic, key):
        return dic[key].values()

    return render_template('detail-stat.html', dic=dic, val=val, keys=keys,
                           get_val=get_val, kkey=kkey)


@result_bp.route('/detail/snv/<filename>/<int:stat>', methods=['GET', 'POST'])
@login_required
def snv_detail(filename, stat):
    dic_stat = {0: '', 1: '开始审核', 2: '一审通过', 3: '二审通过', 4: '审核完成'}
    if stat == 1:
        title = '一审'
        data_k = ['Start', 'Gene.refGene', 'gnomAD_exome_EAS', 'gnomAD_genome_EAS', '1000g2015aug_eas',
                  'esp6500siv2_all']
        df = {
            'status': Snv.query.filter(and_(Snv.Sample_name == filename, Snv.status == dic_stat[stat])).all()
        }
    elif stat == 2:
        title = '二审'
        data_k = ['Start', 'CIViC', 'OncoKB', 'CKB', 'Clinvar', '历史出现次数']
        df = {
            'status': Snv.query.filter(and_(Snv.Sample_name == filename, Snv.status == dic_stat[stat])).all()
        }
    elif stat == 3:
        title = '三审'
        data_k = ['Chr', 'Start', 'Gene.refGene', 'p.HGVS', 'c.HGVS', 'exon']
        df = {
            'status': Snv.query.filter(and_(Snv.Sample_name == filename, Snv.status == dic_stat[stat])).all()
        }
    elif stat == 4:
        title = '结果'
        data_k = ['Chr', 'Start', 'Gene.refGene', 'p.HGVS', 'c.HGVS', 'exon']
        df = {
            'status': Snv.query.filter(and_(Snv.Sample_name == filename, Snv.status == dic_stat[stat])).all()
        }
    elif stat == 0:
        title = '所有突变'
        data_k = ['Chr', 'Start', 'Gene.refGene', 'p.HGVS', 'c.HGVS', 'exon']
        df = {
            'status': Snv.query.filter(Snv.Sample_name == filename).all()
        }
    data_v = [get_name(i) for i in data_k]

    if 'pass' in request.form:
        mut_id = request.form.getlist('check')
        mut_note = request.form.getlist('note')
        for id, note in zip(mut_id, mut_note):
            print(note)
            old_note = Snv.query.filter(Snv.id == id).first().note
            Snv.query.filter(Snv.id == id).update({
                'status': dic_stat[int(stat) + 1],
                'note': '{};{}'.format(old_note, note)
            })
            db.session.commit()

    if 'npass' in request.form:
        mut_id = request.form.getlist('check')
        mut_note = request.form.getlist('note')
        for id, note in zip(mut_id, mut_note):
            print(note)
            Snv.query.filter(Snv.id == id).update({
                'status': '未通过',
                'note': note
            })
            db.session.commit()
    list_stat = [0, 4]

    return render_template('detail-snv.html', stat=stat, data_k=data_k,
                           data_v=data_v, **df, list_stat=list_stat,title=title)


@result_bp.route('/detail/cnv/<filename>/', methods=['GET', 'POST'])
@login_required
def cnv_detail(filename):
    count_dir = current_app.config['UPLOADED_FILERESULT_DEST']
    file_name = os.path.join(os.getcwd(), count_dir, '{}.xlsx'.format(filename))
    res = ResultToSql(file_name)
    dic = res.result_dic('cnv')
    if dic:
        val = dic.values()
        kkey = dic.keys()
        keys = (dic[list(kkey)[0]].keys())
    else:
        val = ''
        keys = ''
        kkey = ''

    def get_val(dic, key):
        return dic[key].values()

    return render_template('detail-cnv.html', dic=dic, val=val, keys=keys,
                           get_val=get_val, kkey=kkey)


@result_bp.route('/detail/sv_no/<filename>/', methods=['GET', 'POST'])
@login_required
def sv_no_detail(filename):
    count_dir = current_app.config['UPLOADED_FILERESULT_DEST']
    file_name = os.path.join(os.getcwd(), count_dir, '{}.xlsx'.format(filename))
    res = ResultToSql(file_name)
    dic = res.result_dic('sv_no')
    if dic:
        val = dic.values()
        kkey = dic.keys()
        keys = (dic[list(kkey)[0]].keys())
    else:
        val = ''
        keys = ''
        kkey = ''

    def get_val(dic, key):
        return dic[key].values()

    return render_template('detail-sv_no.html', dic=dic, val=val, keys=keys,
                           get_val=get_val, kkey=kkey)


@result_bp.route('/detail/chem/<filename>/', methods=['GET', 'POST'])
@login_required
def chem_detail(filename):
    count_dir = current_app.config['UPLOADED_FILERESULT_DEST']
    file_name = os.path.join(os.getcwd(), count_dir, '{}.xlsx'.format(filename))
    res = ResultToSql(file_name)
    dic = res.result_dic('化疗')
    val = dic.values()
    kkey = dic.keys()
    keys = (dic[list(kkey)[0]].keys())

    def get_val(dic, key):
        return dic[key].values()

    return render_template('detail-chem.html', dic=dic, val=val, keys=keys,
                           get_val=get_val, kkey=kkey)
