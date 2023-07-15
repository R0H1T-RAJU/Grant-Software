from datetime import date
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate("firebase.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
grantCollection = u'grants'

batch = db.batch()

# def my_filtering_function(pair):
#     unwanted_key = 'Matt'
#     key, value = pair
#     if float(value['DateUpdated']) >= 1672531200:
#         return True  
#     else:
#         return False 
# def getGrants():
#   grants_ref = db.collection(grantCollection)
#   filteredGrants = grants_ref.where(u"ApplicationStatus", u'==', u'Applied')
#   filteredDict = {x.id : x.to_dict() for x in filteredGrants.stream()}
#   shrunkedDict = dict(filter(my_filtering_function, filteredDict.items()))
#   print(shrunkedDict)
#   print(len(shrunkedDict))

def changeStatus(request):
  grants_ref = db.collection(grantCollection)
# Changes status of grants to open
  changeToOpen_ref = grants_ref.where(u'ApplyStartDate', u'>=', str(date.today()))
  changeToOpen_dict = {x.id : x.to_dict() for x in changeToOpen_ref.stream()}
  filteredChangeToOpen_dict = {}
  if changeToOpen_dict:
    for key, value in changeToOpen_dict.items():
      if not value['ApplyDeadline']  <= str(date.today()) and value['GrantStatus'] != 'Grant Open':
        filteredChangeToOpen_dict[key] = value
    for grantId in filteredChangeToOpen_dict:
      batch.update(grants_ref.document(grantId), {u'GrantStatus' : 'Grant Open'})

# Changes status of grants to closed
  changeToClose_ref = grants_ref.where(u'ApplyDeadline', u'!=', '').where(u'ApplyDeadline', u'<=', str(date.today()))
  changeToClose_dict = {x.id : x.to_dict() for x in changeToClose_ref.stream()}
  filteredChangeToClose_dict = {}
  if changeToClose_dict:
    for key, value in changeToClose_dict.items():
      if not value['GrantStatus'] == 'Grant Closed':
        filteredChangeToClose_dict[key] = value
    for grantId in filteredChangeToClose_dict:
      batch.update(grants_ref.document(grantId), {u'GrantStatus' : 'Grant Closed'})

# sends the updated status data to the database
  if(changeToClose_dict or filteredChangeToOpen_dict): 
    batch.commit()