import multiprocessing
import os
import shutil

from airium import Airium

# Klasa generise finalni prikaz razlika u pokrivenosti koda.
# Zaduzena je za formiranje pocetna stranice i stranica za pojedinacne izvorne datoteke.
class HtmlReport:

    def __init__(self, projectCoverage1, projectCoverage2, coverageInfoDest):

        self.projectCoverage1 = projectCoverage1
        self.projectCoverage2 = projectCoverage2
        self.coverageInfoDest = coverageInfoDest

        self.reports_1 = self.projectCoverage1.reports
        self.reports_2 = self.projectCoverage2.reports

        self.numOfSameSFNames = 1

        # Mapa koja preslikava naziv izvorne datoteke u html stranicu koja joj odgovara.
        self.SFToHtmlPage = {}

        # Promenljive koje se koriste pri paralelnom generisanju html izvestaja za izvorne datoteke.
        # Videti funkciju generateIndividualPagesforAllSF().
        # Ovde su njihove deklaracije, bice postavljne u pomenutoj funkciji koja ujedno i formira decu-procese.
        self.allSFList = None
        self.numOfWorkers = None

    # Funkcija generise pocetnu stranicu izvestaja o pokrivenosti projekta.
    def generateHomePage(self):

        a = Airium()

        a('<!DOCTYPE html>')
        with a.html():
            with a.head():
                a.meta(charset="utf-8")
                a.title(_t="Code Coverage")
                a.link(rel="stylesheet", href="Style/style.css")

            with a.body():

                # Naslov.
                with a.div(klass="headerDiv"):
                    with a.h1():
                        a("Build Code Coverage")

                # MiniReport izvestaji.
                with a.div(klass="parent"):

                    with a.div(klass="float-child"):
                        a(self.generateMiniReport(self.projectCoverage1.miniReport, self.projectCoverage1.test))

                    with a.div(klass="float-child"):
                        a(self.generateMiniReport(self.projectCoverage2.miniReport, self.projectCoverage2.test))

                # Tabela u padajucem elementu sa svim pokrivenih datotekama.
                a.button(_t="Open All Source Files Code Coverage", klass="collapsible", type="button")
                with a.div(klass="content", style="display: none;"):
                    a.hr()
                    a.h3(_t="All Source Files Code Coverage", klass="subheader")
                    a.input(type="text", klass="myInput", id="AllSFSearch", onkeyup="myFunction(\"AllSFSearch\",\"AllSFTable\")", placeholder="Search for SF names..")
                    a(self.generateAllSFList())

                # Tabela u padajucem elementu sa datotekama u kojima postije razlike u pokrivenosti.
                a.button(_t="Open Source Files Code Coverage Diff", klass="collapsible", type="button")
                with a.div(klass="content", style="display: none;"):
                    a.hr()
                    a.h3(_t="Source Files Code Coverage Diff", klass="subheader")
                    a.input(type="text", klass="myInput", id="SFDiffSearch", onkeyup="myFunction(\"SFDiffSearch\",\"SFDiffTable\")", placeholder="Search for SF names..")
                    a(self.generateSFDiffList())

                # Dugme za povratak na vrh stranice.
                a.button(_t="Top", id="myBtn", onclick="topFunction()", title="Go to top", type="button")

                # Dodavanje skripti.
                a.script(src="Javascript/drop_down.js")
                a.script(src="Javascript/top_button.js")
                a.script(src="Javascript/search_tabel.js")

        pageStr = str(a)

        htmlFileName = os.path.join(self.coverageInfoDest, 'html/' + 'CodeCoverage.html')
        with open(htmlFileName, "w") as f:
            f.write(pageStr)

    # Genersi listu svih pogodjenih izvornih datoteka
    # i procenat pokrivenosti jednim i drugim testom.
    def generateAllSFList(self):
        a = Airium()

        # Generise se tabela sa informacijama za sve izvorne datoteke.
        with a.table(klass="mainTable", id="AllSFTable"):

            # Gnerise se zaglavlje tabele.
            with a.tr(klass="mainTr"):

                a.th(_t="Source file absolute path", klass="mainTh")

                with a.th(klass="mainTh"):
                    a.span(_t=self.projectCoverage1.test, klass="badge")

                with a.th(klass="mainTh"):
                    a.span(_t=self.projectCoverage2.test, klass="badge")

            # Pravi se unija izvornih datoteka koje su pokrivene i jednim i drugim testom.
            # To ce biti unija kljuceva recnika.
            sourceFileUnion = set(self.reports_1.keys()).union(set(self.reports_2.keys()))
            print(len(sourceFileUnion))

            for file in sourceFileUnion:

                # Dohvata se odgovarajuca html stranica za tekucu izvornu datoteku.
                htmlPageLink = self.SFToHtmlPage[file]

                # Ispisuje se naziv svake izvorne datoteke kao link na koji moze da se klikne
                # cime se otvara stranica sa detaljnijim izvestajem za tu izvornu datoteku.
                with a.tr(klass="mainTr"):
                    with a.td():
                        a.a(_t=file, href=htmlPageLink, target="_blank")

                    # Za tekucu izvornu datoteku racunamo koji procenat njenih linija je pokriven prvim testom
                    # a koji procenat je pokriven drugim testom.
                    test1_percentageCoverage = 0
                    test2_percentageCoverage = 0

                    # Moze da se desi da su obe liste pokrivenih linija i linija od interesa prazne
                    # gcov generise prazne izvestaje za neke fajlove.            
                    if file in self.reports_1.keys():
                        if len(self.reports_1[file].linesOfInterest) != 0:
                            test1_percentageCoverage = 100.0 * len(self.reports_1[file].coveredLines) / len(self.reports_1[file].linesOfInterest)

                    if file in self.reports_2.keys():
                        if len(self.reports_2[file].linesOfInterest) != 0:
                            test2_percentageCoverage = 100.0 * len(self.reports_2[file].coveredLines) / len(self.reports_2[file].linesOfInterest)

                    test1_percentageCoverage = round(test1_percentageCoverage, 3)
                    test2_percentageCoverage = round(test2_percentageCoverage, 3)

                    # Dohvataju se skupovi pokrivenih linija.
                    if file in self.reports_1:
                        coveredLines_test1 = self.reports_1[file].coveredLines
                    else:
                        coveredLines_test1 = set()

                    if file in self.reports_2:
                        coveredLines_test2 = self.reports_2[file].coveredLines
                    else:
                        coveredLines_test2 = set()

                    # Racuna se razlika u pokrivenim linijama i, u zavisnosti od rezultata,
                    # generise se "diff" oznaka pored jednom ili drugog testa ili oba.
                    t1Difft2 = coveredLines_test1.difference(coveredLines_test2)
                    t2Difft1 = coveredLines_test2.difference(coveredLines_test1)

                    with a.td(style="padding: 0 40px;"):
                        a.progress(_t=test1_percentageCoverage, value=test1_percentageCoverage, max=100)
                        a.label(_t="{:.3f}".format(test1_percentageCoverage) + " %", klass="percentage")
                        if t1Difft2:
                            a.span(_t="diff", klass="badgeDiff")

                    with a.td(style="padding: 0 40px;"):
                        a.progress(_t=test2_percentageCoverage, value=test2_percentageCoverage, max=100)
                        a.label(_t="{:.3f}".format(test2_percentageCoverage) + " %", klass="percentage")
                        if t2Difft1:
                            a.span(_t="diff", klass="badgeDiff")

        return str(a)

    # Generise listu izvornih datoteka u kojima postoje
    # neke razlike u pokrivenosti koda.
    def generateSFDiffList(self):
        a = Airium()

        # Generise se tabela sa informacijama za sve izvorne datoteke.
        with a.table(klass="mainTable", id="SFDiffTable"):

            # Gnerise se zaglavlje tabele.
            with a.tr(klass="mainTr"):

                a.th(_t="Source file absolute path", klass="mainTh")

                with a.th(klass="mainTh"):
                    a.span(_t=self.projectCoverage1.test, klass="badge")

                with a.th(klass="mainTh"):
                    a.span(_t=self.projectCoverage2.test, klass="badge")

            # Pravi se unija izvornih datoteka koje su pokrivene i jednim i drugim testom.
            # To ce biti unija kljuceva recnika.
            sourceFileUnion = set(self.reports_1.keys()).union(set(self.reports_2.keys()))
            print(len(sourceFileUnion))

            for file in sourceFileUnion:

                # Dohvataju se skupovi pokrivenih linija.
                if file in self.reports_1:
                    coveredLines_test1 = self.reports_1[file].coveredLines
                else:
                    coveredLines_test1 = set()

                if file in self.reports_2:
                    coveredLines_test2 = self.reports_2[file].coveredLines
                else:
                    coveredLines_test2 = set()

                # Racuna se razlika u pokrivenim linijama.
                t1Difft2 = coveredLines_test1.difference(coveredLines_test2)
                t2Difft1 = coveredLines_test2.difference(coveredLines_test1)

                # Ako posoji neka razlika, izvorna datoteka se ispisuje u listu.
                if t1Difft2 or t2Difft1:

                    test1_percentageCoverage = 0
                    test2_percentageCoverage = 0

                    # Moze da se desi da su obe liste pokrivenih linija i linija od interesa prazne
                    # gcov generise prazne izvestaje za neke fajlove.                   
                    if file in self.reports_1.keys():
                        if len(self.reports_1[file].linesOfInterest) != 0:
                            test1_percentageCoverage = 100.0 * len(coveredLines_test1) / len(self.reports_1[file].linesOfInterest)


                    if file in self.reports_2.keys():
                        if len(self.reports_2[file].linesOfInterest) != 0:
                            test2_percentageCoverage = 100.0 * len(coveredLines_test2) / len(self.reports_2[file].linesOfInterest)

                    test1_percentageCoverage = round(test1_percentageCoverage, 3)
                    test2_percentageCoverage = round(test2_percentageCoverage, 3)

                    # Dohvata se odgovarajuca html stranica za tekucu izvornu datoteku.
                    htmlPageLink = self.SFToHtmlPage[file]

                    # Ispisuje se naziv svake izvorne datoteke kao link na koji moze da se klikne
                    # cime se otvara stranica sa detaljnijim izvestajem za tu izvornu datoteku.
                    with a.tr(klass="mainTr"):

                        with a.td():
                            a.a(_t=file, href=htmlPageLink, target="_blank")


                        with a.td(style="padding: 0 40px;"):
                            a.progress(_t=test1_percentageCoverage, value=test1_percentageCoverage, max=100)
                            a.label(_t="{:.3f}".format(test1_percentageCoverage) + " %", klass="percentage")
                            if t1Difft2:
                                a.span(_t="diff", klass="badgeDiff")

                        with a.td(style="padding: 0 40px;"):
                            a.progress(_t=test2_percentageCoverage, value=test2_percentageCoverage, max=100)
                            a.label(_t="{:.3f}".format(test2_percentageCoverage) + " %", klass="percentage")
                            if t2Difft1:
                                a.span(_t="diff", klass="badgeDiff")

        return str(a)

    # Formira se izvestaj za kratak uvid o pokrivenost koda testom.
    def generateMiniReport(self, miniReport, testName):
        a = Airium()

        with a.div(klass="miniheader"):

            with a.h3(style="text-align: center;"):
                a("Mini Report")
            with a.h5(klass="badge"):
                a(testName)


            # Formira se po jedan element u listi za svaku stavku iz MiniRport klase.
            with a.ul():

                with a.li(style="padding-top: 10px"):
                    a("Gcda Counter: " + str(miniReport.gcdaCounter))

                with a.li(style="padding-top: 10px"):
                    a("Number of processed reports: " + str(miniReport.numOfProcessedReports))

                with a.li(style="padding-top: 10px"):
                    a("Number of unique files affected by test: " + str(miniReport.numOfUniqueFilesAfectedByTest))

                with a.li(style="padding-top: 10px"):
                    if miniReport.numOfUniqueFilesProcessed == None:
                        a("Number of processed unique files (including files with 0% coverage): Unknown")
                    else:
                        a("Number of processed unique files (including files with 0% coverage): " + str(miniReport.numOfUniqueFilesProcessed))

                with a.li(style="padding-top: 10px"):
                    a("Extensions of the files affected by test: " + str(miniReport.fileExtensions))

                with a.li(style="padding-top: 10px"):
                    a("Extensions counter")
                    with a.table(style="padding-top: 5px;"):
                        for key in sorted(miniReport.extensionsCounter.keys()):
                                with a.tr(klass="extensionTableTr"):
                                    a.td(_t=str(key))
                                    a.td(_t=str(miniReport.extensionsCounter[key]))
        return str(a)

    # =============================================================================================

    # Funkcija prolazi kroz sve izvorne datoteke koje su pogodjene nekim od testova i
    # za svaku formira html stranicu.
    def generateIndividualPagesforAllSF(self):

        self.allSFList = list(set(self.reports_1.keys()).union(set(self.reports_2.keys())))
        self.numOfWorkers = 4

        global numOfSameSFNames_lock
        numOfSameSFNames_lock = multiprocessing.Lock()

        # NAPOMENA: Pri generisanju stranica u html formatu pomocu niti procesa problem pravi
        # koncept "Global Interpreter Lock (GIL)" koji onemogucava nitima da paralelno citaju
        # deljene podatke, vec forsira sinhronizaciju cak i u slucaju da se podaci samo citaju a ne menjaju.
        # Sumarno, vreme izvrsavanja u slucaju niti je vece od vremena sekvencijalnog izvrsavanja - proces se 
        # ponasa kao jednoniti, uz to ima puno prebacivanja konteksta. Tada se trosi vise vremena nego pri 
        # sekvencijalnoj varijanti. Zato je odabrana varijanta sa decom procesa jer deca dobijaju kopije 
        # podataka pa ne pristupaju zajednickim podacima ali je potrosnja radne memorije veca.

        # Pravi se skup dece-procesa.
        with multiprocessing.Pool(processes=self.numOfWorkers) as pool:

            results = pool.map_async(self.threadFn, self.allSFList, chunksize=100)

            results.wait()

            for r in results.get():
                self.SFToHtmlPage[r[0]] = r[1]

            pool.close()
            pool.join()

    # Funkica koji izvrsava svako radnik.
    def threadFn(self, sourceFile):
        hrefValue = self.generateSFPage(sourceFile)
        return (sourceFile, hrefValue)

    # =============================================================================================

    # Funkcija generise stranicu za pojedninace izvorne datoteke i vraca vezu ka njoj.
    # Stranica sadrzi:
    #    - Zbirni izvesta
    #    - Izvestaj o funkcijama
    #    - Izvestaj o razlikama
    #    - Uporedni prikaz pokrivenih linija        
    def generateSFPage(self, sourceFile):

        a = Airium()

        # Generise se sadrzaj html dokumenta.
        a('<!DOCTYPE html>')
        with a.html():
            with a.head():
                a.meta(charset="utf-8")
                a.title(_t=os.path.basename(sourceFile))
                a.link(rel="stylesheet", href="../Style/style.css")

            # Generise se telo html dokumenta.
            with a.body():

                # Generise se naslov.
                with a.div(klass="headerDiv"):
                    with a.h1():
                        a("Code Coverage")
                    with a.p():
                        a("Source file: " + sourceFile)
                
                # Otvara se datoteka sa izvornim kodom i citaju se linije.
                with open(sourceFile, "r") as f:
                    lines = f.read().split("\n")

                # Generise se zbirni izvestaj o pokrivenosi linija.
                a.button(_t="Open Summary Report", klass="collapsible", type="button")
                with a.div(klass="content", style="display: none;"):
                    a.hr()
                    a.h3(_t="Summary Report", klass="subheader")
                    a(self.generateCoveredLinesHtml(sourceFile, lines))

                # Generise se izvestaj o funkcijama.
                a.button(_t="Open Functions Report", klass="collapsible", type="button")
                with a.div(klass="content", style="display: none;"):
                    a.hr()
                    a.h3(_t="Functions Report", klass="subheader")
                    a(self.generateCoveredFunctionsHtml(sourceFile))

                # Generise se izvestaj o razlikama u pokrivenosti linija.
                a.button(_t="Open Coverage Diff", klass="collapsible", type="button")
                with a.div(klass="content", style="display: none;"):
                    a.hr()
                    a.h3(_t="Coverage Diff", klass="subheader")
                    a(self.generateCoverageDiffHtml(sourceFile, lines))

                # Generise se uporedni prikaz pokrivenoh linija.
                a.button(_t="Open Side By Side Comparison", klass="collapsible", type="button")
                with a.div(klass="content", style="display: none;"):
                    a.hr()
                    a.h3(_t="Side By Side Comparison", klass="subheader")
                    a(self.generateSideBySideCoverageHtml(sourceFile, lines))

                # Dugme za povratak na vrh stranice.
                a.button(_t="Top", id="myBtn", onclick="topFunction()", title="Go to top", type="button")

                # Dodavanje skripti.
                a.script(src="../Javascript/drop_down.js")
                a.script(src="../Javascript/top_button.js")

        pageStr = str(a)

        baseName = os.path.basename(sourceFile)

        htmlFileName = self.coverageInfoDest + '/html/Pages/' + baseName + ".html"
        hrefValue = "./Pages/" +  baseName + ".html"

        if os.path.exists(htmlFileName):

            # self.numOfSameSFNames je deljeni resurs koji deca-procesi mogu da citaju i uvecavaju istovremeno.
            # Potrebno sinhronizovati njegovo koriscenje da ne bi doslo do progresnih rezultata.
            with numOfSameSFNames_lock:
                htmlFileName = self.coverageInfoDest + '/html/Pages/' + baseName + "_" + str(self.numOfSameSFNames) + ".html"
                hrefValue = "./Pages/" +  baseName + "_" + str(self.numOfSameSFNames) + ".html"
                self.numOfSameSFNames += 1

        with open(htmlFileName, "w") as f:
            f.write(pageStr)

        return hrefValue

    # Funkcija generise zbirni izvestaj o pokrivenosti linija testovima za jednu izvornu datoteku.
    def generateCoveredLinesHtml(self, sourceFile, lines):

        a = Airium()   

        # Dohvataju se odgovarajuci izvestaji, ukoliko postoje.
        if sourceFile in self.reports_1:
            report1 = self.reports_1[sourceFile]
        else:
            report1 = None

        if sourceFile in self.reports_2:
            report2 = self.reports_2[sourceFile]
        else:
            report2 = None

        # Generise se tabela izvestaja.
        with a.table(klass="mainTable"):

            # Kolone tabele sdrze redom redni br. linije izvorne datoteke, liniju izvorne datoteke,
            # broj pogodaka za svaku liniju, spisak testova koji pogadjaju liniju.
            with a.tr(klass="mainTr"):
                a.th(_t='Line number', klass="mainTh")
                a.th(_t='Line', klass="mainTh")
                a.th(_t='Number of hits', klass="mainTh")
                a.th(_t='Tests that cover line', klass="mainTh")

            # Citaju se linije izvorne datoteke.
            for index, line in enumerate(lines):

                lineNumber = index + 1

                # Zbirna lista testova za jednu liniju.
                testsCoveringLine = []

                lineNumberOfHits = 0
                isLineOfInterest = False

                # Dohvataju se informacije o liniji iz prvog izvestaja (prvi test).
                if report1 != None:
                    if lineNumber in report1.coveredLines:
                        testsCoveringLine.append(self.projectCoverage1.test)
                    if lineNumber in report1.linesOfInterest:
                        isLineOfInterest = True
                        lineNumberOfHits += report1.lineHitCount[lineNumber]

                # Dohvataju se informacije o liniji iz drugog izvestaja (drugi test).
                if report2 != None:
                    if lineNumber in report2.coveredLines:
                        testsCoveringLine.append(self.projectCoverage2.test)
                    if lineNumber in report2.linesOfInterest:
                        isLineOfInterest = True
                        lineNumberOfHits += report2.lineHitCount[lineNumber]

                lineStyleClass = None
                lineNumberOfHitsTextValue = None

                # Oderdjuje se boja kojom ce linija biti obojena i vrednost za kolonu broj pogodaka.
                if isLineOfInterest:
                    lineNumberOfHitsTextValue = str(lineNumberOfHits)
                    if len(testsCoveringLine) != 0:
                        lineStyleClass = "coveredLine"
                    else:
                        lineStyleClass = "uncoveredLine"
                else:
                    lineNumberOfHitsTextValue = "----"
                    lineStyleClass = ""

                # Informacije o tekucoj linije se smestaju u jedan red tabele.
                with a.tr(klass="mainTr"):
                    a.td(_t=str(lineNumber), klass="lineNumber")
                    a.td(_t=line, klass=lineStyleClass)
                    a.td(_t=lineNumberOfHitsTextValue)
                    with a.td(klass="testName"):
                        for test in testsCoveringLine:
                            a.span(_t=test, klass="badge")

        return str(a)

    # Funkcija generise zbirni izvestaj o broju poziva funkcija jedne izvorne datoteke.
    def generateCoveredFunctionsHtml(self, sourceFile):

        a = Airium()

        # Dohvataju se odgovarajuci izvestaji, ukoliko postoje.
        if sourceFile in self.reports_1:
            report1 = self.reports_1[sourceFile]
        else:
            report1 = None

        if sourceFile in self.reports_2:
            report2 = self.reports_2[sourceFile]
        else:
            report2 = None

        functionHitCount = {}

        if report1 != None:
            for fnName, hitCount in report1.functionHitCount.items():
                if fnName in functionHitCount.keys():
                    functionHitCount[fnName] += hitCount
                else:
                    functionHitCount[fnName] = hitCount

        if report2 != None:
            for fnName, hitCount in report2.functionHitCount.items():
                if fnName in functionHitCount.keys():
                    functionHitCount[fnName] += hitCount
                else:
                    functionHitCount[fnName] = hitCount

        with a.table(klass="mainTable"):

            with a.tr(klass="mainTr"):
                a.th(_t='Function name', klass="mainTh")
                a.th(_t='Number of hits', klass="mainTh")

            for key, value in functionHitCount.items():

                with a.tr(klass="mainTr"):
                    a.td(_t=key, klass="functionName")
                    a.td(_t=str(value), klass="numberOfCalls")

        return str(a)

    # Funkcija genersie izvestaj o razlikama u pokrivenosti linija izmedju dva testa za jednu izvornu datoteku.
    def generateCoverageDiffHtml(self, sourceFile, lines):

        # Dohavataju se skupovi pokrivenih linija.
        if sourceFile in self.reports_1:
            r1_coveredLines = self.reports_1[sourceFile].coveredLines
        else:
            r1_coveredLines = set()

        if sourceFile in self.reports_2:
            r2_coveredLines = self.reports_2[sourceFile].coveredLines
        else:
            r2_coveredLines = set()

        # Dohvataju se imena testoma.
        test1_name = self.projectCoverage1.test
        test2_name = self.projectCoverage2.test

        # Linije koje pokriva prvi test a ne pokriva drugi.
        r1Diffr2 = r1_coveredLines.difference(r2_coveredLines)
        # Linije koje pokriva drugi test a ne pokriva prvi.
        r2Diffr1 = r2_coveredLines.difference(r1_coveredLines)

        a = Airium()

        # Generise se tabela izvestaja.
        with a.table(klass="mainTable"):

            # Generisu se nazivi kolona.
            with a.tr(klass="mainTr"):

                a.th(_t="Line Number", klass="mainTh")

                with a.th(klass="mainTh"):
                    a.span(_t=test1_name, klass="badge")
                    a.span(_t=" BUT NOT ")
                    a.span(_t=test2_name, klass="badge")

                a.th(_t="Line Number", klass="mainTh")

                with a.th(klass="mainTh"):
                    a.span(_t=test2_name, klass="badge")
                    a.span(_t=" BUT NOT ")
                    a.span(_t=test1_name, klass="badge")

            # Citaju se linije izvornog koda.
            for index, line in enumerate(lines):

                lineNumber = index + 1

                # Proverava se u koji skup upada linija i u zavisnosti od toga se boji 
                # odgovarajucom bojom.
                with a.tr(klass="mainTr"):
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

    # Funkcija generise uporedni prikaz pokrivenih linija za jednu izvornu datoteku.
    def generateSideBySideCoverageHtml(self, sourceFile, lines):

        # Dohvataju se odgovarajuci izvestaji, ukoliko postoje.
        if sourceFile in self.reports_1:
            r1 = self.reports_1[sourceFile]
        else:
            r1 = None

        if sourceFile in self.reports_2:
            r2 = self.reports_2[sourceFile]
        else:
            r2 = None

        # Dohvataju se imena testoma
        test1_name = self.projectCoverage1.test
        test2_name = self.projectCoverage2.test

        a = Airium()

        # Generise se tabela izvestaja.
        with a.table(klass="mainTable"):

            with a.tr(klass="mainTr"):

                a.th(_t="Line Number", klass="mainTh")

                with a.th(klass="mainTh"):
                    a.span(_t=test1_name, klass="badge")

                a.th(_t="Hit count", klass="mainTh")

                a.th(_t="Line Number", klass="mainTh")

                with a.th(klass="mainTh"):
                    a.span(_t=test2_name, klass="badge")

                a.th(_t="Hit count", klass="mainTh")

            # Citaju se linije izvornog koda.
            for index, line in enumerate(lines):


                lineNumber = index + 1

                # Ako ne postoji izvestaj za izvornu datoteku to znaci
                # da je test ne pokriva.
                if r1 != None:
                    isCoveredByR1 = lineNumber in r1.coveredLines
                else:
                    isCoveredByR1 = False

                if r2 != None:
                    isCoveredByR2 = lineNumber in r2.coveredLines
                else:
                    isCoveredByR2 = False

                lineHitCountR1 = ""
                lineHitCountR2 = ""

                # Dohvatamo informacije o datotekci ukoliko
                # ona posotji u izvestaju za prvi test.
                if r1 != None:
                    if lineNumber in r1.linesOfInterest:
                        lineHitCountR1 = str(r1.lineHitCount[lineNumber])
                    else:
                        lineHitCountR1 = "---"
                else:
                    # Ukoliko ne postoji izvestaj za datoteku u odnosu na jedan test,
                    # sigurno posotji izvestaj za nju u odnosu na drugi test.
                    # Razlog tome je to sto datoteke dolaze iz unije datoteka pokrivenih
                    # nekim od testova. Tada se konsultuje izvestaj u odnosu na drugi test
                    # kako bi se ustanovilo da li je u pitanju linija od interesa ili ne.
                    # Tada ce broj izvrsavanja za sve linije od interesa biti "0".
                    if lineNumber in r2.linesOfInterest:
                        lineHitCountR1 = str(0)
                    else:
                        lineHitCountR1 = "---"

                # Slicno za drugi test.
                if r2 != None:
                    if lineNumber in r2.linesOfInterest:
                        lineHitCountR2 = str(r2.lineHitCount[lineNumber])
                    else:
                        lineHitCountR2 = "---"
                else:
                    if lineNumber in r1.linesOfInterest:
                        lineHitCountR2 = str(0)
                    else:
                        lineHitCountR2 = "---"


                # Proverava se kojim testom je linija pokrivena i u zavisnosti do toga
                # boji se na odgovarajuci nacin.
                with a.tr(klass="mainTr"):
                    if isCoveredByR1 and isCoveredByR2:
                        a.td(_t=str(lineNumber), klass="lineNumber")
                        a.td(_t=line, klass="codeLine coveredLine")
                        a.td(_t=lineHitCountR1, klass="lineNumber")

                        a.td(_t=str(lineNumber), klass="lineNumber")
                        a.td(_t=line, klass="codeLine coveredLine")
                        a.td(_t=lineHitCountR2, klass="lineNumber")
                    elif isCoveredByR1:
                        a.td(_t=str(lineNumber), klass="lineNumber")
                        a.td(_t=line, klass="codeLine coveredLine")
                        a.td(_t=lineHitCountR1, klass="lineNumber")

                        a.td(_t=str(lineNumber), klass="lineNumber")
                        a.td(_t=line, klass="codeLine")
                        a.td(_t=lineHitCountR2, klass="lineNumber")
                    elif isCoveredByR2:
                        a.td(_t=str(lineNumber), klass="lineNumber")
                        a.td(_t=line, klass="codeLine")
                        a.td(_t=lineHitCountR1, klass="lineNumber")

                        a.td(_t=str(lineNumber), klass="lineNumber")
                        a.td(_t=line, klass="codeLine coveredLine")
                        a.td(_t=lineHitCountR2, klass="lineNumber")
                    else:
                        a.td(_t=str(lineNumber), klass="lineNumber")
                        a.td(_t=line, klass="codeLine")
                        a.td(_t=lineHitCountR1, klass="lineNumber")

                        a.td(_t=str(lineNumber), klass="lineNumber")
                        a.td(_t=line, klass="codeLine")
                        a.td(_t=lineHitCountR2, klass="lineNumber")

        return str(a)

    # Pravi direktorijum u kome ce da se cuvaju html stranice.
    def makeHtmlReportDir(self):
        path = os.path.join(self.coverageInfoDest, 'html')
        if os.path.isdir(path):
            raise Exception("ERROR: html/ directory alredy exists in " + self.coverageInfoDest)
        os.mkdir(path)
        pagesDir = os.path.join(path, 'Pages')
        os.mkdir(pagesDir)

    # Kopira direktorijum sa stilovima u formatu css.
    def copyStyleSheet(self):
        destinationDir = os.path.join(self.coverageInfoDest, 'html/Style')
        sourceDir = os.path.dirname(os.path.abspath(__file__)) + '/Style'
        shutil.copytree(sourceDir, destinationDir)

    # Kopira direktorijum sa skriptama pisanim u programskom jeziku JavaScript.
    def copyScripts(self):
        destinationDir = os.path.join(self.coverageInfoDest, 'html/Javascript')
        sourceDir = os.path.dirname(os.path.abspath(__file__)) + '/Javascript'
        shutil.copytree(sourceDir, destinationDir)

    # Ulazna metoda.
    def generateHtml(self):
        self.makeHtmlReportDir()
        self.copyStyleSheet()
        self.copyScripts()
        self.generateIndividualPagesforAllSF()
        self.generateHomePage()

