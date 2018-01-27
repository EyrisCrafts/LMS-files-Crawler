from os import path
from os import makedirs
import scrapy

subjects=[]
subjects_link=[]
val={
	'mpeg':'filter',
	'unknown':'unknown',
	'pdf':'pdf',
	'powerpoint':'pptx',
	'text':'txt',
	'spreadsheet':'csv',
	'archive':'zip',
	'document':'docx'
}
class lms(scrapy.Spider):
	name="lms"
	start_urls=['http://10.0.0.157/login/index.php']

	def cString(self,s):
		return ((s.strip()).replace('/','')).replace(' ','_')
	def properExt(self,s):
		return val[s]

	def parse(self,response):
		yield scrapy.FormRequest.from_response(
			response,
			formxpath='//form[@id="login"]',
			formdata={
				'username':'',
				'password':'',
			},
			callback=self.after_login
			)
	def after_login(self,response):
		yield scrapy.Request('http://10.0.0.157/my/index.php?mynumber=-2',callback=self.findSubjects)

	def findSubjects(self,response):
		self.logger.info('Looking for Subjects...')
		subjects=response.css('li p a[href*="course/view"]::text').extract()
		self.logger.info("Found subjects ")
		self.logger.info(subjects)
		subjects_link=response.css('li p a[href*="course/view"]::attr(href)').extract()	
		#clean
		for index in range(len(subjects)):
			subjects[index]=self.cString(subjects[index])
		#Make Folders
		for subject in subjects:
			if not path.exists(subject):
				makedirs(subject)

		#User input for update of Subject choice
		print ("Please Enter the subject you would like to update.")
		for i in range(len(subjects)):
			print (str(i)+". "+subjects[i])
		print ("-1. Update all.")
		choiceID = int(input())
		if choiceID is not -1:
			subjects = [x for x in subjects if x is subjects[choiceID]]
			subjects_link = [x for x in subjects_link if x is subjects_link[choiceID]]
		
		
		subjects.reverse()
		for link in subjects_link:
			yield scrapy.Request(url=link,callback=self.subject_page,meta={'SubjectName':subjects.pop()})

	def subject_page(self,response):
		self.logger.info("Looking for documents in %s",response.meta['SubjectName'])
		
		docLinks=response.css('a[href*="resource"][class=""]::attr(href)').extract()
		docNames=[]
		docExtensions=[]
		for link in docLinks:
			docNames.append(response.css('div a[href="'+link+'"][class=""] span.instancename::text').extract_first())
			
		for index in range(len(docNames)):
			docNames[index] = self.cString(docNames[index])
		for link in docLinks:
			docExtensions.append(response.css('div a[href="'+link+'"][class=""] img::attr(src)').extract_first())

		for index in range(len(docExtensions)):	
			docExtensions[index] = self.properExt((docExtensions[index].split('/')[-1]).split('-')[0])
		

		
		self.logger.info("The number of documents found Before filter...")
		self.logger.info(len(docNames))
		self.logger.info(len(docExtensions))
		self.logger.info(len(docLinks))
		
#		Filter unwanted
		while 'filter' in docExtensions:
			i=docExtensions.index('filter')
			docNames.remove(docNames[i])
			docLinks.remove(docLinks[i])
			docExtensions.remove('filter')
		
		self.logger.info("The number of documents found...")
		self.logger.info(len(docNames))
		self.logger.info(len(docExtensions))
		self.logger.info(len(docLinks))
		
		
		for index in range(len(docNames)):
			doc=docNames[index]
			ext=docExtensions[index]
			link=docLinks[index]
			
			self.logger.info("Document found "+doc+"."+ext+"  "+link)
	
			if path.isfile("./"+response.meta['SubjectName']+"/"+doc+"."+ext) and ext != 'unknown':
				self.logger.info('%s File already exists',doc+"."+ext)
			else:
				self.logger.info("Downloading %s",doc+"."+ext)
				yield scrapy.Request(
					url=link,
					callback=self.save_pdf,
					meta={'path':"./"+response.meta['SubjectName']+"/"+doc+"."+ext}
				)
		
	def save_pdf(self,response):
		if "view.php" in response.url:
			yield scrapy.Request(
				url=response.css('frame[src*="pluginfile"]::attr(src)').extract_first(),
				callback=self.save_pdf,
				meta=response.meta
			)
		else:
			path=response.meta['path']
			if (path.split('.')[-1] == 'unknown'):
				path = "."+''.join(path.split('.')[:-1])+"." + response.url.split('.')[-1]
			self.logger.info('Saving File %s',path)
			with open(path,'wb') as f:
				f.write(response.body)
