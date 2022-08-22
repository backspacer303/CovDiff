#!/usr/bin/python

from logging import root
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
        self.report = None        
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

# Pokrivenost celog projekta JEDNIM testom
class ProjectCodeCoverage:

    ID = 1

    def __init__(self, projectDirectory, test, command, commandArgs, coverageInfoDest):
        
        self.projectDirectory = os.path.join(projectDirectory, "")
        self.test = test
        self.command = command
        self.commandArgs = commandArgs
        self.coverageInfoDest = os.path.join(coverageInfoDest, "")
    
        self.ID = ProjectCodeCoverage.ID
        ProjectCodeCoverage.ID += 1

        self.testResultsDir = os.path.join(self.coverageInfoDest, "test" + str(self.ID))

        # Moze da se desi da postoje dve gcda datoteke sa istim imenom u razlicitim podirekorijumima
        # Slicno vazi i za gcno
        # Zato se pri kopiranju/pomeranj gcno/gcda dodaje i ovaj brojcani sufiks
        self.numOfSameGcdaFileNames = 1 
        self.numOfSameGcnoFileNames = 1

        # Moguce ekstenzije za naziv datoteke sa izvornim kodom jedne kompilacione jedinice
        # Videti funkciju parseJsonReport()
        self.sourceFilesPossibleExtensions = [".cpp", ".c", ".cc"]

        # Lista objekata sa informacijama o pokrivenosti za svaku kompilacionu jedinicu
        self.reports = []

    # Pokrece zadati test zadatom komandom
    def runTest(self):
        processsRetVal = subprocess.run([self.command, self.test] + self.commandArgs)
        processsRetVal.check_returncode()
    
    # Vrsi pretragu svih gcda datoteka u direktorijumu projekta nakon pokretanja testa.
    # Svaku od pronadjenih kopira u direktorijum sa rezultatima zajedno sa odgovarajucom gcno datotekom,
    # pokrece gcov alat, parsira i pamti rezultate
    def searchForGcda(self):
        
        counter = 0

        for root, dirs, files in os.walk(self.projectDirectory, followlinks=False):            
             
            for file in files:
                
                (fileRoot, fileExt) = os.path.splitext(file)
                
                if fileExt == ".gcda":
                    
                    gcnoAbsPath = os.path.join(root, fileRoot + ".gcno")
                    gcdaAbsPath = os.path.join(root, file)                    

                    self.checkIfGcnoExists(gcnoAbsPath, gcdaAbsPath)
                    self.copyGcno(gcnoAbsPath)
                    gcda = self.moveGcda(gcdaAbsPath) #vraca apsolutnu putanju do gcda datoteke, pomerene u dir. sa rezultatima
                    
                    report = self.runGcov(gcda)

                    self.parseJsonReport(report)

                    counter += 1

        print(counter)    
        

    def parseJsonReport(self, report):
        
        CUCovInfo = CUCoverageInformation()
        
        CUCovInfo.linesOfInterest = set()
        CUCovInfo.coveredLines = set()        
        CUCovInfo.coveredFunctions = set()
        CUCovInfo.lineHitCount = {}
        CUCovInfo.functionHitCount = {}

        CUCovInfo.report = report

        for key in report:
            
            if key == "files":

                files = report[key]

                for fileInfo in files:

                    sourceFileName = fileInfo["file"]

                    # U izvestaju postoji samo jedan objekat koji se odnosi na kompilacionu jedinicu,
                    # njegovo polje "file" sadrzi naziv (tj putanju do) datoteke sa izvornim kodom.  
                    # Svi ostali objekti se odnose na heder datoteke koje su ukljucene u izvornu datoteku.
                    # Ime datoteke sa izvornim kodom se prepoznaje po eksteniziji: ".c", ".cpp" ili ".cc"
                    
                    (root, ext) = os.path.splitext(sourceFileName)

                    if ext in self.sourceFilesPossibleExtensions:
                        
                        # Pamti se naziv datoteke sa izvornim kodom koja odgovara kompilacionoj jedinici
                        CUCovInfo.name = sourceFileName

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
        self.reports.append(CUCovInfo)                    

    # Pokrece gcov alat 
    def runGcov(self, gcda):
        
        name = os.path.basename(gcda)        

        currentWorkDir = os.getcwd()
        os.chdir(self.testResultsDir)  # Kako bi se json fajl generisao u direktorijumu sa rezultatima nakon poziva gcov   
        
        processsRetVal = subprocess.run(["gcov", "--no-output", "--json-format", "--branch-probabilities", name],
                                        stdout=subprocess.DEVNULL,
                                        stderr=subprocess.DEVNULL
                                       )

        processsRetVal.check_returncode()

        os.chdir(currentWorkDir)

        # Pravi se ptanja do nastale arhive sa rezultatom nakon poziva gcov alata
        # i putanja do buduce json datoteke u kojoj ce da se zapamti procitan rezultat
        archiveName = os.path.join(self.testResultsDir, name + ".gcov.json.gz")
        jsonReportFileName = os.path.join(self.testResultsDir, name + ".json")
        
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
               
    
    # Pomera se gcda datoteku u direktorijum sa rezultatima.
    # Vrsi se pomeranje kako datoteka ne bi zaostala u projektu i uticala na pokretanje narednih testova
    def moveGcda(self, gcdaAbsPath):

        base = os.path.basename(gcdaAbsPath)
        (root, ext) = os.path.splitext(base)

        destination = os.path.join(self.testResultsDir, root + "_test" + str(self.ID) + ext) 

        # Moze da se desi da dve gcda datoteke imaju isto ime a razlicit root pa i da u direktorijumu sa
        # rezultatima vec postoji datoteka pod "destination" imenom.
        # U tom slucaju dodaje se jos jedan brojcani sufiks 
        if os.path.exists(destination):
            destination = os.path.join(self.testResultsDir, root + "_" + str(self.numOfSameGcdaFileNames) +
                                                 "_test" + str(self.ID) + ext)
            self.numOfSameGcdaFileNames += 1 

        shutil.move(gcdaAbsPath, destination)

        # Vraca se nova gcda datoteka kako bi se dalje u programu prosledila gcov alatu
        return destination

    # Kopiramo gcno datoteku u direktorijum sa rezultatima
    def copyGcno(self, gcnoAbsPath):

        base = os.path.basename(gcnoAbsPath)
        (root, ext) = os.path.splitext(base)

        destination = os.path.join(self.testResultsDir, root + "_test" + str(self.ID) + ext)

        # Moze da se desi da dve gcno datoteke imaju isto ime a razlicit root pa i da u direktorijumu sa
        # rezultatima vec postoji datoteka pod "destination" imenom.
        # U tom slucaju dodaje se jos jedan brojcani sufiks 
        if os.path.exists(destination):
            destination = os.path.join(self.testResultsDir, root + "_" + str(self.numOfSameGcnoFileNames) + 
                                            "_test" + str(self.ID) + ext)
            self.numOfSameGcnoFileNames += 1

        shutil.copy2(gcnoAbsPath, destination)
        
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
        for CUReport in self.reports:
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
            self.printInfoForFile("/home/syrmia/Desktop/llvm-project/llvm/tools/opt/NewPMDriver.cpp")


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

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument('--source-file', metavar='source_file', action="store",
                        help='the path to the source file to be tested')

    group.add_argument('--directory-path', metavar='directory_path', action="store",
                        help="directory to search for all files affected by the test")

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

    if args.source_file:

        test1 = CodeCoverage(args.source_file, args.test1, args.command, args.command_arg, args.coverage_dest, args.object_path)    
        test2 = CodeCoverage(args.source_file, args.test2, args.command, args.command_arg, args.coverage_dest, args.object_path)
        
        try:
            test1.runCodeCoverage()
        except Exception as e:
            print(e)
            exit()

        try:
            test2.runCodeCoverage()
        except Exception as e:
            print(e)
            exit()
        
        print("\n\n================== Report ========================")
        print("Lines covered with test1 but not test2:")
        print(test1.coveredLines.difference(test2.coveredLines))
        print("Lines covered with test2 but not test1:")
        print(test2.coveredLines.difference(test1.coveredLines))
        print("Lines covered with both tests:")
        print(test1.coveredLines.intersection(test2.coveredLines))
        print("==================================================")

        htmlReport = HtmlReport(args.source_file, [test1, test2], args.coverage_dest)
        htmlReport.generateHtml()
    
    if args.directory_path:

        projectCC = ProjectCodeCoverage(args.directory_path, args.test1, args.command, args.command_arg, args.coverage_dest)
        
        try:
            projectCC.runProjectCodeCoverage()
        except Exception as e:
            print(e)
            exit()
    
if __name__ == "__main__":
  Main()