# Klasa odgovorna za cuvanje informacija o pokrivenosti koda
# jedne izvorne datoteke.
class SFCoverageInformation:

    def __init__(self):
        
        # Naziv datoteke za izvornim kodom.
        self.name = None
        # Skup svih linija iz izvestaja ali ne nuzno sve linije izvornog koda.
        self.linesOfInterest = None
        # Skup pokrivenih linija (linije izvornog koda izvrsene barem jednom).
        self.coveredLines = None
        # Mapa koja pokrivene linije preslikava u odgovarajuci broj izvrsavanja.
        self.lineHitCount = None
        # Skup pokrivenoh funkcija (sve funkcije izvrsene barem jednom).
        self.coveredFunctions = None
        # Mapa koja pokrivene funkcije preslikava u odgovarajuci broj izvrsavanja.
        self.functionHitCount = None
    
    def __str__(self):
        SFstr = ""
        SFstr += self.name + "\n"
        SFstr += "Covered lines: " + str(self.coveredLines) + "\n"
        SFstr += "Function hit count:" + "\n"
        for fName, count in self.functionHitCount.items():
            SFstr += "\t" + fName + "  ----->  " + str(count) + "\n"
        return SFstr

