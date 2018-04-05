from flask import Flask,render_template,render_template_string,request,json,redirect,url_for,g,send_from_directory
from werkzeug.utils import secure_filename
import time
import thread
import sys
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from utils import *
import os
from logger import log
from werkzeug.contrib.fixers import ProxyFix
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
config = {}

@app.route('/')
@app.route('/index.html')
def welcomePage():
    return render_template('index.html',result=cardInfo())

@app.route('/')
@app.route('/index_1.html')
def welcomePage_1():
    return render_template('index_1.html',result=cardInfo())

@app.route('/homeNew')
@app.route('/homeNew.html')
def welcomePage_2():
    return render_template('homeNew.html',result=cardInfo())


@app.route('/page6.html')
def trek():
    return render_template('page6.html')

@app.route('/page3.html')
def contact():
    return render_template('page3.html')

@app.route('/trekCardInfo')
def cardInfo():
    mainData = []
    configFile = 'configs/config'
    config = configParser(configFile)
    for type in ['trek','adventure','camp','event']:
        data = {}
        trekText = config['%sTextInfo'% type]
        trekList = runCmd('ls %s' % trekText)
        trekList = filter(lambda x: not x == '', trekList.split('\n'))
        for trek in trekList:
            data[trek] = getInfoByName(trek)

        for trek, val in data.items():
            val = json.loads(val)
            # trekName = str(trek).replace('_',' ')
            data[trek] = [val["duration"], val['price']]
            # data[trekName] = data.pop(trek)
        trekImg = config['%sImageInfo' % type]
        trekList = runCmd('ls %s' % trekImg)
        trekList = filter(lambda x: not x == '', trekList.split('\n'))
        for trek in trekList:
            images = runCmd('ls %s/%s | head -1' % (trekImg, trek)).rstrip('\n')
            trekName = str(trek).replace('_', ' ')
            data[trek].append('%s/%s/%s' % (trekImg, trek, images))
            data[trekName] = data.pop(trek)
        if not data == {}:
            mainData.append(data)
    print mainData
    return mainData


@app.route('/fullInfo')
def fullInfo():
    return render_template('fullInfo.html')


# sendMail
@app.route('/sendMail',methods= ['POST','GET'])
def sendMail():
    import smtplib
    from smtplib import SMTP as SMTP 
    from email.mime.text import MIMEText
    time = runCmd('date')
    msg = "Name : %s \nPhone Number : %s\nTime Of Query : %s " % (request.args['name'],request.args['phone'],time)
    msg = MIMEText(msg)
    msg['Subject'] = "Customer Query"
    msg['From'] = "abhimanyudtt1@gmail.com"
    msg['To'] = "abhimanyudtt1@gmail.com"
    try : 
        s = smtplib.SMTP("smtp.gmail.com:587")
        s.ehlo()
        s.starttls()
        s.ehlo()
        s.login('abhimanyudtt1@gmail.com', 'i am a good boy?')
        s.sendmail(msg['From'], [msg['To']], msg.as_string())
        s.quit()
    except Exception : 
        pass

    fh=open('./info/leads','a')
    fh.write("Name : %s \nPhone Number : %s\nTime Of Query : %s " % (request.args['name'],request.args['phone'],time))

    return "1"


@app.route('/genericPageProduct',methods=['POST','GET'])
def genericPageProduct():
    # getEventByName
    data = getInfoByName(request.args['name'])
    data = json.loads(data)
    data['url'] = request.url_root

    return render_template('GenericProductDetails.html',result=data)



@app.route('/info/<path:filename>')
def custom_static(filename):
    app.config['CUSTOM_STATIC_PATH'] = './info/'
    return send_from_directory(app.config['CUSTOM_STATIC_PATH'], filename)

@app.route('/page4.html')
def footer():
    return render_template('page4.html')

@app.route('/page5.html')
def header():
    return render_template('page5.html')

@app.route('/gallery.html')
def gallery():
    return render_template('gallery.html')

@app.route('/introduction.html')
def introduction():
    return render_template('introduction.html')


@app.route('/room-details.html')
def roomDetails():
    return render_template('room-details.html')


@app.route('/admin')
def adminLogin():
    return render_template('login.html')

@app.route('/checkforlogin',methods= ['POST'])
def a_function():
    log.info( request.form)
    if request.form['username'] == 'admin' and request.form['password'] == 'admin@123':
        return redirect(url_for('infoEnterPage',messages = {'State':'True'}) )
    else :
        return "Invalid Access"


# deleteData
@app.route('/deleteData',methods= ['GET'])
def deleteData():
    name = str(request.args['name'])
    name = name.rstrip('\n')
    dirList = runCmd('find ./info -name %s -type d' % name).rstrip('\n')
    for file in dirList.split('\n'):
        runCmd('rm -rf %s' % file)
    dirList = runCmd('grep -il %s ./info/*.yml ' % name)
    dirList = dirList.rstrip('\n')
    tempFile = open('./info/temp','w')
    for file in dirList.split('\n'):
        for line in open(file,'r'):
            line = line.rstrip('\n')
            line = ast.literal_eval(line)
            if line['name'] != name:
                tempFile.write('%s\n' % line)
        runCmd('mv ./info/temp %s' % file)

    return redirect(url_for('getInfoAll') )

@app.route('/getInfoAll',methods= ['GET'])
def getInfoAll():
    import ast
    configFile = 'configs/config'
    config = configParser(configFile)
    data = {}
    log.info('Fetching saved information data from FS')
    for eachEvent in ['trek','camp','adventure','event']:
        for line in open(config['%sData' % eachEvent]):
            line = line.rstrip('\n')
            try : 
                line = ast.literal_eval(line)
                data['%s' % line['name'] ] = (line['ShortDef'][0:50],line['price'])
            except SyntaxError:
                pass


    return render_template('information.html',message=data)

@app.route('/infoEnterPage')
def infoEnterPage():
    if not request.args['messages']:
        return "Invalid Access"
    return render_template('enterInfo.html',result=['false'],messages={'State':'True'})


@app.route('/saveInfo',methods=['POST'])
def saveInfo():
    data = {}
    log.debug(request.form)
    log.debug(request.files)
    configFile = 'configs/config'
    config = configParser(configFile)
    print "In debug"
    #2017-08-15 21:35:17,536 ImmutableMultiDict([('name', u'aa'), ('price', u'1300'), ('optionsRadios', u'Trek'), ('paymentPolicy', u'asdf')
    # , ('cancelationPolicy', u'sfdads'), ('lngDef', u'aads'), ('inclusions', u'sdfg'), ('duration', u'1'), ('ShortDef', u'aaaa'),
    # ('itinerary_1', u'12'), ('exclusions', u'sdfg')])
    #2017-08-15 21:35:17,536 ImmutableMultiDict([('picture', <FileStorage: u'adventure.jpg' ('image/jpeg')>)])
    data['name'] =  str(request.form['name']).replace(' ','_')
    print data
    data['price'] = request.form['price']
    print data
    type = request.form['optionsRadios']
    print "type",type
    data['paymentPolicy'] = request.form['paymentPolicy']
    print data
    data['cancelationPolicy'] = request.form['cancelationPolicy']
    print data
    data['inclusions'] = request.form['inclusions']
    print data
    data['exclusions'] = request.form['exclusions']
    print data
    data['duration'] = request.form['duration']
    print data
    data['ShortDef'] = request.form['ShortDef']
    print data
    data['lngDef'] = request.form['lngDef']
    print data
    data['maxAlt'] = request.form['maxAlt']
    print data
    data['distance'] = request.form['distance']
    print data
    data['grade'] = request.form['grade']
    print data
    data['itinerary'] = {}
    for i in xrange(0,int(data['duration'])):
        data['itinerary']['itinerary_%s' %(i+1)] = request.form['itinerary_%s' %(i+1)]
        print data
    print data
    runCmd('mkdir -p %s/%s' % (config['%sTextInfo' % type],data['name']))
    runCmd('mkdir -p %s/%s' % (config['%sImageInfo' % type], data['name']))
    for fileName in ['paymentPolicy','cancelationPolicy','inclusions','exclusions','lngDef'] :
        open('%s/%s/%s' % (config['%sTextInfo' % type],data['name'],fileName),'w').write('%s'.encode("utf-8") % data['%s' % fileName])
        data['%s' % fileName] = '%s/%s/%s' % (config['%sTextInfo' % type],data['name'],fileName)
    open('%s' % config['%sData' % type],'a').write('%s\n'.encode("utf-8") % data)

    # Done with text saving now going to save images

    for i in range(1,len(request.files)+1):
        file = request.files['image_count_%s' % i]
        filename = secure_filename(file.filename)
        app.config['UPLOAD_FOLDER'] = '/'.join([config['%sImageInfo' % type],data['name']])
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return render_template('enterInfo.html', result=['true'], messages={'State': 'True'})


@app.route('/getEventByName',methods=['POST','GET'])
def getEventByName():
    data = getInfoByName(request.args['name'])
    return str(data)

@app.route('/leads',methods=['GET'])
def leads():
    string = runCmd('cat ./info/leads')
    return render_template_string("<html><body><pre>%s</pre></body></html>" % str(string))




if __name__ == "__main__":


    # Running some test before hand to check the directory structure is present or not
    # If not then will create a valid directory structure
    if not len(sys.argv) == 2 :
        log.error('No config file given exiting')
        exit(1)
    log.info('***********************************')
    log.info('*  Restarting UI and Backend app  *')
    log.info('***********************************')

    log.info('Running some test before hand to check the directory structure is present or not')
    log.info('If not then will create a valid directory structure')

    # Check if all the directories are present as per config
    log.info('Checking if all the directories are present as per config')

    configFile = sys.argv[1]
    config = configParser(configFile)
    # Running the app now
    app.run(host = '0.0.0.0',port=5501,debug=True)
    app.logger.addHandler(log)
