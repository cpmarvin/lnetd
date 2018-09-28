import logging

def get_module_logger(mod_name,level):
  logger = logging.getLogger(mod_name)
  handler = logging.StreamHandler()
  formatter = logging.Formatter(
          '%(asctime)s - %(name)s (%(lineno)s) - %(levelname)s: %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
  handler.setFormatter(formatter)
  logger.addHandler(handler)
  level = logging.getLevelName(level)
  logger.setLevel(level)
  return logger
