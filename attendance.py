from os import path
from os import makedirs
import scrapy
import re

usr=""
passwd=""
courseUrl="http://10.0.0.157/course/view.php?id=248"
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
		yield scrapy.Request(courseUrl,callback=self.coursePage)
	def coursePage(self,response):
		self.logger.info('Inside course Page')
		attendance_page = response.css('a[href*="attendance"][class=""]::attr(href)').extract()
		yield scrapy.Request(attendance_page[0],callback=self.find_attendance)
	def find_attendance(self,response):
		self.logger.info('Taking attendance')
		attendances = response.css('a[href*=attendance\/attendance]::attr(href)').extract()
		
		yield scrapy.Request(attendances[0],callback=self.take_attendance)
	def take_attendance(self,response):
		self.logger.info("Got here!!!!!")
		
		m=re.search('sesskey=\w{10}',response.url)
		sesskey=(m.group(0)).split('=')[1]
		
		m=re.search('sessid=\w{4}',response.url)
		sessid=(m.group(0)).split('=')[1]
		self.logger.info(sessid)
		self.logger.info(sesskey)
		
		yield scrapy.FormRequest.from_response(
		response,
		formxpath='//form[@id="mform1"]',
		formdata={
			'sessid':sessid,
			'sesskey':sesskey,
			'sesskey':sesskey,
			'_qf__mod_attendance_student_attendance_form':'1',
			'mform_isexpanded_id_session':'1',
			'status':'785',
			'submitbutton':'Save\+changes',
		}
		)
		
	
