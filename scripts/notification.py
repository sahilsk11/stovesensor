#!/usr/bin/python
import smtplib
import passwords
import shelve
import datetime

notification_data = shelve.open("notification.shelve", writeback=True)
if (not "last_sent" in notification_data):
    notification_data["last_sent"] = 0
    
class notification:

    def __init__(self, phone_number, service):
        self.number = phone_number
        self.provider = service
        
    def send_email(self):
        if (self.can_send_notification()):
            SMTP_SERVER = 'smtp.gmail.com'
            SMTP_PORT = 587
            GMAIL_USERNAME = 'iotspace.tech@gmail.com'
            GMAIL_PASSWORD = passwords.email() #CAUTION: This is stored in plain text!
            
            recipient = self.number+'@' + self.provider
            subject = 'Gas Monitor'
            emailText = 'Alert! Your gas may be on.'
            
            emailText = "" + emailText + ""
            
            headers = ["From: " + GMAIL_USERNAME,
                       "Subject: " + subject,
                       "To: " + recipient,
                       "MIME-Version: 1.0",
                       "Content-Type: text/html"]
            headers = "\r\n".join(headers)
            
            session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            
            session.ehlo()
            session.starttls()
            session.ehlo
            
            session.login(GMAIL_USERNAME, GMAIL_PASSWORD)
            
            session.sendmail(GMAIL_USERNAME, recipient, headers + "\r\n\r\n" + emailText)
            
            session.quit()
            notification_data["last_sent"] = datetime.datetime.now()
    
    def can_send_notification():
        last_time = notification_data["last_sent"]
        if (last_time == 0 or last_time + datetime.timedelta(minutes=5) < datetime.datetime.now()):
            return True
        else:
            return False
        
    def close_shelf(self):
        notification_data.close()
        
if (__name__ == "__main__"):
    notif = notification("4088870718", "tmomail.net")
    if (notif.can_send_notification()):
        print("sending notification")
        notification_data["last_sent"] = datetime.datetime.now()
        notif.send_email()