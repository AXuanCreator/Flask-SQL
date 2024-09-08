import os

from flask import Blueprint, request, render_template, session, url_for
from flask_sqlalchemy import pagination

import Borrow
from Utils.response import ResponseCode, Response
from Utils.helper import Helper
from Borrow.borrow_services import BorrowService
from Config import User, Book, Borrow

borrow_bp = Blueprint('borrow', __name__)


########################################################################
# 真实URL为 /borrow
# GET请求：查询某个特定信息的借阅列表
# POST请求：借阅书籍
########################################################################
@borrow_bp.route('/', methods=['GET', 'POST'])
def book_borrow():
	if request.method == 'GET':
		# 默认使用已登录账户的ID进行查询
		user_id = User.query.filter_by(username=session.get('user_login')).first().id

		# 分页参数
		page = request.args.get('page', 1, type=int)  # 当前页码，默认为1
		per_page = request.args.get('per_page', 10, type=int)  # 每页显示数量，默认为10

		# 查询条件
		args = {
			'user_id': user_id,
		}

		borrows = BorrowService.list_borrow(args)
		pagination = borrows.paginate(page=page, per_page=per_page, error_out=False)

		# 获取书籍信息
		books = {borrow.book_id: Book.query.get(borrow.book_id) for borrow in pagination.items}
		print(books)

		return render_template('book/borrow_info.html', borrows=pagination.items, books=books, pagination=pagination)
	# return Response.response(ResponseCode.SUCCESS, '查询成功', [Helper.to_dict(e) for e in books])

	elif request.method == 'POST':
		form = request.form
		res_code = BorrowService.borrow_book(form)
		if res_code == -3:
			return render_template('message.html', title='错误', message='图书已借阅', redirect_url=url_for('main'))
		if res_code == -2:
			return render_template('message.html', title='错误', message='图书不存在', redirect_url=url_for('main'))
		if res_code == -1:
			return render_template('message.html', title='错误', message='用户不存在', redirect_url=url_for('main'))
		if res_code == 0:
			return render_template('message.html', title='错误', message='借阅受限', redirect_url=url_for('main'))
		if res_code > 0:
			Helper.logging(f'| 用户 {form.get("user_id")} | 借阅 | 书籍 {form.get("book_id")} |')
			return render_template('message.html', title='借阅成功', message=Book.query.filter_by(id=form.get('book_id')).first().title, redirect_url=url_for('main'))


########################################################################
# 真实URL为 /borrow/<id>/return
# POST请求：归还书籍
########################################################################
@borrow_bp.route('/<id>/return', methods=['POST'])
def return_book(id):
	db_borrow = Borrow.query.filter_by(id=id).first()
	book_id = db_borrow.book_id
	user_id = db_borrow.user_id
	book_name = Book.query.filter_by(id=book_id).first().title

	res_code = BorrowService.return_book(id)
	if res_code == -2:
		return render_template('message.html', title='错误', message='借阅记录不存在', redirect_url=url_for('main'))
	if res_code == -1:
		return render_template('message.html', title='错误', message='无法重复归还', redirect_url=url_for('main'))
	if res_code == 0:
		return render_template('message.html', title='信息', message='逾期归还', redirect_url=url_for('main'))
	if res_code == 1:
		Helper.logging(f'| 用户 {user_id} | 归还 | 书籍 {book_id} |')
		return render_template('message.html', title='归还成功', message=book_name, redirect_url=request.referrer)


########################################################################
# 真实URL为 /borrow/<id>/return
# POST请求：续借书籍
########################################################################
@borrow_bp.route('/<id>/renew', methods=['POST'])
def renew_book(id):
	db_borrow = Borrow.query.filter_by(id=id).first()
	book_id = db_borrow.book_id
	user_id = db_borrow.user_id
	book_name = Book.query.filter_by(id=book_id).first().title

	res_code = BorrowService.renew_book(id)
	if res_code == -2:
		return render_template('message.html', title='错误', message='借阅记录不存在', redirect_url=url_for('main'))
	if res_code == -1:
		return render_template('message.html', title='错误', message='图书已归还', redirect_url=url_for('main'))
	if res_code == 0:
		return render_template('message.html', title='错误', message='借阅逾期，请先归还', redirect_url=url_for('main'))
	if res_code == 1:
		Helper.logging(f'| 用户 {user_id} | 续借 | 书籍 {book_id} |')
		return render_template('message.html', title='续借成功', message=book_name, redirect_url=request.referrer)
