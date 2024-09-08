import random
import re
import string
import os
from datetime import datetime

class Helper:
	@staticmethod
	def to_dict(orm):
		json = {key: value for key, value in orm.__dict__.items() if not key.startswith('_')}
		print('\033[35m[DEBUG]\033[0m | TO DICT : ', json)

		return json

	@staticmethod
	def to_dict_list(orm_list):
		return [Helper.to_dict(item) for item in orm_list]

	@staticmethod
	def generate_random_string_with_pattern(pattern, min, max):
		random_string = ''
		while not re.match(pattern, random_string):
			random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(min, max)))

		return random_string

	@staticmethod
	def generate_random_string_with_choice(pattern, min, max):
		return ''.join(random.choices(pattern, k=random.randint(min, max)))

	@staticmethod
	def logging(text):
		current_data = datetime.now().strftime('%Y-%m-%d')
		log_filename = f'Logs/{current_data}.log'

		# 以追加的方式打开该文件，若不存在会自动创建
		with open(log_filename, 'a', encoding='utf-8') as log:
			log.write(text + '\n')
