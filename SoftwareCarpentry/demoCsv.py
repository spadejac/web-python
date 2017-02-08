'''
Created on Nov 10, 2013

@author: Manoj Pillay
@email: mpillay [at] lbl [dot] gov
'''


from bottle import route, run, response, redirect, template, request, post, static_file
from os import listdir
import csv


host = 'localhost'
port = 8080
uploadLocation = '/home/pillay/Downloads/userUploads/'
baseUrl = 'http://%s:%s' % (host, port)


@route('/')
def home():
    linksList = []
    
    # Use of HTML is purposeful, to demonstrate that templates are not 
    # necessary for bottle
    linksList.append('<b><u>Public Pages</b></u>')
    linksList.append('<a href=%s/showUploads>Show uploaded files</a>' % baseUrl)
    linksList.append('<a href=%s/showCsvUploads>Show uploaded CSV files</a>' % baseUrl)
    linksList.append('<br>')
    
    linksList.append('<b><u>Private Pages</b></u>')
    linksList.append('<a href=%s/login>Login</a>' % baseUrl)
    linksList.append('<a href=%s/uploadFile>Upload File</a>' % baseUrl)
    linksList.append('<a href=%s/logout>Logout</a>' % baseUrl)
    linksList.append('<br>')
    
    linksList.append('<b><u>Embedded Pages</b></u>')
    linksList.append('<a href=%s/youtube>Click me</a>' % baseUrl)
    
    
    links = '<br>'.join(linksList)
    
    homepage = '''
           <h1>Python web development using the Bottle Framework</h1>
           <h2>Software Carpentry bootcamp at LBNL - 18 Nov, 2013</h2>
           <a href='http://www.software-carpentry.org'>Software Carpentry</a>
           <br><br><br>
           
           <u><b>Example Pages:</u></b>
           <br><br>
           %s
           <br><br>
           <a>Find source code for this web application on</a>
           <a href='https://github.com/spadejac/web-python/tree/master/SoftwareCarpentry'>GitHub</a>
           <br><br>
           <b><i> Examples created by <a href='http://www.linkedin.com/in/manojpillay'></i>Manoj Pillay</b>
           
           ''' % (links)

    return homepage


@route('/uploadFile')
def upload():
    username = request.get_cookie("account", secret='some-secret-key')
    if username:
        return '''
               <form action="/upload" method="post" enctype="multipart/form-data">
                  Select a file: <input type="file" name="upload" />
                  <input type="submit" value="Start upload" />
               </form>
                ''' 
    
    else:
        return "You are not logged in. Access denied."


@route('/upload', method='POST')
def do_upload():
    allowedFileTypes = ['png', 'jpg', 'jpeg', 'mp3', 'txt', 'csv']
    upload = request.files.get('upload')
    ext = upload.filename.split('.')[-1]
    if ext not in allowedFileTypes:
        return 'File extension not allowed.'

    upload.save(uploadLocation) 
    return 'OK'

@route('/login')
def login():
    return '''
        <form action="/login" method="post">
            Username: <input name="username" type="text" />
            Password: <input name="password" type="password" />
            <input value="Login" type="submit" />
        </form>
    '''
    
@route('/logout')
def logout():
    response.delete_cookie('account')
    return '''
           You have successfully logged out of the restrcited area!
           '''

def check_login(username, password):
    passwords = {
                 'manoj' : 'jonam',
                 'greg'  : 'wilson',
                 'guest' : 'guest'
                }
    try:
        if passwords[username] == password:
            return True
    except:
        return False
    
    return False
        
        
@post('/login')  # or @route('/login', method='POST')
def do_login():
    username = request.forms.get('username')
    password = request.forms.get('password')
    if check_login(username, password):
        response.set_cookie("account", username, secret='some-secret-key')
        return "<p>Your login information was correct.</p>"
    else:
        return "<p>Login failed.</p>"

@route('/static/<filename>')
def server_static(filename):
    return static_file(filename, root=uploadLocation)


@route('/showUploads')
def showUploads():
    files = listdir(uploadLocation)
    uploadsListPage = []
    for f in files:
        fileUrl = '%s/static/%s' % (baseUrl, f)
        uploadsListPage.append('<a href=%s>%s</a>' % (fileUrl, f))
    
    return '<br>'.join(uploadsListPage)



def displayCsvHtmlTemplate(rows):
    return template('html', {'rows':rows})

@route('/csvAsHtml/<filename>')
def showCsvAsHtml(filename):
    start = 1
    end = getNumRecords(filename)
    redirect('/csvAsHtml/%s/filter/%d/%d' %(filename, start, end))
#     Alternatively, one could directly call the function as follows:
#     return showFilteredRows(filename, start, end)
                                    

def getFieldNames(filename):
    with open(filename) as f:
        for row in csv.reader([f.readline()]):
            return row
    
@route('/csvAsHtml/<filename>/csvMetadata/fieldNames')
def returnFieldNames(filename):
    filename = uploadLocation + '/' + filename
    fieldNamesList = getFieldNames(filename)
    return '<br>'.join(fieldNamesList)

    
def getNumRecords(filename):
    filename = uploadLocation + '/' + filename
    with open(filename) as f:
        for i, l in enumerate(f):
            pass
    return i

@route('/csvAsHtml/<filename>/csvMetadata/numRecords')
def returnNumRecords(filename):
    return str(getNumRecords(filename))
        
@route('/csvAsHtml/<filename>/filter/<start:int>/<end:int>')
def showFilteredRows(filename, start, end):
    try:
        assert start <= end
        assert isinstance(start,int)
        assert isinstance(end,int)
        
        filename = uploadLocation + '/' + filename    
        queryParameters = dict(request.query)
        keysToDisplay = queryParameters.keys()       
        if not keysToDisplay:
            keysToDisplay = getFieldNames(filename)
         
        rows = [keysToDisplay]
        lineNum = 0
        
        
        with open(filename) as csvFile:
            csvDict = csv.DictReader(csvFile)
            for record in csvDict:
        
                lineNum += 1
                if start <= lineNum <= end:
                    row = []
                    row = [record.get(key,'') for key in keysToDisplay]
                    if row:
                        rows.append(row)
        
        return displayCsvHtmlTemplate(rows)

    except Exception, e:
        return '''
               URL was constructed incorrectly: %s
               ''' %str(e)
        
@post('/filterCsv/<filename>') 
def call_showFilteredRows(filename):
    start = int(request.forms.get('start'))
    end = int(request.forms.get('end'))
    if start <= end:
        return showFilteredRows(filename, start, end)
    else:
        return 'start cannot be greater than end'


@route('/showCsvUploads')
def showCsvUploads():

    files = listdir(uploadLocation)
    uploadsListPage = []
    for f in files:
        if '.csv' in f:
            fileUrl = '%s/csvAsHtml/%s' % (baseUrl, f)
            contentsLink = '<h3><a href=%s>%s</a></h3>' % (fileUrl, f)
            fieldNamesLink = '<a href=%s/csvMetadata/fieldNames>Field Names</a>' % (fileUrl)
            numRecordsLink = '<a href=%s/csvMetadata/numRecords>Number of records</a>' % (fileUrl)
            filterForm = '''
                         <form action="/filterCsv/%s" method="post" >
                              start: <input name="start" type="text" />
                              end: <input name="end" type="text" />
                              <input value="Filter" type="submit" />
                         </form>
                         ''' %f
            
            links = (5*'&nbsp').join([contentsLink, fieldNamesLink, 
                                       numRecordsLink, filterForm])
            uploadsListPage.append(links)
    return '<br>'.join(uploadsListPage)




@route('/youtube')
def showVideo():
    return '''
           <iframe width="560" height="315" src="//www.youtube.com/embed/neKVyMCwTy0?autoplay=1" frameborder="0" allowfullscreen></iframe>
           '''
           
if __name__ == '__main__':
    run(host=host, port=port, debug=True)
    
    
