from flask import Flask, render_template, flash,request, redirect
import os, shelve, uuid
from urllib.parse import urlparse
from pathlib import Path
from datetime import datetime
app = Flask(__name__)

def start():
  folder = os.path.join(Path.home(), 'anom')
  file = os.path.join(folder,'anomdb')
  os.chdir(Path.home())
  if os.path.exists(folder):
    if os.path.exists(file):
      var = 1
    else:
      os.chdir(folder)
      groupObject = shelve.open('anomdb')
      group = []
      comment = []
      groupObject['comments'] = comment
      groupObject['groups'] = group
      
      groupObject.close()
  else:
    os.mkdir('anom')
    os.chdir(folder)
    groupObject = shelve.open('anomdb')
    group = []
    comment = []
    groupObject['comments'] = comment
    groupObject['groups'] = group
    groupObject.close()
    
@app.route('/')
def index():
  start()
  
  return render_template('index.html')
  
@app.route('/create',methods = ['GET','POST'])
def create():
  folder = os.path.join(Path.home(), 'anom')
  os.chdir(folder)
  error = None
  if request.method == 'POST':
    group_id = uuid.uuid4()
    group = request.form['group']
    
    groupObject = shelve.open('anomdb','c', writeback = True)
    
    groups = groupObject.get('groups')
    
    err = 0
    
    if groups:
      for unit in groups:
        if unit['group']:
          if unit['group'] == group:
            err = 1
            break
        
    if err:
      error = 'Group already exists'
    else:
      obj = {
        'group_id': group_id,
        'group': group
      }
      
      groupObject.get('groups').append(obj)
        
      groupObject.sync()
        
      groupObject.close()
      return redirect('/link?group_id='+ str(group_id))
  return render_template('create.html', error=error)
  
@app.route('/link',methods = ['GET','POST'])
def link():
  group_id = request.args.get('group_id')
  urls = urlparse(request.url)
  url = urls.scheme+'://'+urls.netloc +'/link?group_id='+ group_id
  groupObject = shelve.open('anomdb','r', writeback = True)
  groups = groupObject.get('groups')
  groupLink = []
  for group in groups:
    if str(group['group_id']) == group_id:
      groupLink.append(group)
  print(group)
  return render_template('link.html',link=url,group_id=group_id,group=group)
  
@app.route('/comments')
def comment():
  folder = os.path.join(Path.home(), 'anom')
  os.chdir(folder)
  group_id = request.args.get('group_id')
  groupObject = shelve.open('anomdb','r', writeback = True)
  comments = groupObject['comments']
  groups = groupObject['groups']
  name = ""
  newComments = []
  for comment in comments:
    if comment['group_id'] == group_id:
      newComments.append(comment)
  for group in groups:
    if str(group['group_id']) == group_id:
      name = group['group']
      
  return render_template('view.html',comments=newComments,group=name,group_id=group_id)
  
  
@app.route('/add')
def add():
  group_id = request.args.get('group_id')
  return render_template('add.html',group_id=group_id)
  
  
@app.route('/add/<group_id>',methods = ['GET','POST'])
def new(group_id):
  folder = os.path.join(Path.home(), 'anom')
  os.chdir(folder)
  if request.method == 'POST': 
    group_id = request.form['group_id']
    content = request.form['content']
    content_id = uuid.uuid4()
    date_created = datetime.now()
    
    obj = {
      'group_id': group_id,
      'content': content,
      'content_id': content_id,
      'date_created': date_created.strftime('%H:%M%p %A %b %Y')
    }
    groupObject = shelve.open('anomdb','c', writeback = True)
    
    groupObject.get('comments').append(obj)
        
    groupObject.sync()
        
    groupObject.close()
    return redirect('/comments?group_id='+ str(group_id))
  return render_template('index.html')
  
@app.route('/join',methods = ['GET','POST'])
def join():
  folder = os.path.join(Path.home(), 'anom')
  os.chdir(folder)
  error = None
  group_id = 0
  if request.method == 'POST':
    group = request.form['group']
    groupObject = shelve.open('anomdb','r', writeback = True)
    groups = groupObject.get('groups')
    print(groups)
    if groups != None:
      if len(groups) != 0:
        for unit in groups:
          if unit['group'] == group:
            group_id = unit['group_id']
      else:
        print('22')
        error = 'Group does not exist'
        return render_template('join.html', error=error)
    else:
      print('22')
      error = 'Group does not exist'
      return render_template('join.html', error=error)
        
    
    if group_id == 0:
      error = 'Group does not exist'
      
      return render_template('join.html', error=error)
    return redirect('/link?group_id='+ str(group_id))
  return render_template('join.html', error=error)
  
if __name__ == '__main__':
  app.run(debug=True)