import argparse

_args = None

def parse_cmd():  
  parser = argparse.ArgumentParser(description='jjd wxai server')

  parser.add_argument('-c', '--config', help='configuration file path')
  
  # parse args
  return parser.parse_args()

_args = parse_cmd()


def get_config_file_path():
  return _args.config