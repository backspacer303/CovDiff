import os

# Klasa koja predstavlja baznu klasu za sve tipove zbirnih izvestaja.
# Sadrzi metodu za prihvatanje posetioca klase zaduzene
# za formiranje izvestaja. Implementacija metode u izvedenim klasama
# treba da pozove odgovarajucu metodu posetioca koja ce formirati izvestaj.
class SummaryReport():
    def accept(self, visitor):
        pass

# Klasa odgovorna za cuvanje razlicitih tipova zbirnih informacija
# nastalih nakon pokretanje jednog testa.
class MiniReport(SummaryReport):

    def __init__(self):
        
        # Broj pronadjenih gcda datoteka
        self.gcdaCounter = None
    
        # Broj obradjenih izvestaja.
        # Ovaj broj je veci od broja gcda datoteka jer jedna gcda datoteka
        # moze imati izvestaje za vise izvornih datoteka
        # odgovara duzini liste self.listOfProcessedFileNames.
        self.numOfProcessedReports = None

        # Sva moguca imena datoteka na koja se naislo pri parsiranju.
        # Mnoga se ponavljaju vise puta 
        # (npr. imena header datoteka ukljucenih u razliciite izvorne datoteka).
        self.listOfProcessedFileNames = []

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
        self.ifObjectPath = False

        # Ekstenzije datoteka koje pogadja test.
        self.fileExtensions = set()

        # Broj datoteka po svakoj ekstenziji.
        self.extensionsCounter = {}

    # Implementacija metode accept() nasledjene iz bazne klase Report.
    # Prihvata referencu na objekat klase ProjectCodeCoverage i poziva
    # odgovarajucu metodu za formiranje izvstaja.
    def accept(self, visitor):
        visitor.visitMiniReport(self)

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

