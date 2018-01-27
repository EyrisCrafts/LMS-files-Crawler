# LMS-files-Crawler
Python Scrapy Project to download all files of every course and organize them in folders.

##How to Run
scrapy runspider lms.py

## Requirements
You need Scrapy module for python. 

pip install scrapy

### Notes
This project is for python 2.7

## Possible problems for windows users

Missing win32api module

pip install pypiwin32

If  the problem persists, copy pywintypes27.dll and pythoncom27.dll to c:\Python27\Lib\site-packages\win32
