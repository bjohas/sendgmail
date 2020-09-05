#!/usr/bin/python
from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import base64
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes
import os
import json

from apiclient import errors

from sys import stdin
from sys import argv
import sys

import argparse
import re

"""Send an email message from the user's account.
"""


def create_message(sender, to, cc, bcc, subject, message_text):
    """Create a message for an email.

    Args:
      sender: Email address of the sender.
      to: Email address of the receiver.
      subject: The subject of the email message.
      message_text: The text of the email message.

    Returns:
      An object containing a base64url encoded email object.
    """
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    message['bcc'] = bcc
    message['cc'] = cc
    rawmsg = {'raw': base64.urlsafe_b64encode(
        message.as_string().encode('utf-8')).decode('utf-8')}
    # base64_bytes = b64encode(byte_content)
    # # third: decode these bytes to text
    # # result: string (in utf-8)
    # base64_string = base64_bytes.decode(ENCODING)
    # print (rawmsg)
    return rawmsg
    # TypeError: a bytes-like object is required, not 'str'


def create_draft(service, user_id, message_body):
    """Create and insert a draft email. Print the returned draft's message and id.

    Args:
      service: Authorized Gmail API service instance.
      user_id: User's email address. The special value "me"
      can be used to indicate the authenticated user.
      message_body: The body of the email message, including headers.

    Returns:
      Draft object, including draft id and message meta data.
    """
    try:
        message = {'message': message_body}
        draft = service.users().drafts().create(userId=user_id, body=message).execute()

        print('Draft id: %s\nDraft message: %s' %
              (draft['id'], draft['message']))

        return draft
    except errors.HttpError as error:
        print('An error occurred: %s' % error)
        return None


def create_message_with_attachment(sender, to, cc, bcc, subject, message_text, files):
    """Create a message for an email.

    Args:
      sender: Email address of the sender.
      to: Email address of the receiver.
      subject: The subject of the email message.
      message_text: The text of the email message.
      file: The path to the file to be attached.

    Returns:
      An object containing a base64url encoded email object.
    """
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['cc'] = cc
    message['bcc'] = bcc
    message['subject'] = subject

    msg = MIMEText(message_text)
    message.attach(msg)

    for file in files:
        content_type, encoding = mimetypes.guess_type(file)
        if content_type is None or encoding is not None:
            content_type = 'application/octet-stream'
        main_type, sub_type = content_type.split('/', 1)
        if main_type == 'text':
            fp = open(file, 'r')
            msg = MIMEText(fp.read(), _subtype=sub_type)
            fp.close()
        elif main_type == 'image':
            fp = open(file, 'rb')
            msg = MIMEImage(fp.read(), _subtype=sub_type)
            fp.close()
        elif main_type == 'audio':
            fp = open(file, 'rb')
            msg = MIMEAudio(fp.read(), _subtype=sub_type)
            fp.close()
        else:
            fp = open(file, 'rb')
            msg = MIMEBase(main_type, sub_type)
            msg.set_payload(fp.read())
            fp.close()
        filename = os.path.basename(file)
        msg.add_header('Content-Disposition', 'attachment', filename=filename)
        message.attach(msg)
    #  return {'raw': base64.urlsafe_b64encode(message.as_string())}
    return {'raw': base64.urlsafe_b64encode(message.as_string().encode('utf-8')).decode('utf-8')}


def send_message(service, user_id, message):
    """Send an email message.

    Args:
      service: Authorized Gmail API service instance.
      user_id: User's email address. The special value "me"
      can be used to indicate the authenticated user.
      message: Message to be sent.

    Returns:
      Sent Message.
    """
    try:
        # print(message)
        message = (service.users().messages().send(userId=user_id, body=message)
                   .execute())
        print('Message Id: %s' % message['id'])
        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.send']


def main(args):
    """Shows basic usage of the Gmail API.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    credentialsjson = args.credentials
    tokenpickle = args.token

    if os.path.exists(tokenpickle):
        with open(tokenpickle, 'rb') as token:
            creds = pickle.load(token, encoding='latin1')

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentialsjson, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(tokenpickle, 'wb') as token:
            pickle.dump(creds, token)
            # ^^^ may need changing.

    service = build('gmail', 'v1', credentials=creds)

    # Call the Gmail API
    #results = service.users().labels().list(userId='me').execute()
    #labels = results.get('labels', [])

    mtext = ""
    if args.message != None:
        mtext = args.message

    if args.mfile:
        if args.mfile != '-':
            with open(args.mfile, 'r') as f:
                mtext = mtext + f.read()

    if args.mfile == '-' or (args.mfile == None and args.message == None):
        print("Reading from STDIN")
        if stdin:
            for line in stdin:
                mtext = mtext + line
                
    if args.sfile:
        with open(args.sfile, 'r') as f:
            mtext = mtext + f.read()
    
    subject = args.subject
    to = args.to
    send_from = args.sender
    cc = args.cc
    bcc = args.bcc
#    subject = "Engagement tracker: " + subject

    if args.attach:
        mymessage = create_message_with_attachment(
            send_from, to, cc, bcc, subject, mtext, args.attach)
    else:
        mymessage = create_message(send_from, to, cc, bcc, subject, mtext)
    send_message(service, send_from, mymessage)


# configuration is given a higher priority then command line
# this can be changed if needed

def locateFile(name,args):
    configType = 0
    configPath = ""
    configuration = None
    if name in vars(args):
        configuration = getattr(args, name)
        configType = 1 # config provided via args
    else:
        if os.path.exists(name):
            configType = 1 # config file in same directory
            configuration = name
        else:
            senderavailable = True
            if 'sender' in vars(args) and getattr(args, 'sender') != None:
                senderavailable = True
            else:
                senderavailable = False
            if senderavailable:
                fallback_config_2 = os.path.join(os.environ['HOME'], '.config', 'sendgmail', args.sender, name)
                if os.path.exists(fallback_config_2):            
                    configType = 2 # config file via via args.sender (more specific)
                    configPath = os.path.join(os.environ['HOME'], '.config', 'sendgmail', args.sender)
                    configuration = fallback_config_2
                    sendavailable = True
            if not senderavailable:
                fallback_config_3 = os.path.join(os.environ['HOME'], '.config', 'sendgmail', name)
                if os.path.exists(fallback_config_3):
                    configType = 3 # config file (generic)
                    configPath = os.path.join(os.environ['HOME'], '.config', 'sendgmail')
                    configuration = fallback_config_3
    return configType, configPath, configuration 
                        
def locateFileByKey(mykey, args, config):
    # Figure out credentials
    locatedType = 0
    locatedFile = ""
    if mykey in vars(args) and getattr(args, mykey) != None:
        locatedType = 1 # provided in args
        locatedFile = getattr(args, mykey)
    else:
        test = mykey+'.json'
        if os.path.exists(test):
            locatedType = 2 # credentials file exists locally (overrides config)
            locatedFile = test
        else:
            if mykey in config:
                if re.search("^\w",config[mykey]) and configPath != "":
                    config[mykey] = os.path.join(configPath, config[mykey])
            if mykey in config and os.path.exists(config[mykey]):
                locatedType = 3 # credentials provided in config - overrides direct credentials files
                locatedFile = config[mykey];
            else: 
                test = os.path.join(os.environ['HOME'], '.config', 'sendgmail', args.sender,  mykey+'.json')
                if os.path.exists(test):
                    locatedType = 4 # credentials provided via more specific dir
                    locatedFile = test
                else:
                    test = os.path.join(os.environ['HOME'], '.config', 'sendgmail',  mykey+'.json')
                    if os.path.exists(test):
                        locatedType = 5 # credentials provided less specific dir
                        locatedFile = test
    return locatedType,locatedFile

def getConfigIfNeeded(mykey, args, config):
    if mykey in vars(args) and getattr(args, mykey) != None:
        return getattr(args, mykey)
    elif mykey in config:
        return config[mykey]
    else:
        return None

# MAIN PROGRAMME LOOP    
# Get arguments.
parser = argparse.ArgumentParser(description='Send gmail command line utility')
parser.add_argument('--to', action='store',help='To:-field. A comma separated list of email addresses.')
parser.add_argument('--sender', action='store',help='A single email address: The sender.')
parser.add_argument('--cc', action='store',help='CC:-field. A comma separated list of emails.')
parser.add_argument('--bcc', action='store',help='BCC:-field. A comma separated list of emails.')
parser.add_argument('--subject', action='store',help='Subject provided as string on command line')
parser.add_argument('--message', action='store',help='Message body provided as string on command line')
parser.add_argument('--mfile', action='store',help='A file with the message body.')
parser.add_argument('--sfile', action='store',help='A file with a signature. Will be appended to message.')
parser.add_argument('--attach', nargs='*',help='A list of attachments.')
parser.add_argument('--credentials', action='store',help='Credentials file.')
parser.add_argument('--token', action='store',help='The token file.')
parser.add_argument('--configuration', action='store',help='Configuration file.')
parser.add_argument('--setup', action='store',help='Set up an email account.')

args = parser.parse_args()
#for arg in vars(args):
#    print(arg, getattr(args, arg))

if args.setup:
    if os.path.exists(args.setup):
        print("Config file exists")
        args.configuration = args.setup
    else:
        #parser.print_help()
        if not args.sender:
            print("At least --sender has to be specified.")
            sys.exit();
        with open(args,setup, 'w') as file:
            file.write("{")
            file.write("\t\"sender\": \"{}\",".format(args.sender))
            if args.cc:
                file.write("\t\"cc\": \"{}\",".format(args.cc))
            if args.bcc:
                file.write("\t\"bcc\": \"{}\",".format(args.bcc))
            if args.subject:
                file.write("\t\"subject\": \"{}\",".format(args.subject))
            if args.message:
                file.write("\t\"message\": \"{}\",".format(args.message))
            if args.mfile:
                file.write("\t\"mfile\": \"{}\",".format(args.mfile))
            if args.sfile:
                file.write("\t\"sfile\": \"{}\",".format(args.sfile))
            if args.attach:
                file.write("\t\"attach\": \"{}\",".format(args.attach))
            if args.credentials:
                file.write("\t\"credentials\": \"{}\",".format(args.credentials))
            else:
                file.write("\t\"credentials\": \"{}\",")
            if args.token:
                file.write("\t\"token\": \"{}\"".format(args.token))
            else:
                file.write("\t\"token\": \"{}\"")
            file.write("}")         
        print("Configuration created.")
        sys.exit(1)
        
configType, configPath, configuration = locateFile('config.json',args)
if configuration:
    print("Using configuration method "+ str(configType) +" -> "+configuration)

if args.setup:
    print("Setup")
    with open(args.setup, 'r') as f:
        config = json.load(f)
        print(config)
        creds = None
        if os.path.exists(config["credentials"]):
            print("credentials exist - will use them")
        else:
            if args.credentials:
                print("Credentials supplied - moving into place")
                os.system('mv -i \"{}\" \"{}\"'.format(args.credentials,config["credentials"]))
            else:
                print("Credentials NOT supplied - enable API and save credentials file.")
                print("Setup: Open https://developers.google.com/gmail/api/quickstart/go to enable the client API. Save the file and supply with --credentials")
                sys.exit(1)
        # We now have creentials
        credentialsjson = config["credentials"]
        tokenpickle = config["token"]
        flow = InstalledAppFlow.from_client_secrets_file(credentialsjson, SCOPES)
        creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(tokenpickle, 'wb') as token:
            pickle.dump(creds, token)
            # ^^^ may need changing.
    print("Setup complete.")
    sys.exit(1)
        
# Use the configuration file (if provided, if in same dir, or if in default place)
if configuration:
    with open(configuration, 'r') as f:
        config = json.load(f)
        credType, args.credentials = locateFileByKey('credentials', args, config)
        tokenType, args.token = locateFileByKey('token', args, config)
        print("Using credentials: "+ str(credType) + ": "+ str(args.credentials))
        print("Using token:       "+ str(tokenType) + ": "+ str(args.token))
        # args.to = config['to'] if 'to' in config else args.to
        #if not 'to' in vars(args) and 'to' in config:
        #    args.to = config['to']
        args.to = getConfigIfNeeded('to', args, config)
        #args.sender = config['sender'] if 'sender' in config else args.sender
        args.sender = getConfigIfNeeded('sender', args, config)
        #args.cc = config['cc'] if 'cc' in config else args.cc
        args.cc = getConfigIfNeeded('cc', args, config)
        #args.bcc = config['bcc'] if 'bcc' in config else args.bcc
        args.bcc = getConfigIfNeeded('bcc', args, config)
        #args.subject = config['subject'] if 'subject' in config else args.subject
        args.subject = getConfigIfNeeded('subject', args, config)
        #args.message = config['message'] if 'message' in config else args.message
        args.message = getConfigIfNeeded('message', args, config)
        #args.mfile = config['mfile'] if 'file' in config else args.file
        args.mfile = getConfigIfNeeded('mfile', args, config)
        #args.sfile = config['mfile'] if 'file' in config else args.file
        args.sfile = getConfigIfNeeded('sfile', args, config)
        args.attach = config['attach'] if 'attach' in config else args.attach
else:
    tT,tP,args.token = locateFile('token.pickle',args)
    cT,cP,args.credentials = locateFile('credentials.json',args)
    print("token "+ str(tT) +" -> "+str(args.token))
    print("creds "+ str(cT) +" -> "+str(args.credentials))
    
# This needs fixing still: credentials is sufficient, but a token file must be avaialble (even if empty)
if not( args.token ) or not( args.credentials ):
    print("You must provide credentials/token")
    parser.print_help()
    sys.exit(1)

if not args.to or not args.sender or not args.subject:
    print("You must provide to/sender/subject")
    parser.print_help()
    sys.exit(1)

    
if __name__ == '__main__':
    main(args)
