import gzip
import json
import os
import subprocess

from coverage_information import SFCoverageInformation
from summary_report import MiniReport

# Klasa koja obradjuje informacije o pokrivenosti koda projekta nakon poretanja jendog testa.
# Zaduzena je za pokretanje testova, pokretanje alata gcov, prikupljanje informacije o pokrivenosti 
# koda i cuvanje prikupljenih rezultata.
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

        # Mapa objekata sa informacijama o pokrivenosti za svaku izvornu datoteku.
        # Imena datoteka sa izvornim kodom se preslikavaju u reference na SFCoverageInformation objekte.
        self.reports = {}

        # Sumarni izvestaj o uticaju testa.
        # Videti klasu MiniReport.
        self.miniReport = None


    # Pokrece zadati test zadatom komandom.
    def runTest(self):
        # Ako je zadati test vec sam po sebi izvrsna datoteka,
        # pokrece se bez naziva testa zadatog kao agument.
        if self.command == './':
            self.command = self.test
            processsRetVal = subprocess.run([self.command] + self.commandArgs,
                                            stdout=subprocess.DEVNULL, shell=True
                                        )
        else:
            processsRetVal = subprocess.run([self.command, self.test] + self.commandArgs,
                                        stdout=subprocess.DEVNULL
                                        )

        processsRetVal.check_returncode()

    # Vrsi pretragu svih gcda datoteka u direktorijumu projekta nakon pokretanja testa.
    # Za svaku od pronadjenih gcda datoteka pokrece gcov alat, parsira i pamti rezultate.
    def searchForGcda(self):

        gcdaCounter = 0
        numOfProcessedReports = 0
        listOfProcessedFileNames = []

        # Ukoliko su na ulazu zatade obe opcije --source-file i --object-path
        # ne vrsi se pretraga celog direktorijuma projekta vec se gcda datoteka
        # trazi direkno na zadatoj --object-path putanji.
        if self.targetSourceFile and self.targetObjectPath:

            sourceFileBasename = os.path.basename(self.targetSourceFile)
            (sourceFileRoot, _) = os.path.splitext(sourceFileBasename)

            # Ime gcda datoteke moze biti zadato na jedan od sledeca dva nacina:
            # <sourceFileName>.gcda
            # ili
            # <sourceFileName>.<sourceFileExt>.gcda
            # Proveravaju se oba slucaja a ako gcda datoteka nije pronadjena ni u jednom
            # prijavljuje se greska.
            gcdaBaseName = sourceFileRoot + ".gcda"
            gcdaAbsPath = os.path.join(self.targetObjectPath, gcdaBaseName)

            if not os.path.exists(gcdaAbsPath):

                gcdaBaseName = sourceFileBasename + ".gcda"
                gcdaAbsPath = os.path.join(self.targetObjectPath, gcdaBaseName)

                if not os.path.exists(gcdaAbsPath):

                    raise Exception("ERROR: No gcda file found at specified object path which corresponds to the source file")

            # Formira se putanja do gcno datoteke.
            (gcdaRoot, _) = os.path.splitext(gcdaAbsPath)
            gcnoAbsPath = gcdaRoot + ".gcno"

            # Proverava se da li gcno datoteka postoji.
            self.checkIfGcnoExists(gcnoAbsPath, gcdaAbsPath)

            # Pokrece se gcov alat.
            report = self.runGcov(gcdaAbsPath)

            # Parsira se dobijeni izvestaj.
            (numOfReports, listOfFiles)  = self.parseJsonReport(report)

            numOfProcessedReports += numOfReports
            listOfProcessedFileNames += listOfFiles

            gcdaCounter += 1

            # # Formira se sumarni izvestaj.
            self.miniReport = MiniReport(gcdaCounter, numOfProcessedReports, listOfProcessedFileNames,
                                         self.reports.keys(), self.targetObjectPath != None
                                        )

        # Ukoliko nije zadata --object-path opcija na ulazu,
        # vrsi se pretraga celog direktorijuma projekta kako bi se pronasle
        # gcda datoteke.
        else:
            for root, dirs, files in os.walk(self.projectDirectory, followlinks=False):

                for file in files:

                    (fileRoot, fileExt) = os.path.splitext(file)

                    if fileExt == ".gcda":

                        # Formiraju se putanje do gcda i gcno datoteka.
                        gcnoAbsPath = os.path.join(root, fileRoot + ".gcno")
                        gcdaAbsPath = os.path.join(root, file)

                        # Proverava se da li gcno datoteka postoji.
                        self.checkIfGcnoExists(gcnoAbsPath, gcdaAbsPath)

                        # Pokrece se gcov alat.
                        report = self.runGcov(gcdaAbsPath)

                        # Parsira se dobijeni izvestaj.
                        (numOfReports, listOfFiles)  = self.parseJsonReport(report)

                        numOfProcessedReports += numOfReports
                        listOfProcessedFileNames += listOfFiles

                        gcdaCounter += 1

            # Formira se sumarni izvestaj.
            self.miniReport = MiniReport(gcdaCounter, numOfProcessedReports, listOfProcessedFileNames,
                                         self.reports.keys(), self.targetObjectPath != None
                                        )
    
    # Obradjuje podatke procitane iz izvestaja u formatu json.
    def parseJsonReport(self, report):

        processedReportsCounter = 0
        processedReportsFileNames = []

        for key in report:

            if key == "files":

                files = report[key]

                for fileInfo in files:

                    SFCovInfo = SFCoverageInformation()

                    SFCovInfo.linesOfInterest = set()
                    SFCovInfo.coveredLines = set()
                    SFCovInfo.coveredFunctions = set()
                    SFCovInfo.lineHitCount = {}
                    SFCovInfo.functionHitCount = {}

                    sourceFileName = fileInfo["file"]

                    # Pamti se naziv datoteke sa izvornim kodom.
                    SFCovInfo.name = sourceFileName

                    # Za neke datoteke putanja nema "/" na pocetu sto je znak da su te
                    # putanje relativne u odnosu na prosledjeni bild direktorijum.
                    # Zto se njihove putanje spajaju sa putanjom build direktorijuma kako bi
                    # sve apsolutne putanje bile ispravne.              
                    if not SFCovInfo.name.startswith("/"):
                        SFCovInfo.name = os.path.join(self.projectDirectory, sourceFileName)

                    # Ako je zadata opcija --source-file preskacu se sve izvorne datoteke
                    # cije se ime ne poklapa sa imenom zatadim tom opcijom.
                    if self.targetSourceFile != None and self.targetSourceFile != sourceFileName:
                        processedReportsCounter += 1
                        processedReportsFileNames.append(sourceFileName)
                        continue

                    # Prolazi se kroz sve linije u izvestaju.
                    lines = fileInfo["lines"]
                    for line in lines:

                        # Sve linije koje postoje u izvestaju su linije od interesa.
                        # To nisu nuzno sve linije izvornog koda.
                        SFCovInfo.linesOfInterest.add(line["line_number"])

                        # Za svaku liniju od interesa pamti se i koliko je puta izvrsena,
                        # sto moze biti nula ili vise.
                        SFCovInfo.lineHitCount[line["line_number"]] = line["count"]

                        # Linija se dodaje u skup pokrivenih linija ako je barem jednom izvrsena.
                        if line["count"] != 0:
                            SFCovInfo.coveredLines.add(line["line_number"])

                    # Ukoliko je skup pokrivenoh linija za tekucu izvornu datoteku prazan,
                    # izvestaj se ne odradjuje dalje, ne dodaje se u finalnu listu izvestaja i prelazi se na sledeci.
                    # Napomena: ovaj deo znatno ubrzava izvrsavanje skripte jer se kasnije za ovakve SF ne generise html.
                    if len(SFCovInfo.coveredLines) == 0:
                        processedReportsCounter += 1
                        processedReportsFileNames.append(sourceFileName)
                        continue

                    # Prolazi se kroz sve funkcije u izvestaju.
                    functions = fileInfo["functions"]
                    for function in functions:

                        # Za svaku funkciju se pamti koliko je puta izvrsena (pozvana)
                        # sto moze biti nula ili vise puta.
                        SFCovInfo.functionHitCount[function["name"]] = function["execution_count"]

                        # Funkcija se dodaje u skup pokrivenih funkcija ako je baren jednom izvrsena.
                        if function["execution_count"] != 0:
                            SFCovInfo.coveredFunctions.add(function["name"])

                    # Pamti se objekat sa informacijama o pokrivenosti koda za tekucu izvornu datoteku.
                    self.addReport(SFCovInfo)
                    processedReportsCounter += 1
                    processedReportsFileNames.append(sourceFileName)

        return processedReportsCounter, processedReportsFileNames

    # Dodaje prikupljene informacije o pokrivenosti koda u mapu reports.
    def addReport(self, SFCovInfo):

        fileName = SFCovInfo.name

        # Ukoliko vec postoji obejtak sa informacijama o datoteci sa izvornim kodom tada se
        # azuriraju informacije koje on sadrzi.
        if fileName in self.reports.keys():

            # Dohvat se referenca na postojeci objekat sa informacijala o izvornoj datoteci.
            existingReportRef = self.reports[fileName]

            # Prvai se unija skupa linija od interesa, pokrivenih linija i pokrivenih funkcija.
            existingReportRef.linesOfInterest = existingReportRef.linesOfInterest.union(SFCovInfo.linesOfInterest)
            existingReportRef.coveredLines = existingReportRef.coveredLines.union(SFCovInfo.coveredLines)
            existingReportRef.coveredFunctions = existingReportRef.coveredFunctions.union(SFCovInfo.coveredFunctions)

            # Azurira se broj izvrsavanja linija u postojecem objektu.
            # Prolazi se kroz mapu koja cuva broj izvrsavanja svake linije u okviru novog objekta.
            for lineNum, hitCount in SFCovInfo.lineHitCount.items():
                # Proveravase da li ista ta mapa postojeceg objekta vec sadrzi neku vrednost za broj izvrsavanja tekuce linije.
                if lineNum in existingReportRef.lineHitCount.keys():
                    # Ako je to slucaj, postojeci broj izvrsavanja linije se uvecava za vrednost iz novog objekta.
                    existingReportRef.lineHitCount[lineNum] += hitCount
                else:
                    # Ako to nije slucaj, dodaje se novi par (linija, br.izvrsavanja) u pstojeci objekat sa vrednostima iz novog objekta.
                    existingReportRef.lineHitCount[lineNum] = hitCount

            # Azurira se broj izvrsavanja funkcija u postojecem objektu.
            # Prolazi se kroz mapu koja cuva broj izvrsavanja svake funkcije u okviru novog objekta.
            for fnName, execCount in SFCovInfo.functionHitCount.items():
                # Proveravase da li ista ta mapa postojeceg objekta vec sadrzi neku vrednost za broj izvrsavanja tekuce funkcije.
                if fnName in existingReportRef.functionHitCount.keys():
                    # Ako je to slucaj, postojeci broj izvrsavanja funkcije se uvecava za vrednost iz novog objekta.
                    existingReportRef.functionHitCount[fnName] += execCount
                else:
                    # Ako to nije slucaj, dodaje se novi par (funkcija, br.izvrsavanja) u pstojeci objekat sa vrednostima iz novog objekta.
                    existingReportRef.functionHitCount[fnName] = execCount

        # Ukoliko ne postoji obejtak sa informacijama o datoteci sa izvornim kodom tada se
        # novi objekat pamti u mapi. 
        else:
            self.reports[fileName] = SFCovInfo

    # Pokrece alat gcov.
    def runGcov(self, gcda):

        currentWorkDir = os.getcwd()
        # Menja se radni direktorijum, kako bi se json fajl generisao u direktorijumu 
        # sa rezultatima pri poziu alata gcov.
        os.chdir(self.coverageInfoDest)  

        processsRetVal = subprocess.run(["gcov", "--no-output", "--json-format", "--branch-probabilities", "--demangled-names", gcda],
                                        stdout=subprocess.DEVNULL,
                                        stderr=subprocess.DEVNULL
                                       )

        processsRetVal.check_returncode()

        os.chdir(currentWorkDir)

        name, _ = os.path.splitext(os.path.basename(gcda))

        # Pravi se putanja do nastale arhive sa rezultatom nakon poziva gcov alata
        # i putanja do buduce json datoteke u kojoj ce da se zapamti procitan rezultat.
        archiveName = os.path.join(self.coverageInfoDest, name + ".gcov.json.gz")

        # Putanje se prosledjuju metodi readArchiveAndSaveJson() koja vraca ucitani json objekat
        # pa se taj objekat vraca i iz ove metode.
        return self.readArchiveAndSaveJson(archiveName)

    # Otvara arhivu i cita json izvesraj iz nje,
    # pamti json objekat u datoteci na prosedjenoj putanji i
    # vraca procitani json objekat u vidu mape.
    def readArchiveAndSaveJson(self, archiveName):

        if not os.path.exists(archiveName):
            print("Ne postoji:", archiveName)
            raise Exception("ERROR: archive that contains json report does not exist")

        with gzip.open(archiveName, 'rb') as f:
            report = json.load(f)

        os.remove(archiveName)

        return report

    # Provera da li postoji gcno datoteka za pronadjenu gcda datoteku.
    def checkIfGcnoExists(self, gcnoAbsPath, gcdaAbsPath):
        if not os.path.exists(gcnoAbsPath):
            print(gcnoAbsPath)
            raise Exception("ERROR: gcno file does not exists in project directory (Gcda file found here:  " + gcdaAbsPath + ")")

    # Pravi se direktorijum u kojem ce da se cuvaju svi rezultati.
    def makeCoverageInfoDestDir(self):
        if not os.path.exists(self.coverageInfoDest):
            try:
                os.mkdir(self.coverageInfoDest)
            except OSError as e:
                print(e)

    # Cisti se ceo projekat od prethodnih pokretanja testova.
    def clearProjectFromGcda(self):
        for root, dirs, files in os.walk(self.projectDirectory):
            for file in files:
                (fileRoot, fileExt) = os.path.splitext(file)
                if fileExt == ".gcda":
                    os.remove(os.path.join(root, file))

    # Ulazna metoda.
    # Pokrece ceo proces generisanja izvestaja nad projektom.
    def runProjectCodeCoverage(self):
            self.clearProjectFromGcda()
            self.runTest()
            self.makeCoverageInfoDestDir()
            self.searchForGcda()

