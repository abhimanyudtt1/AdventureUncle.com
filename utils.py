import subprocess
from logger import log
import os
import ast

def runCmd(cmd, logging=True):
    '''
    Modularizing command part for cli and shell Cmd commands
    '''
    (stdout, stderr) = subprocess.Popen('%s' % cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE,
                                        shell=True).communicate()

    if logging:
        log.info('Command : %s . stdout : %s . stderr : %s' % (cmd, stdout, stderr))
    if stderr == None:
        return stdout
    elif stdout == None:
        return stderr
    else:
        return "%s\n%s" % (stderr, stdout)


def configParser(file):
    import re
    infoData = {}
    lineNumber = 0
    if not os.path.isfile(file):
        log.error('No config file named %s present please check' % file)
        exit(1)
    log.info('Config file %s present. Validating the file now' % file)

    for line in open(file,'r'):
        lineNumber += 1
        if line == '\n' or line.startswith('#'):
            continue
        line = line.rstrip('\n')
        line = line.replace(' ','')
        if not line.count('=') == 1 :
            log.error('Config file : %s : Line has too many "=" signs' % (file,lineNumber))
            exit(1)
        line = line.split('=')
        infoData[line[0]] = line[1]
    log.info('Config file %s validated and parsed' % file)
    log.info('Now creating directory structure if not present')

    for k,v in infoData.items():
        if not ( os.path.isfile(v) or os.path.isdir(v) ):
            log.warning('File/dir %s not present will create and ignore' % v)
            # Now checking if the file is a dir or a file
            if '.yml' in v:
                dir = os.path.abspath(os.path.join(v, os.pardir))
                runCmd('mkdir -p %s' % dir)
                runCmd('touch %s' % v)
            else:
                dir = v
                runCmd('mkdir -p %s' % dir)

        else:
            log.warning('File/dir %s  present' % v)

    return infoData


def getAllConfigFiles(file):
    config = configParser(file)
    data = {}
    for type in ['treck','adventure','camp','event']:
        for line in open(config['%sData'] % type,'r'):
            line = line.rstrip('\n')
            line = ast.literal_eval(line)
            data[line['name']] = line

    return data


def getInfoByName(name):
    file = 'configs/config'
    config = configParser(file)
    #print "config : ",config
    counter = 0 
    for type in ['trek', 'adventure', 'camp', 'event']:
        cmd = 'grep "\'%s\'" %s ' % (name,config["%sData" % type])
        data = runCmd(cmd)
        if not data == "":
            break
    log.info('data : %s ' % data)
    for each in data.split('\n'):
        log.info('counter:%s' % counter)
        each = ast.literal_eval(each.rstrip('\n'))
        counter += 1 
        if each['name'] == name :
            response = each
            break
    if 'trek' in response['lngDef'].lower():
        response['optionsRadios'] = 'trek'
        cmd = 'find ./info/imageInfoAllProducts/Trek/%s -type f' % response['name']
    elif 'camp' in response['lngDef'].lower():
        response['optionsRadios'] = 'camp'
        cmd = 'find ./info/imageInfoAllProducts/Camp/%s -type f' % response['name']
    elif 'adventure' in response['lngDef'].lower():
        response['optionsRadios'] = 'adventure'
        cmd = 'find ./info/imageInfoAllProducts/Adventure/%s -type f' % response['name']
    elif 'event' in response['lngDef'].lower():
        response['optionsRadios'] = 'event'
        cmd = 'find ./info/imageInfoAllProducts/Event/%s -type f' % response['name']

    for k in ['cancelationPolicy','paymentPolicy','exclusions','inclusions','lngDef']:
        output = runCmd('cat %s' % response[k])
        response[k] = output
    output = runCmd(cmd)
    count = 0
    response['image'] = {}
    for line in output.split('\n'):
        count += 1
        if line == "":
            continue

        response['image']['image_count_%s' % count] = line

    # Making json
    import json
    #print response
    #print str(json.dumps(response))
    return str(json.dumps(response))



    if data == "":
        return False

