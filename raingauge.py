'''
Created on Sep 12, 2012

@author: csimpson
'''
import ConfigParser
import urllib2
import sqlite3
import datetime as DT
import smtplib

from optparse import OptionParser
from datetime import date, timedelta 
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

def fetchRainfall(station):
    print 'Retrieving rainfall from ' + station
    url = BASE_URL.format(station, timestamp.day, timestamp.year, timestamp.month)
    print url
    weatherData = urllib2.urlopen(url)
    html = weatherData.read()
    
    onlyTables = SoupStrainer(class_="contentData") 
    
    soup = BeautifulSoup(html.encode("utf8"), "lxml", parse_only=onlyTables)
    contentTable = soup.find(text='Precipitation:')
    contentTable = contentTable.find_parent('tr')
    
    inchStr = contentTable.find(class_='b')
    rainfall = float(inchStr.contents[0].string)
    recordRainFall(rainfall)
    
def recordRainFall(inches):
    iso = str(timestamp.isoformat())
    print 'Station reporting ' + str(inches) + ' inches on ' + iso
    
    checkEntrySQL = "SELECT Count(Id) FROM Rainfall WHERE Date='"+iso+"';"
    insertDataSQL = "INSERT INTO Rainfall(Inches, Date) VALUES('"+str(inches)+"','"+iso+"');"
    
    cursor.execute(checkEntrySQL)
    if not cursor.fetchone()[0]:
        cursor.execute(insertDataSQL)
    else:
        print 'Date already recorded'
        #cleanUp()
        #return
    db.commit()
    shouldSendEmail()
    db.close()   

def shouldSendEmail():
    rainfall = getThreeDayRainfall()
    if rainfall < 1.00 and int(rainfall) is not -1:
        getLastEmailSentSQL = "SELECT Date FROM EmailSent ORDER BY Id DESC LIMIT 1;"
        cursor.execute(getLastEmailSentSQL)
        result = cursor.fetchone()
        
        if result is not None:
            emailDate = DT.datetime.strptime(result[0], '%Y-%m-%d')
            timeDiff =  DT.datetime.strptime(timestamp.isoformat(), '%Y-%m-%d') - emailDate
            if timeDiff.days > 3:
                print 'Last email sent more than 3 day ago'
                sendEmail(water_message.format(rainfall))
            else:
                print 'Not sending email, less than 3 days'
        else:
            print 'Sending email no email ever sent'
            sendEmail(water_message.format(rainfall))
        return
    elif rainfall >= 1.00:
        print 'Not sending email rainfall '+str(rainfall)+' inches in the last three days'
    else:
        print 'Not sending email not enough data points'

def getThreeDayRainfall():
    getLastThreeDaysSQL = "SELECT * FROM Rainfall ORDER BY Id DESC LIMIT 3;"
    cursor.execute(getLastThreeDaysSQL)
    rows = cursor.fetchall()
    totalIn = -1.00
    if rows.__len__() > 2:
        totalIn = 0.00
        for row in rows:
            totalIn += round(float(row[1]), 2)
    return totalIn 

def sendEmail(message):
    print 'sending email'
    subject = 'Rain Gauge'
    sentEmailSQL ="INSERT INTO EmailSent(Date) VALUES('"+str(timestamp.isoformat())+"');"
    cursor.execute(sentEmailSQL)
    db.commit()
    subject += 'Water Your Garden!'

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = config.get('email','sender')
    msg['To'] = config.get('email', 'receiver')
    
    msg.attach(MIMEText(config.get('email', 'greeting') + message + signature))
    
    smtp = smtplib.SMTP(config.get('email', 'smtp_url'), config.get('email', 'smtp_port'))
    #smtp.set_debuglevel(1)
    
    smtp.ehlo()
    smtp.starttls()
    smtp.ehlo()
    smtp.login(msg['From'],config.get('email','password'))
    smtp.sendmail(msg['From'], msg['To'], msg.as_string())
    smtp.close()

if __name__ == '__main__':
    #Base website url for getting local weather information.
    BASE_URL = 'http://www.wunderground.com/weatherstation/WXDailyHistory.asp?ID={0}&day={1}&year={2}&month={3}'
    
    #Email content
    water_message = 'It\'s been three days since there was an inch of rainfall.  The last three days had {0} inches'
    signature = '\nBest,\nYour House'
    
    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option("-c", "--config", dest="config", default="config.cfg", help="Custom configuration file path")
    (options, args) = parser.parse_args()
    
    config = ConfigParser.SafeConfigParser({'db_path':'rainfall.db', 'greeting':'Hello,\n'})
    config.read(options.config);
    
    #Connect db.
    db = sqlite3.connect(config.get('db','db_path'))
    cursor = db.cursor()
    
    #Get yestarday's date so we can get to 24 hour rain fall
    timestamp = date.today() - timedelta(1)
    
    #We can now look at our rainfall.
    fetchRainfall(config.get('location','station'))
