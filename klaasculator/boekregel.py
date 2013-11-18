from euro import *

class Balansregel:
    """Deze class beschrijft een regel zoals die op begin en eindbalansen verschijnt.

    Het heeft self.rekening als rekeningnummer, self.naam als naam en self.waarde als waarde.
    """

    def __init__(self, rekening = 0, naam = '', waarde = Euro()):
        """Initialiseer."""
        self.rekening = rekening
        self.naam = naam
        self.waarde = waarde

    def __cmp__(self, other):
        """Vergelijk met een andere blansregel."""
        return self.rekening.__cmp__(other.rekening)

    def __str__(self):
        """String-representatie."""
        return str(self.rekening) + ', ' + self.naam + ', ' + str(self.waarde)
    
class Boekregel:
    """Beschrijft een boekregel zoals die in journaal en grootboek voorkomen.
    
    Datamembers zijn self.nummer (Bknr.), self.datum (Datum), self.rekening (rek.), self.kascie (ctr.), self.omschrijving
    (Hoofdomschrijving), self.tegen2 (tegr2), self.tegen (tegr1), self.waarde (debet, credit) en self.omschrijving2
    (Extra omschrijving).
    """

    def __init__(self,
                 nummer = 0,
                 datum = 0,
                 rekening = 0,
                 kascie = '',
                 omschrijving = '',
                 tegen2 = 0,
                 tegen = 0,
                 waarde = Euro(),
                 omschrijving2 = ''):
        """Initialiseer."""
        self.nummer = nummer
        self.datum = datum
        self.rekening = rekening
        self.kascie = kascie
        self.omschrijving = omschrijving
        self.tegen2 = tegen2
        self.tegen = tegen
        self.waarde = waarde
        self.omschrijving2 = omschrijving2

    def __str__(self):
        """String-representatie."""
        return str(self.nummer) + ', ' + str(self.datum) + ', ' + str(self.rekening) + ', ' + self.kascie + ', ' + self.omschrijving + ', ' + str(self.tegen2) + ', ' + str(self.tegen) + ', ' + str(self.waarde) + ', ' + self.omschrijving2

def sorter_dn(een, twee):
    """Compare-functie voor boekregels sorteren, journaal (datum, nummer)."""
    if een.datum < twee.datum:
        return -1
    elif een.datum > twee.datum:
        return 1
    elif een.nummer < twee.nummer:
        return -1
    elif een.nummer > twee.nummer:
        return 1
    return 0

def sorter_rdn(een, twee):
    """Compare-functie voor boekregels sorteren, grootboek (rekening, datum, nummer)."""
    if een.rekening < twee.rekening:
        return -1
    elif een.rekening > twee.rekening:
        return 1
    return sorter_dn(een, twee)

def sorter_odn(een, twee):
    """Compare-functie voor boekregels sorteren, korte dclijst (omschrijving, datum, nummer)."""
    if een.omschrijving < twee.omschrijving:
        return -1
    elif een.omschrijving > twee.omschrijving:
        return 1
    return sorter_dn(een, twee)

def sorter_rodn(een, twee):
    """Compare-functie voor boekregels sorteren, dclijst (rekening, omschrijving, datum, nummer)."""
    if een.rekening < twee.rekening:
        return -1
    elif een.rekening > twee.rekening:
        return 1
    return sorter_odn(een, twee)

class Kortedcregel:
    """Een regel zoals in een samenvatting van debiteuren-crediteuren lijst.
    
    self.naam is een naam, self.waarde de waarde en self.omschrijving de omschrijving
    """

    def __init__(self, naam = '', waarde = Euro(), omschrijving = '', datum = 0):
        """Initialiseer."""
        self.naam = naam
        self.waarde = waarde
        self.omschrijving = omschrijving
        self.datum = datum

    def __str__(self):
        """String-representatie."""
        return self.naam + ',' + str(self.datum) +  ',' + str(self.waarde) + ', ' + self.omschrijving
        
def sorter_dckort_w(een, twee):

    if een.waarde < twee.waarde:
        return 1
    elif een.waarde > twee.waarde:
        return -1
    elif een.waarde == twee.waarde:
        return 0
    
