import ftplib
server = ftplib.FTP()
server.connect('127.0.0.1', 21)
server.login('XcenaX','Dagad582')
server.dir()