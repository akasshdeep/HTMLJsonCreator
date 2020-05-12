#!/usr/bin/env python3
"""
Author: Akassh Deep

Color coding for flagging exceptions:
Critical : #ADDFFF -> Blue
High : #FF0000 -> Red
Medium : #F9966B -> Orange
Low : #FFFF00 -> Yellow

"""
import os
import sys
import datetime
from zipfile import ZipFile 
import shutil
import glob
from bs4 import BeautifulSoup
import json

cssStatement = '<link rel="stylesheet" type="text/css" href="reportStylesheet.css">'
scriptPath = os.path.dirname(os.path.realpath(__file__))

def getTime(format):
	if(format == "timestamp"):
		return (str(datetime.datetime.timestamp(datetime.datetime.now())).split(".")[0])
	elif(format == "date"):
		return (datetime.datetime.now())


def getZipFile(dir):
	print("Getting ZIP file")
	for file in os.listdir(dir):
		if(file.endswith(".zip")):
			return file


def extractZip(fileName):
	with ZipFile(fileName, 'r') as zip:
		 print('Extracting all the files now...')
		 zip.extractall()



def device_to_chassis_mapping(scriptPath , fileName):
	nodeNames = []
	os.chdir(scriptPath+"/"+fileName+"/Full")
	for d in os.listdir("."):
		if os.path.isdir(d) and d !="summary" and d!="commonImages":
			for file in os.listdir(d):
				if(file.endswith(".html")):
					with open(d+"/"+file , "r") as f:
						fileData = str(f.readlines())
						startInd = fileData.find("Node Name:")
						endInd = fileData.find("</b>", startInd)
						nodeName = (fileData[startInd:endInd]).split(":")[1]
						#print(nodeName)
						startInd2 = fileData.find("Model:")
						endInd2 = fileData.find("</b>", startInd2)
						Model = (fileData[startInd2:endInd2]).split(":")[1]
						#print(Model)
						nodeNames.append({"node name" : nodeName, "Model" : Model})
	return(nodeNames)


def extractTable(file_name):
	data = ""
	with open(file_name , "r") as f:
		data = f.read()
	if(len(data) > 1):
		return(data[data.find('<TABLE') : data.find('</TABLE>') + 8])
	else:
		return data


def createJson(file_name , jsonDir):
        jsonData = {"NMSArea" : "" , "Critical" : 0 , "High" : 0 , "Medium" : 0 , "Low" : 0 , "data" : []}

        #The input to this function is file_name and this is already full path. Can be used directly in code further.
        #Write code here to append the data and update critical, high,medium and low values.
        # Function getColumnNames returns a list of all column names. Takes as input full/path/with/fileName
        # Function getTableData returns only the data rows of table in String format.  Takes as input full/path/with/fileName
        # Use column names (got from getColumnNames) as json keys and cell values in (got from getTableData) as values for the keys and update "Data" field of jsonData variable
        print(file_name)
        column_names, u = getColumnNames(file_name)
        #print(column_names)
        table_data = getTableData(file_name)
        #print(table_data)
        Sev_data = getSevData(file_name)
        #print(Sev_data)
        if len(Sev_data)==0:
                print("No Color Coding found")
        i = 0
        #print(t)
        while i < u :
                table_data.pop(0)
                i = i + 1
        #print(table_data)
        #jjson_data= { "data":[]}
        if len(table_data)== 1:
                jjson ={table_data[0]:""}
                jsonData["data"].append(jjson)
                with open(jsonDir+"/"+getTableName(file_name)[0]+".json" , "w") as jsonFile:
                        jsonFile.write(json.dumps(jsonData))        
        else:
                l=0
                m=0
                n=0
                for z in range(len(table_data)):
                        jjson = {}
                        if len(column_names)== l :
                                l = 0
                                #print("L=" , l)
                        jjson[column_names[l]]= { "value" : table_data[m] , "Sev" : Sev_data[n]}
                        m=m+1
                        l=l+1
                        n=n+1
                        #print(jjson)
                        jsonData["data"].append(jjson)
                        #print(jsonData)

                #with open("adc.json" , "w") as jsonFile:
                    #jsonFile.write(json.dumps(jjson_data))
                #jsonObject=table_data
                #jsonData["data"].append(jsonObject)
                with open(jsonDir+"/"+getTableName(file_name)[0]+".json" , "w") as jsonFile:
                        jsonFile.write(json.dumps(jsonData))



def tableToNMSMapping(file_name):
	html_data = ""
	table_to_NMS_Mapping_json = {}
	with open(file_name , "r") as f:
		html_data = f.read()
	soup = BeautifulSoup(html_data, features="html.parser")
	anchors = soup.find_all("a")
	for anchor in anchors:
		name = anchor.text.strip()
		if(name != ""):
			if("Management" in name):
				key = name
			else:
				if(key in table_to_NMS_Mapping_json.keys()):
					table_to_NMS_Mapping_json[key].append(name)
				else:
					table_to_NMS_Mapping_json[key]= [name]

	return(table_to_NMS_Mapping_json)




def getTableData(file_name):
	html_data = ""
	with open(file_name , "r") as f:
		html_data = f.read()
	soup = BeautifulSoup(html_data , features="html.parser")
	stat_table = soup.find('table')
	#print(stat_table)
	#stat_table=stat_table[0]
	data=[]
	for row in stat_table.find_all('tr'):
		for cell in row.find_all('td'):
			y=cell.text
			data.append(y)
	#print(data)
	return(data)

def getSevData(file_name):
        html_data = ""
        with open(file_name , "r") as f:
                html_data = f.read()
        soup = BeautifulSoup(html_data, features="html.parser")
        stat_table = soup.find('table')
        #stat_table=stat_table[0]
        classes = [value
                   for element in soup.find_all(class_=True)
                   for value in element["class"]]
        #print(classes)
        rtn = []
        for word in classes:
                if word.startswith(("RTN" , "LTN" , "RTY" , "LTY", "RBN", "RBY", "MMN", "RMN")):
                        rtn.append(word)
        #print(rtn)
        for loc, item in enumerate(rtn):
                if item == 'RTN':
                        rtn[loc] = "White"
                elif item == 'LTN':
                        rtn[loc] = "White"
                elif item == 'RTN-ADDFFF':
                        rtn[loc] = "Blue"
                elif item == 'RTN-FF0000':
                        rtn[loc] = "Red"
                elif item == 'RTN-F9966B':
                        rtn[loc] = "Orange"
                elif item == 'RTN-FFFF00':
                        rtn[loc] = "Yellow"
        return(rtn)


def getTableName(file_name):
	html_data = ""
	tableName = []
	with open(file_name , "r") as f:
		html_data = f.read()
	if(len(html_data) > 2):
		soup = BeautifulSoup(html_data, features="html.parser")
		x = soup.find("thead")
		rows = x.findChildren('tr')
		tableName = [x.getText() for x in rows[0].findChildren('td')]

	return(tableName)

def getColumnNames(file_name):
        html_data = ""
        columnNames = []
        with open(file_name , "r") as f:
                html_data = f.read()

        soup = BeautifulSoup(html_data, features="html.parser")
        x = soup.find("thead")
        rows = x.findChildren('tr')
        if len(rows) == 1:
                columnNames = [x.getText().replace("\xa0","") for x in rows[0].findChildren('td')]
                h = len(columnNames) + 1
        elif len(rows) == 2:
                columnNames = [x.getText().replace("\xa0","") for x in rows[1].findChildren('td')]
                h = len(columnNames) + 1
        else:
                d1=[]
                for d1_element in rows[1].find_all('td'):
                        d1_final=d1_element.text
                        d1.append(d1_final)
                d2=[]
                for d2_element in rows[2].find_all('td'):
                        d2_final=d2_element.text
                        d2.append(d2_final)
                d4 = d1 + d2
                h = len(d4) + 1
                colspan_final=[]
                for col_element in rows[1].find_all(colspan=True):
                        for col in col_element["colspan"]:
                                colspan_final.append(col)
                columnNames=[]
                t=0
                for count, span in enumerate(colspan_final):
                        if span == '1':
                                columnNames.append(d1[count])
                                #print(count)
                        elif span == '2':
                                columnNames.append(d2[t])
                                columnNames.append(d2[t+1])
                                t=t+2
                                #print(count)
                        elif span == '3':
                                columnNames.append(d2[t])
                                columnNames.append(d2[t+1])
                                columnNames.append(d2[t+2])
                                t=t+3
                                #print(count)
                        elif span == '4':
                                columnNames.append(d2[t])
                                columnNames.append(d2[t+1])
                                columnNames.append(d2[t+2])
                                columnNames.append(d2[t+3])
                                t=t+4
                                print(count)
                        elif span == '6':
                                columnNames.append(d2[t])
                                columnNames.append(d2[t+1])
                                columnNames.append(d2[t+2])
                                columnNames.append(d2[t+3])
                                columnNames.append(d2[t+4])
                                columnNames.append(d2[t+5])
                                t=t+5
                                #print(count)
                        
        return(columnNames, h)


def getAuditSummary(file_name):
	with open(file_name , "r") as f:
		html_data = f.read()

	soup = BeautifulSoup(html_data, features="html.parser")
	tables = soup.find_all("table")

	for table in tables:
		head = table.find_all("thead")
		for h in head:
			rows = h.findChildren('tr')
			tableName = [x.getText() for x in rows[0].findChildren('td')]
			if(tableName[0] != ""):
				if(len(tableName) == 1):
					with open("summaryTables/"+tableName[0]+".html" , "w") as f:
						f.write(str(table))
				elif("Exception Type" in tableName[0]):
					with open("summaryTables/"+"Overall Exceptions.html" , "w") as f:
						f.write(str(table))

if __name__ == '__main__':
        
        startTime = getTime("date")
        print("Script Initiating at : " , str(datetime.datetime.now()).split(".")[0])
        

        fileName = getZipFile(scriptPath)
        print("Creating ExceptionTables directory. This will store all exception tables only")
        if not os.path.exists("ExceptionTables"):
                os.makedirs("ExceptionTables")
        extractZip(fileName)
        fileName = fileName.split(".")[0]

        #device name and model details
        devToChassisMap = device_to_chassis_mapping(scriptPath, fileName)
        os.chdir(scriptPath+"/ExceptionTables")
        if not os.path.exists("data"):
                os.makedirs("data")
        if not os.path.exists("summaryTables"):
                os.makedirs("summaryTables")    
        with open("data/"+"deviceDetails.json", "w") as f:
                f.write(str(devToChassisMap))


        print("Initiating data extraction from HTML tables")
        for item in os.listdir(scriptPath+"/"+fileName+"/Full/summary"):
                if("Audit_Overview.html" in item):
                        getAuditSummary(scriptPath+"/"+fileName+"/Full/summary/"+item)
                elif("Audit_Summary.html" in item):
                        getAuditSummary(scriptPath+"/"+fileName+"/Full/summary/"+item)
                elif("Detailed_Findings.html" in item):
                        tableToNMSMap = tableToNMSMapping(scriptPath+"/"+fileName+"/Full/summary/"+item)
                        with open("data/"+"tableToNMSMap.json", "w") as f:
                                f.write(json.dumps(tableToNMSMap))
                elif (os.path.isdir(scriptPath+"/"+fileName+"/Full/summary/"+item) and "chart" not in item):
                        for f in os.listdir(scriptPath+"/"+fileName+"/Full/summary/"+item):
                                tableData = extractTable(scriptPath+"/"+fileName+"/Full/summary/"+item+"/"+f)
                                if(len(tableData) > 1):
                                        with open(f,"w") as file:
                                                file.write(tableData)

        print("Creating JSON directory under ExceptionTables. This directory will store HTML table data in JSON format")


        os.chdir(scriptPath+"/ExceptionTables")
        if not os.path.exists("json"):
                os.makedirs("json")
        jsonDir = scriptPath+"/ExceptionTables/json"
        print("Creating JSON ... ")
        
        for f in os.listdir(scriptPath+"/ExceptionTables"):
                if(f.endswith(".html")):
                        createJson(scriptPath+"/ExceptionTables/"+f ,jsonDir)

        for f in os.listdir(scriptPath+"/ExceptionTables"+"/summaryTables"):
                print(scriptPath+"/ExceptionTables"+"/summaryTables"+f)
                if(f.endswith(".html")):
                        createJson(scriptPath+"/ExceptionTables/"+"/summaryTables/"+f ,jsonDir)
                        
        endTime = getTime("date")

        print("Copying CSS file ...")
        shutil.copy2(scriptPath+"/"+fileName+"/Full/commonImages/"+"reportStylesheet.css"  ,scriptPath+"/ExceptionTables/"+"reportStylesheet.css")
        
        #clean up code
        print("Cleaning up ...")
        os.remove(scriptPath+"/AuditReportViewer.htm")
        shutil.rmtree(scriptPath+"/"+fileName)

        print("Time taken for exceution : " , str(endTime - startTime).split(".")[0] )
        

                                
