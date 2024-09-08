from flask import Blueprint, request, session, redirect, url_for, render_template

import User
from Config import ReturnCode, User, UserConfig
from Utils import Response, ResponseCode
from .user_services import UserServices

user_bp = Blueprint('user', __name__)


########################################################################
# 拦截器
# 当访问除 UserConfig.ALLOW_PATH 和 /user开头/code结尾 的URL外
# 其他URL都会检测Session的user_login是否存在内容，即已验证
# 若未经过验证，则导航到user_login中
########################################################################
@user_bp.before_request
def user_login_interceptor():
    if request.path.startswith('/user'):
        if request.path in UserConfig.ALLOW_PATH:
            return
        if request.path.startswith('/user/') and request.path.endswith('/code'):
            # 验证码
            return
        if session.get('user_login') is None:
            return redirect(url_for('user.user_login'))  # 重新导航到/login视图函数，需要包含蓝图名称


########################################################################
# Login路由，真实URL为 /user/login
# GET请求返回登陆页面
# POST请求验证登陆结果
########################################################################
@user_bp.route('/login', methods=['GET', 'POST'])
def user_login():
    print('\033[35m[DEBUG]\033[0m | Login | Session | User Login Status : ', session.get('user_login'))
    print('\033[35m[DEBUG]\033[0m | Login | Session | User Register Status : ', session.get('register'))
    if request.method == 'GET':
        if session.get('user_login'):
            # 对注册信息进行清空
            if session.get('register') is not None:
                session['register'] = False  # 防御性

            # MARK:这里将会导向管理员面板
            if session.get('user_login') == 'admin':
                return redirect(url_for('admin.admin'))

            db_user = User.query.filter_by(username=session['user_login']).first()
            if db_user is not None:
                return redirect(url_for('user.user_info', id=db_user.id))

        return render_template('user/login.html')

    elif request.method == 'POST':
        user_request = request.form
        username = user_request.get('username')
        password = user_request.get('password')
        remember_me = user_request.get('remember_me')

        print('\033[35m[DEBUG]\033[0m | Login | Session : ', session)

        # 仅在Python>=3.10可用match case
        match UserServices.login(username, password):
            case ReturnCode.SUCCESS:
                if remember_me is not None:  # TODO:需要和拦截器分开，如时间更长
                    session['user_login'] = username
                    session.permanent = True  # 启用Config的Session清空时间
                else:
                    session['user_login'] = username
                    session.permanent = False

                return redirect(url_for('user.user_info', id=User.query.filter_by(username=username).first().id))

            case ReturnCode.USER_NOT_EXIST:
                return render_template('message.html', title='错误', message='不存在用户', redirect_url=url_for('main'))
            case ReturnCode.PASSWORD_NOT_ALLOWED:
                return render_template('message.html', title='错误', message='密码错误', redirect_url=url_for('main'))
            case _:
                print('\033[34m[WARN]\033[0m | Controller-->Login | Unexpected Output')


########################################################################
# Register路由，真实URL为 /user/register
# GET请求有两种作用：1.检测session是否存在用户信息，若有，则将信息载入到数据库；2.返回注册页面
# POST请求：将Register页面的内容载入到Session中
########################################################################
@user_bp.route('/register', methods=['GET', 'POST'])
def user_register():
    # GET请求分为两种
    # 1.查询session是否存储着用户信息，若有，则直接载入到数据库并清空Session内容，然后返回至Login
    # 2.若无，则显示Register的页面信息
    if request.method == 'GET':
        if session.get('register') is not None and session['register']:
            # 关闭注册状态
            session['register'] = False
            match UserServices.register(session, commit=True):
                case ReturnCode.SUCCESS:
                    # 清空Session中的注册信息
                    register_keys = ['username', 'name', 'gender', 'phone', 'mail', 'password', 'register']
                    for key in register_keys:
                        del session[key]
                    print('\033[35m[DEBUG]\033[0m | Register GET | Session Clear : ', session)

                    return redirect(url_for('user.user_login'))

                case ReturnCode.USERNAME_NOT_ALLOWED:
                    return render_template('message.html', title='错误', message='Username格式错误', redirect_url=url_for('main'))
                case ReturnCode.USERNAME_REPEATED:
                    return render_template('message.html', title='错误', message='Username已被使用', redirect_url=url_for('main'))
                case ReturnCode.PASSWORD_NOT_ALLOWED:
                    return render_template('message.html', title='错误', message='Password格式错误', redirect_url=url_for('main'))
                case ReturnCode.MAIL_NOT_ALLOWED:
                    return render_template('message.html', title='错误', message='Email格式错误', redirect_url=url_for('main'))
                case ReturnCode.MAIL_REPEATED:
                    return render_template('message.html', title='错误', message='Email重复', redirect_url=url_for('main'))
                case ReturnCode.INFO_NOT_ALLOWED:
                    return render_template('message.html', title='错误', message='输入信息不完整', redirect_url=url_for('main'))
                case _:
                    print('\033[34m[WARN]\033[0m | Controller-->Register | Unexpected Output')
        else:
            return render_template('user/register.html')


    # POST请求则用于将Register的页面信息存入Session里
    elif request.method == 'POST':
        print('\033[35m[DEBUG]\033[0m | Register POST Before Loading | Session : ', session)

        # 对Session进行赋值操作
        user_request = request.form
        if user_request['password'] != user_request['repassword']:
            return render_template('message.html', title='错误', message='两次输入的密码不相同', redirect_url=url_for('main'))
        for key in user_request.keys():
            if user_request[key] == '':
                return render_template('message.html', title='错误', message='输入信息不完整', redirect_url=url_for('main'))
            session[key] = user_request[key]
        session['register'] = True  # 启用注册状态

        print('\033[35m[DEBUG]\033[0m | Register POST After Loading | Session : ', session)
        return redirect(url_for('user.user_send_code'))  # GET请求，因为从Session中获取信息


########################################################################
# Deregister路由，真实URL为 /user/<id>/deregister
# GET请求：注销用户
########################################################################
@user_bp.route('/<id>/deregister', methods=['GET'])
def user_deregister(id):
    if request.method == 'GET':
        # 若已通过验证码验证
        if session.get('deregister') is not None and session['deregister'] == id:
            del session['deregister']
            del session['mail']
            if session.get('user_login'):
                del session['user_login']

            match UserServices.deregister(id):
                case ReturnCode.SUCCESS:
                    return redirect(url_for('user.user_login'))
                case ReturnCode.USER_NOT_EXIST:
                    return render_template('message.html', title='错误', message='无法查询到用户', redirect_url=url_for('main'))

        session['mail'] = User.query.get(id).mail
        session['deregister'] = id

        return redirect(url_for('user.user_send_code'))


########################################################################
# SendCode路由，真实URL为 /user/send-code
# GET请求：向Session存储的邮箱用户发送验证码
# POST请求：向指定邮箱用户发送验证码
########################################################################
@user_bp.route('/send-code', methods=['GET', 'POST'])
def user_send_code():
    # GET请求负责两种情况：
    # 1. Session里存有Mail内容，直接处理
    # 2. Session里无Mail内容，则返回HTML并通过POST请求进行处理
    if request.method == 'GET':
        if session.get('mail') is not None:
            match UserServices.send_mail(session['mail']):
                case ReturnCode.SUCCESS:
                    return redirect(url_for('user.user_verify_code', mail=session['mail']))  # 由于该URL带有参数，需要显式传入
                case ReturnCode.FAIL:
                    return render_template('message.html', title='错误', message='验证码错误', redirect_url=url_for('main'))
                case ReturnCode.MAIL_NOT_ALLOWED:
                    return render_template('message.html', title='错误', message='邮箱错误', redirect_url=url_for('main'))
        else:
            return render_template('user/reset-password-mail.html')

    elif request.method == 'POST':
        mail = request.form.get('mail')
        match UserServices.send_mail(mail):
            case ReturnCode.SUCCESS:
                return redirect(url_for('user.user_verify_code', mail=mail))  # 由于该URL带有参数，需要显式传入
            case ReturnCode.FAIL:
                return render_template('message.html', title='错误', message='发送邮件失败', redirect_url=url_for('main'))
            case ReturnCode.MAIL_NOT_ALLOWED:
                return render_template('message.html', title='错误', message='邮箱错误', redirect_url=url_for('main'))


########################################################################
# CheckCode路由，真实URL为 /user/<mail>/code
# GET请求：返回检验验证码的页面
# POST请求：检验验证码是否正确
########################################################################
@user_bp.route('/<mail>/code', methods=['GET', 'POST'])
def user_verify_code(mail):
    if request.method == 'GET':
        return render_template('user/check-code.html')

    elif request.method == 'POST':
        match UserServices.check_code(mail, request.form.get('code'), need_user_check=False):
            case ReturnCode.SUCCESS:
                print('\033[35m[DEBUG]\033[0m | Verify Code POST | Session : ', session)

                # 当Session存有Register信息时，则代表此时为注册状态
                # 当Session存有Deregister信息时，则表示此时为注销状态
                # 若无，则代表此时在重置密码阶段
                # 注意，这种写法较为暴力，但在验证码使用场景较少时简单有效
                if session.get('register') is not None and session.get('register'):
                    return redirect(url_for('user.user_register'))

                elif session.get('deregister') is not None and session.get('deregister'):
                    return redirect(url_for('user.user_deregister', id=session['deregister']))

                else:
                    return redirect(url_for('user.user_change_password', id=User.query.filter_by(mail=mail).first().id))
            # return ReturnCode.
            # return Response.response(ResponseCode.SUCCESS, 'Check Code Success', User.query.filter_by(mail=mail).first().id)
            case ReturnCode.FAIL:
                return render_template('message.html', title='错误', message='验证码错误', redirect_url=url_for('main'))
            case ReturnCode.MAIL_NOT_ALLOWED:
                return render_template('message.html', title='错误', message='邮箱错误', redirect_url=url_for('main'))


########################################################################
# ChangePassword路由，真实URL为 /user/<id>/password
# GET请求：返回重置密码的页面
# POST请求：更改密码
########################################################################
@user_bp.route('/<id>/password', methods=['GET', 'POST'])
def user_change_password(id):
    # 该视图函数需要验证状态
    if request.method == 'GET':
        return render_template('user/reset-password.html')

    # 为何更新信息时不使用PUT？
    # 因为Jinja2的HTML表单仅仅支持POST和GET :)
    elif request.method == 'POST':
        user_request = request.form
        if user_request['password'] != user_request['repassword']:
            return render_template('message.html', title='错误', message='密码不相同', redirect_url=url_for('main'))

        match UserServices.change_password(id, user_request.get('password')):
            case ReturnCode.SUCCESS:  # TODO:实际上并没有对密码是否和原先的密码重复做判断
                print('\033[35m[DEBUG]\033[0m | Reset Password | Success : ', id)
                return redirect(url_for('user.user_login'))
            case ReturnCode.USER_NOT_EXIST:
                return render_template('message.html', title='错误', message='无法查询到用户', redirect_url=url_for('main'))
            case ReturnCode.FAIL:
                return render_template('message.html', title='错误', message='密码为空', redirect_url=url_for('main'))
            case ReturnCode.PASSWORD_NOT_ALLOWED:
                return render_template('message.html', title='错误', message='密码格式错误', redirect_url=url_for('main'))


########################################################################
# Info路由，真实URL为 /user/<id>
# GET请求：返回用户信息
# POST请求：更改用户信息
########################################################################
@user_bp.route('/<id>', methods=['GET', 'POST'])
def user_info(id):
    if request.method == 'GET':
        db_user = User.query.get(id)
        if db_user is None:
            return Response.response(ResponseCode.ACCOUNT_NOT_EXIST, 'Could Not Find The User', None)

        return render_template('user/info.html',
                               id=db_user.id,
                               username=db_user.username,
                               name=db_user.name,
                               phone=db_user.phone,
                               mail=db_user.mail,
                               gender=db_user.gender)

    elif request.method == 'POST':
        user_request = request.form
        print(user_request)
        match UserServices.update_user(id, user_request):
            case ReturnCode.SUCCESS:
                return redirect(url_for("user.user_info", id=id))
            case ReturnCode.USER_NOT_EXIST:
                return render_template('message.html', title='错误', message='用户不存在', redirect_url=url_for('main'))
            case ReturnCode.USERNAME_NOT_ALLOWED:
                return render_template('message.html', title='错误', message='Username格式错误', redirect_url=url_for('main'))
            case ReturnCode.USERNAME_REPEATED:
                return render_template('message.html', title='错误', message='Username重复', redirect_url=url_for('main'))
            case ReturnCode.GENDER_NOT_ALLOWED:
                return render_template('message.html', title='错误', message='未知性别', redirect_url=url_for('main'))
            case ReturnCode.MAIL_NOT_ALLOWED:
                return render_template('message.html', title='错误', message='邮箱错误', redirect_url=url_for('main'))
            case ReturnCode.MAIL_REPEATED:
                return render_template('message.html', title='错误', message='邮箱已存在', redirect_url=url_for('main'))


########################################################################
# 以下的路由都是一些测试用路由
########################################################################
@user_bp.route('/redirect/login', methods=['GET'])
def redirect_login():
    del session['user_login']
    return redirect(url_for('user.user_login'))


@user_bp.route('/<id>/update/info', methods=['GET'])
def update_info(id):
    db_user = User.query.get(id)
    if db_user is None:
        return "THIS IS TEST"

    return render_template('user/update.html',
                           id=id,
                           username=db_user.username,
                           name=db_user.name,
                           phone=db_user.phone,
                           mail=db_user.mail,
                           gender=db_user.gender)


@user_bp.route('/tools/sessionclear', methods=['GET'])
def clear_session():
    session.clear()
    return redirect(url_for('main'))
