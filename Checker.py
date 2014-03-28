# Name:        CheckNewActs
# Purpose:      This script checks for new Acts coming to North Sea Jazz 2014
#               and sends an e-mail when one has been detected
#
# Author:      laakenb
#
# Created:     27/03/2014
#-------------------------------------------------------------------------------

# Script should run every hour using crontab

import urllib2, csv, smtplib, sys, os, re
from email.mime.text import MIMEText

# DevMode toggle stops mail from being sent and instead prints
# mail output to console
devMode = False

# Send messages to:
toaddrs  = ['mannerisms@gmail.com']

# Path to Script
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

def main():
    #Read NSJ site
    newArtists = getNewArtists()

    #Open Previous list of acts
    previousArtists = getPreviousArtists()

    #Compare new list to previous list
    addedArtists = compareArtists(newArtists,previousArtists)

    # Check if there are any new artists
    if len(addedArtists)>0:

        #Format message
        formattedNewArtists = formatMessage(addedArtists)

        #If act in new list that is not in old list, send mail
        sendMessage(formattedNewArtists)

        #save new list as previous list
        txt = open(__location__+"/previousArtists.txt", "w")
        for artist in newArtists:
            txt.write(str(artist)+"\n")
        txt.close()


def formatMessage(addedArtists):
    SUBJECT = "Newly confirmed artist(s) coming to North Sea Jazz Festival 2014"
    formatTxt = ""
    for artist in addedArtists:
        formatTxt += str(artist)+"\n"
    message = 'Subject: %s\n\n%s' % (SUBJECT, formatTxt)
    return message

def compareArtists(newArtists, oldArtists):
    newAdditions = []
    for artist in newArtists:
        if artist not in oldArtists:
            newAdditions.append(artist)
    return newAdditions

def getNewArtists():

    # Read the NSJ website
    response = urllib2.urlopen(u'http://www.northseajazz.com/nl/programma/')
    html = response.read().replace("</strong>","</strong>,")
    response.close()

    #Clean Acts text and save as list
    newArtists = [] # List for new artists
    lookUp = "</strong>"
    cleanHTML = ""

    # Extract the sections with performance data
    for item in html.split("<br />"):
        if lookUp in item:
            cleanHTML += item [ item.find(lookUp)+len(lookUp) : ]

    # Split the artists into a list
    for item in cleanHTML.split(","):
        if devMode:
          print item.strip().replace("&amp;","&").replace("&nbsp;","").replace("&rsquo;","'")
        newArtists.append(item.strip().replace("&amp;","&").replace("&nbsp;","").replace("&rsquo;","'").replace("&Uuml;","U"))

    newArtists.sort()
    return newArtists


def getPreviousArtists():

    previousArtists = []

    rf =  open(__location__+"/previousArtists.txt", "r")
    for line in rf:
        previousArtists.append(line.strip())
    rf.close()

    return sorted(previousArtists)

def sendMessage(newArtists):

    creds = []

    rc =  open(__location__+"/config.txt", "r")
    txt = rc.read()
    creds = re.findall("'([^']*)'", txt)
    rc.close()

    fromaddr = creds[0]+'@gmail.com'
    msg = newArtists

    # Credentials (if needed)
    username = creds[0]
    password = creds[1]

    if(devMode):
      print "username =",username,"password:",password,"\n"
      print msg

    else:
      # The actual mail send
      server = smtplib.SMTP('smtp.gmail.com:587')
      server.starttls()
      server.login(username,password)
      server.sendmail(fromaddr, toaddrs, msg)
      server.quit()



if __name__ == '__main__':
    main()
