# Copyright (C) 2020 Manuel Saldivar / manuelsaldivar@outlook.com.ar, Lucas Aimaretto / laimaretto@gmail.com
#
# This is logAnalyzer
#
# logAnalyzer is free software: you can redistribute it and/or modify
# it under the terms of the 3-clause BSD License.
#
# logAnalyzer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY of any kind whatsoever.
#

import textfsm
import pandas as pd
import csv
import xlsxwriter
import glob
import argparse
import yaml
from sys import platform as _platform
import json
import re
from ttp import ttp

def readTemplate(fileTemplate, templateFolder, templateEngine):
	
	# Read the list of templates passed by CSV of textFSM and return template read list (read)
	# list of parsed variable names, list of template names 
	# If fileTemplate is omitted, then all the templates inside the folder are considered.
	
	if fileTemplate != '':
		with open(fileTemplate,'r') as f:
			templates = [x.replace('\n','') for x in f.readlines()]
	else:
		templates = [f.replace(templateFolder,'') for f in glob.glob(templateFolder + '*') if 'majorFile.yml' not in f]

	d = {}

	for i,tmpltName in enumerate(templates):

		d[tmpltName] = {
			'listOfcolumns':[],
			'commandKey':'',
		}	

		fName = templateFolder+tmpltName

		with open(fName) as f:
			tmpltLines = f.readlines()

		for line in tmpltLines:

			if templateEngine == 'textFSM':

				h1 = line.find('Value')
				h2 = line.find('#Command:')
				
				if h1 != -1:
					col = line.split(' ')[-2]
					#listOfcolumns[i].append(col)
					d[tmpltName]['listOfcolumns'].append(col)
				
				if h2 != -1:
					cmd = line.split(': ')[1].strip('\n')
					#commandKey[i].append(cmd)
					d[tmpltName]['commandKey'] = cmd

			if templateEngine == 'ttp':

				h1 = line.find('Columns: ')
				h2 = line.find('Command: ')
				
				if h1 != -1:
					col = line.split(': ')[1].strip('\n').split(",")
					#listOfcolumns[i].append(col)
					d[tmpltName]['listOfcolumns'] = col
				
				if h2 != -1:
					cmd = line.split(': ')[1].strip('\n')
					#commandKey[i].append(cmd)
					d[tmpltName]['commandKey'] = cmd				

	print('#####Successfully Loaded Templates#####')
	return d 

def makeParsed(nomTemplate, routerLog, templateFolder, templateEngine, columnss):
	"""
	Parse through textFSM (reading the file again)

	Args:
		nomTemplate (string): name of file containgin the textFSM template
		routerLog (string):   logs of router
		tmpltFolder

	Returns:
		list with results
	"""

	if templateEngine == 'textFSM':

		template         = open(templateFolder + nomTemplate)
		results_template = textfsm.TextFSM(template)
		parsed_results   = results_template.ParseText (routerLog)

		# With list of results, we build a Pandas DataFrame
		parsed_results = pd.DataFrame(parsed_results, columns= columnss)

	if templateEngine == 'ttp':

		with open(templateFolder + nomTemplate) as f:
			template = f.read()

		parser = ttp(data=routerLog, template=template)
		parser.parse()

		output = parser.result(format='table')
		parsed_results = output[0][1][0]

		parsed_results = pd.DataFrame(parsed_results, columns= columnss)

	return parsed_results

def readLog(logFolder, formatJson):
	"""
	Reads logs, and stores router logs in memory for processing

	Args:
		logFolder (string):  name of folder
		formatJson (string): "yes" or "no"
	"""

	if formatJson == 'yes':

		ending = '*rx.json'

	else:

		ending = '*rx.txt'

	if _platform == "linux" or _platform == "linux2" or _platform == "darwin":
    	# linux

		listContent  = [f for f in glob.glob(logFolder  + ending)]

	elif _platform == "win64" or _platform == "win32":
    	# Windows 64-bit

		listContent  = [f.replace("\\", '/') for f in glob.glob(logFolder  + ending)]
	else:
		print(str(_platform) + ": not a valid platform. Quitting....")
		quit()

	d = {}

	if formatJson == 'yes':

		for name in listContent:
			with open(name) as f:
				d[name] = json.load(f)

	else:
	
		for name in listContent:
			with open(name) as f:
				d[name] = f.read()

	print('#########Logs Loaded Successfully#########')

	return d

def verifyMajorFile(majorFile):
	"""We verify the majorFile.yml before moving on.
	Returns:
		[dict]: [Dictionary with words of major information, for templates if have any words additional to down]
	"""

	try:
		with open(majorFile,'r') as f:
			majorMatrix = yaml.load(f, Loader=yaml.FullLoader)
	except:
		print("Missing " + majorFile + " file. Quitting..")
		quit()

	return majorMatrix

def parseResults(dTmpl, dLog, templateFolder, templateEngine):
	"""
	Build the Dataframe from textFSM filter, index and router log

	Args:
		dTmpl (dict):        dictionary with info from templates.
		dLog (dict):         dicitonary with logs. Each key is the fileName; the value, is the content of the log.
		templateFolder (str):   folder of templates

	Returns:
		_type_: _description_
	"""

	datosEquipo  = {}

	for tmpltName in dTmpl.keys():

		columnss    = dTmpl[tmpltName]['listOfcolumns']
		commandKey  = dTmpl[tmpltName]['commandKey']
		dfTemp      = pd.DataFrame(columns=columnss)

		for routerLogKey in dLog.keys():

			routerLogFname  = routerLogKey.split("/")[-1]
			fileType        = routerLogFname.split('.')[1]

			print(routerLogFname , tmpltName)

			if fileType == 'json': 
				# If text format is json, else, we continue work with rx_txt

				routerName = dLog[routerLogKey]['name']

				# logs es cada comando que se ejecuto en el router, dentro del json file.
				for cmdsLogs in dLog[routerLogKey].keys():

					# prog es el nombre del comando en cada template file
					prog = re.compile(commandKey)

					# searchKey es el regex match entre logs y prog
					match = prog.search(cmdsLogs)

					if match: 
						#if command(in template) == command(in key of router) then we stores log info in routeLog variable
						# significa que el comando se ejecutó en el router y existe un template
						# para ese comando.

						# {
						# 	'logs1':'output1',
						# 	'logs2':'output2',
						# 	'logsN':'outputN',
						# }

						# "/show router 4001 route-table | match No": "No. of Routes: 566",
						# "/show router 4002 route-table | match No": "MINOR: CLI Invalid router \"4002\".\u0007",
						# "/show router route-table | match No": "No. of Routes: 3337",						

						routerLog = cmdsLogs + '\n' + dLog[routerLogKey][cmdsLogs] + '\n'

						# We parse results from the key:value association
						# A list is returnd with results
						dfResult = makeParsed(tmpltName, routerLog, templateFolder, templateEngine, columnss)

						dfResult['NAME'] = routerName

						dfTemp = pd.concat([dfTemp, dfResult])

			else:
				# if here, we analyze plain text Files
				pass
				# routerName = routers[i1][0].replace('_rx.txt','')
				# routerLog  = content[i1]

				# # "/show router 4001 route-table | match No": "No. of Routes: 566",
				# # "/show router 4002 route-table | match No": "MINOR: CLI Invalid router \"4002\".\u0007",
				# # "/show router route-table | match No": "No. of Routes: 3337",	

				# parsed_results = makeParsed(nomTemplate, routerLog)

				# if len(parsed_results) == 0:
				# 	# if the parse is empty, we save the name of the routers
				# 	parsed_results = [routerName]
				# 	for empty in range(len(columnss)-1):
				# 		parsed_results.append('NOT VALUE')

				# 	parsed_results = [parsed_results]
				# 	dfResult = pd.DataFrame(parsed_results, columns= columnss)
				# else:
				# 	dfResult = pd.DataFrame(parsed_results, columns= columnss)
				# 	dfResult['NAME'] = routerName

				# dfTemp = pd.concat([dfTemp, dfResult])

		# It is stored in the dataEquipment dictionary with the key nomTemplate
		# the DF with the data of all routers
		datosEquipo[tmpltName] = dfTemp

		# I added this here because it was already done in main ().
		# It is cleaner like this ...
		datosEquipo[tmpltName].reset_index(level=0, inplace=True)
		datosEquipo[tmpltName] = datosEquipo[tmpltName].drop(columns='index')		

	return datosEquipo

def searchDiff(datosEquipoPre, datosEquipoPost):#Makes a new table, in which it brings the differences between two tables (post-pre)

	countDif = {}	

	for key in datosEquipoPre.keys():

		dfUnion = pd.merge(datosEquipoPre[key], datosEquipoPost[key], how='outer', indicator='Where').drop_duplicates()
		dfInter = dfUnion[dfUnion.Where=='both']
		dfCompl = dfUnion[~(dfUnion.isin(dfInter))].dropna(axis=0, how='all').drop_duplicates()
		dfCompl['Where'] = dfCompl['Where'].str.replace('left_only','Pre')
		dfCompl['Where'] = dfCompl['Where'].str.replace('right_only','Post')

		countDif[key] = dfCompl.sort_values(by=['NAME'])

	return countDif

def findMajor(count_dif, templateFolder):
	#Makes a table from the results of searching for Major errors in the post table define in yml file for specific template, or down if is not define the words for the template, which are not in the Pre table

	countDown  = {}
	majorWords = verifyMajorFile(templateFolder + 'majorFile.yml')

	for key in count_dif.keys():
		if key in majorWords:
			majorWords[key].append('down')
			df         = pd.DataFrame()
			for j in majorWords[key]:
				df1 = count_dif[key][count_dif[key]['Where']=='Post']
				if len(df1) > 0:
					df1 = df1[df1.apply(lambda r: r.str.contains(j, case=False).any(), axis=1)]

				else:
					df1 = pd.DataFrame(columns=count_dif[key].columns)

				df=pd.concat([df, df1])

			countDown[key] = df

		else:
			df = count_dif[key][count_dif[key]['Where']=='Post']
			if len(df) > 0:
				df = df[df.apply(lambda r: r.str.contains('down', case=False).any(), axis=1)]
			else:
				df = pd.DataFrame(columns=count_dif[key].columns)

			countDown[key] = df

	return countDown

def makeTable(datosEquipoPre, datosEquipoPost):#Sort the table pre and post to present in Excel

	df_all          = {}
	datosEquipoPre1 = datosEquipoPre.copy()
	
	for temp in datosEquipoPre.keys():

		datosEquipoPre1[temp]['##']='##'

		df_all[temp] = pd.concat([datosEquipoPre1[temp], datosEquipoPost[temp]], axis=1, keys=('Pre-Check', 'Post-Check'))

	return df_all

def constructExcel(df_final, count_dif, searchMajor, folderLog):#Sort the data and format creating the Excel
	"""_summary_

	Args:
		df_final (pandas): DataFrame with pre and post data
		count_dif (pandas): DataFrame with only differences
		searchMajor (pandas): DataFrame with only errors
		folderLog (string): name of the folder
	"""

	fileName  = folderLog[:-1] + ".xlsx"

	writer    = pd.ExcelWriter(fileName, engine='xlsxwriter') #creates instance of an excel workbook
	workbook  = writer.book

	print('Saving Excel')
	
	# Create index tab
	indexSheet = workbook.add_worksheet('index')

	for idx,template in enumerate(df_final.keys()):

		dfData  = df_final[template]
		dfDiff  = count_dif[template]
		dfMajor = searchMajor[template]

		sheet_name = template.replace('nokia_sros_','')
		sheet_name = sheet_name.replace('.template','')
		sheet_name = sheet_name.replace('_template','')
		sheet_name = sheet_name.replace('.ttp','')
		sheet_name = sheet_name.replace('.','_')

		if len(sheet_name) > 31:
			sheet_name = sheet_name[:31]

		# Selecting Tab's color and error messages
		if len(dfData) == 0:
			output = 'blue'
		elif len(dfMajor) == 0 and len(dfDiff) == 0:
			output = 'green'
		elif len(dfMajor) == 0 and len(dfDiff) != 0:
			output = 'yellow'
		elif len(dfMajor) != 0:
			output = 'orange'

		d = dict(
			blue = dict(
				colorTab = 'blue',
				warnText = '####### NO Parsing Detected ###############',
				errText  = '####### NO Parsing Detected ###############',
				shortText = 'no parsing',
				),		
			green = dict(
				colorTab = 'green',
				warnText = '####### NO POST-TASK CHANGES DETECTED #####',
				errText  = '####### NO MAJOR ERRORS FOUND #############',
				shortText = 'ok',
				),
			yellow = dict(
				colorTab = 'yellow',
				warnText = '####### CHANGES DETECTED ##################',
				errText  = '####### NO MAJOR ERRORS FOUND #############',
				shortText = 'warning',
				),
			orange = dict(
				colorTab = 'orange',
				warnText = '####### CHANGES DETECTED ##################',
				errText  = '####### MAJOR ERRORS DETECTED POST-TASK ###',
				shortText = 'error',
			)
		)

		# cell format
		cell_format  = workbook.add_format({'color': 'red', 'font_size': 14, 'fg_color': d[output]['colorTab'], 'align': 'center', 'border': 1 })

		# Building index
		srcCol   = 'A'+str(idx+1)
		indexSheet.write_url(srcCol, 'internal:'+sheet_name+'!A1', string=sheet_name)
		indexSheet.write(idx,1, d[output]['shortText'], cell_format)

		# Creating Tab
		worksheet = workbook.add_worksheet(sheet_name)
		worksheet.set_tab_color(d[output]['colorTab'])
		writer.sheets[sheet_name] = worksheet
		dfData.to_excel(writer, sheet_name=sheet_name, startrow=0, startcol=0) #creates Excel File
		worksheet.write_url('A1', 'internal:index!A1', string='Index')
		
		### Changes Section
		srcCol   = 'A'+str(len(dfData)+5)
		dstCol   = 'H'+str(len(dfData)+5)
		colRange = srcCol + ':' + dstCol
		warnTex  = d[output]['warnText']
		worksheet.merge_range(colRange, warnTex, cell_format)
		if len(dfDiff) > 0:
			dfDiff.to_excel(writer, sheet_name=sheet_name, startrow=len(dfData)+6, startcol=0)

		### Major Error Section
		srcCol   = 'A'+str((len(dfData)+(len(dfDiff)))+9)
		dstCol   = 'H'+str((len(dfData)+(len(dfDiff)))+9)
		colRange = srcCol + ':' + dstCol
		errText   = warnTex  = d[output]['errText']
		worksheet.merge_range(colRange, errText, cell_format)
		if len(dfMajor) > 0:
			dfMajor.to_excel(writer, sheet_name=sheet_name, startrow=(len(dfData)+(len(dfDiff)))+10, startcol=0)
		
		print('#')
	
	writer.save() #saves workbook to file in python file directory

def main():

	parser1 = argparse.ArgumentParser(description='Log Analysis', prog='PROG', usage='%(prog)s [options]')
	parser1.add_argument('-pre', '--preFolder',     type=str, required=True, help='Folder with PRE Logs. Must end in "/"',)
	parser1.add_argument('-post','--postFolder' ,   type=str, default='',    help='Folder with POST Logs. Must end in "/"',)
	parser1.add_argument('-csv', '--csvTemplate',   type=str, default='', help='CSV with list of templates names to be used in parsing. If the file is omitted, then all the templates inside --templateFolder, will be considered for parsing. Default=None.')
	parser1.add_argument('-json', '--formatJson',   type=str, default = 'yes', choices=['yes','no'], help='logs in json format: yes or no.')
	parser1.add_argument('-tf', '--templateFolder', type=str, default='TemplatesTextFSM/', help='Folder where templates reside. Default=TemplatesTextFSM/')
	parser1.add_argument('-te', '--templateEngine', choices=['ttp','textFSM'], default='textFSM', type=str, help='Engine for parsing.')
	parser1.add_argument('-v'  ,'--version',        help='Version', action='version', version='Saldivar/Aimaretto - (c)2022 - Version: 3.1.1' )

	args           = parser1.parse_args()
	preFolder      = args.preFolder
	postFolder     = args.postFolder
	csvTemplate    = args.csvTemplate
	formatJson     = args.formatJson
	templateFolder = args.templateFolder
	templateEngine = args.templateEngine

	if _platform == "win64" or _platform == "win32":
		templateFolder = templateFolder.replace('/', '\\')

	dTmplt = readTemplate(csvTemplate, templateFolder, templateEngine)

	if preFolder != '' and postFolder == '':
		
		dLog = readLog(preFolder, formatJson)

		df_final    = parseResults(dTmplt, dLog, templateFolder, templateEngine)
		count_dif   = {}
		searchMajor = {}

		for key in df_final.keys():
			count_dif[key]   = pd.DataFrame(columns=df_final[key].columns)
			searchMajor[key] = pd.DataFrame(columns=df_final[key].columns)

		constructExcel(df_final, count_dif, searchMajor, preFolder)

	elif preFolder != '' and postFolder != '':

		dLogPre  = readLog(preFolder, formatJson)
		dLogPost = readLog(postFolder, formatJson)
			
		datosEquipoPre  = parseResults(dTmplt, dLogPre, templateFolder, templateEngine)
		datosEquipoPost = parseResults(dTmplt, dLogPost, templateFolder, templateEngine)

		count_dif       = searchDiff(datosEquipoPre, datosEquipoPost)
		searchMajor     = findMajor(count_dif, templateFolder)
		df_final        = makeTable(datosEquipoPre, datosEquipoPost)

		constructExcel(df_final, count_dif, searchMajor, postFolder)

	elif preFolder == '':
		print('Incorrect Folder, Please Verify')

main()
