import os
from datetime import datetime

from flask import Flask, Blueprint, request, render_template, session, redirect, url_for, flash
from .admin_services import AdminService
from Utils import ResponseCode, Response
from Utils import Helper
from Config import Admin, ReturnCode

admin_bp = Blueprint('admin', __name__)

########################################################################
# 真实URL为 /admin
# GET请求: 管理员控制面板
########################################################################
@admin_bp.route('/', methods=['GET'])
def admin():
    db_admin = Admin.query.filter_by(username=session.get('user_login')).first()
    id = db_admin.id
    return render_template('admin/admin.html', id=id)

########################################################################
# 真实URL为 /admin/login
# POST请求：登陆
########################################################################
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if session.get('user_login'):
            # 对注册信息进行清空
            if session.get('register') is not None:
                session['register'] = False  # 防御性

            db_user = Admin.query.filter_by(username=session['user_login']).first()
            if db_user is not None:
                return redirect(url_for('user.user_info', id=db_user.id))

        return render_template('admin/login.html')

    elif request.method == 'POST':
        admin_request = request.form
        username = admin_request.get('username')
        password = admin_request.get('password')
        remember_me = admin_request.get('remember_me')

        print('\033[35m[DEBUG]\033[0m | Login | Session : ', session)

        # 仅在Python>=3.10可用match case
        match AdminService.login(username=username, password=password):
            case 1:
                if remember_me is not None:  # TODO:需要和拦截器分开，如时间更长
                    session['user_login'] = username
                    session.permanent = True  # 启用Config的Session清空时间
                else:
                    session['user_login'] = username
                    session.permanent = False

                return redirect(url_for('main'))

            case -1:
                return render_template('message.html', title='错误', message='管理员不存在', redirect_url=url_for('main'))
            case 0:
                return render_template('message.html', title='错误', message='密码错误', redirect_url=url_for('main'))
            case _:
                print('\033[34m[WARN]\033[0m | Controller-->Login | Unexpected Output')


########################################################################
# 真实URL为 /admin/<id>
# GET请求：获取管理员信息
########################################################################
@admin_bp.route('/<int:id>', methods=['GET', 'POST'])
def admin_info(id):
    if request.method == 'GET':
        """获取管理员的基本信息"""
        admin = AdminService.get_admin_by_id(id)
        if admin:
            return render_template('admin/admin_info.html', admin=admin)
        return render_template('message.html', title='错误', message='管理员不存在', redirect_url=url_for('main'))

    elif request.method == 'POST':
        """修改管理员的基本信息"""
        res_code = AdminService.update_admin(id, request.form)
        if res_code == 1:
            return render_template('message.html', title='信息', message='修改成功', redirect_url=request.referrer)
        if res_code == -1:
            return render_template('message.html', title='错误', message='管理员不存在', redirect_url=url_for('main'))
        return render_template('message.html', title='错误', message='系统错误', redirect_url=url_for('main'))


########################################################################
# 真实URL为 /admin/<id>/password
# POST请求：修改管理员密码
########################################################################
@admin_bp.route('/<int:id>/password', methods=['GET', 'POST'])
def modify_admin_password(id):
    if request.method == 'GET':
        admin = AdminService.get_admin_by_id(id)
        return render_template('admin/admin_password.html', admin=admin)

    elif request.method == 'POST':
        """修改管理员的登录密码"""
        res_code = AdminService.update_password(id, request.form)
        if res_code == 1:
            return Response.response(ResponseCode.SUCCESS, '修改成功', id)
        if res_code == -1:
            return render_template('message.html', title='错误', message='管理员不存在', redirect_url=url_for('main'))
        if res_code == 0:
            return render_template('message.html', title='错误', message='密码错误', redirect_url=url_for('main'))


########################################################################
# 真实URL为 /admin/<id>/logging
# GET请求: 返回日志信息
########################################################################
@admin_bp.route('/<int:id>/logging', methods=['GET'])
def check_logging(id):
    # 获取当前页码，默认是第一页
    page = request.args.get('page', 1, type=int)
    per_page = 10  # 每页显示的日志数

    # 获取传递的日期参数，默认使用当前日期
    selected_date = request.args.get('date')
    if selected_date:
        try:
            # 确保日期格式正确
            current_date = datetime.strptime(selected_date, '%Y-%m-%d').strftime('%Y-%m-%d')
        except ValueError:
            current_date = datetime.now().strftime('%Y-%m-%d')  # 如果日期格式不正确，使用当前日期
    else:
        current_date = datetime.now().strftime('%Y-%m-%d')  # 默认使用当前日期

    log_filename = os.path.join('Logs', f'{current_date}.log')

    logs = []
    has_next = False

    # 读取日志文件
    if os.path.exists(log_filename):
        with open(log_filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            total_logs = len(lines)
            start = (page - 1) * per_page
            end = start + per_page
            logs_to_display = lines[start:end]

            # 解析日志内容
            for line in logs_to_display:
                parts = line.strip().split('|')
                parts = parts[1:-1]  # 去除头尾的空字符
                print(parts)
                if len(parts) == 3:
                    user, action, book = parts
                    logs.append({'user': user.strip(), 'action': action.strip(), 'book': book.strip()})

            # 检查是否有下一页
            has_next = end < total_logs

    # 渲染模板并传递日志和分页信息
    return render_template('admin/admin_logging.html', id=id, logs=logs, page=page, has_next=has_next)
