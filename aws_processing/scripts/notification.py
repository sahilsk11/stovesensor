import boto3
import passwords
 
def send_notification(number, code):
    # Create an SNS client
    client = boto3.client(
        "sns",
        aws_access_key_id=passwords.key(),
        aws_secret_access_key=passwords.access(),
        region_name="us-east-1"
    )
     
    # Send your sms message.
    client.publish(
        PhoneNumber=number,
        Message="Alert! Your gas may be on. To view the status, go to www.iotspace.tech/stovesensor?code="+code
    )