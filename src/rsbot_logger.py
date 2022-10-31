import logging


filename = 'RSBot.log'
logPath = '.'
FORMAT = '%(levelname)s:%(asctime)s:%(module)s:line#%(lineno)s:%(msg)s'


rslog = logging.getLogger(name="rsbot")

logging.basicConfig(level=logging.DEBUG, filename=filename, format=FORMAT)
formatter = logging.Formatter(FORMAT)

fileHandler = logging.FileHandler("{0}/{1}.log".format(logPath, filename))
consoleHandler = logging.StreamHandler()

fileHandler.setFormatter(formatter)
consoleHandler.setFormatter(formatter)

rslog.addHandler(consoleHandler)
rslog.addHandler(fileHandler)

if __name__ == '__main__':
	rslog.debug('Logging something interesting')
