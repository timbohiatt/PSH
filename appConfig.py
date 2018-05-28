
import os 

class Config:


	APP_NAME = 'PSH'

	IMG_STAGE_DIR = 'static/media/MPSH_entries/stage/' 
	IMG_FINAL_DIR = 'static/media/MPSH_entries/final/'

	AWS_S3_ROOT = os.environ['AWS_S3_ROOT']

	#GOOGLE_APPLICATION_CREDENTIALS = "secure/googleCreds.json"	

	GOOGLE_VISION_MIN_LABEL_SCORE = 0.60

	AWS_DEFAULT_REGION = 'ap-southeast-2'

	SQLALCHEMY_TRACK_MODIFICATIONS = False	
	SQLALCHEMY_TRACK_MODIFICATIONS = False


class LocalConfig(Config):
	DEBUG = True

	SECRET_KEY = 'MP$H_2019_prd'

	MYSQL_HOST = 'localhost'
	MYSQL_USER = 'root'
	MYSQL_PASSWORD = 'Condor14!'
	MYSQL_CURSORCLASS = 'DictCursor'
	#MYSQL_DB = 'MPSH'
	MYSQL_DBALC = 'PSH'

	SQLALCHEMY_TRACK_MODIFICATIONS = False	
	SQLALCHEMY_DATABASE_URI = 'mysql://' + MYSQL_USER + ':' + MYSQL_PASSWORD + '@' + MYSQL_HOST + '/' + MYSQL_DBALC
	SQLALCHEMY_TRACK_MODIFICATIONS = False

	AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID'] 
	AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY'] 



class DevelopmentConfig(Config):
	DEBUG = True

	IMG_STAGE_DIR = '/opt/python/current/app/static/media/MPSH_entries/stage/'
	IMG_FINAL_DIR = '/opt/python/current/app/static/media/MPSH_entries/final/'

	SECRET_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
	AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID'] 
	AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY'] 

	MYSQL_HOST = os.environ['MYSQL_HOST'] 
	MYSQL_USER = os.environ['MYSQL_USER'] 
	MYSQL_PASSWORD = os.environ['MYSQL_PASSWORD'] 
	MYSQL_CURSORCLASS = 'DictCursor'
	MYSQL_DBALC = 'PSH'

	SQLALCHEMY_DATABASE_URI = 'mysql://' + MYSQL_USER + ':' + MYSQL_PASSWORD + '@' + MYSQL_HOST + '/' + MYSQL_DBALC
	SQLALCHEMY_TRACK_MODIFICATIONS = False	
	



	
class TestConfig(Config):

	DEBUG = True
	TESTING = True

	SECRET_KEY = os.environ['AWS_SECRET_ACCESS_KEY']

	AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID'] 
	AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY'] 

	MYSQL_HOST = os.environ['MYSQL_HOST'] 
	MYSQL_USER = os.environ['MYSQL_USER'] 
	MYSQL_PASSWORD = os.environ['MYSQL_PASSWORD']  
	MYSQL_CURSORCLASS = 'DictCursor'
	MYSQL_DBALC = 'PSH'

	SQLALCHEMY_DATABASE_URI = 'mysql://' + MYSQL_USER + ':' + MYSQL_PASSWORD + '@' + MYSQL_HOST + '/' + MYSQL_DBALC
	SQLALCHEMY_TRACK_MODIFICATIONS = False	





class ProductionConfig(Config):
	DEBUG = False

	SECRET_KEY = os.environ['AWS_SECRET_ACCESS_KEY']

	AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID'] 
	AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY'] 

	MYSQL_HOST = os.environ['MYSQL_HOST'] 
	MYSQL_USER = os.environ['MYSQL_USER'] 
	MYSQL_PASSWORD = os.environ['MYSQL_PASSWORD'] 
	MYSQL_CURSORCLASS = 'DictCursor'
	MYSQL_DBALC = 'PSH'

	SQLALCHEMY_DATABASE_URI = 'mysql://' + MYSQL_USER + ':' + MYSQL_PASSWORD + '@' + MYSQL_HOST + '/' + MYSQL_DBALC
	SQLALCHEMY_TRACK_MODIFICATIONS = False	











