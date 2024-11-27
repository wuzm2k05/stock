import os
import configparser
from . import args

"""
_default_thread_pool_num = 10
_default_thread_pool_queue_size = 10
"""

def parse_config():
  config = configparser.ConfigParser()
  file_path = args.get_config_file_path()
  if (not file_path):
    file_path = 'config.ini'
  
  config.read(file_path,encoding='utf-8')
  return config

# if we need to reload the config file, need to use another configparser to read the file again
config = parse_config()

################################################################################################
#### snowball config
def get_snowball_key():
  return config.get('snowball','key', fallback=os.environ.get('SNOWBALL_KEY', ''))

def get_snowball_account():
  return config.get('snowball','account', fallback=os.environ.get('SNOWBALL_ACCOUNT', ''))

def get_snowball_server():
  return config.get('snowball','server', fallback=os.environ.get('SNOWBALL_SERVER', 'sandbox.snbsecurities.com'))

def get_snowball_port():
  return config.get('snowball','port', fallback=os.environ.get('SNOWBALL_PORT', '443'))

################################################################################################
#### policy config
def get_policy_check_interval_in_seconds():
  return config.getint('policy', 'check_interval_in_seconds',fallback=int(os.environ.get('POLICY_INTERVAL_SECONDS',300)))

def get_policy_min_trade_stocks():
  return config.getint('policy', 'min_trade_stocks',fallback=int(os.environ.get('POLICY_MIN_TRADE_STOCKS',1000)))

def get_policy_stocks_config():
  #{"stock_name":{"stock_currency":"HKD, USD","max_price":"max_price","min_price":"min_price","degree":"degree","total_amount_money":"total_money","reserve_stocks":"how many stocks reserved","round_stocks":"round stocks","min_trade_stocks":1000,"fraction":"fration of price"},}
  return config.get('policy','stocks_config', fallback=os.environ.get('POLICY_STOCKS_CONFIG', ''))

################################################################################################
### logging system
def get_log_file_name():
  return config.get('logging', 'file_name', fallback=os.environ.get('LOGGING_FILE_NAME',"stock.log"))

def get_log_backup_file_num():
  return config.getint('logging', 'backup_file_num',fallback=int(os.environ.get('LOGGING_BACKUP_FILE_NUM',3)))

def get_log_backup_file_size():
  return config.getint('logging', 'backup_file_size',fallback=int(os.environ.get('LOGGING_BACKUP_FILE_SIZE',10000000)))

# logging destination: console,file console file
def get_log_destination():
  return config.get('logging', 'destination', fallback=os.environ.get('LOGGING_DESTINATION',"console"))

# logging level: debug info warning error critical
def get_log_level():
  return config.get('logging', 'level', fallback=os.environ.get('LOGGING_LEVEL',"info"))

#######################################################################################################
### email config
def get_send_email_addr():
  return config.get('email','send_email', fallback=os.environ.get('EMAIL_SEND_EMAIL_ADDR',"79809620@qq.com"))

def get_email_password():
  return config.get('email','password', fallback=os.environ.get('EMAIL_PASSWORD',"xxxxxxxx"))

def get_to_emails_addr():
  return config.get('email','to_email', fallback=os.environ.get('EMAIL_TO_EMAILS_ADDR',"79809620@qq.com"))

def get_email_smtp_server():
  return config.get('email','smtp_server', fallback=os.environ.get('EMAIL_SMTP_SERVER',"smtp.qq.com"))

def get_email_smtp_port():
  return config.getint('email','smtp_port', fallback=os.environ.get('EMAIL_SMTP_PORT',587))


########################################################################################################
### report policy
def get_report_start_hour():
  return config.getint('report','start_hour', fallback=os.environ.get('REPORT_START_HOUR',18))

def get_report_end_hour():
  return config.getint('report','end_hour', fallback=os.environ.get('REPORT_END_HOUR',20))

### output all configrations
def output_configs(log):
  log.info("=================configs=====================")
  for section in config.sections():
    for key, value in config.items(section):
        log.info(f"{section}.{key} = {value}")
  log.info("\n")
        