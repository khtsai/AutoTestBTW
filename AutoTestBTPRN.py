import difflib, sys, os, tempfile, io, csv;
#codecs
from subprocess import check_output,CalledProcessError
from datetime import datetime
from shutil import copyfile

def logDiff(data):
    try:
        print(logFilePath)
        with open(logFilePath, 'a', encoding='utf-8') as logFile:
            if isinstance(data, str):
                print(data,end='')
                logFile.write(data)
            else:
                for line in data:
                    print(line.encode('utf-8'))
                    logFile.write(line)
    except IOError as e:
        print("I/O error{}: {}".format(e.errno, e.strerror))

def logToCSV(templateFile, testFile, result):
    tempFlag = 0
    if not os.path.exists(csvFilePath):
        tempFlag = 1       
    headers = ["templateFile", "testFile", "result"]
    rows = {"templateFile": os.path.splitdrive(templateFile)[1], "testFile": testFile, "result": result}
    with open(csvFilePath,'a') as csvFile:
        f_csv = csv.DictWriter(csvFile, fieldnames= headers)
        
        if (tempFlag == 1):
            f_csv.writeheader()
            tempFlag ==0
        f_csv.writerow(rows)

def logSysInfo(inputText):
    logDiff("{}{}{}".format('-'*5,inputText,'-'*5+'\n'*2))

def logFormatting(matchType, lineText, resultText):
    resultText = resultText.replace(matchType,"",1)
    temp = "{:<35}{}".format(lineText, resultText)
    return temp

def cmpPRN(templateFilePath, testFilePath, logFilePath):
    #check two .prn files
        try:
            with open(templateFilePath, 'r', encoding='utf-8', errors="replace") as templateFile,\
                 open(testFilePath, 'r', encoding='utf-8', errors="replace") as testFile:
                #diff = difflib.ndiff(templateFile.readlines(),testFile.readlines())
                diff = difflib.ndiff(templateFile.readlines(),testFile.readlines())

                #index, addForMatchLine, addForOldFileLine, addForNewFileLine, checkMismatchORMissing
                misNum,curLineNum,oldLineNum,newLineNum,flag,flagCaret, missBothFlag = 0,0,0,0,0,0,0
                #initial a space for saving each line of the files
                tempList=[]
                
                for line in diff:
                    #match
                    if line.startswith(' '):
                        missBothFlag = 0
                        curLineNum += 1
                        #sys.stdout.write("Old File, line: {}, text: {}"\
                        #                .format(curLineNum+oldLineNum,line))
##                    elif line.startswith('-'):
##                        tempList.append(line)
##                    elif line.startswith('+'):
##                        tempList.append(line)
##                    elif line.startswith('?'):
##                        tempList.append(line)
##                    else:
##                        tempList.append("startswith('else')")
                                        
                    # Mismatch occurs in the old file
                    elif line.startswith('-'):
                        oldLineNum += 1
                        misNum += 1
                        missBothFlag = 0
                        lineText = "{}. At line {} in old file, text: ".format(misNum, curLineNum+oldLineNum)                              
                        tempList.append(logFormatting('-',lineText,line))
                        tempList.append(logFormatting('',"{}. Missing text in new file: ".format(misNum),\
                                                      " {}...\n\n".format("^"*(len(line)-2)))) #-2 is for -/+ with one space
                    # Mismatch occurs in the new file    
                    elif line.startswith('+'):
                        newLineNum += 1
                        misNum +=1
                        missBothFlag = 0
                        lineText = "{}. At line {} in new file, text: ".format(misNum, curLineNum+newLineNum)
                        tempList.append(logFormatting('+',lineText,line))
                        
                        #if flag equals 1, it means mismatching instead of missing text, so no need to add missing text message
                        if flag == 1:
                            flag = 0
                            #-?+? token
                            missBothFlag = 1                            
                            tempList.append("\r\n")
                        else:
                            #tempList.append(logFormatting('+',lineText,line))
                            tempList.append(logFormatting('',"{}. Missing text in old file: ".format(misNum),\
                                                      " {}...\r\n\r\n".format("^"*(len(line)-2))
                                                                          ))                           
                    elif line.startswith('?'):
                        if missBothFlag == 1:
                            tempList.pop()
                            lineText = "{}. Mismatching text: ".format(misNum)
                            tempList.append(logFormatting('?',lineText,line)+"\r\n")
                            missBothFlag = 0
                            
                        # + means there are something more in the new file
                        elif "+" in line:
                            misNum -= 1
                            lineText = "{}. Mismatching text: ".format(misNum)
                            
                            # pop out a reduntent Missing text log in new file
                            tempList.pop()

                            # reduce misNum as + and ?'s misNum were added extra ONE
                            temp = tempList.pop().split('.',1)
                            temp[0] = misNum
                            
                            # pop out a reduntent Missing text log in old fIle
                            tempList.pop()
                            
                            tempList.append(logFormatting('?',lineText,line))
                            tempList.append(".".join([str(x) for x in temp]) + "\n")

                        # - means there are something more in the old file
                        # ^ mismatch b/w the old and new file
                        else:
                                # to avoid logging Missing text in new file as it is mismatching
                                flag = 1
                                # to avoid logging ? with ^ duplicate
                                # the duplicate will occur on the new file
                                    
                                lineText = "{}. Mismatching text: ".format(misNum)
                                
                                # pop out a reduntent Missing text in old fIle
                                tempList.pop()
                                tempList.append(logFormatting('?',lineText,line))
                                
                                # reduce misNum as +'s misNum will be added extra ONE
                                misNum -= 1

##                        elif "-" in line:
##                            if (flagCaret == 0):
##                                # to avoid logging Missing text in new file as it is mismatching
##                                flag = 1
##                                # to avoid logging ? with ^ duplicate
##                                # the duplicate will occur on the new file
##                                if "^" in line:
##                                    flagCaret = 1
##                                    
##                                lineText = "{}. Mismatching text: ".format(misNum)
##                                
##                                # pop out a reduntent Missing text in old fIle
##                                tempList.pop()
##                                tempList.append(logFormatting('?',lineText,line))
##                                
##                                # reduce misNum as +'s misNum will be added extra ONE
##                                misNum -= 1
##                            else:
##                                flagCaret = 0
                        
            if(len(tempList) > 0):
                tempList.append("***Match Failed!!***\r\n\r\n")
                logDiff(tempList)
                #logToCSV(templateFilePath, testFilePath, "Match Failed")
                if (os.path.isfile(testFilePath)):
                    renamedtestFilePath = os.path.join(os.path.dirname(testFilePath),\
                                                           "[ERROR]"+os.path.basename(testFilePath))
                    os.rename(testFilePath, renamedtestFilePath)
            else:
                logDiff("***Match Passed!!***\r\n\r\n")
                #logToCSV(templateFilePath, testFilePath, "Match Passed")
                
        except Exception as e:
                    logSysInfo("Exception error({0}): {1} at cmpPRN".format(e.errno, e.strerror))

def checkDir(templateDirectory, testFileDirectory, tmpPRNDir, logFilePath):
    # Make classification of the folder in tempFolder
    tmpPRNDir = os.path.join(tmpPRNDir,os.path.basename(templateDirectory))
    if not os.path.exists(tmpPRNDir):
        os.makedirs(tmpPRNDir)
        
    try:   
        for file in os.listdir(templateDirectory):
            #LOG the file/folder which is going to be processed.
            print(file.rsplit(".")[0].encode('utf-8'))
            logSysInfo(templateDirectory +"\\"+ file)
            
            # searching .prn file in templateFilePath 
            if file.endswith(".prn"):
                btwPath = os.path.join(templateDirectory,file.rsplit('.')[0]+".btw")

                #searching .btw file
                # if testFileDirectory is null, run bartend.exe to generate testFile for comparing difference.
                if (not os.path.isfile(os.path.join(testFileDirectory,file))):
                    
                    if(os.path.isfile(btwPath)):
                        btwFileName = os.path.basename(btwPath)
                        newPRNFileName = os.path.join(tmpPRNDir,os.path.splitext(btwFileName)[0]+"[TEST].prn")

                        try:
                            #running BT CMD
                            BTCommand = 'bartend.exe /AF=\"' + btwPath + "\"" +\
                                    ' /PRNFILE=\"'+ newPRNFileName +'\" /p /X'
                            check_output(BTCommand, shell=True)
                        except CalledProcessError as e:
                            logSysInfo("BT commands: \"{}\" failed".format(BTCommand))
                        
                        templateFilePath = os.path.join(templateDirectory,file)
                        testFilePath = newPRNFileName
                        cmpPRN(templateFilePath, testFilePath, logFilePath)
                        
                    else:
                        logSysInfo("Error: Cannot find {}".format(btwPath))
                            
                #searching .prn file
                #find existing testFile for comparing difference
                else:
                    testFilePath = os.path.join(testFileDirectory, file)
                    if (os.path.isfile(testFilePath)):
                        # move the testFile to the temparory folder
                        copiedFilePath = os.path.join(tmpPRNDir, file)
                        copyfile(testFilePath, copiedFilePath)
                    
                        templateFilePath = os.path.join(templateDirectory,file)
                        cmpPRN(templateFilePath, copiedFilePath, logFilePath)
                    else:
                        logSysInfo("Error: Cannot find {}".format(testFilePath))

            # searching folders in templateFilePath and testFileDirectory to recursive checkDir method
            elif (os.path.isdir(os.path.join(templateDirectory,file))):
                # child-folder
                subTemplateDirectory = os.path.join(templateDirectory,file)
                if(testFileDirectory != ""):
                    subTestFileDirectory = os.path.join(testFileDirectory, file)
                checkDir(subTemplateDirectory, subTestFileDirectory, tmpPRNDir, logFilePath)
            
    except IOError as e:
        logSysInfo(" I/O error({0}): \"{1}\" {2} at checkDir ".format(e.errno,templateDirectory,e.strerror))
    
    except Exception as e:
        logSysInfo(" Exception error({0}): {1} at checkDir ".format(e.errno, e.strerror))

if getattr(sys, 'frozen', False):
    # frozen
    rootDir = os.path.dirname(sys.executable)
else:
    # unfrozen
    rootDir = os.path.dirname(os.path.realpath(__file__))

#curTime, logFileDir, prePRNPath, newPRNPath
currentTime = datetime.now().strftime("%Y%m%d-%H%M%S")
logFilePath = os.path.join(rootDir,"log-{}.txt".format(currentTime))
csvFilePath = os.path.join(rootDir,"log-{}.csv".format(currentTime))

try:
    with tempfile.TemporaryDirectory(prefix="%tempPRN%",suffix="%tempPRN%",dir=rootDir) as tmpPRNDir:
        logSysInfo("Created temporary directory at {}".format(tmpPRNDir))
        # load from file:
        with open(r'Setting.txt', 'r') as f:
            settingReader = csv.DictReader(f, skipinitialspace=True)
            for row in settingReader:
                #print(row["templateFilePath"],row["testFilePath"])
                checkDir(row["templateFilePath"],row["testFilePath"],tmpPRNDir, logFilePath)
        print()
        key = input("type any key will remove the temporary folder")

except IOError as e:
    logSysInfo(" I/O error({0}): {1} {2} at main ".format(e.errno, rootDir + "Setting.txt", e.strerror))
    
except Exception as e:
    logSysInfo(" Exception error({0}): {1} at main ".format(e.errno, e.strerror))
        
input("Press enter to close program")
