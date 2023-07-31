import os

# Klasa odgovorna za cuvanje razlicitih tipova zbirnih informacija
# nastalih nakon pokretanje jednog testa.
class MiniReport:

    def __init__(self, gcdaCounter, numOfProcessedReports, listOfProcessedFileNames, reports, ifObjectPath):
        
        # Broj pronadjenih gcda datoteka
        self.gcdaCounter = gcdaCounter
    
        # Broj obradjenih izvestaja.
        # Ovaj broj je veci od broja gcda datoteka jer jedna gcda datoteka
        # moze imati izvestaje za vise izvornih datoteka
        # odgovara duzini liste self.listOfProcessedFileNames.
        self.numOfProcessedReports = numOfProcessedReports

        # Sva moguca imena datoteka na koja se naislo pri parsiranju.
        # Mnoga se ponavljaju vise puta 
        # (npr. imena header datoteka ukljucenih u razliciite izvorne datoteka).
        self.listOfProcessedFileNames = listOfProcessedFileNames

        # Broj datoteka koje pogadja test
        # (bez datoteka sa 0% pokrivenosti).
        self.numOfUniqueFilesAfectedByTest = None

        # Broj jedinstevnih datoteka za koje je postojao izvestaj
        # to su jedinstvena imena iz liste self.listOfProcessedFileNames
        # medju njima su i datoteke sa 0% pokrivenosti.
        self.numOfUniqueFilesProcessed = None

        # Ukoliko je na ulazu zadata opcija --object-path ne moze se znati
        # tacan broj fajlova koje test pokriva jer je obradjena samo jedna
        # gcda datoteka. Ekvivalentno, u listi self.listOfProcessedFileNames
        # se tada nalaze samo imena izvornih datoteka iz jedne gcda datoteke
        # ifObjectPath je indikator za --object-path.
        self.ifObjectPath = ifObjectPath

        # Ekstenzije datoteka koje pogadja test.
        self.fileExtensions = None

        # Broj datoteka po svakoj ekstenziji.
        self.extensionsCounter = None
        
        self.makeReport(reports)

    def makeReport(self, reports):

        self.numOfUniqueFilesAfectedByTest = len(reports)
        
        # Koristi se skup da se uklone duplikati.
        uniqeFileNames = set(self.listOfProcessedFileNames)
        self.numOfUniqueFilesProcessed = len(uniqeFileNames)

        # U slucaju zadate opcije --object-path ne moze se govoriti o 
        # broju jedinstvenih datoteka koje test pokriva.
        if self.ifObjectPath:
            self.numOfUniqueFilesProcessed = None
        
        # Pomocna funkcija koja vraca ekstenziju imena datoteke.
        def toExt(e):
            (root, extension) = os.path.splitext(e)
            return extension

        # Mapiraju se dobijena imena datoteka u ekstenzije
        # Koristi se skup da se ukolne duplikati.
        mappedToExt_it = map(lambda e: toExt(e), reports)
        mappedToExt = list(mappedToExt_it)        
        self.fileExtensions = set(mappedToExt)

        # Za svkau eksteniziju se pamti koliko datoteka se njome zavrsava.
        self.extensionsCounter = {}
        for name in reports:
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
        print("Number of unique files affected by test:", self.numOfUniqueFilesAfectedByTest)
        print("Number of processed unique files (including files with 0% coverage):", self.numOfUniqueFilesProcessed)
        print("Extensions of files affected by test:", self.fileExtensions)
        print("Extensions counter:")
        for key, value in self.extensionsCounter.items():
            print("\t" + "\"" + key + "\"" + " : " + str(value))
        print("===================================================================")

