'''
Created on Nov 10, 2013

@author: Manoj Pillay
@email: mpillay [at] lbl [dot] gov
'''


from bottle import route, run, template, request, post, static_file
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
    linksList.append('<a href=%s/login>Login Test</a>' % baseUrl)
    linksList.append('<a href=%s/uploadFile>Upload File</a>' % baseUrl)
    linksList.append('<a href=%s/showUploads>Show uploaded files</a>' % baseUrl)
    linksList.append('<a href=%s/showCsvUploads>Show uploaded CSV files</a>' % baseUrl)
    linksList.append('<a href=%s/youtube>Click me</a>' % baseUrl)
    
    links = '<br>'.join(linksList)
    
    homepage = '''
           <h1>Python web development using the Bottle Framework</h1>
           <h2>Software Carpentry bootcamp at LBNL - 18 Nov, 2013</h2>
           <br><br><br>
           
           <u><b>Example Pages:</u></b>
           <br><br>
           %s
           
           <h3> Examples created by Manoj Pillay</h3>
           
           
           ''' % (links)

    return homepage


@route('/uploadFile')
def upload():
    return '''
           <form action="/upload" method="post" enctype="multipart/form-data">
               Select a file: <input type="file" name="upload" />
               <input type="submit" value="Start upload" />
           </form>
           '''


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

@route('/csvAsHtml/<filename>')
def showCsvAsHtml(filename):
    queryParameters = dict(request.query)
    
    filename = uploadLocation + '/' + filename 
    rows = []
    keysToDisplay = queryParameters.keys()
    
    with open(filename) as csvFile:
        if keysToDisplay:
            csvDict = csv.DictReader(csvFile)
            rows.append(keysToDisplay)
            for record in csvDict:
                row = []
                for key in record:
                        if key in keysToDisplay:
                            row.append(record[key])
                rows.append(row)
        else:
            rows = list(tuple(rec) for rec in csv.reader(csvFile))
    return template('html', {'rows':rows})
        
    
@route('/showCsvUploads')
def showCsvUploads():
    files = listdir(uploadLocation)
    uploadsListPage = []
    for f in files:
        if '.csv' in f:
            fileUrl = '%s/csvAsHtml/%s' % (baseUrl, f)
            uploadsListPage.append('<a href=%s>%s</a>' % (fileUrl, f))
    return '<br>'.join(uploadsListPage)
                                    

@route('/youtube')
def showVideo():
    return '''
           <iframe width="560" height="315" src="//www.youtube.com/embed/neKVyMCwTy0?autoplay=1" frameborder="0" allowfullscreen></iframe>
           '''
           
if __name__ == '__main__':
    run(host=host, port=port, debug=True)
    
    
