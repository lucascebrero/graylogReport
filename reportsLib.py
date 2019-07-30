#!/usr/bin/python3

import os
import csv
import json
import datetime
import requests
import _pickle as pickle

## MAIL ##
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE
from email import encoders
###


############################## TOKENS ############################################

# Create API token
def createToken(args):
    # User and password
    auth = (args['<user>'], args['<password>'])

    # POST Parameters
    headers = {'Accept': 'application/json', 'X-Requested-By': 'XMLHttpRequest'}
    url = "http://" + args['<server>'] + ":" + args['--port'] + "/api/users/" + auth[0] + "/tokens/"  + args['<tokenName>']

    try:
        r = requests.post(url, headers=headers, auth=auth)
        tokend = json.loads(r.text)
        saveToken(tokend)

    except Exception as e:
        exit(0)

# Delete API token
def deleteToken(args):

    # User and password
    auth = (args['<user>'], args['<password>'])

    # Delete token from server
    headers = {'Accept': 'application/json', 'X-Requested-By': 'XMLHttpRequest'}
    url = "http://" + str(args['<server>']) + ":" + str(args['--port']) + "/api/users/" + auth[0] + "/tokens/" + str(args['<tokenValue>'])
    try:
        r = requests.delete(url, headers=headers, auth=auth)
        if r:
            print(args['<tokenValue>'] + " token has succesfully been removed")

            # Update token db 
            updateTokens(args)
        else:
            print(r.text)
            print("An error has ocurred")
    except Exception as e:
        exit(0)

# Save token to file
def saveToken(tokend):
    tokenDB = 'token.db'
    tokendList = []

    try:
        with open(tokenDB, 'rb') as f:
            tokendList = pickle.load(f)
    except Exception as e:
        
        if not tokendList:
            tokendList = []

    # Add new token to token dictionary
    tokendList.append(tokend)

    # Save token dictionary list
    try:
        with open(tokenDB, 'wb') as f:
            pickle.dump(tokendList,f)

    except Exception as e:
        exit(0)

    print("The token has been created")

# Load tokens from file 
def loadTokens():
    tokenDB = 'token.db'

    try:
        with open(tokenDB,'rb') as f:
            tokendList = pickle.load(f)
        return tokendList

    except Exception as e:
        exit(0)

# List tokens from file
def listTokens(args):
    tokendList = loadTokens()
    print("Token List")
    for i in tokendList:
        print("- " + i['name'] + " -> " + i['token'] + " last access: " + i['last_access'])

# Retrieves specified token, by name, from file and returns it
def getToken(tname):
    tokendl = loadTokens()
    token = [ x for x in tokendl if x['name'] == tname]
    return token[0]['token'] 

# Get tokens from API and store them in local file
def updateTokens(args):
    
    tokenDB = 'token.db'
    auth = (args['<user>'], args['<password>'])

    # POST for getting token list 
    url = "http://" + str(args['<server>']) + ":" + str(args['--port']) + "/api/users/" + args['<user>'] +"/tokens"

    tokendList = []
    try:
        req = requests.get(url, auth=auth)
        aux = json.loads(req.text)
        for i in aux['tokens']:
            tokendList.append(i)
            
    # Save token dictionary list to db
        with open(tokenDB, 'wb') as f: 
            pickle.dump(tokendList,f)

    except Exception as e:
        exit(0)


#----------------------------------------------------------------------------------#
############################## SEARCHES ############################################

# Get saved searches from graylog API 
def getSearches(args):
    
    auth = (args['<tokenValue>'],"token")
    url = "http://" + str(args['<server>']) + ":" + str(args['--port']) + "/api/search/saved" 
    searches = {} 

    try: 
        req = json.loads(requests.get(url, auth=auth).text) 
        
        for i in req['searches']: 
            searches[i['title']] =  [ i['id'], i['query']['query']] 
        

        if args['--searchName']:
            print("%s" % searches[args['--searchName']][1])
            return searches[args['--searchName']][1]
        
        else:
            for i in searches:
                print("%s: %s\n" % (i,searches[i][1]))
           	
    except Exception as e: 
        print(e)


#---------------------------------------------------------------------------------#
############################## REPORTS ############################################

# Absolute search report
def absoluteReport(args): 
    auth = (args['<tokenValue>'], "token")
    fileName = ""    

    root = "http://" + args['<server>'] + ":"+ args['--port'] +"/api/search/universal/absolute/export" 

    if not args['--filename']:
        fileName = str(args['<startUTC>']) + "_" + str(args['<endUTC>']) + ".csv" 

    else:
        fileName = args['--filename']

    try: 
        r = requests.get(root, params=[("query", args['<searchQuery>']), ("from", args['<startUTC>']),("to", args['<endUTC>']), ("fields", args['<fields>'])], auth=auth)
        
        
    except Exception as e:
        exit(0)

    exportReport(r.text, fileName)

# Relative search report
def relativeReport(args): 
    auth = (args['<tokenValue>'], "token")
    fileName = ""    
    
    root = "http://" + args['<server>'] + ":"+ args['--port'] +"/api/search/universal/relative/export" 
    fileName = "last-" + args['<rel>'] + ".csv"

    try: 
        r = requests.get(root, params=[("query", args['<searchQuery>']), ("range", args['<rel>']), ("fields", args['<fields>'])], auth=auth) 
    except Exception as e:
        exit(0)

    exportReport(r.text, fileName)

# Export CSV
def exportReport(response, fileName):
        print("Exporting report. ..")
        try:
           #Save to file
           with open(fileName, 'w') as f:
               f.write(response)

        except Exception as e:
            exit(0)

# Send report by email
def sendReport(args):
    # Create message
    msg = MIMEMultipart()
    msg['From'] = args['<sender>']
    msg['To'] = COMMASPACE.join([args['<toaddr>']])
    msg['Subject'] = args['--subject']

    # Create attachment
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(open(args['<filename>'],'rb').read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment', filename=args['<filename>'])
    msg.attach(part)

    # Send mail
    try: 
        smtp = smtplib.SMTP(args['<mailserver>']) 
        smtp.ehlo() 
        smtp.starttls() 
        smtp.sendmail(args['<sender>'],args['<toaddr>'], msg.as_string()) 
        smtp.quit()

    except Exception as e: 
        exit(0)

