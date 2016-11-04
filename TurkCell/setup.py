from distutils.core import setup
import py2exe
import os

librariesPath = os.path.join(os.path.dirname(__file__), 'libraries')

Mydata_files = []

for files in os.listdir(librariesPath):
	f1 = librariesPath + '/'+ files
	if os.path.isfile(f1): # skip directories
		f2 = 'libraries', [f1]
		Mydata_files.append(f2)

iconPath = os.path.join(os.path.dirname(__file__), 'images/2gig.ico') 
icon = 'images', [iconPath]
Mydata_files.append(icon)


setup(
	name="2GIG-3GTL-A-GC3",
	version="1.0",
	author="AmericoL",
	console=['IMEI_writer.py'],
	data_files = Mydata_files
	)