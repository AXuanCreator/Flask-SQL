############################### VERSION 1.0 ###############################
# 此模块管理所有的配置信息
############################### VERSION 1.0 ###############################
import datetime
import os


class AppConfig():
	# MySQL
	# HOSTNAME = '127.0.0.1'
	# PORT = '3306'
	# USERNAME = 'root'
	# PASSWORD = '9966330'
	# DATABASE = 'flask-web'  # 架构名
	#
	# SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}?charset=utf8"
	# SQLALCHEMY_TRACKr_MODIFICATIONS = False
	# SECRET_KEY = 'your_secret_key'

	# SQLite
	DATABASE_FILE = 'flask-web.db'
	SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_FILE}'
	SECRET_KEY = 'fireflysowonderful'

	# FLASK
	DEBUG = True
	PERMANENT_SESSION_LIFETIME = datetime.timedelta(days=7)  # 7天后Session过期

	# MAIL
	MAIL_SERVER = 'smtp.sinpor.top'
	MAIL_PORT = 465
	MAIL_USE_TLS = False  # STARTTLS
	MAIL_USE_SSL = True  # SSL
	MAIL_USERNAME = 'eigb903@sinpor.top'
	MAIL_PASSWORD = 'sinpor123'
	MAIL_DEFAULT_SENDER = ('Coder', 'eigb903@sinpor.top')
	MAIL_DEBUG = False


class DbConfig:
	pass


class UserConfig:
	MAX_BORROW_BOOKS = 30
	MAX_BORROW_DAYS = 30

	MAIL_CODE = '0123456789'
	MAIL_CODE_LEN = 6
	MAIL_CODE_OUTTIME = 600  # 10min

	ALLOW_PATH = ['/user/login', '/user/register', '/user/send-code', '/user/test', '/user/tools/sessionclear']


class ReturnCode:
	SUCCESS = 'SUCCESS'
	FAIL = 'FAIL'
	USERNAME_NOT_ALLOWED = 'USERNAMENOTALLOWED'
	USERNAME_REPEATED = 'USERNAMEREPEATED'
	PASSWORD_NOT_ALLOWED = 'PASSWORDNOTALLOWED'
	GENDER_NOT_ALLOWED = 'GENDERNOTALLOWED'
	MAIL_NOT_ALLOWED = 'MAILNOTALLOWED'
	MAIL_REPEATED = 'MAILREPEATED'
	INFO_NOT_ALLOWED = 'INFONOTALLOWED'
	USER_NOT_EXIST = 'USERNOTEXIST'
	NAME_NOT_ALLOWED = 'NAMENOTALLOWED'
	BOOK_NOT_EXIST = 'BOOKNOTEXIST'
	CATEGORY_EXIST = 'CATEGORYEXIST'
	CATEGORY_NOT_EXIST = 'CATEGORYNOTEXIST'


class Regex:
	"""
	正则表达式
	^ ：表示开头
	a-z ：表示匹配小写字母
	[...] ：表示一个字符的规则
	* ：表示前面的[...]可以有零次或多次
	{a,b} ：表示前面的符合[...]的字符至少有a个，至多有b个
	(?=.*[...]) ：正向肯定预查，表示字符串里至少包含一个符合[...]规则的字符
	"""
	username_pattern = r'^[a-zA-Z][a-zA-Z0-9]{4,}$'
	password_pattern = r'^(?=.*[a-z])(?=.*[A-Z]).{8,}$'
	mail_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9]+\.[a-zA-Z]{2,}$'

	# 这个并非为正则表达式，但依旧放在这里
	name_pattern = "王张李赵陈刘周林孙吴郑蒋沈韩杨朱秦许何吕施张孔曹严华金魏陶姜陈韩小逸黄陡晓臭榴称泉黎船新锈遍实米吵侮冈僵够纯泥盗极闲续挣王琴感言范赏欲厉喉资御假或种尚准常忧锤衣飞寺代合态务礼杆触植铺忍膝转哥痰打梳田迫须程搜影简猎福伶悔位巷拨疫康挠毒泊苍刃悟钱语惯界氏"


class TrainConfig:
	epoch = 40
