from flask import Flask, render_template, session
from flask_cors import CORS

from Config import db, AppConfig, User, Book
from Admin import admin_bp
from Book import book_bp
from User import user_bp
from Borrow import borrow_bp
from Book import bookcategory_bp, BookServices
from User.Mail import mail


def create_app():
	# 创建Flask应用实例，对所有域名开放
	app = Flask(__name__)
	CORS(app)

	# 读取所有参数
	app.config.from_object(AppConfig)

	# 加载蓝图
	app.register_blueprint(user_bp, url_prefix='/user')
	app.register_blueprint(book_bp, url_prefix='/book')
	app.register_blueprint(bookcategory_bp, url_prefix='/book-category')
	app.register_blueprint(admin_bp, url_prefix='/admin')
	app.register_blueprint(borrow_bp, url_prefix='/borrow')

	# 初始化数据库
	db.init_app(app)
	with app.app_context():
		db.create_all()  # 将ORM模型同步至数据库

	# 初始化邮箱
	mail.init_app(app)

	return app


app = create_app()


########################################################################
# 首页
########################################################################
@app.route('/', methods=['GET'])
def main():
	is_logged = True if session.get('user_login') else False
	book_list = []

	if is_logged and session.get('user_login') != 'admin':
		id = User.query.filter_by(username=session.get('user_login')).first().id
		book_id_list = BookServices.recommend_book_module(id)
		book_list = [Book.query.filter_by(id=id).first().title for id in book_id_list]

	return render_template('main.html', is_logged=is_logged, recommended_books=book_list)


@app.route('/test')
def test():
	return render_template('admin/admin.html', id=1)


if __name__ == '__main__':
	app.run()
