#!/usr/bin/python

import sys
import os
import subprocess
import argparse
import shutil
import json
import gzip
from airium import Airium

class CUCoverageInformation:

    def __init__(self):

        self.name = None       
        self.linesOfInterest = None # Sve linije iz izvestaja ali ne nuzno sve linije izvornog koda
        self.coveredLines = None
        self.lineHitCount = None        
        self.coveredFunctions = None
        self.functionHitCount = None
    
    def __str__(self):

        CUstr = ""
        CUstr += self.name + "\n"        
        CUstr += "Covered lines: " + str(self.coveredLines) + "\n"
        CUstr += "Function hit count:" + "\n"
        for fName, count in self.functionHitCount.items():
            CUstr += "\t" + fName + "  ----->  " + str(count) + "\n"
        return CUstr


class MiniReport:

    def __init__(self, gcdaCounter, numOfProcessedReports, listOfProcessedFileNames, reports):
        
        # Broj pronadjenih gcda datoteka
        self.gcdaCounter = gcdaCounter

        # Broj obradjenih izvestaja 
        # Ovaj broj je veci od broja gcda datoteka jer jedna gcda datoteka
        # moze imati izvestaje za vise izvornih datoteka
        # odgovara duzini liste self.listOfProcessedFileNames
        self.numOfProcessedReports = numOfProcessedReports

        # Sva moguca imena datoteka na koja se naislo pri parsiranju
        # Mnoga se ponavljaju vise puta 
        # (npr. imena header datoteka ukljucenih u razliciite izvorne datoteka)
        self.listOfProcessedFileNames = listOfProcessedFileNames

        # Broj sacuvanih CUCoverageInformation objekata
        self.numOfSavedCUCovInfoObjects = None

        # Broj datoteka koje pogadja test
        # (jedinstvena imena iz liste self.listOfProcessedFileNames)
        self.numOfUniqueFiles = None

        # Ekstenzije datoteka koje pogadja test
        self.fileExtensions = None

        # Broj datoteka po svakoj ekstenziji
        self.extensionsCounter = None
        
        self.makeReport(reports)

    def makeReport(self, reports):

        self.numOfSavedCUCovInfoObjects = len(reports)
        
        # Koristi se skup da se uklone duplikati
        uniqeFileNames = set(self.listOfProcessedFileNames)
        self.numOfUniqueFiles = len(uniqeFileNames)
        
        # Pomocna funkcija koja vraca ekstenziju imena datoteke
        def toExt(e):
            (root, extension) = os.path.splitext(e)
            return extension

        # Mapiraju se dobijena imena datoteka u ekstenzije
        # Koristi se skup da se ukolne duplikati
        mappedToExt_it = map(lambda e: toExt(e), self.listOfProcessedFileNames)
        mappedToExt = list(mappedToExt_it)        
        self.fileExtensions = set(mappedToExt)

        # Za svkau eksteniziju se pamti koliko datoteka se njome zavrsava
        self.extensionsCounter = {}
        for name in uniqeFileNames:
            extension = toExt(name)            
            if extension in self.extensionsCounter.keys():
                self.extensionsCounter[extension] += 1
            else:
                self.extensionsCounter[extension] = 1
        
        self.printReport()        

    def printReport(self):

        print("=========================== Mini Report ===========================")
        print("Gcda Counter:", self.gcdaCounter)
        print("Number of processed reports:", self.numOfProcessedReports)
        print("Number of saved CUCovInfo objects:", self.numOfSavedCUCovInfoObjects)
        print("Number of unique files affected by test:", self.numOfUniqueFiles)
        print("Extensions of the affected files:", self.fileExtensions)
        print("Extensions counter:")
        for key, value in self.extensionsCounter.items():
            print("\t" + "\"" + key + "\"" + " : " + str(value))
        print("===================================================================")


# Pokrivenost celog projekta JEDNIM testom
class ProjectCodeCoverage:

    ID = 1

    def __init__(self, projectDirectory, test, command, commandArgs, coverageInfoDest, targetSourceFile, objectPath):
        
        self.projectDirectory = os.path.join(projectDirectory, "")
        self.test = test
        self.command = command
        self.commandArgs = commandArgs
        self.coverageInfoDest = os.path.join(coverageInfoDest, "")

        self.targetSourceFile = targetSourceFile
        self.objectPath= objectPath

        self.ID = ProjectCodeCoverage.ID
        ProjectCodeCoverage.ID += 1

        self.testResultsDir = os.path.join(self.coverageInfoDest, "test" + str(self.ID))

        # Moze da se desi da postoje dve gcda datoteke sa istim imenom u razlicitim podirekorijumima
        # Slicno vazi i za gcno. Tada ce i json datoteke sa rezultatima imati isti naziv.
        # Zato se pri formiranju json datoteke dodaje i ovaj brojcani sufiks, da se ne bi rezultati pregazili
        self.numOfSameJsonFileNames = 1

        # Mapa objekata sa informacijama o pokrivenosti za svaku kompilacionu jedinicu
        # Imena datoteka sa izvornim kodom se preslikavaju u reference na CUCoverageInformation objekte 
        self.reports = {}

        # Mali izvestaj o uticaju testa 
        # Videti klasu MiniReport
        self.miniReport = None


    # Pokrece zadati test zadatom komandom
    def runTest(self):
        processsRetVal = subprocess.run([self.command, self.test] + self.commandArgs,
                                        stdout=subprocess.DEVNULL,
                                        stderr=subprocess.DEVNULL
                                       )
        processsRetVal.check_returncode()    
    
    # Vrsi pretragu svih gcda datoteka u direktorijumu projekta nakon pokretanja testa.
    # Za svaku od pronadjenih gcda datoteka pokrece gcov alat, parsira i pamti rezultate
    def searchForGcda(self):
        
        gcdaCounter = 0
        numOfProcessedReports = 0
        listOfProcessedFileNames = []

        for root, dirs, files in os.walk(self.projectDirectory, followlinks=False):            
             
            for file in files:
                
                (fileRoot, fileExt) = os.path.splitext(file)
                
                if fileExt == ".gcda":
                    
                    gcnoAbsPath = os.path.join(root, fileRoot + ".gcno")
                    gcdaAbsPath = os.path.join(root, file)                    

                    self.checkIfGcnoExists(gcnoAbsPath, gcdaAbsPath)                    
                    
                    report = self.runGcov(gcdaAbsPath)

                    (numOfReports, listOfFiles)  = self.parseJsonReport(report)
                    
                    numOfProcessedReports += numOfReports
                    listOfProcessedFileNames += listOfFiles

                    gcdaCounter += 1

        self.miniReport = MiniReport(gcdaCounter, numOfProcessedReports, listOfProcessedFileNames, self.reports.values())


    def parseJsonReport(self, report):    
        
        processedReportsCounter = 0
        processedReportsFileNames = []

        for key in report:
            
            if key == "files":

                files = report[key]
                                
                for fileInfo in files:

                    CUCovInfo = CUCoverageInformation()
        
                    CUCovInfo.linesOfInterest = set()
                    CUCovInfo.coveredLines = set()        
                    CUCovInfo.coveredFunctions = set()
                    CUCovInfo.lineHitCount = {}
                    CUCovInfo.functionHitCount = {}                    

                    sourceFileName = fileInfo["file"]                                    
                    
                    # Pamti se naziv datoteke sa izvornim kodom koja odgovara kompilacionoj jedinici
                    CUCovInfo.name = sourceFileName

                                        
                    # Ako je zadata opcija --source-file preskacu se sve kompilacione  jedinice
                    # cije se ime ne poklapa sa imenom zatadim tom opcijom
                    if self.targetSourceFile != None and self.targetSourceFile != sourceFileName:
                        processedReportsCounter += 1
                        processedReportsFileNames.append(sourceFileName)                        
                        continue
                    
                    if self.targetSourceFile:
                        print("sourceFile", self.targetSourceFile)
                        print("CUCovInfo.name", CUCovInfo.name )


                    # Prolazi se kroz sve linije u izvestaju
                    lines = fileInfo["lines"]
                    for line in lines:
                        
                        # Sve linije koje postoje u izvestaju su linije od interesa.
                        # To nisu nuzno sve linije izvornog koda
                        CUCovInfo.linesOfInterest.add(line["line_number"])

                        # Za svaku liniju od interesa pamti se i koliko je puta izvrsena,
                        # sto moze biti nula ili vise
                        CUCovInfo.lineHitCount[line["line_number"]] = line["count"]

                        # Linija se dodaje u skup pokrivenih linija ako je barem jednom izvrsena
                        if line["count"] != 0:
                            CUCovInfo.coveredLines.add(line["line_number"])
                        
                    # Prolazi se kroz sve funkcije u izvestaju 
                    functions = fileInfo["functions"]
                    for function in functions:
                        
                        # Za svaku funkciju se pamti koliko je puta izvrsena (pozvana)
                        # sto moze biti nula ili vise puta
                        CUCovInfo.functionHitCount[function["name"]] = function["execution_count"]
                        
                        # Funkcija se dodaje u skup pokrivenih funkcija ako je baren jednom izvrsena
                        if function["execution_count"] != 0:
                            CUCovInfo.coveredFunctions.add(function["name"])
        
                    # Pamti se objekat sa informacijama o pokrivenosti koda za tekucu kompilacionu jedinicu                                        
                    self.addReport(CUCovInfo)
                    processedReportsCounter += 1
                    processedReportsFileNames.append(sourceFileName) 

        return processedReportsCounter, processedReportsFileNames

    
    def addReport(self, CUCovInfo):
        
        fileName = CUCovInfo.name

        # Ukoliko vec postoji obejtak sa informacijama o datoteci sa izvornim kodom tada se
        # azuriraju informacije koje on sadrzi
        if fileName in self.reports.keys():
            
            # Dohvat se referenca na postojeci objekat sa informacijala o izvornoj datoteci 
            existingReportRef = self.reports[fileName]

            # Prvai se unija skupa linija od interesa, pokrivenih linija i pokrivenih funkcija
            existingReportRef.linesOfInterest = existingReportRef.linesOfInterest.union(CUCovInfo.linesOfInterest)
            existingReportRef.coveredLines = existingReportRef.coveredLines.union(CUCovInfo.coveredLines)
            existingReportRef.coveredFunctions = existingReportRef.coveredFunctions.union(CUCovInfo.coveredFunctions)

            # Azurira se broj izvrsavanja linija u postojecem objektu
            # Prolazi se kroz mapu koja cuva broj izvrsavanja svake linije u okviru novog objekta
            for lineNum, hitCount in CUCovInfo.lineHitCount.items():
                
                # Proveravase da li ista ta mapa postojeceg objekta vec sadrzi neku vrednost za broj izvrsavanja tekuce linije
                if lineNum in existingReportRef.lineHitCount.keys():
                    
                    # Ako je to slucaj, postojeci broj izvrsavanja linije se uvecava za vrednost iz novog objekta
                    existingReportRef.lineHitCount[lineNum] += hitCount
                
                else:

                    # Ako to nije slucaj, dodaje se novi par (linija, br.izvrsavanja) u pstojeci objekat sa vrednostima iz novog objekta
                    existingReportRef.lineHitCount[lineNum] = hitCount


            # Azurira se broj izvrsavanja funkcija u postojecem objektu
            # Prolazi se kroz mapu koja cuva broj izvrsavanja svake funkcije u okviru novog objekta 
            for fnName, execCount in CUCovInfo.functionHitCount.items():
                
                # Proveravase da li ista ta mapa postojeceg objekta vec sadrzi neku vrednost za broj izvrsavanja tekuce funkcije
                if fnName in existingReportRef.functionHitCount.keys():
                    
                    # Ako je to slucaj, postojeci broj izvrsavanja funkcije se uvecava za vrednost iz novog objekta
                    existingReportRef.functionHitCount[fnName] += execCount
                
                else:
                    
                    # Ako to nije slucaj, dodaje se novi par (funkcija, br.izvrsavanja) u pstojeci objekat sa vrednostima iz novog objekta
                    existingReportRef.functionHitCount[fnName] = execCount

        # Ukoliko ne postoji obejtak sa informacijama o datoteci sa izvornim kodom tada se
        # novi objekat pamti u mapi   
        else:

            self.reports[fileName] = CUCovInfo



    # Pokrece gcov alat 
    def runGcov(self, gcda):                        

        currentWorkDir = os.getcwd()
        os.chdir(self.testResultsDir)  # Kako bi se json fajl generisao u direktorijumu sa rezultatima nakon poziva gcov   
        
        processsRetVal = subprocess.run(["gcov", "--no-output", "--json-format", "--branch-probabilities", gcda],
                                        stdout=subprocess.DEVNULL,
                                        stderr=subprocess.DEVNULL
                                       )

        processsRetVal.check_returncode()

        os.chdir(currentWorkDir)

        name = os.path.basename(gcda)

        # Pravi se ptanja do nastale arhive sa rezultatom nakon poziva gcov alata
        # i putanja do buduce json datoteke u kojoj ce da se zapamti procitan rezultat
        archiveName = os.path.join(self.testResultsDir, name + ".gcov.json.gz")
        jsonReportFileName = os.path.join(self.testResultsDir, name + ".json")
        
        # Ukoliko je vec pronadjena gcda datoteka sa imenom "name"
        # Tada se menja naziv json dodavanjem brojcanog sufiksa datoteke da se ne bi pregazili rezultati 
        if os.path.exists(jsonReportFileName):
            jsonReportFileName = os.path.join(self.testResultsDir, name + str(self.numOfSameJsonFileNames) + ".json")
            self.numOfSameJsonFileNames += 1
        
        # Putanje se prosledjuju metodi readArchiveAndSaveJson() koja vraca ucitani json objekat
        # pa se taj objekat vraca i iz ove metode
        return self.readArchiveAndSaveJson(archiveName, jsonReportFileName)
    
    # Otvara arhivu i cita json izvesraj iz nje,
    # pamti json objekat u datoteci na prosedjenoj putanji i
    # vraca procitani json objekat
    def readArchiveAndSaveJson(self, archiveName, jsonReportFileName):               
        
        if not os.path.exists(archiveName):
            raise Exception("ERROR: archive that contains json report does not exist")

        with gzip.open(archiveName, 'rb') as f:
            report = json.load(f)
        
        os.remove(archiveName)        

        with open(jsonReportFileName, 'w') as f:
            json.dump(report, f, indent=4)

        return report     
        
    # Provera da li postoji gcno datoteka za pronadjenu gcda datoteku
    def checkIfGcnoExists(self, gcnoAbsPath, gcdaAbsPath):
        if not os.path.exists(gcnoAbsPath):
            print(gcnoAbsPath)
            raise Exception("ERROR: gcno file does not exists in project directory (Gcda file found here:  " + gcdaAbsPath + ")")                

    # Pravi se direktorijum u kojem ce da se pamte svi rezultati
    def makeCoverageInfoDestDir(self):
        if not os.path.exists(self.coverageInfoDest):
            try:
                os.mkdir(self.coverageInfoDest)
            except OSError as e:
                print(e) 
    
    # Pravi se folder u koji ce da se sacuvaju gcda, gcno i json datoteke
    def makeTestResultsDir(self):        
        if os.path.isdir(self.testResultsDir):
            raise Exception("ERROR: " + "test" + str(self.ID) + "/" + " directory alredy exists in " + self.coverageInfoDest)
        os.mkdir(self.testResultsDir)

    # Cisti se ceo projekat od prethodnih pokretanja testova
    def clearProjectFromGcda(self):
        for root, dirs, files in os.walk(self.projectDirectory):            
            for file in files:
                (fileRoot, fileExt) = os.path.splitext(file)
                if fileExt == ".gcda":
                    os.remove(os.path.join(root, file))

    # Samo za debagovanje - IZBRISATI
    def countGcda(self):
        counter = 0 
        for root, dirs, files in os.walk(self.projectDirectory):            
            for file in files:
                (fileRoot, fileExt) = os.path.splitext(file)
                if fileExt == ".gcda":
                    counter += 1
        print("Counted gcda:", counter)

    # Samo za debagovanje - IZBRISATI
    def printInfoForFile(self, name):
        for CUReport in self.reports.values():
            if CUReport.name == name:
                print(CUReport)


    # Ulazna metoda.
    # Pokrece ceo proces generisanja izvestaja nad projektom
    def runProjectCodeCoverage(self):
            self.clearProjectFromGcda()
            self.countGcda()
            self.runTest()
            self.countGcda()
            self.makeCoverageInfoDestDir()
            self.makeTestResultsDir()
            self.searchForGcda()
            #self.printInfoForFile("/home/syrmia/Desktop/llvm-project/llvm/tools/opt/NewPMDriver.cpp")


#--------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------

class CodeCoverage:

    ID = 1

    def __init__(self, sourceFile, test, command, commandArgs, coverageInfoDest, objectFileDest):
        self.sourceFile = sourceFile
        self.test = os.path.basename(test)
        self.ID = CodeCoverage.ID
        self.command = command
        self.commandArgs = commandArgs
        self.coverageInfoDest = os.path.join(coverageInfoDest, "")        
        self.objectFileDest = None

        if objectFileDest:
            self.objectFileDest = objectFileDest
            self.objectFileDest = os.path.join(self.objectFileDest, "")

        self.sourceFileNameWithExt = None
        self.sourceFileNameWithNoExt = None
        self.sourceFileRoot = None
        self.sourceFileExt = None

        self.gcnoFileName = None
        self.gcdaFileName = None

        self.report = None
        self.linesOfInterest = None # sve linije iz izvestaja ali ne nuzno sve linije izvornog koda
        self.coveredLines = None
        self.lineHitCount = None        
        self.coveredFunctions = None
        self.functionHitCount = None

        self.parseSourceFileName()

        CodeCoverage.ID = CodeCoverage.ID + 1

    def parseSourceFileName(self):
        if not os.path.exists(self.sourceFile):
            raise Exception("ERROR: source file does not exist")
        self.sourceFileNameWithExt = os.path.basename(self.sourceFile)
        (self.sourceFileRoot, self.sourceFileExt) = os.path.splitext(self.sourceFile)
        self.sourceFileNameWithNoExt = os.path.basename(self.sourceFileRoot)

    def makeCoverageInfoDestDir(self):
        if not os.path.exists(self.coverageInfoDest):
            try:
                os.mkdir(self.coverageInfoDest)
            except OSError as e:
                print(e) 

    def copyGcno(self):
        
        #Dva slucaja za imenovanje gdno datoteka:
        #fileName.cpp.gcno ili filename.gcno
        gcnoFileName_withExt_tmp = self.sourceFileRoot + self.sourceFileExt + '.gcno'
        gcnoFileName_noExt_tmp = self.sourceFileRoot + '.gcno'

        #Ako je objektni fajl generisan na razlicitom mestu u odnosu na izvorni
        #Tada se i .gcno generise na mestu gde je objektni fajl
        if self.objectFileDest:
            gcnoFileName_withExt_tmp = self.objectFileDest + self.sourceFileNameWithExt + '.gcno'
            gcnoFileName_noExt_tmp = self.objectFileDest + self.sourceFileNameWithNoExt + '.gcno'
        
        if os.path.exists(gcnoFileName_withExt_tmp):            
            gcnoFileName_tmp = gcnoFileName_withExt_tmp
        elif os.path.exists(gcnoFileName_noExt_tmp):            
            gcnoFileName_tmp = gcnoFileName_noExt_tmp
        else:
            raise Exception("ERROR: .gcno file does not exist")

        self.makeCoverageInfoDestDir()        
        shutil.copy2(gcnoFileName_tmp, self.coverageInfoDest + self.sourceFileNameWithNoExt + '_test' + str(self.ID) + '.gcno')
        self.gcnoFileName = self.coverageInfoDest + self.sourceFileNameWithNoExt + '_test' + str(self.ID) + '.gcno'

    def moveGcda(self, gcda):
        shutil.move(gcda, self.coverageInfoDest + self.sourceFileNameWithNoExt + '_test' + str(self.ID) + '.gcda')
        self.gcdaFileName = self.coverageInfoDest + self.sourceFileNameWithNoExt + '_test' + str(self.ID) + '.gcda'


    def readArchive(self):
        archiveName = self.coverageInfoDest + self.sourceFileNameWithExt + ".gcov.json.gz"        
        if not os.path.exists(archiveName):
            raise Exception("ERROR: archive that contains json report does not exist")

        with gzip.open(archiveName, 'rb') as f:
            self.report = json.load(f)
        
        os.remove(archiveName)

    def checkIfGcdaIsCreated(self):
        #Dva slucaja za imenovanje gcda datoteka:
        #fileName.cpp.gcda ili filename.gcda
        gcdaFileName_withExt_tmp = self.sourceFileRoot + self.sourceFileExt + '.gcda' 
        gcdaFileName_noExt_tmp = self.sourceFileRoot + '.gcda'

        #Ako je objektni fajl generisan na razlicitom mestu u odnosu na izvorni
        #Tada se i .gcda generise na mestu gde je objektni fajl
        if self.objectFileDest:
            gcdaFileName_withExt_tmp = self.objectFileDest + self.sourceFileNameWithExt + '.gcda' 
            gcdaFileName_noExt_tmp = self.objectFileDest + self.sourceFileNameWithNoExt + '.gcda'
                               
        if os.path.exists(gcdaFileName_withExt_tmp):            
            gcdaFileName_tmp = gcdaFileName_withExt_tmp
        elif os.path.exists(gcdaFileName_noExt_tmp):            
            gcdaFileName_tmp = gcdaFileName_noExt_tmp
        else:
            raise Exception("ERROR: .gcda file does not exist, after running test: " + self.test)

        return gcdaFileName_tmp

    def runTest(self):
                
        processsRetVal = subprocess.run([self.command, self.test] + self.commandArgs)
        
        processsRetVal.check_returncode()

        gcdaFileName = self.checkIfGcdaIsCreated()

        self.moveGcda(gcdaFileName)

    def runGcov(self):        

        currentWorkDir = os.getcwd()
        os.chdir(self.coverageInfoDest)  #kako bi se json fajl generisao u dest_dir nakon poziva gcov      
        
        (root, ext) = os.path.splitext(self.gcdaFileName)
        searchPath = os.path.basename(root)
        processsRetVal = subprocess.run(["gcov", "--no-output", "--json-format", "--branch-probabilities", "--object-file", searchPath, self.sourceFile])        
        
        processsRetVal.check_returncode()

        os.chdir(currentWorkDir)
        
        self.readArchive()
                    
    def saveJsonReport(self):
        jsonReportFileName = self.coverageInfoDest + "report_test" + str(self.ID) + ".json"
        with open(jsonReportFileName, 'w') as f:
            json.dump(self.report, f, indent=4)

    def parseReport(self):
        
        self.coveredLines = set()
        self.coveredFunctions = set()        
        self.linesOfInterest = set()
        self.lineHitCount = {}
        self.functionHitCount = {}

        for key in self.report:

            if key == "files":
            
                files = self.report[key]

                for fileInfo in files:
                    
                    #Ako su gcno/gcda u razilicitom direkt. od izvornog onda ce 
                    #u izvestaju "file" polje biti apsolutna putanja do izvornog fajla
                    #Ako gcno/gcda u istom direktorijumu kao i izvorni fajl onda ce
                    #u izvestaju "file" polje biti samo naziv izvornog fajla sa ekstenzijom
                    sourceFileName = fileInfo["file"]
                    if sourceFileName == self.sourceFile or sourceFileName == self.sourceFileNameWithExt:

                        #print("-------------------------------------->self   " + self.sourceFile)
                        #print("-------------------------------------->report " + sourceFileName)
                                                
                        lines = fileInfo["lines"]
                        for l in lines:
                            if l["count"] != 0:
                                self.coveredLines.add(l["line_number"])
                            
                            self.linesOfInterest.add(l["line_number"])
                            self.lineHitCount[l["line_number"]] = l["count"]
                        
                        functions = fileInfo["functions"]
                        for f in functions:
                            if f["execution_count"] != 0:
                                self.coveredFunctions.add(f["name"])
                            self.functionHitCount[f["name"]] = f["execution_count"]

    def runCodeCoverage(self):
        self.copyGcno()
        self.runTest()
        self.runGcov()
        self.saveJsonReport()
        self.parseReport()

class HtmlReport:
    
    def __init__(self, sourceFile, codeCoverageReports, coverageInfoDest):
        self.sourceFile = sourceFile
        self.codeCoverageReports = codeCoverageReports
        self.coverageInfoDest = os.path.join(coverageInfoDest, "")

    def coveredLinesHtml(self):
        
        a = Airium()
        with open(self.sourceFile, "r") as f:
            
            with a.table():
                
                with a.tr():
                    a.th(_t='Line number')
                    a.th(_t='Line')
                    a.th(_t='Number of hits')
                    a.th(_t='Tests that cover line')

                for count, line in enumerate(f):
                    
                    lineNumber = count + 1
                    testsCoveringLine = [] #zbirna lista testova za jednu liniju

                    lineNumberOfHits = 0
                    isLineOfInterest = False

                    for r in self.codeCoverageReports:
                        if lineNumber in r.coveredLines:
                            testsCoveringLine.append(r.test)
                        if lineNumber in r.linesOfInterest:
                            isLineOfInterest = True
                            lineNumberOfHits = lineNumberOfHits + r.lineHitCount[lineNumber]

                    lineStyleClass = None
                    lineNumberOfHitsTextValue = None


                    if isLineOfInterest:
                        lineNumberOfHitsTextValue = str(lineNumberOfHits)
                        if len(testsCoveringLine) != 0:
                            lineStyleClass = "coveredLine"
                        else:
                            lineStyleClass = "uncoveredLine"
                    else:
                        lineNumberOfHitsTextValue = "----"
                        lineStyleClass = ""

                    
                    with a.tr():
                        a.td(_t=str(lineNumber), klass="lineNumber")
                        a.td(_t=line, klass=lineStyleClass)
                        a.td(_t=lineNumberOfHitsTextValue)
                        with a.td(klass="testName"):
                            for test in testsCoveringLine:                            
                                a.span(_t=test, klass="badge")               
                                                
        
        return str(a)

    def coveredFunctionsHtml(self):
        a = Airium()

        functionHitCount = {}

        for r in self.codeCoverageReports:
            for key, value in r.functionHitCount.items():
                if key in functionHitCount.keys():
                    functionHitCount[key] = functionHitCount[key] + value
                else:
                    functionHitCount[key] = value

        with a.table():
                
            with a.tr():
                a.th(_t='Function name')
                a.th(_t='Number of hits')
            
            for key, value in functionHitCount.items():

                with a.tr():
                    a.td(_t=key, klass="functionName")
                    a.td(_t=str(value), klass="numberOfCalls")                                        

        return str(a)

    # generise diff za dva odabrana izvestaja (proslediti indekse izvestaja)
    def generateCoverageDiffHtml(self, r1_index, r2_index):
        
        r1 = self.codeCoverageReports[r1_index]
        r2 = self.codeCoverageReports[r2_index]

        #linije koje pokriva prvi test a ne pokriva drugi
        r1Diffr2 = r1.coveredLines.difference(r2.coveredLines)
        #linije koje pokriva drugi test a ne pokriva prvi
        r2Diffr1 = r2.coveredLines.difference(r1.coveredLines)
        
        a = Airium()
        
        with a.table():
                
            with a.tr():
                a.th(_t="Line Number")
                with a.th():
                    a.span(_t=r1.test, klass="badge")
                    a.span(_t=" BUT NOT ")
                    a.span(_t=r2.test, klass="badge")
                a.th(_t="Line Number")                
                with a.th():
                    a.span(_t=r2.test, klass="badge")
                    a.span(_t=" BUT NOT ")
                    a.span(_t=r1.test, klass="badge")

            with open(self.sourceFile, "r") as f:
                for count, line in enumerate(f):
                    
                    lineNumber = count + 1
                                        
                    with a.tr():
                        if lineNumber in r1Diffr2:
                            a.td(_t=str(lineNumber), klass="lineNumber")
                            a.td(_t=line, klass="codeLine diffFirst")
                            a.td(_t=str(lineNumber), klass="lineNumber")
                            a.td(_t=line, klass="codeline") 
                        elif lineNumber in r2Diffr1:
                            a.td(_t=str(lineNumber), klass="lineNumber")
                            a.td(_t=line, klass="codeline")
                            a.td(_t=str(lineNumber), klass="lineNumber")
                            a.td(_t=line, klass="codeLine diffSecond")
                        else:
                            a.td(_t=str(lineNumber), klass="lineNumber")
                            a.td(_t=line, klass="codeline")
                            a.td(_t=str(lineNumber), klass="lineNumber")
                            a.td(_t=line, klass="codeline")

        return str(a)
    
    def generateSideBySideCoverageHtml(self, r1_index, r2_index):
        
        r1 = self.codeCoverageReports[r1_index]
        r2 = self.codeCoverageReports[r2_index]

        a = Airium()
        
        with a.table():
                
            with a.tr():
                a.th(_t="Line Number")
                with a.th():
                    a.span(_t=r1.test, klass="badge")
                a.th(_t="Line Number")
                with a.th():
                    a.span(_t=r2.test, klass="badge")

            with open(self.sourceFile, "r") as f:
                for count, line in enumerate(f):

                    lineNumber = count + 1

                    isCoveredByR1 = lineNumber in r1.coveredLines
                    isCoveredByR2 = lineNumber in r2.coveredLines

                    with a.tr():
                        if isCoveredByR1 and isCoveredByR2:
                            a.td(_t=str(lineNumber), klass="lineNumber")
                            a.td(_t=line, klass="codeLine coveredLine")
                            a.td(_t=str(lineNumber), klass="lineNumber")
                            a.td(_t=line, klass="codeLine coveredLine") 
                        elif isCoveredByR1:
                            a.td(_t=str(lineNumber), klass="lineNumber")
                            a.td(_t=line, klass="codeLine coveredLine")
                            a.td(_t=str(lineNumber), klass="lineNumber")
                            a.td(_t=line, klass="codeLine") 
                        elif isCoveredByR2:
                            a.td(_t=str(lineNumber), klass="lineNumber")
                            a.td(_t=line, klass="codeLine")
                            a.td(_t=str(lineNumber), klass="lineNumber")
                            a.td(_t=line, klass="codeLine coveredLine") 
                        else:
                            a.td(_t=str(lineNumber), klass="lineNumber")
                            a.td(_t=line, klass="codeLine")
                            a.td(_t=str(lineNumber), klass="lineNumber")
                            a.td(_t=line, klass="codeLine")
        
        return str(a)

    
    def makeHtmlReportDir(self):
        path = os.path.join(self.coverageInfoDest, 'html')
        if os.path.isdir(path):
            raise Exception("ERROR: html/ directory alredy exists in " + self.coverageInfoDest)
        os.mkdir(path)
        stylePath = os.path.join(path, 'Style')
        os.mkdir(stylePath)

    def copyStyleSheet(self):
        styleSheetPath = os.path.dirname(os.path.abspath(__file__)) + '/Style/style.css'
        shutil.copy2(styleSheetPath, self.coverageInfoDest + "html/Style/style.css")

    def generateHtml(self):
        
        self.makeHtmlReportDir()
        self.copyStyleSheet()

        a = Airium()

        #JS kod za reagovanje na klik dugmeta: collapse elementi
        script = """
        var coll = document.getElementsByClassName("collapsible");
        var i;
        
        for (i = 0; i < coll.length; i++) {
        coll[i].addEventListener("click", function() {
            this.classList.toggle("active");
            var content = this.nextElementSibling;
            if (content.style.display === "block") {
            content.style.display = "none";
            } else {
            content.style.display = "block";
            }
        });
        }
        """

        a('<!DOCTYPE html>')
        with a.html():
            with a.head():
                a.meta(charset="utf-8")
                a.title(_t="Code Coverage")
                a.link(rel="stylesheet", href="Style/style.css")

            with a.body():                

                with a.div(klass="header"):
                    with a.h1():
                        a("Code Coverage")
                    with a.p():
                        a("Source file: " + self.sourceFile) 
                
                a.button(_t="Open Summary Report", klass="collapsible", type="button")
                with a.div(klass="content", style="display: none;"):
                    a.hr()
                    a.h3(_t="Summary Report", klass="subheader")
                    a(self.coveredLinesHtml())

                a.button(_t="Open Functions Report", klass="collapsible", type="button")
                with a.div(klass="content", style="display: none;"):
                    a.hr()
                    a.h3(_t="Functions Report", klass="subheader")
                    a(self.coveredFunctionsHtml())

                a.button(_t="Open Coverage Diff", klass="collapsible", type="button")
                with a.div(klass="content", style="display: none;"):
                    a.hr()
                    a.h3(_t="Coverage Diff", klass="subheader")
                    a(self.generateCoverageDiffHtml(0,1))

                a.button(_t="Open Side By Side Comparison", klass="collapsible", type="button")
                with a.div(klass="content", style="display: none;"):
                    a.hr()
                    a.h3(_t="Side By Side Comparison", klass="subheader")
                    a(self.generateSideBySideCoverageHtml(0,1))                            
                
                a.script(_t=script)

        pageStr = str(a)     
        
        htmlFileName = self.coverageInfoDest + 'html/' + 'CodeCoverage.html'
        with open(htmlFileName, "w") as f:
            f.write(pageStr)


def parse_program_args(parser):

    #group = parser.add_mutually_exclusive_group(required=True)

    parser.add_argument('directory_path', metavar='directory_path', action="store",
                    help="directory to search for all files affected by the test")

    parser.add_argument('--source-file', metavar='source_file', action="store",
                        help='the path to the source file of intrest')

    parser.add_argument('--object-path',  metavar='object_path', action="store",
                        help="if source file is specified and object file is on other place than source file")

    parser.add_argument('test1', metavar='test1', action="store",
                        help='the first test to be run (ll file)')
    parser.add_argument('test2', metavar='test2', action="store",
                        help='the second test to be run (ll file)')
    parser.add_argument('coverage_dest', metavar='coverage_dest', action="store",
                        help='directory for storing code coverage information')
    parser.add_argument('command', metavar='command', action="store",
                        help='command to run the tests')
    parser.add_argument('command_arg', metavar='command_arg', action="store", nargs='*',
                        help='command arguments must be specified in the form -<option>')
                        
    return parser.parse_args()

def Main():
    
    parser = argparse.ArgumentParser(description='Run tests and generate code coverage diff.')
    args = parse_program_args(parser)
    
    #print(args)
    #exit()

    for i in range(0,len(args.command_arg)):
        if not args.command_arg[i].startswith("-") and args.command_arg[i-1] != '-o':
            args.command_arg[i] = "-" + args.command_arg[i]

    # if args.source_file:

    #     test1 = CodeCoverage(args.source_file, args.test1, args.command, args.command_arg, args.coverage_dest, args.object_path)    
    #     test2 = CodeCoverage(args.source_file, args.test2, args.command, args.command_arg, args.coverage_dest, args.object_path)
        
    #     try:
    #         test1.runCodeCoverage()
    #     except Exception as e:
    #         print(e)
    #         exit()

    #     try:
    #         test2.runCodeCoverage()
    #     except Exception as e:
    #         print(e)
    #         exit()
        
    #     print("\n\n================== Report ========================")
    #     print("Lines covered with test1 but not test2:")
    #     print(test1.coveredLines.difference(test2.coveredLines))
    #     print("Lines covered with test2 but not test1:")
    #     print(test2.coveredLines.difference(test1.coveredLines))
    #     print("Lines covered with both tests:")
    #     print(test1.coveredLines.intersection(test2.coveredLines))
    #     print("==================================================")

    #     htmlReport = HtmlReport(args.source_file, [test1, test2], args.coverage_dest)
    #     htmlReport.generateHtml()
    
    if args.directory_path:

        projectCC = ProjectCodeCoverage(args.directory_path, args.test1, args.command, args.command_arg, args.coverage_dest, args.source_file, args.object_path)
        
        try:
            projectCC.runProjectCodeCoverage()
        except Exception as e:
            print(e)
            exit()
    
if __name__ == "__main__":
  Main()