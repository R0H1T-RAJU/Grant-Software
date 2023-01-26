import smtplib
import datetime
import time
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate("meta-tracker-355700-115e985e285d.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
grantCollection = u'grants'
userCollection = u'users'

batch = db.batch()

senderEmail = "toysfortexans@gmail.com"
senderPassword = "bcgrzogzqnakxpow"
recieverEmails = ['']

# def getUsernames():
#   usernames = []
#   users_ref = db.collection(userCollection).order_by('username')
#   users = users_ref.stream()
#   users_dict = {x.id : x.to_dict() for x in users}
#   for user in users_dict.values():
#     usernames.append(user['username'])
#   return usernames

def getLastMonday(week):
  today = datetime.date.today()     
  lastMonday = today + datetime.timedelta(days=-today.weekday(), weeks=week)
  mondayTimestamp = time.mktime(lastMonday.timetuple()) 
  return datetime.datetime.timestamp(datetime.datetime.fromtimestamp(mondayTimestamp))

def getGrantCreatedByData():
  grants_ref = db.collection(grantCollection)
  lastMonday = getLastMonday(-1)
  lastSunday = getLastMonday(0) - 1
  query_ref = grants_ref.where(u'DateCreated', u'>=', lastMonday).where(u'DateCreated', u'<=', lastSunday).select(['CreatedBy'])
  query = query_ref.stream()
  return {'data' : {x.id : x.to_dict() for x in query}, 
    'startDate' : datetime.datetime.fromtimestamp(lastMonday),  
    'endDate' : datetime.datetime.fromtimestamp(lastSunday)  
  } 

def totalGrants(users):
  createdByCount = {}
  grantData =  getGrantCreatedByData()
  createdBy = grantData['data']
  for x in createdBy:
    name = createdBy[x].get('CreatedBy', 'unknown')
    createdByCount[name] = createdByCount.get(name, 0) + 1
  for user in users:
    createdByCount[user] = createdByCount.get(user, 0)
  grantData['summary'] = createdByCount
  return grantData

def sendEmail(request):
  server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
  server.login(senderEmail, senderPassword) 

  grantInfo = totalGrants('test')

  subject = "Grant Report For " + grantInfo['startDate'].strftime('%m/%d/%Y') + " - " + grantInfo['endDate'].strftime('%m/%d/%Y')
  body = ''

  for x, y  in grantInfo['summary'].items():
    body += '%s created %s grants this week\n\n'%(x, y)

  msg = f'Subject: {subject}\n\n{body}'
  
  for email in recieverEmails:
    server.sendmail(senderEmail, email, msg)
    print('sent email') 

  return 'program ran'


