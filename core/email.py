import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from . import config
from . import logger

_log = logger.get_logger()

def send_email(subject, body):
  try:
    from_email = config.get_send_email_addr()
    to_email = config.get_to_emails_addr()
    password = config.get_email_password()
    
    # Create the email header
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    # Attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))
    
    # Create SMTP session for sending the mail
    server = smtplib.SMTP(config.get_email_smtp_server(), config.get_email_smtp_port())  # use gmail with port
    server.starttls()  # enable security

    # Login with your Gmail account
    server.login(from_email, password)

    # Convert the Multipart msg into a string
    text = msg.as_string()

    # Send the mail
    server.sendmail(from_email, to_email, text)

    # Terminate the SMTP session
    server.quit()

    _log.info(f"Email sent successfully to {to_email}")
  except Exception as e:
    _log.error(f"Failed to send email. Error: {e}")


