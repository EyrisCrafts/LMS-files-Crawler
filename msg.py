from os import path
from os import makedirs
import scrapy
import re

usr=""
passwd=""
usmanID="295"
usmanurl='http://10.0.0.157/message/index.php?id=295'
message="This too."
class lms(scrapy.Spider):
	name="lms"
	start_urls=['http://10.0.0.157/login/index.php']

	def cString(self,s):
		return ((s.strip()).replace('/','')).replace(' ','_')
	def properExt(self,s):
		return val[s]

	def parse(self,response):
		self.logger.info('Initiating login request.')
		yield scrapy.FormRequest.from_response(
			response,
			formxpath='//form[@id="login"]',
			formdata={
				'username':usr,
				'password':passwd,
			},
			callback=self.after_login
			)
	def after_login(self,response):
		self.logger.info('Login successful.')
		yield scrapy.Request(usmanurl,callback=self.sendMessage)
	def sendMessage(self,response):
		self.logger.info('Now printing response')
		m=re.search('"sesskey":"\w{10}"',response.text)
		key=(m.group(0)).split(':')[1]
		key=key[1:len(key)-1]
		self.logger.info(key)
		yield scrapy.FormRequest.from_response(
		response,
		formxpath='//form[@id="mform2"]',
		formdata={
			'id':'295',
			'viewing':'unread',
			'sesskey':key,
			'_qf__send_form':'1',
			'message':message,
			'submitbutton':'Send\+message',
		},
		callback=self.messageSent
		)
	def messageSent(self,response):
		self.logger.info('Message sent')
		
	
