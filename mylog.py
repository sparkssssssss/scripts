import logging

class Mylog:
    def __init__(self,tag,filename):
        self.filename = filename
        logging.basicConfig(level=logging.INFO,
                            filename=self.filename,
                            datefmt='%Y/%m/%d %H:%M:%S',
                            format='%(asctime)s, %(name)s, %(levelname)s, %(lineno)d  , %(message)s')
        self.logger = logging.getLogger(tag)

    def info(self,msg):
        self.logger.info(msg)

    def warning(self,msg):
        self.logger.warning(msg)

    def error(self,msg):
        self.logger.error(msg)
  
    def debug(self,msg):
        self.debug(msg)
