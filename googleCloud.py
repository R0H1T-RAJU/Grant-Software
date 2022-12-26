import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


# Use a service account
cred = credentials.Certificate("meta-tracker-355700-115e985e285d.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
grantCollection = u'grants'
userCollection = u'users'

batch = db.batch()

def addData(newGrant):
  db.collection(grantCollection).document().set(newGrant)

def deleteData(id):
  db.collection(grantCollection).document(id).delete()

def readData():
  grants_ref = db.collection(grantCollection)
  docs = grants_ref.stream()
  return {x.id : x.to_dict() for x in docs}

def getUsers():
  userNameList = []
  userPasswordList = []
  users_ref = db.collection(userCollection)
  users = users_ref.stream()
  users_dict = {x.id : x.to_dict() for x in users}
  for user in users_dict.values():
    userNameList.append(user['username'])
    userPasswordList.append(user['password'])
  return {'usernames' : userNameList, 'passwords' : userPasswordList}

def createUser(username, password):
  newUser = {'password' : password, 'username' : username}
  db.collection(userCollection).document().set(newUser)
