from tools import *
from boekstuk import *
from config import *

##
## Sheet_jr_abstract
##

class Sheet_jr_abstract:
    """Abstracte class voor Sheet_jr en Sheet_jr_ro.

    Gebruik dit niet direct, dit is enkel een methode om met multiple inheritance dubbele code te besparen (Sheet_jr en
    Sheet_jr_ro lijken veel op elkaar).
    """
    def __getitem__(self, i):
        """Operator [].

        Geeft de Boekregel op rij i.
        """
        return self.getboekregel(i)

    def __iter__(self):
        """Iterator support.
        
        Dit maakt het mogelijk om over de sheet te itereren als een lijst boekregels. Slaat lege regels over.
        """
        self.i = -1
        return self

    def next(self):
        """Zie __iter__()."""
        self.i += 1
        if self.i >= self.rows():
            raise StopIteration
        if not self.getint(self.i, 0) and not self.getint(self.i, 1):
            return self.next()
        return self.getboekregel(self.i)

    def getwaarde(self, row):
        """Geeft een bedrag in euros op een row."""
        return Euro(self.getfloat(row, 7) - self.getfloat(row, 8))

    def getboekregel(self, row):
        """Geeft de boekregel op een zekere row."""
        return Boekregel(self.getint(row, 0),
                         self.getint(row, 1),
                         self.getint(row, 2),
                         self.getstring(row, 3),
                         self.getstring(row, 4),
                         self.getint(row, 5),
                         self.getint(row, 6),
                         self.getwaarde(row),
                         self.getstring(row, 9))

    def check(self, nummer, datum, row):
        """Hulpfunctie voor find.

        Dit geeft > 1 als we verder moeten zoeken, en < 1 als we terug moeten.
        """
        if self.getint(row, 1) == 0:
            row += 1;
	if self.getint(row, 1) == 0:
            return 1;

        if self.getint(row, 1) > datum:
            return 1;
        elif self.getint(row, 1) < datum:
            return -1;

        if self.getint(row, 0) > nummer:
            return 1;
        elif self.getint(row, 0) < nummer:
            return -1;
	return 0;

    def find(self, nummer, datum):
        """Vind de regel waar een bepaald boekstuk (nummer, datum) begint.

        Deze methode gaat ervan uit dat het journaal gesorteerd is. Het zoekt eerst met bisectie grofweg waar het moet zijn
        en daarna (omdat er bijvoorbeeld ook lege regels kunnen zijn), exact waar het begint.
        """
        a = 0
        b = self.rows()
        g = (a + b) / 2
        
        if self.check(nummer, datum, a) >= 0:
            return 0

        while g > a and g < b:
            c = self.check(nummer, datum, g)
            if c > 0:
                b = g
                g = (a + b) / 2
            elif c < 0:
                a = g
                g = (a + b) / 2
            else:
                g -= 5

        for i in range(a, b + 1):
            if self.getint(i, 1) > datum:
                return i - 1
            elif self.getint(i, 1) == datum and self.getint(i, 0) > nummer:
                return i - 1

        return b

    def getboekstuk(self, nummer, datum):
        """Geef het boekstuk met dit nummer en datum."""
        b = Boekstuk(nummer, datum)
        b.extend(filter(lambda x: x.nummer == nummer and x.datum == datum, self))
        return b

    def getboekstuk_local(self, row):
        """Vergelijkbaar met getboekstuk.

        Verschil is dat dit alleen lokaal zoekt bij row (of row - 1 als row leeg is). Dit wordt gebruikt voor Tegenregel.
        Retourneert het boekstuk en de regel vlak na het boekstuk.
        """
        if row < 0:
            return Boekstuk()

        nummer = self.getint(row, 0)
        if row and not nummer:
            row -= 1
            nummer = self.getint(row, 0)
        datum = self.getint(row, 1)

        while row and self.getint(row, 0) == nummer and self.getint(row, 1) == datum:
            row -= 1
        row += 1

        b = Boekstuk(nummer, datum)
        while self.getint(row, 0) == nummer and self.getint(row, 1) == datum:
            b.append(self.getboekregel(row))
            row += 1
        return b, row

##
## Sheet_jr
##
    

class Sheet_jr(Sheet, Sheet_jr_abstract):
    """Deze class beschrijft een sheet van het 'journaal-type'.

    Dat is dus sheets als het journaal, grootboek of debiteuren-crediteuren lijst.
    """
    def __init__(self, sheet, startrow = 2, endrow = None):
        """Initialiseer.

        startrow is de rij waarop we beginnen. Dit om niet de 'kop' mee te nemen. endrow is waar we ophouden. Dit is by
        default de laaste boeking
        """
        self.startrow = startrow
        if sheet == None:
            self.data = [[u'']*10]
        else:
            if endrow == None:
                endrow = laatsteboeking(sheet)
            Sheet.__init__(self, sheet, 0, self.startrow, 9, endrow)

    def __setitem__(self, i, b):
        """Operator [].

        Zet de Boekregel op rij i.
        """
        self.setboekregel(i, b)

    def setwaarde(self, row, waarde):
        """Set de waarde op een row."""
        if waarde.dc == DEBET:
            self.setfloat(row, 7, float(waarde))
            self.setfloat(row, 8, 0.0)
        else:
            self.setfloat(row, 7, 0.0)
            self.setfloat(row, 8, float(waarde))

    def setboekregel(self, row, b):
        """Set een boekregel."""
        self.setint(row, 0, b.nummer)
        self.setint(row, 1, b.datum)
        self.setint(row, 2, b.rekening)
        self.setstring(row, 3, b.kascie)
        self.setstring(row, 4, b.omschrijving)
        self.setint(row, 5, b.tegen2)
        self.setint(row, 6, b.tegen)
        self.setwaarde(row, b.waarde)
        self.setstring(row, 9, b.omschrijving2)

    def write(self, sheet, insert = False, erase = False):
        """Schrijf de data naar een werkblad.

        Als erase == True, dan wordt het werkblad helemaal leeggehaald voordat er naar geschreven wordt.
        """
        Sheet.write(self, sheet, 0, self.startrow, insert, erase)

##
## Sheet_jr_ro
##

class Sheet_jr_ro(Sheet_ro, Sheet_jr_abstract):
    """Het read-only broertje van Sheet_jr.

    Zie de opmerkingen bij Sheet_ro.
    """
    def __init__(self, sheet, startrow = 2, endrow = None):
        """Initialiseer.

        startrow is de rij waarop we beginnen. Dit om niet de 'kop' mee te nemen. endrow is waar we ophouden. Dit is by
        default de laaste boeking
        """
        self.startrow = startrow
        if sheet == None:
            self.data = ((u'',)*10,)
        else:
            if endrow == None:
                endrow = laatsteboeking(sheet)
            Sheet_ro.__init__(self, sheet, 0, self.startrow, 9, endrow)

    def write(self, sheet, insert = False, erase = False):
        """Schrijf de data naar een werkblad.
        
        Als erase == True, dan wordt het werkblad helemaal leeggehaald voordat er naar geschreven wordt.
        """
        
        Sheet_ro.write(self, sheet, 0, self.startrow, insert, erase)

##
## Sheet_bl_abstrace
##


class Sheet_bl_abstract(Sheet_ro):
    """Abstracte class voor Sheet_bl en Sheet_bl_ro.

    Zie de opmerkingen bij Sheet_jr_abstract.
    """
    def __getitem__(self, i):
        """Operator [].

        Geeft de Balansregel op rij i.
        """
        return self.getbalansregel(i)

    def __iter__(self):
        """Iterator support.

        Dit maakt het mogelijk om over de sheet te itereren als een lijst balansregels. Slaat lege regels over.
        """
        self.i = -1
        return self

    def next(self):
        """Zie __iter__()."""
        self.i += 1
        if self.i >= self.rows():
            raise StopIteration
        if not self.getint(self.i, 0):
            return self.next()
        return self.getbalansregel(self.i)

    def getwaarde(self, rekening):
        """Deze methode vertelt je hoeveel euro er op een bepaalde rekening staat.

        rekening kan een int of string zijn.
        """
        if type(rekening) == str or type(rekening) == unicode:
            for i in range(self.rows()):
                if self.getstring(i, 2) == rekening:
                    return Euro(self.getfloat(i, 5) - self.getfloat(i, 6))
        else:
            for i in range(self.rows()):
                if self.getint(i, 0) == rekening:
                    return Euro(self.getfloat(i, 5) - self.getfloat(i, 6))
        return Euro()

    def getbalansregel(self, row):
        """Geeft de balansregel."""
        return Balansregel(self.getint(row, 0),
                           self.getstring(row, 2),
                           Euro(self.getfloat(row, 5) - self.getfloat(row, 6)))

##
## Sheet_bl
##

class Sheet_bl(Sheet, Sheet_bl_abstract):
    """Dit is voor een balans-achtige sheet.

    Zoals dus de begin- en eindbalans en resulatenrekening.
    """

    def __init__(self, sheet, startrow = 4):
        """Initialiseer."""
        self.startrow = startrow

        if sheet == None:
            self.data = [[u'']*7]
        else:
            e = laatsteboeking(sheet)
            Sheet.__init__(self, sheet, 1, self.startrow, 7, e)

    def __setitem__(self, i, b):
        """Operator [].

        Zet de Balansregel op rij i.
        """
        self.setbalansregel(i, b)

    def setwaarde(self, rekening, waarde):
        """Deze methode zet hoeveel euro er op een rekening moet staan.

        rekening kan een int of string zijn. Geeft True als het gelukt is, anders False.
        """
        if type(rekening) == str or type(rekening) == unicode:
            for i in range(self.rows()):
                if self.getstring(i, 2) == rekening:
                    if waarde.dc == DEBET:
                        self.setfloat(i, 5, float(waarde))
                        self.setfloat(i, 6, 0.0)
                    else:
                        self.setfloat(i, 5, 0.0)
                        self.setfloat(i, 6, float(waarde))
                    return True
        else:
            for i in range(self.rows()):
                if self.getint(i, 0) == rekening:
                    if waarde.dc == DEBET:
                        self.setfloat(i, 5, float(waarde))
                        self.setfloat(i, 6, 0.0)
                    else:
                        self.setfloat(i, 5, 0.0)
                        self.setfloat(i, 6, float(waarde))
                    return True

        return False

    def setbalansregel(self, row, b):
        """Set de balansregel."""
        self.setint(row, 0, b.rekening)
        self.setstring(row, 2, b.naam)
        if b.waarde.dc == DEBET:
            self.setfloat(row, 5, float(b.waarde))
            self.setfloat(row, 6, 0.0)
        else:
            self.setfloat(row, 5, 0.0)
            self.setfloat(row, 6, float(b.waarde))

    def write(self, sheet):
        Sheet.write(self, sheet, 1, self.startrow, False, True)

##
## Sheet_bl_ro
##


class Sheet_bl_ro(Sheet_ro, Sheet_bl_abstract):
    """Read-only broertje van Sheet_bl.

    Zie de opmerkingen bij Sheet_ro.
    """

    def __init__(self, sheet, startrow = 4):
        """Initialiseer."""
        self.startrow = startrow

        if sheet == None:
            self.data = ((u'',)*7,)
        else:
            e = laatsteboeking(sheet)
            Sheet_ro.__init__(self, sheet, 1, self.startrow, 7, e)
    
    def write(self, sheet):
        Sheet_ro.write(self, sheet, 1, self.startrow, False, True)

