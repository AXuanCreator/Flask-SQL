############################### VERSION 1.0 ###############################
# 此模块用于定义Database模型
# 该模块可用于多个数据库，如MySQL，Oracle，且无需改动代码
############################### VERSION 1.0 ###############################

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
	__tablename__ = 'tb_user'
	id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
	username = db.Column(db.String(80), unique=True, nullable=True)
	password = db.Column(db.String(80), nullable=True)
	name = db.Column(db.String(20), nullable=True)
	gender = db.Column(db.String(20), nullable=True)
	phone = db.Column(db.String(80), unique=True, nullable=True)
	email = db.Column(db.String(80), unique=True, nullable=True)
	max_borrow_days = db.Column(db.BigInteger, default=-1)  # 若为-1，则说明Service出现问题
	max_borrow_books = db.Column(db.BigInteger, default=-1)
	created_at = db.Column(db.DateTime, server_default=db.func.now())  # server_default有更高优先级


class Admin(db.Model):
	__tablename__ = 'tb_admin'
	id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
	username = db.Column(db.String(80), unique=True, nullable=True)
	password = db.Column(db.String(80), nullable=True)
	name = db.Column(db.String(20), nullable=True)
	phone = db.Column(db.String(80), unique=True, nullable=True)
	email = db.Column(db.String(80), unique=True, nullable=True)
	created_at = db.Column(db.DateTime, server_default=db.func.now())


class Book(db.Model):
	__tablename__ = 'tb_book'
	id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
	title = db.Column(db.String(80), unique=True, nullable=True)
	author = db.Column(db.String(20), nullable=True)
	publisher = db.Column(db.String(20), nullable=True)
	quantity = db.Column(db.Integer)
	created_at = db.Column(db.DateTime, server_default=db.func.now())

	# Foreign Key
	category_id = db.Column(db.BigInteger, db.ForeignKey('tb_book_category.id'))


class BookCategory(db.Model):
	__tablename__ = 'tb_book_category'
	id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
	name = db.Column(db.String(20), unique=True, nullable=True)
	quantity = db.Column(db.Integer)
	create_at = db.Column(db.DateTime, server_default=db.func.now())


class Borrow(db.Model):
	__tablename__ = 'tb_borrow'
	id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
	borrow_date = db.Column(db.DateTime, server_default=db.func.now())
	return_date = db.Column(db.DateTime)
	really_return_date = db.Column(db.DateTime)

	# Foreign Key
	user_id = db.Column(db.BigInteger, db.ForeignKey('tb_user.id'))
	book_id = db.Column(db.BigInteger, db.ForeignKey('tb_book.id'))
