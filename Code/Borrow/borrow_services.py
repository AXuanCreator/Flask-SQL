import datetime

from Config import db, Borrow, Book, User


class BorrowService:
	@staticmethod
	def list_borrow(args):
		# 获取查询参数
		id = args.get('id')
		user_id = args.get('user_id')
		book_id = args.get('book_id')
		category_id = args.get('category_id')
		contain_finished = args.get('contain_finished', '0')

		query = db.session.query(Borrow).join(Book)

		# 添加条件过滤
		if user_id:
			query = query.filter(Borrow.user_id == int(user_id))
		if book_id:
			query = query.filter(Borrow.book_id == int(book_id))
		if category_id:
			query = query.filter(Book.category_id == int(category_id))
		if contain_finished == '0':  # 默认不包含已归还的借阅记录
			query = query.filter(Borrow.really_return_date.is_(None))
		if id:
			query = query.filter(Borrow.id == int(id))

		# 返回查询结果，此事为一个SQLAlchemy对象
		return query

	@staticmethod
	def borrow_book(body):
		"""
		:return: -3：重复借阅； -2：图书不存在；-1：用户不存在；0：达到最大借阅数；1：借阅成功
		"""
		user_id = body.get('user_id')
		book_id = body.get('book_id')
		user = User.query.get(user_id)
		book = Book.query.get(book_id)
		if not book:
			return -2
		if not user:
			return -1
		user_borrows_query = Borrow.query.filter_by(user_id=user_id).filter(Borrow.really_return_date.is_(None))
		if len(user_borrows_query.all()) >= user.max_borrow_books:
			return 0
		# 查询是否有未归还的重复图书
		user_borrows_query = user_borrows_query.filter_by(book_id=book_id)
		if len(user_borrows_query.all()) > 0:
			return -3
		borrow_date = datetime.datetime.now()
		return_date = borrow_date + datetime.timedelta(days=user.max_borrow_days)
		new_borrow = Borrow(user_id=user_id, book_id=book_id, borrow_date=borrow_date, return_date=return_date)
		db.session.add(new_borrow)
		db.session.commit()
		return new_borrow.id

	@staticmethod
	def return_book(id):
		"""
		:return -2：借阅记录不存在；-1：不可重复归还；0：逾期归还；1：归还成功
		"""
		borrow = Borrow.query.get(id)
		if borrow is None:
			return -2
		if borrow.really_return_date is not None:
			return -1
		if datetime.datetime.now() > borrow.return_date:
			borrow.really_return_date = datetime.datetime.now()
			return 0
		borrow.really_return_date = datetime.datetime.now()
		db.session.commit()
		return 1

	@staticmethod
	def renew_book(id):
		"""
		:return -2：借阅记录不存在；-1：图书已归还；0：借阅已到期；1：续借成功
		"""
		borrow = Borrow.query.get(id)
		user = User.query.get(borrow.user_id)
		if borrow is None:
			return -2
		if borrow.really_return_date is not None:
			return -1
		if datetime.datetime.now() > borrow.return_date:
			borrow.really_return_date = datetime.datetime.now()
			return 0

		borrow.return_date = datetime.datetime.now() + datetime.timedelta(days=user.max_borrow_days)
		db.session.commit()

		return 1
