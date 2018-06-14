
import os 

class Config:


	APP_NAME = 'PSH'

	PUSHOVER_ENABLED = 'False'

	HTTP_CORE = os.environ['HTTP_CORE'] 
	REDIRECT_PARAM = "HTTP"

	IMG_STAGE_DIR = 'static/media/MPSH_entries/stage/' 
	IMG_FINAL_DIR = 'static/media/MPSH_entries/final/'
	MAIL_TEMPLATE_DIR = 'static/mail/'

	AWS_S3_ROOT = os.environ['AWS_S3_ROOT']
	AWS_S3_ORGIMG = "static/media/MPSH_entries/Original"
	AWS_S3_SMALLIMG = "static/media/MPSH_entries/Small"
	AWS_S3_THUMBIMG = "static/media/MPSH_entries/Thumbnail"

	#Pushover Notification Keys.
	PUSHOVER_USERKEY = os.environ['PUSHOVER_USERKEY']
	PUSHOVER_API = os.environ['PUSHOVER_API']


	#Photo Analysis Functions
	RUN_GOOGLEVISION = os.environ['RUN_GOOGLEVISION']



	#GOOGLE_APPLICATION_CREDENTIALS = "secure/googleCreds.json"	

	GOOGLE_VISION_MIN_LABEL_SCORE = 0.60 

	AWS_DEFAULT_REGION = 'ap-southeast-2'

	SQLALCHEMY_TRACK_MODIFICATIONS = False	
	SQLALCHEMY_TRACK_MODIFICATIONS = False

	#Email Configuration.
	MAIL_SERVER = os.environ['SMTP_SERVER']
	MAIL_PORT = os.environ['SMTP_PORT']
	MAIL_USE_TLS = False #os.environ['MAIL_TLS']
	MAIL_USE_SSL = os.environ['MAIL_SSL']
	#MAIL_DEBUG : default app.debug
	MAIL_USERNAME = os.environ['MAIL_USERNAME']
	MAIL_PASSWORD = os.environ['MAIL_PASSWORD']

	#MAIL_DEFAULT_SENDER : default None
	#MAIL_MAX_EMAILS : default None
	#MAIL_SUPPRESS_SEND : default app.testing
	#MAIL_ASCII_ATTACHMENTS : default False



class LocalConfig(Config):
	DEBUG = True
	PUSHOVER_ENABLED = 'True'
	SECRET_KEY = 'MP$H_2019_prd'

	MYSQL_HOST = 'localhost'
	MYSQL_USER = os.environ['MYSQL_USER'] 
	MYSQL_PASSWORD = os.environ['MYSQL_PASSWORD']
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
	REDIRECT_PARAM = os.environ['REDIRECT_PARAM']

	IMG_STAGE_DIR = '/opt/python/current/app/static/media/MPSH_entries/stage/'
	IMG_FINAL_DIR = '/opt/python/current/app/static/media/MPSH_entries/final/'

	SECRET_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
	AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID'] 
	AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY'] 
	PUSHOVER_ENABLED = os.environ['PUSHOVER_ENABLED'] 

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

	REDIRECT_PARAM = os.environ['REDIRECT_PARAM']

	SECRET_KEY = os.environ['AWS_SECRET_ACCESS_KEY']

	AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID'] 
	AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY'] 
	PUSHOVER_ENABLED = os.environ['PUSHOVER_ENABLED'] 

	MYSQL_HOST = os.environ['MYSQL_HOST'] 
	MYSQL_USER = os.environ['MYSQL_USER'] 
	MYSQL_PASSWORD = os.environ['MYSQL_PASSWORD']  
	MYSQL_CURSORCLASS = 'DictCursor'
	MYSQL_DBALC = 'PSH'

	SQLALCHEMY_DATABASE_URI = 'mysql://' + MYSQL_USER + ':' + MYSQL_PASSWORD + '@' + MYSQL_HOST + '/' + MYSQL_DBALC
	SQLALCHEMY_TRACK_MODIFICATIONS = False	





class ProductionConfig(Config):
	DEBUG = False

	REDIRECT_PARAM = os.environ['REDIRECT_PARAM']

	SECRET_KEY = os.environ['AWS_SECRET_ACCESS_KEY']

	AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID'] 
	AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY'] 
	PUSHOVER_ENABLED = os.environ['PUSHOVER_ENABLED'] 

	MYSQL_HOST = os.environ['MYSQL_HOST'] 
	MYSQL_USER = os.environ['MYSQL_USER'] 
	MYSQL_PASSWORD = os.environ['MYSQL_PASSWORD'] 
	MYSQL_CURSORCLASS = 'DictCursor'
	MYSQL_DBALC = 'PSH'

	SQLALCHEMY_DATABASE_URI = 'mysql://' + MYSQL_USER + ':' + MYSQL_PASSWORD + '@' + MYSQL_HOST + '/' + MYSQL_DBALC
	SQLALCHEMY_TRACK_MODIFICATIONS = False	











