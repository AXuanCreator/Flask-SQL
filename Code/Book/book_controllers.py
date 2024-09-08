from math import ceil

from flask import Blueprint, request, render_template, session, url_for

from Config import ReturnCode, Book, User
from Utils import Response, ResponseCode, Helper
from .book_services import BookServices

book_bp = Blueprint('book', __name__)


########################################################################
# 真实URL为/book/add
# GET: 跳转至书籍添加页面
# POST: 添加书籍
########################################################################
@book_bp.route('/add', methods=['GET', 'POST'])
def book_add():
	if request.method == 'GET' and session.get('user_login') == 'admin':
		return render_template('admin/book_add.html')

	elif request.method == 'POST':
		# 添加书籍
		book_request = request.form
		match BookServices.insert_book(book_request):
			case ReturnCode.SUCCESS:
				book_name = book_request.get('title')
				Helper.logging(f'| 管理员 | 添加 | 书籍 {book_name} |')
				return render_template('message.html', title='添加书籍成功', message=book_name, redirect_url=request.referrer)
			case ReturnCode.FAIL:
				return render_template('message.html', title='错误', message='信息错误', redirect_url=url_for('main'))
			case _:
				return render_template('message.html', title='错误', message='未知', redirect_url=url_for('main'))


########################################################################
# 真实URL为/book/update/<id>
# GET: 跳转至书籍信息更新页面
# POST: 书籍信息更新
########################################################################
@book_bp.route('/update/<int:id>', methods=['GET', 'POST'])
def book_update(id):
	if request.method == 'GET' and session.get('user_login') == 'admin':
		book = Book.query.filter_by(id=id).first()
		return render_template('admin/book_update.html', id=id, book=book)

	elif request.method == 'POST':
		# 更新书籍信息
		book_request = request.form
		match BookServices.update_book(id, book_request):
			case ReturnCode.SUCCESS:
				Helper.logging(f'| 管理员 | 更新 | 书籍 {id} |')
				return render_template('message.html', title='更新书籍成功', message=book_request.get('title'), redirect_url=url_for('main'))
			case ReturnCode.FAIL:
				return render_template('message.html', title='错误', message='未找到书籍', redirect_url=url_for('main'))


########################################################################
# 真实URL为 /book/<id>/delete
# POST请求：删除当前ID的书籍
########################################################################
@book_bp.route('/<id>/delete', methods=['POST'])
def book_delete(id):
	if request.method == 'POST' and session.get('user_login') == 'admin':
		# 删除书籍
		book_name = Book.query.filter_by(id=id).first().title
		match BookServices.delete_book(id):
			case ReturnCode.SUCCESS:
				Helper.logging(f'| 管理员 | 删除 | 书籍 {id} |')
				return render_template('message.html', title='删除成功', message=book_name, redirect_url=request.referrer)
			case ReturnCode.BOOK_NOT_EXIST:
				return render_template('message.html', title='错误', message='未找到书籍', redirect_url=url_for('main'))


########################################################################
# 真实URL为 /book
# GET请求：根据关键词获取多个书籍
########################################################################
@book_bp.route('/', methods=['GET'])
def book_info():
	if request.method == 'GET':
		keywords = request.args.to_dict()  # 从URL中获取参数
		try:
			page = int(request.args.get('page', 1))
			per_page = int(request.args.get('per_page', 10))
		except ValueError:
			return render_template('message.html', title='错误', message='输入参数错误', redirect_url=url_for('main'))

		books, total = BookServices.list_book(keywords, page, per_page)
		if not books:
			return render_template('message.html', title='错误', message='未找到书籍', redirect_url=url_for('main'))

		total_pages = ceil(total / per_page)
		pagination = {
			'total': total,
			'page': page,
			'per_page': per_page,
			'total_pages': total_pages
		}

		# 分成两种情况：
		# 普通用户：仅有借阅选项
		# 管理员：拥有更高的权限
		if session.get('user_login'):
			if session.get('user_login') == 'admin':
				return render_template('admin/book_info.html', books=books, pagination=pagination)
			else:
				user_id = User.query.filter_by(username=session.get('user_login')).first().id
				return render_template('book/book_info.html', books=books, pagination=pagination, user_id=user_id)
		else:
			return render_template('message.html', title='错误', message='请先登陆', redirect_url=url_for('main'))


########################################################################
# 真实URL为 /book/<id>
# GET请求：根据ID获取单个书籍
########################################################################
@book_bp.route('/<id>', methods=['GET'])
def book_operation(id):
	if request.method == 'GET':
		book = BookServices.get_book(id)
		if book:
			return Response.response(ResponseCode.SUCCESS, '书籍查找成功', Helper.to_dict(book))
		else:
			return render_template('message.html', title='错误', message='未找到书籍', redirect_url=url_for('main'))


########################################################################
# 真实URL为 /book/<id>/recommend
# GET请求：获取推荐的书籍
########################################################################
@book_bp.route('/<id>/recommend', methods=['GET'])
def book_recommend(id):
	if request.method == 'GET':
		recommend_list = BookServices.recommend_book_module(id)

		if recommend_list:
			return Response.response(ResponseCode.SUCCESS, '推荐成功', recommend_list)

		return render_template('message.html', title='错误', message='推荐失败', redirect_url=url_for('main'))
