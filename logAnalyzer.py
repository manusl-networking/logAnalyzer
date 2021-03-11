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

def readTemplate(fileTemplate):  
	
	# Read the list of templates passed by CSV of textFSM and return template read list (read)
	# list of parsed variable names, list of template names 
	
	with open(fileTemplate,'r') as fTemplate:
		reader 	  = csv.reader(fTemplate)
		templates = list(reader)
	
	cantTemplate     = len(templates)
	results_template = []
	template         = []
	var              = []
	index            = []
	for t in range(cantTemplate):
		template.append(open('Templates/'+templates[t][0]))
		print(template[t])
		var.append(template[t].readlines())
		r1   = len(var[t])
		var1 = []
		index.append([])
		for i1 in range(r1):
			h1 = var[t][i1].find('Value')
			if h1 != -1:
				var1 = var[t][i1].split(' ')
				index[t].append(var1[-2])
	print('#####Successfully Loaded Templates#####')
	return template, index, templates

def makeParsed(nomTemplate, routerLog): #Parse through textFSM (reading the file again)

	template         = open('Templates/'+nomTemplate)
	results_template = textfsm.TextFSM(template)
	parsed_results   = results_template.ParseText (routerLog)
	return parsed_results

def readLog(logFolder): #Reads CSV, and stores router logs in memory for processing

	listContent  = [f for f in glob.glob(logFolder  + '*rx.txt')]

	routers     = [[f.split("/")[1]] for f in listContent]

	content        = []
	
	for f in listContent:
		fopen = open(f,'r')
		content.append(fopen.read())
		fopen.close()

	print('#########Logs Loaded Successfully#########')

	return content, routers

def parseResults(read_template, index, content, templates, routers): #Build the Dataframe from textFSM filter, index and router log

	datosEquipo  = {}
	cantTemplate = len(templates)
	cantRouters  = len(content)

	for i in range(cantTemplate):
		nomTemplate = templates[i][0]
		columnss    = index[i]
		dfTemp      = pd.DataFrame(columns=columnss)
		
		for i1 in range(cantRouters):

			print(routers[i1][0] , nomTemplate)

			routerLog      = content[i1]
			parsed_results = makeParsed(nomTemplate, routerLog)
			

			if len(parsed_results) == 0:
				# if the parse is empty, we save the name of the routers
				parsed_results = [routers[i1][0]]
				for empty in range(len(columnss)-1):
					parsed_results.append('NOT VALUE')

				parsed_results=[parsed_results]
	
				dfResult = pd.DataFrame(parsed_results, columns= columnss)
			else:
				dfResult = pd.DataFrame(parsed_results, columns= columnss)
			
			dfTemp = pd.concat([dfTemp, dfResult])

		# It is stored in the dataEquipment dictionary with the key nomTemplate
		# the DF with the data of all routers

		datosEquipo[nomTemplate] = dfTemp

		# I added this here because it was already done in main ().
		# It is cleaner like this ...
		datosEquipo[nomTemplate].reset_index(level=0, inplace=True)
		datosEquipo[nomTemplate] = datosEquipo[nomTemplate].drop(columns='index')		

	return datosEquipo

def searchDiff(datosEquipoPre, datosEquipoPost):#Makes a new table, in which it brings the differences between two tables (post-pre)

	countDif        = {}	

	for key in datosEquipoPre.keys():

		dfUnion = pd.merge(datosEquipoPre[key], datosEquipoPost[key], how='outer', indicator='Where').drop_duplicates()
		dfInter = dfUnion[dfUnion.Where=='both']
		dfCompl = dfUnion[~(dfUnion.isin(dfInter))].dropna(axis=0, how='all').drop_duplicates()
		dfCompl['Where'] = dfCompl['Where'].str.replace('left_only','before')
		dfCompl['Where'] = dfCompl['Where'].str.replace('right_only','after')

		countDif[key] = dfCompl.sort_values(by=['NAME'])


	return countDif

def findDown(count_dif):#Makes a table from the results of searching for 'Down' in the post table, which are not in the Pre table

	countDown = {}

	for key in count_dif.keys():

		df = count_dif[key][count_dif[key]['Where']=='after']
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

		df_all[temp] = pd.concat([datosEquipoPre1[temp], datosEquipoPost[temp]], axis=1, keys=('Before the Task', 'After the task'))

	return df_all

def constructExcel(df_final, count_dif, searchDown, folderLog):#Sort the data and format creating the Excel

	fileName  = folderLog[:-1] + ".xlsx"

	writer    = pd.ExcelWriter(fileName, engine='xlsxwriter') #creates instance of an excel workbook
	workbook  = writer.book
	namesheet = []

	print('Saving Excel')
	
	for temp in df_final.keys():

		sheet_name = temp.replace('nokia_sros_show_','').replace('.template','')

		if len(sheet_name) > 31:
			sheet_name = sheet_name[:31]

		if len(searchDown[temp]) == 0 and len(count_dif[temp]) == 0:
			colorTab = 'green'
		elif len(searchDown[temp]) == 0 and len(count_dif[temp]) != 0:
			colorTab = 'yellow'
		elif len(searchDown[temp]) != 0:
			colorTab = 'orange'

		worksheet = workbook.add_worksheet(sheet_name)
		worksheet.set_tab_color(colorTab)
		writer.sheets[sheet_name] = worksheet

		cell_format = workbook.add_format({'color': 'red', 'font_size': 14, 'fg_color': 'yellow', 'align': 'center', 'border': 1 })
		
		df_final[temp].to_excel(writer, sheet_name=sheet_name, startrow=0, startcol=0) #creates workbook

		worksheet.merge_range('A'+str(len(df_final[temp])+5)+':'+'H'+str(len(df_final[temp])+5), '#############  CHANGES DETECTED #############', cell_format)
		worksheet.merge_range('A'+str((len(df_final[temp])+(len(count_dif[temp])))+9)+':'+'H'+str((len(df_final[temp])+(len(count_dif[temp])))+9), '#############  DOWN STATES DETECTED POST-TASK #############', cell_format)
		
		if len(count_dif[temp]) == 0:
			worksheet.merge_range('A'+str(len(df_final[temp])+5)+':'+'H'+str(len(df_final[temp])+6), '#############  NO POST-TASK CHANGES DETECTED #############', cell_format)
		else:
			count_dif[temp].to_excel(writer, sheet_name=sheet_name, startrow=len(df_final[temp])+6, startcol=0)
			
		if len(searchDown[temp]) == 0:
			worksheet.merge_range('A'+str((len(df_final[temp])+(len(count_dif[temp])))+10)+':'+'H'+str((len(df_final[temp])+(len(count_dif[temp])))+9), '#############  NO STATES FOUND DOWN #############', cell_format)
		else:
			searchDown[temp].to_excel(writer, sheet_name=sheet_name, startrow=(len(df_final[temp])+(len(count_dif[temp])))+10, startcol=0)
		print('#')
	
	writer.save() #saves workbook to file in python file directory

def main():

	parser1 = argparse.ArgumentParser(description='Log Analysis', prog='PROG', usage='%(prog)s [options]')
	parser1.add_argument('-pre', '--preFolder',   type=str, required=True, help='Folder with PRE Logs. Must end in "/"',)
	parser1.add_argument('-post','--postFolder' , type=str, default='',    help='Folder with POST Logs. Must end in "/"',)
	parser1.add_argument('-csv', '--csvTemplate', type=str, required=True, help='CSV con with templates to use in parsing.')

	args        = parser1.parse_args()
	preFolder   = args.preFolder
	postFolder  = args.postFolder
	csvTemplate = args.csvTemplate


	results_template, index, templates = readTemplate(csvTemplate)

	if preFolder != '' and postFolder == '':

		contentPre, routers = readLog(preFolder)
		df_final            = parseResults(results_template, index, contentPre,  templates, routers)
		count_dif = {}
		searchDown= {}
		for key in df_final.keys():
			count_dif[key]      = pd.DataFrame(columns=df_final[key].columns)
			searchDown[key]     = pd.DataFrame(columns=df_final[key].columns)
		constructExcel(df_final, count_dif, searchDown, preFolder)

	elif preFolder != '' and postFolder != '':
            
		contentPre, routersPre   = readLog(preFolder)
		contentPost, routersPost = readLog(postFolder)

		if routersPre != routersPost:
			print("There is not the same amount of logs in PRE vs POST. Check. Exit")
			quit()
			
		datosEquipoPre  = parseResults(results_template, index, contentPre,  templates, routersPre)
		datosEquipoPost = parseResults(results_template, index, contentPost, templates, routersPost)
		count_dif       = searchDiff(datosEquipoPre, datosEquipoPost)
		searchDown      = findDown(count_dif)
		df_final        = makeTable(datosEquipoPre, datosEquipoPost)
		constructExcel(df_final, count_dif, searchDown, postFolder)

	elif preFolder == '':
		print('Incorrect Folder, Please Verify')

main()
