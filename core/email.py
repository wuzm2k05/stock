import datetime,time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from . import config
from . import logger

_log = logger.get_logger()

_alert_history = {}
_current_date = None

# 首次告警后的等待时间（分钟）
INITIAL_INTERVAL = 5
# 后续告警的时间间隔倍增因子
INTERVAL_MULTIPLIER = 3
# 时间间隔的单位（分钟）
TIME_UNIT = datetime.timedelta(minutes=1)

def send_error_email(error_info):
  global _alert_history
  global _current_date
  
  now = datetime.datetime.now()
  today = now.date()
  
  if today != _current_date:
    _alert_history = {}
    _current_date = today
    _log.info(f"[{now}] new day, reset alert email settings")
  
  if error_info not in _alert_history:
    _alert_history[error_info] = {"next_send_time": now, "interval": INITIAL_INTERVAL}
  
  if now >= _alert_history[error_info]["next_send_time"]:
    #send email
    send_email("Internal Error",error_info)
    
    _alert_history[error_info]["next_send_time"] = now + _alert_history[error_info]["interval"] * TIME_UNIT
    _alert_history[error_info]["interval"] *= INTERVAL_MULTIPLIER
    
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


