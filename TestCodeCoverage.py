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

    def __init__(self, gcdaCounter, numOfProcessedReports, listOfProcessedFileNames, reports, ifObjectPath):
        
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

        # Ukoliko je na ulazu zadata opcija --object-path ne moze se znati
        # tacan broj fajlova koje test pokriva jer je obradjena samo jedna
        # gcda datoteka. Ekvivalentno, u listi self.listOfProcessedFileNames
        # se tada nalaze samo imena izvornih datoteka iz jedne gcda datoteke
        # ifObjectPath je indikator za --object-path
        self.ifObjectPath = ifObjectPath

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

        # U slucaju zadate opcije --object-path ne moze se govoriti o 
        # broju jedinstvenih datoteka koje test pokriva
        if self.ifObjectPath:
            self.numOfUniqueFiles = None
        
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

    def __init__(self, projectDirectory, test, command, commandArgs, coverageInfoDest, targetSourceFile, targetObjectPath):
        
        self.projectDirectory = os.path.join(projectDirectory, "")
        self.test = test
        self.command = command
        self.commandArgs = commandArgs
        self.coverageInfoDest = os.path.join(coverageInfoDest, "")

        self.targetSourceFile = targetSourceFile
        self.targetObjectPath = targetObjectPath

        self.ID = ProjectCodeCoverage.ID
        ProjectCodeCoverage.ID += 1

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

        # Ukoliko su na ulazu zatade obe opcije --source-file i --object-path
        # ne vrsi se pretraga celog direktorijuma projekta vec se gcda datoteka
        # trazi direkno na zadatoj --object-path putanji
        if self.targetSourceFile and self.targetObjectPath:
            
            sourceFileBasename = os.path.basename(self.targetSourceFile)
            (sourceFileRoot, _) = os.path.splitext(sourceFileBasename)


            # Ime gcda datoteke moze biti zadato na jedan od sledeca dva nacina:
            # <sourceFileName>.gcda
            # ili
            # <sourceFileName>.<sourceFileExt>.gcda
            # Proveravaju se oba slucaja a ako gcda datoteka nije pronadjena ni u jednom
            # prijavljuje se greska
            gcdaBaseName = sourceFileRoot + ".gcda"
            gcdaAbsPath = os.path.join(self.targetObjectPath, gcdaBaseName)
        
            if not os.path.exists(gcdaAbsPath):

                gcdaBaseName = sourceFileBasename + ".gcda"
                gcdaAbsPath = os.path.join(self.targetObjectPath, gcdaBaseName)

                if not os.path.exists(gcdaAbsPath):

                    raise Exception("ERROR: No gcda file found at specified object path which corresponds to the source file")
            
            # Formira se putanja do gcno datoteke
            (gcdaRoot, _) = os.path.splitext(gcdaAbsPath)
            gcnoAbsPath = gcdaRoot + ".gcno"

            # Proverava se da li gcno datoteka postoji
            self.checkIfGcnoExists(gcnoAbsPath, gcdaAbsPath)

            # Pokrece se gcov alat
            report = self.runGcov(gcdaAbsPath)

            # Parsira se dobijeni izvestaj
            (numOfReports, listOfFiles)  = self.parseJsonReport(report)

            numOfProcessedReports += numOfReports
            listOfProcessedFileNames += listOfFiles

            gcdaCounter += 1

            # # Formira se mali izvestaj 
            self.miniReport = MiniReport(gcdaCounter, numOfProcessedReports, listOfProcessedFileNames, 
                                         self.reports.values(), self.targetObjectPath != None
                                        )
        
        # Ukoliko nije zadata --object-path opcija na ulazu,
        # vrsi se pretraga celog direktorijuma projekta kako bi se pronasle
        # gcda datoteke
        else:

            for root, dirs, files in os.walk(self.projectDirectory, followlinks=False):            
                
                for file in files:
                    
                    (fileRoot, fileExt) = os.path.splitext(file)
                    
                    if fileExt == ".gcda":
                        
                        # Formiraju se putanje do gcda i gcno datoteka
                        gcnoAbsPath = os.path.join(root, fileRoot + ".gcno")
                        gcdaAbsPath = os.path.join(root, file)                    

                        # Proverava se da li gcno datoteka postoji
                        self.checkIfGcnoExists(gcnoAbsPath, gcdaAbsPath)                    
                        
                        # Pokrece se gcov alat
                        report = self.runGcov(gcdaAbsPath)

                        # Parsira se dobijeni izvestaj
                        (numOfReports, listOfFiles)  = self.parseJsonReport(report)
                        
                        numOfProcessedReports += numOfReports
                        listOfProcessedFileNames += listOfFiles

                        gcdaCounter += 1
            
            # Formira se mali izvestaj
            self.miniReport = MiniReport(gcdaCounter, numOfProcessedReports, listOfProcessedFileNames, 
                                         self.reports.values(), self.targetObjectPath != None
                                        )


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
        os.chdir(self.coverageInfoDest)  # Kako bi se json fajl generisao u direktorijumu sa rezultatima nakon poziva gcov   
        
        processsRetVal = subprocess.run(["gcov", "--no-output", "--json-format", "--branch-probabilities", gcda],
                                        stdout=subprocess.DEVNULL,
                                        stderr=subprocess.DEVNULL
                                       )

        processsRetVal.check_returncode()

        os.chdir(currentWorkDir)

        name = os.path.basename(gcda)

        # Pravi se ptanja do nastale arhive sa rezultatom nakon poziva gcov alata
        # i putanja do buduce json datoteke u kojoj ce da se zapamti procitan rezultat
        archiveName = os.path.join(self.coverageInfoDest, name + ".gcov.json.gz")
        
        # Putanje se prosledjuju metodi readArchiveAndSaveJson() koja vraca ucitani json objekat
        # pa se taj objekat vraca i iz ove metode
        return self.readArchiveAndSaveJson(archiveName)
    
    # Otvara arhivu i cita json izvesraj iz nje,
    # pamti json objekat u datoteci na prosedjenoj putanji i
    # vraca procitani json objekat
    def readArchiveAndSaveJson(self, archiveName):               
        
        if not os.path.exists(archiveName):
            raise Exception("ERROR: archive that contains json report does not exist")

        with gzip.open(archiveName, 'rb') as f:
            report = json.load(f)
        
        os.remove(archiveName)        

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
            self.searchForGcda()
            #self.printInfoForFile("/home/syrmia/Desktop/llvm-project/llvm/tools/opt/NewPMDriver.cpp")


class HtmlReport:

    def __init__(self, buildCoverage1, buildCoverage2, coverageInfoDest):
        
        self.buildCoverage1 = buildCoverage1
        self.buildCoverage2 = buildCoverage2
        self.coverageInfoDest = coverageInfoDest

        self.reports_1 = self.buildCoverage1.reports
        self.reports_2 = self.buildCoverage2.reports

        self.script = """
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

    def generateHomePage(self):

        a = Airium()

        a('<!DOCTYPE html>')
        with a.html():
            with a.head():
                a.meta(charset="utf-8")
                a.title(_t="Code Coverage")
                a.link(rel="stylesheet", href="Style/style.css")
            
            with a.body():                
                
                # Naslov
                with a.div(klass="headerDiv"):
                    with a.h1():
                        a("Build Code Coverage")
                
                # MiniReport izvestaji
                with a.div(klass="parent"):

                    with a.div(klass="float-child"):
                        a(self.generateMiniReport(self.buildCoverage1.miniReport, self.buildCoverage1.test))

                    with a.div(klass="float-child"):
                        a(self.generateMiniReport(self.buildCoverage2.miniReport, self.buildCoverage2.test))
                
                # Tabela u padajucem elementu sa svim pokrivenih datotekama 
                a.button(_t="Open All Compilation Unit Code Coverage", klass="collapsible", type="button")
                with a.div(klass="content", style="display: none;"):
                    a.hr()
                    a.h3(_t="All Compilation Unit Code Coverage", klass="subheader")
                    a(self.generateAllCUList())


                a.script(_t=self.script)



        pageStr = str(a)             

        htmlFileName = os.path.join(self.coverageInfoDest, 'html/' + 'CodeCoverage.html')
        with open(htmlFileName, "w") as f:
            f.write(pageStr)


    def generateAllCUList(self):
        a = Airium()

        # Generise se tabela sa informacijama za sve kompilacione jedinice
        with a.table(klass="mainTable"):
            
            # Gnerise se zaglavlje tabele
            with a.tr(klass="mainTr"):
                
                a.th(_t="Source file apbsolute path", klass="mainTh")
                
                with a.th(klass="mainTh"):
                    a.span(_t=self.buildCoverage1.test, klass="badge")
                
                with a.th(klass="mainTh"):
                    a.span(_t=self.buildCoverage2.test, klass="badge")

            # Pravi se unija CU koje su pokrivene i jednim i drugim testom
            # To ce biti unija kljuceva recnika 
            sourceFileUnion = set(self.reports_1.keys()).union(set(self.reports_2.keys()))
            print(len(sourceFileUnion))

            for file in sourceFileUnion:
                
                # Ispisujemo svaku CU kao link na koje ce kasnije moci da se klikne
                # cime se otvara stranica sa detaljnijim izvestajem za tu CU
                with a.tr(klass="mainTr"):
                    with a.td():
                        a.a(_t=file, href="", target="_blank")

                    # Za tekucu CU racunamo koji procenat njenih linija je pokriven prvim testom
                    # a koji procenat je pokriven drugim testom
                    test1_percentageCoverage = 0
                    test2_percentageCoverage = 0
                    

                    #BUG moze da se desi da su obe liste pokrivenih linija i linija od interesa prazne
                    # # Bice da gcov generise prazne izvestaje za neke fajlove - PROVERITI                    
                    if file in self.reports_1.keys():
                        if len(self.reports_1[file].linesOfInterest) != 0:
                            test1_percentageCoverage = 100.0 * len(self.reports_1[file].coveredLines) / len(self.reports_1[file].linesOfInterest)


                    if file in self.reports_2.keys():
                        if len(self.reports_2[file].linesOfInterest) != 0:
                            test2_percentageCoverage = 100.0 * len(self.reports_2[file].coveredLines) / len(self.reports_2[file].linesOfInterest)

                    a.td(_t=str(test1_percentageCoverage))
                    a.td(_t=str(test2_percentageCoverage))

        return str(a)
    
            
    def generateMiniReport(self, miniReport, testName):
        a = Airium()

        with a.div(klass="miniheader"):

            with a.h3(style="text-align: center;"):
                a("Mini Report")
            with a.h5(klass="badge"):
                a(testName)


            # Formira se po jedan element u listi za svaku stavku iz MiniRport klase
            with a.ul(): 
                
                with a.li(style="padding-top: 10px"):
                    a("Gcda Counter: " + str(miniReport.gcdaCounter))

                with a.li(style="padding-top: 10px"):
                    a("Number of processed reports: " + str(miniReport.numOfProcessedReports))
                
                with a.li(style="padding-top: 10px"):
                    a("Number of saved CUCovInfo objects: " + str(miniReport.numOfSavedCUCovInfoObjects))
                
                with a.li(style="padding-top: 10px"):
                    if miniReport.numOfUniqueFiles == None:
                        a("Number of unique files affected by test: Unknown")
                    else:
                        a("Number of unique files affected by test: " + str(miniReport.numOfUniqueFiles))
                
                with a.li(style="padding-top: 10px"):                    
                    a("Extensions of the affected files: " + str(miniReport.fileExtensions))
                
                with a.li(style="padding-top: 10px"):
                    a("Extensions counter")
                    with a.table(style="padding-top: 5px;"):
                        for key in sorted(miniReport.extensionsCounter.keys()):                            
                                with a.tr(klass="extensionTableTr"):
                                    a.td(_t=str(key))
                                    a.td(_t=str(miniReport.extensionsCounter[key]))
        return str(a)



    # Pravi direktorijum u kome c da se cuvaju html stranice
    def makeHtmlReportDir(self):
        path = os.path.join(self.coverageInfoDest, 'html')
        if os.path.isdir(path):
            raise Exception("ERROR: html/ directory alredy exists in " + self.coverageInfoDest)
        os.mkdir(path)
        stylePath = os.path.join(path, 'Style')
        os.mkdir(stylePath)

    # Kopira datoteku sa stilovima u direktorijum sa rezultatima
    def copyStyleSheet(self):
        styleSheetPath = os.path.dirname(os.path.abspath(__file__)) + '/Style/style.css'
        shutil.copy2(styleSheetPath, os.path.join(self.coverageInfoDest, "html/Style/style.css"))

    # Ulazna metoda
    def generateHtml(self):
        self.makeHtmlReportDir()
        self.copyStyleSheet()
        self.generateHomePage()


#--------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------

class HtmlReportOLD:
    
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
            

    projectCCTest1 = ProjectCodeCoverage(args.directory_path, args.test1, args.command, args.command_arg, args.coverage_dest, args.source_file, args.object_path)
    projectCCTest2 = ProjectCodeCoverage(args.directory_path, args.test2, args.command, args.command_arg, args.coverage_dest, args.source_file, args.object_path)
    
    try:
        projectCCTest1.runProjectCodeCoverage()
    except Exception as e:
        print(e)
        exit()

    try:
        projectCCTest2.runProjectCodeCoverage()
    except Exception as e:
        print(e)
        exit()


    htmlReport = HtmlReport(projectCCTest1, projectCCTest2, args.coverage_dest)
    htmlReport.generateHtml()

    
if __name__ == "__main__":
  Main()