
import os
import io
import sys
import uuid
import random
import re
from PIL import Image
import boto3
import watchtower, logging, logging.config
from pushover import init, Client
from datetime import datetime, timedelta
from decimal import Decimal
# Flask Imports
from flask import Flask, flash, json, jsonify, redirect, render_template, request, session, url_for
from flask_uploads import UploadSet, IMAGES
from flask_mail import Message, Mail

from flask_wtf.file import FileField, FileAllowed, FileRequired
# WTForms Imports
from wtforms import FileField, Form, PasswordField, SelectField, StringField, validators
from flask_mysqldb import MySQL
from functools import wraps
from passlib.hash import sha256_crypt

from google.cloud import vision
from google.cloud.vision import types
# SQL Alchemy
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from sqlalchemy import and_
#Flask Social
#from flask_social import Social, SQLAlchemyConnectionDatastore, login_failed
#from flask_social.utils import get_connection_values_from_oauth_response


# Custom Files
import appConfig as ac

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
application = Flask(__name__)





if "RunEnv" in os.environ:
		env = os.environ['RunEnv'] 
else:
	env = 'local'

#env = sys.argv[1] if len(sys.argv) > 2 else 'dev'
if env == 'local':
	application.config.from_object('appConfig.LocalConfig')
elif env == 'dev':
	application.config.from_object('appConfig.DevelopmentConfig')
elif env == 'test':
	application.config.from_object('appConfig.TestConfig')
elif env == 'prod':
	application.config.from_object('appConfig.ProductionConfig')
else:
	raise ValueError('Invalid environment name')

application.config["RunEnv"] = env

#Load Mail Configuration
mail = Mail(application)


# Application Configuration for SQL Alchemy
db = SQLAlchemy(application)
images = UploadSet('images', IMAGES)



## ==WRAPPERS===================================================================
#@application.before_request
#def before_request():
#	if (application.config['RunEnv'] is not "local"):
#		if request.url.startswith('http://'):
#			url = request.url.replace('http://', 'https://', 1)
#			code = 301
#			return redirect(url, code=code)


def loginStatus(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'loggedIn' in session:
			return f(*args, **kwargs)
		else:
			flash("Please login to access content!", 'danger')
			return redirect(url_for('login', _scheme=application.config["REDIRECT_PARAM"], _external=True))
	return wrap

 

@application.errorhandler(404)
def page_not_found(e):
	return render_template('home.html', headerEntry=sqlA_GET_Entries_RND()), 404

# ==ROUTES=====================================================================
# View Site Index Page.
@application.route('/')
def index():
	return render_template('home.html', headerEntry=sqlA_GET_Entries_RND())

# View the About Page


@application.route('/about')
def about():
	return render_template('about.html', headerEntry=sqlA_GET_Entries_RND())

# View the Contact Page


@application.route('/contact')
def contact():
	return render_template('contact.html', headerEntry=sqlA_GET_Entries_RND())


@application.route('/scorecard')
@loginStatus
def scorecard():
	scorecard = listScorecard()
	listScores = None
	if (len(scorecard['users'])>3):
		listScores = True
	else:
		listScores = False
	return render_template('scorecard.html', listScores=listScores, scorecard=scorecard, headerEntry=sqlA_GET_Entries_RND())

# Listing all Entries


@application.route('/entries')
@loginStatus
def entries():
	entries = sqlA_GET_Entries_FILT_compID_approved(session['competitionID'])
	return render_template('entries.html', entries=entries, entriesAvailable=(len(entries) >= 1), headerEntry=sqlA_GET_Entries_RND())

@application.route('/entries/category/<string:categoryID>/')
@loginStatus
def entriesByCategory(categoryID):
	entries = sqlA_GET_Entries_FILT_compID_approved_categoryID(session['competitionID'], categoryID)
	return render_template('entries.html', entries=entries, entriesAvailable=(len(entries) >= 1), headerEntry=sqlA_GET_Entries_RND())


# Approve Entries
@application.route('/approve')
@loginStatus
def approveEntries():
	return render_template('approve.html', headerEntry=sqlA_GET_Entries_RND())

# View Entry By ID


@application.route('/entries/entry/<string:entryID>/')
def entry(entryID):
	entries = sqlA_GET_Entries_FILT_compID_approved(session['competitionID'])
	return render_template('entry.html', entryID=entryID, headerEntry=sqlA_GET_Entries_RND())

@application.route('/entries/tags/<string:tag>/')
def entriesTags(tag):
	entries = sqlA_GET_Entries_FILT_compID_approved(session['competitionID'])
	return render_template('entries.html', entries=entries, entriesAvailable=(len(entries) >= 1), headerEntry=sqlA_GET_Entries_RND())


# Registering a New User
@application.route('/register', methods=['GET', 'POST'])
def register():
	form = form_userRegistation(request.form)
	if request.method == 'POST' and form.validate():

		newUser = sqlA_ADD_Users(form.userName.data, form.firstName.data, form.lastName.data,
					   form.email.data, sha256_crypt.encrypt(str(form.password.data)))
		GUID = newUUID = uuid.uuid4().hex

		sqlA_ADD_GUIDRequest(GUID, 1, newUser.id) # 1 = Activate User
		mail_send_UserRegistration(newUser, GUID)
		msg(str("Registering: " + str(form.userName.data)))
		flash('User Sign up is Completed! Please Login.', 'success')
		return redirect(url_for('accountPendingActivation', _scheme=application.config["REDIRECT_PARAM"], _external=True))

	return render_template('register.html', form=form, headerEntry=sqlA_GET_Entries_RND())



# Registering a New Entry
@application.route('/submitEntry', methods=['GET', 'POST'])
@loginStatus
def submitEntry():

	# Category Drop Down Field.
	# Get Available Categories from DB and present them as Entry Options in the Form.
	# Categories will only be presented to the user if they have not already
	# been submitted and JUDGED as approved & the day has concluded.

	# Get List of Categoires that a User Can Submit.
	outstandingCategories = sqlA_GET_AvailableCategories_FILT_userID_compID(session['userID'], session['competitionID'])
	#outstandingCategories = sqlA_GET_AllCategories_FILT_compID(session['competitionID'])
	#outstandingCategories = sqlA_GET_AvailableCategories_FILT_userID(session['userID'])

	categories = []
	for category in outstandingCategories:
		if (category.value > 1):
			pTxt = "Points"
		else:
			pTxt = "Point"

		categoryTitle = ("(" + str(category.value) + " " + pTxt + ") " + category.title)
		categories.append((category.id, categoryTitle))

	form = form_submitEntry(request.form, obj=categories)
	# Set the Categories for the Drop Down.
	form.cateogryID.choices = categories

# 	if request.method == 'POST':
# 		# Will Submit Entry if POST and Validated Form.
# 		target = os.path.join(APP_ROOT, application.config['IMG_STAGE_DIR'])
# 		# If the file uploaded during Pre-Process rename the TMP file to final File.
# 		if (os.path.isfile("".join([target, form.tmpFileName.data])) == True):
# 			filename = (form.tmpFileName.data).replace('_tmp_', '', 1)
# 			UUID = form.entryImageUUID.data
# 			os.rename(("".join([target, form.tmpFileName.data])), ("".join([target, filename])))

# 		# No File was uploaded in the "Pre-Process" so it is being uploaded now.
# 		# Google Vision Will be run over the file again.
# 		else:
# 			for file in request.files.getlist("entryImage"):
# 				filename, UUID = image_fileNameGenerator(session['userName'], form.cateogryID.data, False)
# 				imagePath = "".join([target, filename])
# 				file.save(imagePath)

# 				json.dumps(processEntry(imagePath, filename, UUID))

# 		#### S3 File Move Logic HERE!
# 		imgOrgURL,imgSmallURL, imgThumbURL = processAWSS3Save(imagePath, filename, UUID)

# 		sqlA_ADD_Entry(session['userID'], session['competitionID'], form.cateogryID.data, str(
# 			form.entryTitle.data), str(form.entryDescription.data), str(UUID), str(filename), imgOrgURL,imgSmallURL, imgThumbURL, latitude, longitude, placeID, placeName, placeAddress)

# 		flash('Photo Entry is Completed! Good Luck!', 'success')
# 		return redirect(url_for('index', _scheme=application.config["REDIRECT_PARAM"], _external=True))

	return render_template('submit.html', form=form, headerEntry=sqlA_GET_Entries_RND())




@application.route('/profile/<string:userID>/')
@loginStatus
def profile(userID):
	
	userDetails = sqlA_GET_User_FILT_id(userID)
	userStats = sqlA_GET_User_Statistics_FILT_User_CompID(userID, session['competitionID'])
	if (session["userID"] == int(userID))	:
		userEntries = sqlA_GET_Entries_FILT_compID_userID(session['competitionID'], userID)
	else:
		userEntries = sqlA_GET_Entries_FILT_compID_approved_userID(session['competitionID'], userID) 

	return render_template('dashboard.html', entries=userEntries, userDetails=userDetails, userStats=userStats)


@application.route('/logout')
@loginStatus
def logout():

	msg(str("User " + session['userName'] + " Logging Out!"))
	# Get The User Object
	currentUser = sqlA_GET_User_FILT_id(session['userID'])
	currentUser.updateLastLogout()
	db.session.commit()
	session.clear()
	#flash('You are now logged out!', 'success')
	return redirect(url_for('login', _scheme=application.config["REDIRECT_PARAM"], _external=True))


@application.route('/login', methods=['POST', 'GET'])
def login():
	if request.method == 'POST':

		# Get Login Form Details
		msg(str("User attempting to login as User: " + request.form['username']))
		# Attempt Login with Username
		currentUser = sqlA_GET_User_FILT_Username(request.form['username'])
		if currentUser is None:
			# No Username so Attempt Login with Email
			currentUser = sqlA_GET_User_FILT_Email(request.form['username'])
			# Check if
			if currentUser is None:
				# Neither Email or Username Exists. Login Fails
				msg(str("Login Failed for username " + request.form['username']))
				error = "Invalid Login."
				return render_template('login.html', error=error, headerEntry=sqlA_GET_Entries_RND())

		# Username or Email Found Now Verifying Password
		if sha256_crypt.verify(request.form['password'], currentUser.password):
			# Password Confirmed and User is Authenticated
			session['loggedIn'] = True
			session['userName'] = currentUser.userName
			session['firstName'] = currentUser.firstName
			session['userID'] = currentUser.id
			session['competitionID'] = 1
			# Update the Users Last Login Timestamp.
			currentUser.updateLastLogin()
			db.session.commit()
			flash('You are  now logged in!', 'success')
			return redirect(url_for('profile',userID=session['userID'], _scheme=application.config["REDIRECT_PARAM"], _external=True))
		else:
			# Ther User Exists but the Password Supplied was inccorect.
			msg(str("Login Failed for username " + request.form['username']))
			error = "Invalid Login."
			return render_template('login.html', error=error, headerEntry=sqlA_GET_Entries_RND())

	# Return Loign Screen as Default Route.
	return render_template('login.html', headerEntry=sqlA_GET_Entries_RND())



@application.route('/register/pending/')
def accountPendingActivation():
	return render_template('activation.html', expired=False, notFound=False, activated=False, registered=True)


@application.route('/register/activation/<string:regGUID>/')
def accountActivate(regGUID):

	expired = None
	notFound = None
	activated = None

	currentAction = sqlA_GET_GUIDRequest(regGUID, 1) #1 = User Activation
	if currentAction is not None:
		currentUser = sqlA_GET_User_FILT_id_inactive(currentAction.objectID)
		if currentUser is not None:
			currentUser.activateUser()
			db.session.commit()
			currentAction.GUIDActionRun()
			db.session.commit()
			activated = True
		else:
			expired = True

	else:
		expired = True


	#Put the code here that will look up the regGUID. 
	#If the regGUID is found then activate the user and delete the GUID from the DB. Then display success message and link to login.
	#If the regGUID isn't found or is not linked to a user display appropriate registration error.
	return render_template('activation.html', expired=expired, notFound=notFound, activated=activated, registered=False)


@application.route('/user/passwordReset/<string:passGUID>/')
@loginStatus
def accountPassReset(passGUID):
	#Put the code here that will look up the regGUID. 
	#If the regGUID is found then activate the user and delete the GUID from the DB. Then display success message and link to login.
	#If the regGUID isn't found or is not linked to a user display appropriate registration error.
	return render_template('passwordReset.html')



# ============================================================================


# ==FORMS=====================================================================
# User Registation Class
class form_userRegistation(Form):
	# Submit a Registration for the Scavenger Hunt.
	userName = StringField('User Name', [validators.Length(min=8, max=30)])
	firstName = StringField('First Name', [validators.Length(min=1, max=50)])
	lastName = StringField('Last Name', [validators.Length(min=1, max=50)])
	email = StringField('Email Address', [validators.Length(min=5, max=90)])
	password = PasswordField('Password', [
		validators.DataRequired(), validators.EqualTo('passwordConfirm', message="Passwords do not match!")
	])
	passwordConfirm = PasswordField('Confirm Password')

# Entry Entry Submission Class


class form_submitEntry(Form):
	# Submit and Entry Photograph for the Scavenger Hunt.
	cateogryID = SelectField(u'Photo Category', coerce=int)
	entryTitle = StringField('Photo Title', [validators.Length(min=1, max=150)])
	entryDescription = StringField('Photo Description', [validators.Length(min=1, max=250)])
	entryImage = FileField('Image File', validators=[FileRequired(), FileAllowed(images, 'Images only!')])
	entryImageUUID = StringField()
	tmpFileName = StringField()


# ============================================================================
# ==SUPPPORT FUNCTIONS========================================================
# ============================================================================

#Migrate EC2 to S3
def processAWSS3Save(imagePath, filename, UUID):

	Image.MAX_IMAGE_PIXELS = 1000000000

	target = os.path.join(APP_ROOT, application.config['IMG_FINAL_DIR'])
	source = os.path.join(APP_ROOT, application.config['IMG_STAGE_DIR'])


	if (os.path.isfile("".join([source, filename])) == True):

		s3 = boto3.client('s3', aws_access_key_id=application.config['AWS_ACCESS_KEY_ID'], aws_secret_access_key=application.config['AWS_SECRET_ACCESS_KEY'])
		bucket = application.config['AWS_S3_ROOT']

		bucket_location = s3.get_bucket_location(Bucket=bucket)
		

		originalFilename = "original_" + str(UUID)
		smallFilename = "small_" + str(UUID)
		thumbFilename = "thumb_" + str(UUID)

		
		originalFile = ("".join([source, filename]))
		im = Image.open(originalFile)

		#Make Original Image JPEG
		im.save(("".join([target, originalFilename])), "JPEG")

		#Make Small/Web Image JPEG
		maxsize = (1028, 1028)
		im.thumbnail(maxsize, Image.ANTIALIAS)
		im.save(("".join([target, smallFilename])), "JPEG")

		#Make Thumbnail Image JPEG
		maxsize = (257, 257)
		im.thumbnail(maxsize, Image.ANTIALIAS)
		im.save(("".join([target, thumbFilename])), "JPEG")

		#Cleanup Source File
		os.remove(("".join([source, filename])))


		imgOrgURL = None
		imgSmallURL = None
		imgThumbURL = None

		#Uploading Original Image
		key_name = str(application.config['AWS_S3_ORGIMG']+"/"+originalFilename)
		s3.upload_file(("".join([target, originalFilename])), bucket, key_name, ExtraArgs={'ACL': 'public-read'})
		imgOrgURL = "https://s3-{0}.amazonaws.com/{1}/{2}".format(bucket_location['LocationConstraint'],bucket, key_name)
		os.remove(("".join([target, originalFilename])))

		#Uploading Small/Web Image
		key_name = str(application.config['AWS_S3_SMALLIMG']+"/"+smallFilename)
		s3.upload_file(("".join([target, smallFilename])), bucket, key_name, ExtraArgs={'ACL': 'public-read'})
		imgSmallURL = "https://s3-{0}.amazonaws.com/{1}/{2}".format(bucket_location['LocationConstraint'],bucket, key_name)
		os.remove(("".join([target, smallFilename])))

		#Uploading Thumb Image
		key_name = str(application.config['AWS_S3_THUMBIMG']+"/"+thumbFilename)
		s3.upload_file(("".join([target, thumbFilename])), bucket, key_name, ExtraArgs={'ACL': 'public-read'})
		imgThumbURL ="https://s3-{0}.amazonaws.com/{1}/{2}".format(bucket_location['LocationConstraint'],bucket, key_name)
		os.remove(("".join([target, thumbFilename])))

		return imgOrgURL,imgSmallURL, imgThumbURL

	else:
		return None, None, None


def processTag(tag):
	if tag is not None:
		tag = tag.lower()
		tag = tag.strip()
		regex = re.compile('[^a-zA-Z0-9]')
		tag = regex.sub('', tag)
		return tag
	else:
		return None


# Generate Photo File Name
def image_fileNameGenerator(userID, category, tmpFlag):

	newUUID = uuid.uuid4().hex
	filename = str((str(userID) + "_" + str(category) + "_" + str(newUUID)))

	if (tmpFlag == True):
		filename = str("_tmp_" + filename)

	return filename, newUUID

# Check if the Email address being registered is already in the DB.


def register_CheckExistingEmailAddress(in_Email):
	if (sqlA_GET_User_FILT_Email(in_Email) is None):
		# Email not registered. Return Reuslts False.
		return False
	else:
		# Email is already registered. Return Reuslts True.
		return True


# Check if the Username address being registered is already in the DB.
def register_CheckExistingUsername(in_Username):
	if (sqlA_GET_User_FILT_Username(in_Username) is None): 
		# Username not registered. Return Reuslts False.
		return False
	else:
		# Username is already registered. Return Reuslts True.
		return True


def processEntry(imgPath, filename, UUID):
	# Analyse the Image using Google Vision to return known information about the image store it within the Database.
	# Instantiates a client
	client = vision.ImageAnnotatorClient()
	# The name of the image file to annotate
	file_name = str(imgPath)

	response_json = {}
	response_json["UUID"] = UUID
	response_json["TMPFileName"] = filename

	# Loads the image into memory
	with io.open(file_name, 'rb') as image_file:
		content = image_file.read()
	image = types.Image(content=content)
	

	googleVision = run_googleVision(image)
	response_json["Vision"] = googleVision

	return response_json


def run_googleVision(image):

	vision_objects = {}
	vision_children = []
	vision_children_labels = []

	if(application.config["RUN_GOOGLEVISION"] == True):
		# Performs label detection on the uploaded image
		response = client.label_detection(image=image)
		# Build the List of Vision Label Objects
		for label in response.label_annotations:
			vision_label_item = {}
			vision_label_item["Description"] = label.description.title()
			vision_label_item["Score_Raw"] = label.score
			vision_label_item["Score_Dec"] = (round(Decimal(vision_label_item["Score_Raw"]), 2) * 100)
			vision_label_item["Topicality"] = label.topicality
			vision_label_item["Mid"] = label.mid
			if (float(vision_label_item["Score_Raw"]) >= application.config['GOOGLE_VISION_MIN_LABEL_SCORE']):
				vision_label_item["Upload_Display"] = "True"
			else:
				vision_label_item["Upload_Display"] = "False"
			vision_children_labels.append(vision_label_item)
		

	vision_objects["labels"] = vision_children_labels
	vision_children.append(vision_objects)

	return vision_children





def listScorecard():

	comp = sqlA_GET_Competition_FILT_compID(session["competitionID"])

	scorecard = {}
	users = []
	headerDates = []

	# Get all Users in the Competition
	results = sqlA_GET_Competition_Users_FILT_compID(session["competitionID"])

	# For Every User generate their entry scorecard.
	for item in results:
		user = {}

		user["userID"] = item.id
		user["userName"] = item.userName
		user["rank"] = None
		user["totalScore"] = 0

		entries = sqlA_GET_Entries_FILT_compID_approved_userID(session["competitionID"], user["userID"])
		entryScoreCard = []
		headerDates = []

		for i in range((comp.competitionFinishDate - comp.competitionStartDate).days + 1):
			day = {}
			date = (comp.competitionStartDate + timedelta(days=i)).date()
			day["date"] = date
			day["validEntry"] = False
			day["score"] = 0
			headerDates.append(date) 
			for entry in entries:
				
				if (str(date) == str(entry.sysCreated.date())):

					day["validEntry"] = True
					day["cateogryID"] = entry.category.id
					day["cateogryTitle"] = entry.category.title
					day["cateogryDescription"] = entry.category.description
					day["score"] = entry.category.value
					day["id"] = entry.id
					day["entryTitle"] = entry.title
					day["entryDescription"] = entry.description
					user["totalScore"] = int(user["totalScore"]) + int(day["score"])
			   

			   
			if (day["validEntry"] == False):
				if (date < datetime.now().date()):
					#The Day has passed and No Entry was submitted. 
					#Generate Negative Score based on competition rules. (Each Competition can have its own Penalty Score)
					day["score"] = int(comp.penaltyMissedEntry)
					user["totalScore"] = int(user["totalScore"]) + int(day["score"])
				else:
					#The Day has not yet passed and is therefore represented by a blank. 
					day["score"] = 0
					user["totalScore"] = int(user["totalScore"]) + int(day["score"])

			entryScoreCard.append(day)

		user["entries"] = entryScoreCard
		users.append(user)


	usersSorted = [(dict_["totalScore"], dict_) for dict_ in users]
	usersSorted.sort(reverse=True)
	results = [dict_ for (key, dict_) in usersSorted]

	currentRank = 1
	lastScore = 99999
	maxRank = 0
	for result in results:

		if (result["totalScore"] == lastScore):
			result["rank"] = (currentRank - 1)
		else:
			result["rank"] = (currentRank)
			currentRank = (currentRank + 1)
			
		maxRank = currentRank
		lastScore = result["totalScore"]


	scorecard["users"] = results
	scorecard["maxRank"] = maxRank
	scorecard["headers"] = headerDates


	#with open('dumps.json', 'w') as f:
	#    f.write(json.dumps(scorecard, sort_keys=True, indent=4, separators=(',', ': ')))
	#    f.close()
	
   

	return scorecard


def updateEntryStatus(entry, judgement):

	# JudgmentType (1 = Percentage Judgment, 2 = Admin Only Judging, 3 = Min Votes Judging)
	competition = sqlA_GET_Competition_FILT_compID(session["competitionID"])

	# % Based Approval
	if (competition.judgementType == 1):
		competitors = sqlA_GET_CompetitionUser_FUNC_Count_FILT_compID(session["competitionID"])

		# Check if Entry had Met the Required Player % to Approve
		if (float(sqlA_GET_Entry_FUNC_Count_FILT_Approvals(entry.id)) /
				float(competitors)) >= float(competition.judgeMinApprovePercentage):
			msg(str("Entry: (" + str(entry.id) + ") by User: "+str(entry.uploader.userName)+ " is being Approved using the % Crowd Sourcing Method"))
			entry.entryStatus[0].approveEntry()
			mail_send_entryApproved(entry.id)
			return entry
		# Check if Entry had Met the Required Player % to Reject
		elif (float(sqlA_GET_Entry_FUNC_Count_FILT_Rejections(entry.id)) / float(competitors)) >= float(competition.judgeMinRejectPercentage):
			msg(str("Entry: (" + str(entry.id) + ") by User: "+str(entry.uploader.userName)+ " is being Rejected using the % Crowd Sourcing Method"))
			entry.entryStatus[0].rejectEntry()
			mail_send_entryRejected(entry.id)
			return entry
		else:
			entry.entryStatus[0].progressEntry()
			return entry
	# Admin Based Approval
	elif (competition.judgementType == 2):
		if (judgement == 1):
			msg(str("Entry: (" + str(entry.id) + ") by User: "+str(entry.uploader.userName)+ " is being Approved using the Admin Method"))
			entry.entryStatus[0].approveEntry()
			mail_send_entryApproved(entry.id)
			return entry
		else:
			msg(str("Entry: (" + str(entry.id) + ") by User: "+str(entry.uploader.userName)+ " is being Rejected using the Admin Method"))
			entry.entryStatus[0].rejectEntry()
			mail_send_entryRejected(entry.id)
			return entry
	# Vote Based Approval
	elif (competition.judgementType == 3):
		# Check if Entry had Met the Required Player Votesto Approve
		if (float(sqlA_GET_Entry_FUNC_Count_FILT_Approvals(entry.id)) >= float(competition.judgeMinApproveVotes)):
			msg(str("Entry: (" + str(entry.id) + ") by User: "+str(entry.uploader.userName)+ " is being Approved using the Voting Method"))
			entry.entryStatus[0].approveEntry()
			mail_send_entryApproved(entry.id)
			return entry
		# Check if Entry had Met the Required Player Votes to Reject
		elif (float(sqlA_GET_Entry_FUNC_Count_FILT_Rejections(entry.id)) >= float(competition.judgeMinRejectVotes)):
			msg(str("Entry: (" + str(entry.id) + ") by User: "+str(entry.uploader.userName)+ " is being Rejected using the Voting Method"))
			entry.entryStatus[0].rejectEntry()
			mail_send_entryRejected(entry.id)
			return entry
		else:
			entry.entryStatus[0].progressEntry()
			return entry
	# No True Approval Method Provided.
	else:
		return entry


def msg(in_msg):
	application.logger.info(in_msg)
	pushover_send(in_msg)


def awsSession():
	session = boto3.session.Session(aws_access_key_id=application.config["AWS_ACCESS_KEY_ID"],aws_secret_access_key=application.config["AWS_SECRET_ACCESS_KEY"],region_name=application.config["AWS_DEFAULT_REGION"])
	return session

def boto3Client(service):
	client = boto3.client(service,aws_access_key_id=application.config["AWS_ACCESS_KEY_ID"],aws_secret_access_key=application.config["AWS_SECRET_ACCESS_KEY"])#,aws_session_token=awsSession(),)
	return client


# ============================================================================
# ======== API V1 ============================================================
# ============================================================================
@application.route('/api/v1.0/judge/getEntry', methods=['POST'])
def get_api_v1_judgeGetEntry():

	results = {}
	# Execute a Select for the Next Entry that needs Judging.
	# Select should return oldest Submitted with least votes.
	# Where Requesting User has not voted on image before.
	# Where Requesting User did not submit image.
	# Where Requesting User is not tagged (NEEDS TO BE MODIFIED LATER WHEN TAGGING IS IMPLEMENTED)
	selection = sqlA_GET_Entries_FILT_compID_pending_notSelf_ORD_longestWait(
		session['competitionID'], session['userID'])

	if not selection:
		entries = False
	else:
		for item in selection:
			results["entryTitle"] = item.title
			results["entryDescription"] = item.description
			results["entry_date"] = item.sysCreated
			results["overallStatus"] = item.entryStatus[0].status.statusTitle
			results["imgFileName"] = item.imgFileName
			results["originalURL"] = item.S3imgOrgURL
			results["smallURL"] = item.S3imgSmallURL
			results["thumbnailURL"] = item.S3imgThumbURL
			results["firstName"] = item.uploader.firstName
			results["lastName"] = item.uploader.lastName
			results["userName"] = item.uploader.userName
			results["entryID"] = item.id
			category = sqlA_GET_AllCategories_FILT_compID_catID(session['competitionID'], item.categoryID)
			results["categoryID"] = category.id
			results["categoryValue"] = category.value
			results["categoryTitle"] = category.title
			results["categoryDescription"] = category.description
			entries = True
	# Returning a New Entry to be judged.
	return jsonify({'Entry': results, 'Entries': entries})

@application.route('/api/v1.0/entry/submit', methods=['POST'])
def get_api_v1_entrySubmit():

	statusCode = 400
	status = "Upload Failed"
	statusLongText = "There was an error uploading your entry into the database. Please fresh the page and try again"

	if request.method == 'POST':
		# Will Submit Entry if POST and Validated Form.
		target = os.path.join(APP_ROOT, application.config['IMG_STAGE_DIR'])
		data = json.loads(request.data)

		# If the file uploaded during Pre-Process rename the TMP file to final File.
		if (os.path.isfile("".join([target, data["tmpFileName"]])) == True):
			filename = (data["tmpFileName"].replace('_tmp_', '', 1))
			UUID = data["UUID"]
			os.rename(("".join([target, data["tmpFileName"]])), ("".join([target, filename])))

			#### S3 File Move Logic HERE!
			imgOrgURL,imgSmallURL, imgThumbURL = processAWSS3Save(("".join([target, filename])), filename, UUID)

			
			#Clean and Process Tags
			uploadedTags = data["uploadTags"]
			cleanTags = []
			for tag in uploadedTags:

				cleanTags.append(processTag(tag))
				#Remove Duplicate Tags
				cleanTags = list(set(cleanTags))

			#Handling Tags
			tags = []
			#Add Competition Tag
			tag = {}
			tag["text"] = processTag(sqlA_GET_Competition_Tag(session["competitionID"]))
			tag["type"] = 1 #Competition Tag Type
			if tag["text"] is not None:
				tags.append(tag)
				while tag["text"] in cleanTags: cleanTags.remove(tag["text"])
			#Add Category Tags
			tag = {}
			tag["text"] = processTag(sqlA_GET_Category_Tag(data["categoryID"], session["competitionID"]))
			tag["type"] = 2 #Category Tag Type
			if tag["text"] is not None:
				tags.append(tag)
				while tag["text"] in cleanTags: cleanTags.remove(tag["text"])		
			#Add Username Tag
			tag = {}
			tag["text"] = processTag(session["userName"])
			tag["type"] = 3 #Username Tag Type
			if tag["text"] is not None:
				tags.append(tag)
				while tag["text"] in cleanTags: cleanTags.remove(tag["text"])
			#Add Custom Tags
			for item in cleanTags:
				tag = {}
				tag["text"] = processTag(item)
				tag["type"] = 4 #User Generated
				tags.append(tag)

			sqlA_ADD_Entry(session['userID'], session['competitionID'], data["categoryID"], str(
				data["title"]), str(data["description"]), str(UUID), str(filename), imgOrgURL,imgSmallURL, imgThumbURL, data["entryLocation"], tags)


			for item in data["imageLabels"]:
				tags.append(item)

			statusCode = 200
			status = "Upload Successful"
			statusLongText = "Your Entry has been accepted and it pending the judges approval."
			msg(str("User: " + str(session["userName"] + " added a New Entry.")))
	

	return jsonify({'statusCode': statusCode, 'status': status, 'statusLongText': statusLongText})







@application.route('/api/v1.0/entry/approve', methods=['POST'])
def get_api_v1_entryApprove():

	if (int(request.form["judgment"]) == 1):
		msg(str("User: " + str(session["userName"] + " approved an entry.")))
		judgment = 1
	else:
		judgment = -1
		msg(str("User: " + str(session["userName"] + " rejected an entry.")))
	sqlA_ADD_Approval(request.form["entryID"], session["userID"], judgment, request.form["msg"])

	# AJAX Request from Client to Approve a Single Entry.
	return jsonify({'text': "Judgment Completed"})



@application.route('/api/v1.0/category/categoryGuide', methods=['POST'])
def get_api_v1_getCategoryGuide():
	if request.method == 'POST':
		data = json.loads(request.data)
		#print data["categoryID"]
		return json.dumps("Pending The Category Rules")


@application.route('/api/v1.0/entry/outstandingCategories', methods=['POST'])
def get_api_v1_outstandingCategories():

	outstandingCategories = sqlA_GET_AvailableCategories_FILT_userID_compID(session['userID'], session['competitionID'])

	categories = []
	for category in outstandingCategories:
		if (category.value > 1):
			pTxt = "Points"
		else:
			pTxt = "Point"

		categoryValue = (str(category.value) + " " + pTxt)
		categoryTitle = ("(" + str(category.value) + " " + pTxt + ") " + category.title)
		categories.append((category.id, categoryTitle, category.description, category.value, category.title))
	return json.dumps(categories)

@application.route('/api/v1.0/photo/upload', methods=['POST'])
def get_api_v1_photoUpload():
	#logAPI(request.url_rule, "START", json_obj)
	target = os.path.join(APP_ROOT, application.config['IMG_STAGE_DIR'])
	file = request.files['file']
	filename, UUID = image_fileNameGenerator(session['userName'], "", True)
	imagePath = "".join([target, filename])
	file.save(imagePath)
	# Process all the Information and formating of an Entry after saving the file locally.
	json_data = json.dumps(processEntry(imagePath, filename, UUID))
	return str(json_data)
	#return "String Test"


@application.route('/api/v1.0/existingUserCheck', methods=['POST'])
def get_api_v1_existingUserCheck():
	json_obj = json.loads(request.data)
	item = register_CheckExistingUsername(json_obj['userName'])
	if item == True:
		return "False"
	else:
		return "True"


@application.route('/api/v1.0/existingEmailCheck', methods=['POST'])
def get_api_v1_existingEmailCheck():
	json_obj = json.loads(request.data)
	item = register_CheckExistingEmailAddress(json_obj['email'])
	if item == True:
		return "False"
	else:
		return "True"


# Log all the API Data to the system.
def logAPI(route, marker, requestData):
	msg("API: [" + str(route) + "] [" + marker + "] with Request Data: " + str(requestData))
	return


# ============================================================================


# ============================================================================
# ==SQL ALCHEMY CLASSES=======================================================


class User(db.Model):
	__tablename__ = 'User'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	userName = db.Column(db.String(150))
	firstName = db.Column(db.String(150))
	lastName = db.Column(db.String(150))
	email = db.Column(db.String(250))
	bio = db.Column(db.String(4000))
	password = db.Column(db.String(250))
	lastLogin = db.Column(db.DateTime)
	lastLogout = db.Column(db.DateTime)
	lastEntry = db.Column(db.DateTime)
	lastJudged = db.Column(db.DateTime)
	totalEntries = db.Column(db.Integer)
	totalJudgements = db.Column(db.Integer)
	profileIMGOriginalFileName = db.Column(db.String(500))
	profileIMGNewFileName = db.Column(db.String(500))
	sysActive = db.Column(db.Integer)
	sysCreated = db.Column(db.DateTime, default=datetime.now)
	sysUpdated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
	# ==[ Vitural Columns ]==
	entries = db.relationship('Entry', backref='User', lazy='dynamic')
	approver = db.relationship('EntryApprovals', backref='User', lazy='dynamic')
	#entryTag = db.relationship("EntryTag")

	# ==[ User Object Methods ]==
	def __init__(self, userName, firstName, lastName, email, password):
		# Required
		self.userName = userName
		self.firstName = firstName
		self.lastName = lastName
		self.email = email
		self.password = password
		self.sysActive = 0
		# Additional
		self.totalEntries = 0
		self.totalJudgements = 0

	def activateUser(self):
		self.sysActive = 1
		return

	def updateLastLogin(self):
		self.lastLogin = datetime.now()
		return

	def updateLastLogout(self):
		self.lastLogout = datetime.now()
		return


class SYSTexts(db.Model):
	__tablename__ = 'sysTexts'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	langKey = db.Column(db.String(3))
	pageCode = db.Column(db.String(100))
	pageTextID = db.Column(db.String(100))
	pageTextOptionID = db.Column(db.Integer)
	text = db.Column(db.String(4000))
	sysActive = db.Column(db.Integer)
	sysCreated = db.Column(db.DateTime, default=datetime.now)
	sysUpdated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)



class GUIDActions(db.Model):
	__tablename__ = 'GUIDActions'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	GUID = db.Column(db.String(100))
	actionCode = db.Column(db.Integer)
	objectID = db.Column(db.Integer) #Holds UserID or Entry ID
	active_from = db.Column(db.DateTime)
	active_to = db.Column(db.DateTime)
	actionCompleted = db.Column(db.DateTime)
	sysActive = db.Column(db.Integer)
	sysCreated = db.Column(db.DateTime, default=datetime.now)
	sysUpdated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

	def __init__(self, GUID, actionCode, objectID):
		# Required
		self.GUID = GUID
		self.actionCode = actionCode
		self.objectID = objectID
		self.activate_from = datetime.now()
		self.activate_to = self.activate_from + timedelta(days=2)
		self.sysActive = 1

	def GUIDActionRun(self):
		# Set Entry Status to "In Progress"
		self.sysActive = 0
		self.actionCompleted = datetime.now()
		return




class EntryApprovals(db.Model):
	__tablename__ = 'EntryApprovals'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	entry = db.Column(db.Integer, db.ForeignKey('Entries.id'))
	# StatusID
	ApproverID = db.Column(db.Integer, db.ForeignKey('User.id'))
	# ApprovalID
	approval = db.Column(db.Integer)
	comment = db.Column(db.String(4000))
	sysActive = db.Column(db.Integer)
	sysCreated = db.Column(db.DateTime, default=datetime.now)
	sysUpdated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
	# ==[ Vitural Columns ]==
	approver  = db.relationship("User", back_populates="approver")

	# ==[ User Object Methods ]==
	def __init__(self, entryID, approverID, approval, comment):
		# Required
		self.entry = entryID
		self.ApproverID = approverID
		self.approval = approval
		self.comment = comment
		self.sysActive = 1


class Categories(db.Model):
	__tablename__ = 'Categories'
	id = db.Column(db.Integer, primary_key=True)
	Competition = db.Column(db.Integer, db.ForeignKey('Competition.id'))
	# tagID
	title = db.Column(db.String(250))
	description = db.Column(db.String(4000))
	tagText = db.Column(db.String(250))
	value = db.Column(db.Integer)
	active_from = db.Column(db.DateTime)
	active_to = db.Column(db.DateTime)
	sysActive = db.Column(db.Integer)
	sysCreated = db.Column(db.DateTime, default=datetime.now)
	sysUpdated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
	# ==[ Vitural Columns ]==
	entries = db.relationship("Entry")


class JudgementType(db.Model):
	__tablename__ = 'JudgementType'
	id = db.Column(db.Integer, primary_key=True)
	judgementCode = db.Column(db.String(10))
	judgementTitle = db.Column(db.String(150))
	sysActive = db.Column(db.Integer)
	sysCreated = db.Column(db.DateTime, default=datetime.now)
	sysUpdated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
	# ==[ Vitural Columns ]==


class Competition(db.Model):
	__tablename__ = 'Competition'
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(150))
	description = db.Column(db.String(250))
	tagText = db.Column(db.String(250))
	judgementType = db.Column(db.Integer, db.ForeignKey('JudgementType.id'))
	judgeMinApprovePercentage = db.Column(db.Float)
	judgeMinRejectPercentage = db.Column(db.Float)
	judgeMinApproveVotes = db.Column(db.Integer)
	judgeMinRejectVotes = db.Column(db.Integer)
	competitionStartDate = db.Column(db.DateTime)
	competitionFinishDate = db.Column(db.DateTime)
	categoryReleaseDate = db.Column(db.DateTime)
	penaltyMissedEntry = db.Column(db.Integer)
	sysActive = db.Column(db.Integer)
	sysCreated = db.Column(db.DateTime, default=datetime.now)
	sysUpdated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
	# ==[ Vitural Columns ]==
	entries = db.relationship("Entry")
	categories = db.relationship("Categories")


class Tags(db.Model):
	__tablename__ = 'Tags'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	competitionID = db.Column(db.Integer, db.ForeignKey('Competition.id'))
	tagText = db.Column(db.String(250))
	tagType = db.Column(db.Integer, db.ForeignKey('TagType.id'))
	tagCount = db.Column(db.Integer, default=1)
	sysActive = db.Column(db.Integer)
	sysCreated = db.Column(db.DateTime, default=datetime.now)
	sysUpdated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
	# ==[ Vitural Columns ]==
	entries  = db.relationship("EntryTag", uselist=True, back_populates="tagID")



	def __init__(self, competitionID, tagText, tagType ):
		# Required
		self.competitionID = competitionID
		self.tagText = tagText
		self.tagType = tagType
		self.sysActive = 1

	def tagUpdate(self):
		# Set Entry Status to "In Progress"
		self.tagCount = (self.tagCount + 1)
		return



class TagType(db.Model):
	__tablename__ = 'TagType'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	tagType = db.Column(db.String(150))
	sysActive = db.Column(db.Integer)
	sysCreated = db.Column(db.DateTime, default=datetime.now)
	sysUpdated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
	# ==[ Vitural Columns ]==



class EntryTag(db.Model):
	__tablename__ = 'EntryTag'
	id = db.Column(db.Integer, primary_key=True)
	competitionID = db.Column(db.Integer, db.ForeignKey('Competition.id'))
	entry = db.Column(db.Integer, db.ForeignKey('Entries.id'))
	tag = db.Column(db.Integer, db.ForeignKey('Tags.id'))
	sysActive = db.Column(db.Integer)
	sysCreated = db.Column(db.DateTime, default=datetime.now)
	sysUpdated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
	# ==[ Vitural Columns ]==
	entryID  = db.relationship("Entry", uselist=True, back_populates="tags")

	tagID  = db.relationship("Tags", uselist=False,)# back_populates="entries")

	#tags = db.relationship("Tags", back_populates="Entries")

	def __init__(self, competitionID, entryID, tagID):
		# Required
		self.competitionID = competitionID
		self.entry = entryID
		self.tag = tagID
		self.sysActive = 1


class Entry(db.Model):
	__tablename__ = 'Entries'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	userID = db.Column(db.Integer, db.ForeignKey('User.id'))
	competitionID = db.Column(db.Integer, db.ForeignKey('Competition.id'))
	#locationID = db.Column(db.Integer, db.ForeignKey('Location.id'))
	categoryID = db.Column(db.Integer, db.ForeignKey('Categories.id'))
	title = db.Column(db.String(150))
	description = db.Column(db.String(4000))
	# statusID = db.Column(db.Integer, db.ForeignKey('User.id'))
	imgUUID = db.Column(db.String(100))
	imgFileName = db.Column(db.String(250))
	sysActive = db.Column(db.Integer)
	sysCreated = db.Column(db.DateTime, default=datetime.now)
	sysUpdated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
	S3imgOrgURL = db.Column(db.String(4000))
	S3imgSmallURL = db.Column(db.String(4000))
	S3imgThumbURL = db.Column(db.String(4000))
	# ==[ Vitural Columns ]==
	uploader = db.relationship("User", backref=db.backref("User", uselist=False))
	category = db.relationship("Categories", backref=db.backref("category", uselist=False))
	entryStatus = db.relationship("EntryStatus", backref='entry')
	location  = db.relationship("Location", uselist=False, back_populates="entry")

	tags  = db.relationship("EntryTag", uselist=True, back_populates="entryID")


	# ==[ User Object Methods ]==
	def __init__(self, userID, competitionID, cateogryID, title, description, imgUUID, imgFileName, imgOrgURL,imgSmallURL, imgThumbURL):
		# Required
		self.userID = userID
		self.competitionID = competitionID
		self.categoryID = cateogryID
		self.title = title
		self.description = description
		self.imgUUID = imgUUID
		self.imgFileName = imgFileName
		self.sysActive = 1
		self.S3imgOrgURL=imgOrgURL
		self.S3imgSmallURL=imgSmallURL
		self.S3imgThumbURL=imgThumbURL

class Location(db.Model):
	__tablename__ = 'Locations'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	entryID = db.Column(db.Integer, db.ForeignKey('Entries.id'))
	competitionID = db.Column(db.Integer, db.ForeignKey('Competition.id'))
	latitude = db.Column(db.String(45))
	longitude = db.Column(db.String(45))
	placeID = db.Column(db.String(100))
	placeName = db.Column(db.String(500))
	placeAddress = db.Column(db.String(500))
	sysActive = db.Column(db.Integer)
	sysCreated = db.Column(db.DateTime, default=datetime.now)
	sysUpdated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
	# ==[ Vitural Columns ]==
	entry = db.relationship('Entry', back_populates="location")

	# ==[ User Object Methods ]==
	def __init__(self, entryID, competitionID, latitude, longitude, placeID, placeName, placeAddress ):
		# Required
		self.entryID = entryID
		self.competitionID = competitionID
		self.latitude = latitude
		self.longitude = longitude
		self.placeID = placeID
		self.placeName = placeName
		self.placeAddress = placeAddress
		self.sysActive = 1




class EntryStatus(db.Model):
	__tablename__ = 'EntryStatus'
	#id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	entryID = db.Column(db.Integer, db.ForeignKey('Entries.id'), primary_key=True)
	statusTypeID = db.Column(db.Integer, db.ForeignKey('StatusType.id'), primary_key=True)

	sysActive = db.Column(db.Integer)
	sysCreated = db.Column(db.DateTime, default=datetime.now)
	sysUpdated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
	# ==[ Vitural Columns ]==
	status = db.relationship('StatusType', lazy='joined')

	def __init__(self, entryID, statusTypeID):
		# Required
		self.entryID = entryID
		self.statusTypeID = statusTypeID
		self.sysActive = 1

	def progressEntry(self):
		# Set Entry Status to "In Progress"
		self.statusTypeID = 2
		return

	def approveEntry(self):
		# Set Entry Status to "Approved"
		self.statusTypeID = 3
		return

	def rejectEntry(self):
		# Set Entry Status to "Rejected"
		self.statusTypeID = 4
		return


class StatusType(db.Model):
	__tablename__ = 'StatusType'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	statusTitle = db.Column(db.String(150))
	sysActive = db.Column(db.Integer)
	sysCreated = db.Column(db.DateTime, default=datetime.now)
	sysUpdated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
	# ==[ Vitural Columns ]==


# === SQL Alchemy  - Create Methods
# =======================================



def sqlA_ADD_Users(userName, firstName, lastName, email, password):
	newUser = User(userName, firstName, lastName, email, password)
	db.session.add(newUser)
	db.session.commit()
	return newUser


def sqlA_ADD_Entry(userID, competitionID, cateogryID, title, description, imgUUID, imgFileName, imgOrgURL,imgSmallURL, imgThumbURL, LocationData, tags):

	# Get Status Type
	statusType = StatusType.query.filter(and_(StatusType.id == 1, StatusType.sysActive == 1)).first()
	newEntry = Entry(userID, competitionID, cateogryID, title, description, imgUUID, imgFileName, imgOrgURL,imgSmallURL, imgThumbURL)
	db.session.add(newEntry)
	db.session.commit()
	newLocationData = Location(newEntry.id, competitionID, LocationData["place-latitude"], LocationData["place-longitude"], LocationData["place-id"], LocationData["place-name"], LocationData["place-address"])
	db.session.add(newLocationData)
	newEntryStatus = EntryStatus(newEntry.id, statusType.id)
	db.session.add(newEntryStatus)
	db.session.commit()
	
	#Add/Update Entry Tags.
	for tag in tags:
		tagText = tag["text"] 
		tagType = tag["type"]
		sqlA_ADD_Tag(newEntry.id, userID, competitionID, tagText, tagType)

	return


def sqlA_ADD_Approval(entryID, userID, approval, comment):

	# Get the Entry Object
	entry = Entry.query.filter(and_(Entry.id == entryID, Entry.sysActive == 1)).first()
	# Create Entry Approval Object for Entry Object
	newApproval = EntryApprovals(entry.id, userID, approval, comment)
	db.session.add(newApproval)
	db.session.commit()

	# Run the Approval update Status Logic for recent Approval
	entry = updateEntryStatus(entry, approval)
	db.session.add(entry)
	db.session.commit()

	return


# === SQL Alchemy  - Query Methods
# =======================================

# SQL - GET - Users
# =======================================
def sqlA_GET_Users():
	# Return Users.
	# Filter:
	#	SysActive = 1
	results = User.query.filter_by(sysActive=1).order_by(User.userName).all()
	return


def sqlA_GET_User_FILT_id_inactive(in_id):
	# Return Users.
	# Filter:
	#	ID
	#	SysActive = 1
	results = User.query.filter(and_(User.id == in_id, User.sysActive == 0)).first()
	return results

def sqlA_GET_User_FILT_id(in_id):
	# Return Users.
	# Filter:
	#	ID
	#	SysActive = 1
	results = User.query.filter(and_(User.id == in_id, User.sysActive == 1)).first()
	return results


def sqlA_GET_User_FILT_Username(in_username):
	# Return Users.
	# Filter:
	#	Username
	#	SysActive = 1
	results = User.query.filter(and_(User.userName == in_username, User.sysActive == 1)).first()
	return results


def sqlA_GET_User_FILT_Email(in_email):
	# Return Users.
	# Filter:
	#	Email Address
	#	SysActive = 1
	results = User.query.filter(and_(User.email == in_email, User.sysActive == 1)).first()
	return results


# SQL - GET - GUID 
# =======================================

def sqlA_GET_GUIDRequest(GUID, ID):
	#results = GUIDActions.query.filter(and_(GUIDActions.GUID == GUID, GUIDActions.sysActive == 1, GUIDActions.active_from <= datetime.now(), GUIDActions.active_to >= datetime.now())).first()
	results = GUIDActions.query.filter(and_(GUIDActions.GUID == GUID, GUIDActions.sysActive == 1)).first()
	return results

def sqlA_ADD_GUIDRequest(GUID, actionCode, objectID):

	newGUID = GUIDActions(GUID, actionCode, objectID)
	db.session.add(newGUID)
	db.session.commit()
	return 
	






# SQL - GET - Categories
# =======================================


def sqlA_GET_AllCategories_FILT_compID(in_competitionID):
	# Return Categories.
	# Filter:
	#	CompetitionID
	#	SysActive = 1
	categories = Categories.query.filter(and_(Categories.id == in_competitionID, Categories.sysActive == 1)).all()
	return categories

def sqlA_GET_AllCategories_FILT_compID_catID(in_competitionID,in_categoryID):
	# Return Categories.
	# Filter:
	#	CompetitionID
	#	SysActive = 1
	categories = Categories.query.filter(and_(Categories.id == in_categoryID, Competition.id == in_competitionID, Categories.sysActive == 1)).first()
	return categories


# def sqlA_GET_AvailableCategories_FILT_compID(in_competitionID):
#	categories = Categories.query.filter(and_(Competition.id == in_competitionID, Competition.sysActive == 1)).all()
#	return categories

def sqlA_GET_AvailableCategories_FILT_userID_compID(in_userID, in_competitionID):
	
	entiresResults = sqlA_GET_Entries_FILT_compID_approved_userID(in_competitionID, in_userID)
	entryList = []
	categoriesList = []

	for entry in entiresResults: 
		#print entry.sysCreated.date(), datetime.now().date()
		if (entry.sysCreated.date() < datetime.now().date()):
			entryList.append(entry.categoryID)

	categories = Categories.query.filter(and_(Competition.id == in_competitionID, Categories.sysActive == 1)).all()
	for category in categories:
		if category.id not in entryList:
			categoriesList.append(category)

	results = categoriesList
	return results

# def sqlA_GET_Entries_FILT_compID_userID_approved(in_competitionID, in_userID):
#	results = Entry.query.filter(and_(Entry.userID == in_userID, Entry.competitionID == in_competitionID, Entry.sysActive == 1)).all()
#	msg(results)
#	return results


# def sqlA_GET_Entries_FILT_compID_userID(in_competitionID, in_userID):
#	results = Entry.query.filter(and_(Entry.userID == in_userID, Entry.competitionID == in_competitionID, Entry.sysActive == 1)).all()
#	msg(results)
#	return results


# SQL - GET - Tags
# =======================================

def sqlA_GET_Competition_Tag(competitionID):

	competition = sqlA_GET_Competition_FILT_compID(competitionID)
	if competition is not None:
		return competition.tagText
		
	return None

def sqlA_GET_Category_Tag(categoryID, competitionID):
	category = sqlA_GET_AllCategories_FILT_compID_catID(competitionID,categoryID)
	if category is not None:
		return category.tagText

	return None

# SQL - ADD - Tags
# =======================================

def sqlA_ADD_Tag(entryID, userID, competitionID, tagText, tagType):

	#search for the tag. If Existing for this competition it will be returned. (Search By TagType, Tagtext)
	tagID = None
	tag = Tags.query.filter(and_(Tags.sysActive == 1, Tags.competitionID==competitionID, Tags.tagText==tagText, Tags.tagType==tagType)).first()
	
	if tag is None:
		newTag = Tags(competitionID, tagText, tagType)
		db.session.add(newTag)
		db.session.commit()
		tagID = newTag.id
	else:
		tag.tagUpdate()
		tagID = tag.id

	newEntryTag = EntryTag(competitionID, entryID, tagID)
	db.session.add(newEntryTag)
	db.session.commit()



# SQL - GET - Competition
# =======================================

def sqlA_GET_Competition_FILT_compID(in_competitionID):
	# Return Competition.
	# Filter:
	#   CompetitionID
	#   SysActive = 1
	return Competition.query.filter(and_(Competition.id == in_competitionID, Entry.sysActive == 1, )).first()


def sqlA_GET_Competition_Users_FILT_compID(in_competitionID):
	# Return Competition.
	# Filter:
	#   CompetitionID
	#   SysActive = 1
	results = User.query.filter(and_(Competition.id == in_competitionID, Entry.sysActive == 1, )).all()
	return results


def sqlA_GET_CompetitionUser_FUNC_Count_FILT_compID(in_competitionID):
	# Return Count of users in a Competition
	# Filter:
	#   CompetitionID
	#   SysActive = 1

	users = db.session.query(User).filter(User.sysActive == 1, )
	countUsers = users.statement.with_only_columns([db.func.count()]).order_by(None)
	count = db.session.execute(countUsers).scalar()
	return count


# SQL - GET - Entries
# =======================================
def sqlA_GET_Entries_RND():
	# Return Entries.
	# Filter:
	#   CompetitionID
	#   SysActive = 1
	#


	count = db.session.query(Entry).count()
	if (count >= 1):
		rand = random.randrange(0, count) 
		row = db.session.query(Entry)[rand]
	else:
		row = None

	return row


def sqlA_GET_Entries_FILT_compID(in_competitionID):
	# Return Entries.
	# Filter:
	#   CompetitionID
	#   SysActive = 1
	#
	return Entry.query.filter(and_(Entry.competitionID == in_competitionID, Entry.sysActive == 1, )).all()

def sqlA_GET_Entries_FILT_compID_entryID(in_competitionID, in_entryID):
	# Return Entries.
	# Filter:
	#   CompetitionID
	#   SysActive = 1
	#
	return Entry.query.filter(and_(Entry.competitionID == in_competitionID, Entry.id == in_entryID, Entry.sysActive == 1, )).first()


def sqlA_GET_Entries_FILT_compID_userID(in_competitionID, in_userID):
	# Return Entries.
	# Filter:
	#   CompetitionID
	#   SysActive = 1
	#   EntryStatus = "Approved" (NOT 1 = Pending, 2 = In Progress or 4 = Rejected)
	selection = Entry.query.filter(
		and_(
			Entry.competitionID == in_competitionID,
			Entry.sysActive == 1,
			Entry.userID == in_userID,
		)).order_by(
		Entry.sysCreated).all()
	results = []
	for entry in selection:
		if (entry.entryStatus[0].status.id != 4):
			results.append(entry)
	return results


def sqlA_GET_Entries_FILT_compID_approved_userID(in_competitionID, in_userID):
	# Return Entries.
	# Filter:
	#   CompetitionID
	#   SysActive = 1
	#   EntryStatus = "Approved" (NOT 1 = Pending, 2 = In Progress or 4 = Rejected)
	selection = Entry.query.filter(
		and_(
			Entry.competitionID == in_competitionID,
			Entry.sysActive == 1,
			Entry.userID == in_userID,
		)).order_by(
		Entry.sysCreated).all()
	results = []
	for entry in selection:
		if (entry.entryStatus[0].status.id == 3):
			results.append(entry)
	return results

def sqlA_GET_Entries_FILT_compID_approved_categoryID(in_competitionID, in_categoryID):
	# Return Entries.
	# Filter:
	#   CompetitionID
	#   SysActive = 1
	#   EntryStatus = "Approved" (NOT 1 = Pending, 2 = In Progress or 4 = Rejected)
	selection = Entry.query.filter(
		and_(
			Entry.competitionID == in_competitionID,
			Entry.sysActive == 1,
			Entry.categoryID == in_categoryID
		)).order_by(
		Entry.sysCreated).all()
	results = []
	for entry in selection:
		if (entry.entryStatus[0].status.id == 3):
			results.append(entry)
	return results


def sqlA_GET_Entries_FILT_compID_approved(in_competitionID):
	# Return Entries.
	# Filter:
	#	CompetitionID
	#	SysActive = 1
	#   EntryStatus = "Approved" (NOT 1 = Pending, 2 = In Progress or 4 = Rejected)
	selection = Entry.query.filter(
		and_(
			Entry.competitionID == in_competitionID,
			Entry.sysActive == 1,
		)).order_by(
		Entry.sysCreated).all()
	results = []
	for entry in selection:
		if (entry.entryStatus[0].status.id == 3):
			results.append(entry)
	return results


def sqlA_GET_Entries_FILT_compID_rejected(in_competitionID):
	# Return Entries.
	# Filter:
	#   CompetitionID
	#   SysActive = 1
	#   EntryStatus = "Rejected" (NOT 1 = Pending, 2 = In Progress or 3 = Approved)
	selection = Entry.query.filter(and_(Entry.competitionID == in_competitionID, Entry.sysActive == 1, )).all()
	results = []
	for entry in selection:
		if (entry.entryStatus[0].status.id == 4):
			results.append(entry)
	return results


def sqlA_GET_Entries_FILT_compID_pending(in_competitionID):
	# Return Entries.
	# Filter:
	#   CompetitionID
	#   SysActive = 1
	#   EntryStatus = "Pending & In Progress" (NOT 3 = Approved or 4 = Rejected)
	selection = Entry.query.filter(and_(Entry.competitionID == in_competitionID, Entry.sysActive == 1, )).all()
	results = []
	for entry in selection:
		if (entry.entryStatus[0].status.id in [1, 2]):
			results.append(entry)

	return results


def sqlA_GET_Entries_FILT_compID_pending_notSelf(in_competitionID, in_userID):
	# Return Entries.
	# Filter:
	#   CompetitionID
	#   SysActive = 1
	#   EntryStatus = "Pending & In Progress" (NOT 3 = Approved or 4 = Rejected)
	#   UserID != My Own user ID. (Cannot get own pending posts)
	selection = Entry.query.filter(
		and_(
			Entry.competitionID == in_competitionID,
			Entry.sysActive == 1,
			Entry.userID != in_userID)).all()
	results = []
	for entry in selection:
		if (entry.entryStatus[0].status.id in [1, 2]):
			results.append(entry)
	return results


def sqlA_GET_Entries_FILT_compID_pending_notSelf_ORD_longestWait(in_competitionID, in_userID):
	# Return Entries.
	# Filter:
	#   CompetitionID
	#   SysActive = 1
	#   EntryStatus = "Pending & In Progress" (NOT 3 = Approved or 4 = Rejected)
	#   UserID != My Own user ID. (Cannot get own pending posts)
	selection = Entry.query.filter(
		and_(
			Entry.competitionID == in_competitionID,
			Entry.sysActive == 1,
			Entry.userID != in_userID)).all()
	results = []
	for entry in selection:
		if (entry.entryStatus[0].status.id in [1, 2]):
			if entry.S3imgSmallURL is not None:
				alreadyApproved = sqlA_GET_EntryApprovals_FUNC_Count_FILT_EntryID_UserID(entry.id, in_userID)
				if (alreadyApproved < 1):
					results.append(entry)

	return results


def sqlA_GET_Entry_FUNC_Count_FILT_Approvals(in_EntryID):
	# Return Count of Approvals for an Entry
	# Filter:
	#   EntryID
	#   SysActive = 1
	#   Aproval = +1
	entryApprovals = db.session.query(EntryApprovals).filter(
		and_(
			EntryApprovals.sysActive == 1,
			EntryApprovals.approval == 1,
			EntryApprovals.entry == in_EntryID))
	countApprovals = entryApprovals.statement.with_only_columns([db.func.count()]).order_by(None)
	return db.session.execute(countApprovals).scalar()


def sqlA_GET_Entry_FUNC_Count_FILT_Rejections(in_EntryID):
	# Return Count of Approvals for an Entry
	# Filter:
	#   EntryID
	#   SysActive = 1
	#   Aproval = -1

	entryRejections = db.session.query(EntryApprovals).filter(
		and_(
			EntryApprovals.sysActive == 1,
			EntryApprovals.approval == -1,
			EntryApprovals.entry == in_EntryID))
	countRejections = entryRejections.statement.with_only_columns([db.func.count()]).order_by(None)
	return db.session.execute(countRejections).scalar()



def sqlA_GET_Rejections_FILT_entryID(in_EntryID):
	# Return Count of Approvals for an Entry
	# Filter:
	#   EntryID
	#   SysActive = 1
	#   Aproval = -1

	entryRejections = db.session.query(EntryApprovals).filter(
		and_(
			EntryApprovals.sysActive == 1,
			EntryApprovals.approval == -1,
			EntryApprovals.entry == in_EntryID))
	return entryRejections


def sqlA_GET_EntryApprovals_FUNC_Count_FILT_EntryID_UserID(in_EntryID, in_ApproverID):

	entryApprovals = db.session.query(EntryApprovals).filter(
		and_(
			EntryApprovals.sysActive == 1,
			EntryApprovals.ApproverID == in_ApproverID,
			EntryApprovals.entry == in_EntryID))
	stmt = entryApprovals.statement.with_only_columns([db.func.count()]).order_by(None)
	entryApprovals = db.session.execute(stmt).scalar()
	return entryApprovals

	




def sqlA_GET_User_Statistics_FILT_User_CompID(in_userID, in_competitionID):

	#Get the Number of approved Entries for a User in a Competition
	entries = db.session.query(Entry).filter(
		and_(
			Entry.userID == in_userID,
			Entry.competitionID == in_competitionID,
			Entry.sysActive == 1
			)
		)


	pendingEntries = 0
	approvedEntries = 0
	rejectedEntries = 0
	currentScore = 0
	currentRank = 0

	returnData = listScorecard()
	
	for user in returnData["users"]:
		if (int(user["userID"]) == int(in_userID)):
			currentRank = user["rank"]
			currentScore = user["totalScore"]

	for entry in entries:
		if (entry.entryStatus[0].statusTypeID in [1,2]):
			pendingEntries = pendingEntries + 1
		elif (entry.entryStatus[0].statusTypeID == 3):
			approvedEntries = approvedEntries + 1
		elif (entry.entryStatus[0].statusTypeID == 4):
			rejectedEntries = rejectedEntries + 1
		else:
			None

	totalEntries = (approvedEntries + pendingEntries)

	stats = {"approvedEntries":approvedEntries
			,"pendingEntries":pendingEntries
			,"rejectedEntries":rejectedEntries
			,"totalEntries":totalEntries
			,"currentScore":currentScore
			,"currentRank":currentRank}

	return stats

# ============================================================================
# ============================================================================
# MAIL FUNCTIONS
# ============================================================================
def mail_checkUserPreferences(preference):
	return True

def mail_send_UserRegistration(in_User, GUID):

	if mail_checkUserPreferences("registration"):

		actGUID = GUID
		userName = in_User.userName
		firstName = in_User.firstName

		mailSubject = "Welcome to The Hunt"
		mailSender = "webmaster@photoscavhunt.com"

		mailRecipent = [entry.uploader.email, "iguvfk3vrs@pomail.net"]
		msgHTML = render_template('/mail/mail_UserRegistration.html', in_confirmEmailLink=(application.config["HTTP_CORE"]+"/register/activation/"+actGUID+"/"), in_username=userName, in_firstName=firstName)
		mail_send(mailSubject, mailSender, mailRecipent, msgHTML)
		return

	return


def mail_send_entryApproved(in_entryID):

	if mail_checkUserPreferences("entryApproved"):
		entry = sqlA_GET_Entries_FILT_compID_entryID(session["competitionID"], in_entryID)

		userName = entry.uploader.userName
		firstName = entry.uploader.firstName

		mailSubject = str("Hey " + firstName + ", Your entry has been Approved.")
		mailSender = "webmaster@photoscavhunt.com"

		mailRecipent = [entry.uploader.email, "iguvfk3vrs@pomail.net"]
		msgHTML = render_template('/mail/mail_entryApproved.html', entry=entry, in_username=userName, in_firstName=firstName)
		mail_send(mailSubject, mailSender, mailRecipent, msgHTML)

	return

def mail_send_entryRejected(in_entryID):

	if mail_checkUserPreferences("entryRejected"):

		entry = sqlA_GET_Entries_FILT_compID_entryID(session["competitionID"], in_entryID)
		rejections = sqlA_GET_Rejections_FILT_entryID(in_entryID)
		
		userName = entry.uploader.userName
		firstName = entry.uploader.firstName

		mailSubject = str("Hey " + firstName + ", Your entry has been Rejected.")
		mailSender = "webmaster@photoscavhunt.com"

		mailRecipent = [entry.uploader.email, "iguvfk3vrs@pomail.net"]
		msgHTML = render_template('/mail/mail_entryRejected.html', entry=entry, rejections=rejections, in_username=userName, in_firstName=firstName)
		mail_send(mailSubject, mailSender, mailRecipent, msgHTML)
		return

	return


def mail_send(in_subject, in_sender, in_recipients, in_msgHTML):
	messageObject = Message(subject=in_subject,sender=in_sender,recipients=in_recipients)
	messageObject.html = in_msgHTML
	print(messageObject)
	mail.send(messageObject)

	return


def pushover_send(in_msg):
	if(application.config["PUSHOVER_ENABLED"] == 'True'):
		client = Client(application.config["PUSHOVER_USERKEY"], api_token=application.config["PUSHOVER_API"])
		client.send_message(str(in_msg), title=("PSH Message - "+str(application.config["RunEnv"])))


# ============================================================================
# ============================================================================
# ADMIN FUNCTIONS
# ============================================================================

@application.route('/admin/dashboard/', methods=['POST'])
def admin_manage_dashboard():
	return

@application.route('/admin/cateogries/edit', methods=['POST'])
def admin_manage_categories():
	return

@application.route('/admin/users/edit', methods=['POST'])
def admin_manage_users():
	return


@application.route('/admin/entries/edit', methods=['POST'])
def admin_manage_entries():
	return

@application.route('/admin/competition/edit', methods=['POST'])
def admin_manage_competitions():
	return


@application.route('/mail/test/<string:type>/')
def admin_mail_test(type):


	if type == "reject":
		in_entryID = 1
		entry = sqlA_GET_Entries_FILT_compID_entryID(session["competitionID"], in_entryID)
		rejections = sqlA_GET_Rejections_FILT_entryID(in_entryID)

		userName = entry.uploader.userName
		firstName = entry.uploader.firstName

		return  render_template('/mail/mail_entryRejected.html', entry=entry, rejections=rejections, in_username=userName, in_firstName=firstName)
	elif type == "approve":
		in_entryID = 1
		entry = sqlA_GET_Entries_FILT_compID_entryID(session["competitionID"], in_entryID)

		userName = entry.uploader.userName
		firstName = entry.uploader.firstName


		return  render_template('/mail/mail_entryApproved.html', entry=entry, in_username=userName, in_firstName=firstName)



# ============================================================================
# ============================================================================


if __name__ == '__main__':

	#msg("Connecting to MYSQL HOST: " + str(application.config["MYSQL_HOST"]))
	#msg("Connecting to DB URI : "+ str(application.config["SQLALCHEMY_DATABASE_URI"]))


	#application.secret_key = 'MP$H_2019_prd'
	#application.config['DEBUG'] = True
	#application.config['HOST'] = '0.0.0.0'
	#application.run(port=5002)
	#manager.run()
	application.run()
