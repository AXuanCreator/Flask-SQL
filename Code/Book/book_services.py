#!/user/bin/env python3
# -*- coding: utf-8 -*-
from Config import Book, ReturnCode, db, BookCategory, Borrow
from Recommend import infer
from sqlalchemy import func


class BookServices:

	@staticmethod
	def insert_book(book_request):
		"""插入书籍"""
		request_keys = ['title', 'author', 'publisher', 'quantity', 'category_id']
		title, author, publisher, quantity, category_id = (book_request.get(key) for key in request_keys)

		if any(var is None for var in [title, author, category_id, publisher, quantity]):
			return ReturnCode.FAIL

		insert_book = Book(title=title, author=author, category_id=category_id, publisher=publisher, quantity=quantity)

		db.session.add(insert_book)
		db.session.commit()

		return ReturnCode.SUCCESS

	@staticmethod
	def get_book(id):
		"""根据id获取书籍"""
		return Book.query.get(id)

	@staticmethod
	def list_book(keywords, page, per_page):
		"""根据关键词获取书籍列表"""
		query = Book.query

		filters = {
			'title': Book.title.like,
			'author': Book.author.like,
			'publisher': Book.publisher.like,
			'category_id': Book.category_id.__eq__
		}

		for key, filter_func in filters.items():
			if key in keywords and keywords[key]:
				if key == 'category_id':
					query = query.filter(filter_func(keywords[key]))
				else:
					query = query.filter(filter_func(f"%{keywords[key]}%"))

		total = query.count()
		books = query.offset((page - 1) * per_page).limit(per_page).all() # 从这里获取不同分页的内容

		return books, total

	@staticmethod
	def update_book(id, update_data):
		"""更新书籍信息"""
		# TODO:书籍分类不存在
		book = Book.query.get(id)
		if 'title' in update_data:
			book.title = update_data['title']
		if 'author' in update_data:
			book.author = update_data['author']
		if 'publisher' in update_data:
			book.publisher = update_data['publisher']
		if 'quantity' in update_data:
			book.quantity = update_data['quantity']
		if 'category_id' in update_data:
			book.category_id = update_data['category_id']

		db.session.add(book)
		db.session.commit()

		return ReturnCode.SUCCESS

	@staticmethod
	def delete_book(id):
		"""删除书籍"""
		book = Book.query.get(id)
		if not book:
			return ReturnCode.BOOK_NOT_EXIST

		db.session.delete(book)
		db.session.commit()

		return ReturnCode.SUCCESS

	@staticmethod
	def recommend_book_module(id):
		"""推荐书籍"""
		borrow_list = [borrow.book_id for borrow in Borrow.query.filter_by(user_id=id)]
		book_list = [book.id for book in Book.query.order_by(func.random()).limit(5).all()]

		if borrow_list is None:
			return None

		recommend_list = infer(borrow_list, book_list)  # 推理
		recommend_list = [book_id for book_id, rating in zip(book_list, recommend_list) if
		                  rating > 3.7]  # TODO : 为什么是3.7为分界点呢，因为模型有点问题，收敛3.7左右

		if recommend_list is None:
			return None

		return recommend_list
