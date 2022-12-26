from flask import Flask, render_template, request, url_for, redirect, session, g
import googleCloud as gc
import quickstart as calendar
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = '0854f7f761d6b80e4e366b38848d3bf35c6d723490739765'
app.secret_key = '0854f7f761d6b80e4e366b38848d3bf35c6d723490739765'

applicationStatusList = ['None', 'Applied', 'Accepted', 'Rejected']
grantStatusList = ['None', 'Grant Open', 'Grant Closed']

class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __repr__(self):
        return f'<User: {self.username}>'


user_data = gc.getUsers()
usernames = user_data['usernames']
passwords = user_data['passwords']
count = 0
users = []

for username in usernames:
    users.append(User(id=count, username=username, password=passwords[usernames.index(username)]))
    count+=1

@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        user = [x for x in users if x.id == session['user_id']][0]
        g.user = user


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user_id', None)
        username = request.form['username']
        password = request.form['password']
        verifiedUsers = [x for x in users if x.username == username]

        if(len(verifiedUsers) != 0):
            verifiedUser = verifiedUsers[0]
            if verifiedUser and verifiedUser.password == password:
                session['user_id'] = verifiedUser.id
                return redirect(url_for('index'))

        return redirect(url_for('login'))
  
    return render_template('login.html')


@app.route('/home/', methods=['GET'])
def index():
    if not g.user:
        return redirect(url_for('login'))
    grants = gc.readData()
    return render_template('index.html', grants = grants, grantTotal = len(grants)) 


@app.route('/create/', methods=['POST'])
def add():
    newGrant = request.form.to_dict()
    newGrant['CreatedBy'] = g.user.username
    newGrant['DateCreated'] = time.time()
    calendar.createEvent(newGrant['Name'], newGrant['GrantDescription'], newGrant['ApplyDeadline'])
    gc.addData(newGrant)
    return redirect("/home", code=302)       


@app.route('/edit/', methods=['POST', 'GET'])
def edit():
    action = request.form['action']
    if action == 'remove' or action == 'edit':
        grantid = request.form['grantid']
        doc = gc.db.collection(gc.grantCollection).document(grantid).get().to_dict()
        return render_template('edit.html', doc=doc, action=action, grantid=grantid, applicationStatusList=applicationStatusList, grantStatusList=grantStatusList)
    elif action == 'create':
        return render_template('edit.html', action=action, applicationStatusList=applicationStatusList, grantStatusList=grantStatusList)


@app.route('/delete/', methods=['POST'])
def remove():
    removeid = request.form['grantid']
    calendar.deleteEvent(request.form['Name'])
    gc.deleteData(removeid)
    return redirect("/home/", code=302)


@app.route('/view/', methods=['POST'])
def view():
    grantid = request.form['grantid']
    doc = gc.db.collection(gc.grantCollection).document(grantid).get().to_dict()
    return render_template('edit.html', action='view', doc=doc)


@app.route('/save/', methods=['POST'])
def save():
    grantid = request.form['grantid']
    newValues = request.form.to_dict()
    if newValues['ApplyDeadline'] == '':
        calendar.deleteEvent(newValues['Name']) 
    else:
        calendar.updateEvent(newValues['Name'], newValues['ApplyDeadline'], newValues['GrantDescription'])
    newValues['DateUpdated'] = time.time()
    newValues['UpdatedBy'] = g.user.username
    del newValues['grantid']
    grantEdit_ref = gc.db.collection(gc.grantCollection).document(grantid)
    grantEdit_ref.update(newValues)
    return redirect("/home/", code=302) 

@app.route('/test/')
def test():
    return render_template('test.html')


@app.route('/api/grants/') 
def grantsAPI():
    return gc.readData()

if __name__ == "__main__":
    app.run(debug=True)

