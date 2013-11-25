"""Hier staat de functies die afhankelijk zijn van csv-bestanden.

Het leek mij wellicht handig dat het naast de klaasculator te draaien in een geladen spreadsheetprogramma, dat het ook te
draaien is zonder, en dan werken op csv-bestanden als sheets.
"""

import csv
from datetime import date


def _datetoint(dag, maand, jaar):
    """Geef de int-representatie van een datum.

    De int hoort het aantal dagen sinds 30 december 1899 te zijn (waarom niet 1-1-1900 weet ik ook niet).
    """
    datum = date(jaar, maand, dag)
    epoch = date(1899, 12, 30)
    return datum.toordinal() - epoch.toordinal()

def getactivecell(): # is dit nodig?
    """Geeft de geselecteerde cel terug."""
    raise Exception('Dit is niet beschikbaar in CSV.')

def getactivesheet(): # is dit nodig?
    """Geeft het geselecteerde sheet terug."""
    raise Exception('Dit is niet beschikbaar in CSV.')

def getsheetbyname(name):
    """Retourneer het sheet 'name'.

    In CSV houdt dat in dat name een bestandsnaam is en een list met rijen teruggegeven wordt.
    """
    try:
        if not name.endswith('.csv'):
            name += '.csv'
        
        f = open(name, 'rb')
        reader = csv.reader(f)
        
        sheet = []
        for row in reader:
            sheet.append(row)

        f.close()
        return sheet
    except:
        raise Exception('Kon sheet \'%s\' niet openen.' % name)

def laatsteboeking(sheet):
    """Geeft het laagste index terug waarop nog dingen staan in een sheet.

    sheet kan een string zijn (de naam van een sheet), of een list zoals geretourneerd door getsheetbyname
    """
    if type(sheet) == str or type(sheet) == unicode:
        sheet = getsheetbyname(sheet)

    return len(sheet) - 1

class Sheet:
    """Deze class representeert de data op een sheet."""
    
    def __init__(self, sheetname, left, bottom, right, top):
        """Maak de sheet van de sheet sheetname, in de range left, bottom, right, top.
        
        Voor de goede orde: left staat voor de linker kolom, right voor de rechter, bottom voor de laagste rij (dus die
        bovenin je scherm staat) en top voor de hoogste rij (ondering je scherm). Deze zijn 0-gebasseerd.
        Dus bijvoorbeeld Sheet('Journaal', 2, 4, 5, 8) selecteerd de range C5:F9.
        """
        
        if top - bottom < 0:
            self.data = [['']*(right - left + 1)]
        else:

            sheet = getsheetbyname(sheetname)

            self.data = []

            for r in range(bottom, top + 1):
                try:
                    self.data.append(sheet[r][left:right + 1])
                except IndexError:
                    self.data.append(['']*(right - left + 1))

    def columns(self):
        """Het aantal kolommen."""
        return len(self.data[0])

    def enlarge(self, newrows):
        """Maak het aantal rijen op de sheet groter tot newrows."""
        while self.rows() <= newrows:
            self.data.append(['']*self.columns())

    def getfloat(self, row, col):
        """Geeft item op col, row, in float-representatie."""
        try:
            return float(self.data[row][col])
        except:
            return 0.0

    def getint(self, row, col):
        """Geeft item op col, row, in int-representatie."""
        try:
            return int(self.data[row][col])
        except:
            # we willen ook met data om kunnen gaan zoals die standaard door openoffice worden opgeslagen, dus bv.
            # '5 feb 1984'
            try:
                dag, maand, jaar = self.data[row][col].split()

                maand = maand.lower()

                if maand == 'jan':
                    maand = 1
                elif maand == 'feb':
                    maand = 2
                elif maand == 'mrt' or maand == 'mar':
                    maand = 3
                elif maand == 'apr':
                    maand = 4
                elif maand == 'mei' or maand == 'may':
                    maand = 5
                elif maand == 'jun':
                    maand = 6
                elif maand == 'jul':
                    maand = 7
                elif maand == 'aug':
                    maand = 8
                elif maand == 'sep':
                    maand = 9
                elif maand == 'okt' or maand == 'oct':
                    maand = 10
                elif maand == 'nov':
                    maand = 11
                elif maand == 'dec':
                    maand = 12

                jaar = int(jaar)
                if jaar < 1000:
                    y = date.today().year
                    jaar += (y / 1000) * 1000

                return _datetoint(int(dag), maand, jaar)
            except:
                return 0

    def getstring(self, row, col):
        """Geeft item op col, row, in string-representatie."""
        try:
            return str(self.data[row][col])
        except:
            return ''

    def rows(self):
        """Het aantal rijen."""
        return len(self.data)

    def setfloat(self, row, col, f, allow_zero = False):
        """Set item f op col, row als float.

        Als allow_zero = False, dan word een 0 omgezet in een lege string.
        """
        if row >= self.rows():
            self.enlarge(row)

        if not allow_zero and not f:
            self.data[row][col] = ''
        else:
            self.data[row][col] = float(f)

    def setint(self, row, col, i, allow_zero = False):
        """Set item i op col, row als int.

        Als allow_zero = False, dan word een 0 omgezet in een lege string.
        """
        if row >= self.rows():
            self.enlarge(row)

        if not allow_zero and not i:
            self.data[row][col] = ''
        else:
            self.data[row][col] = int(i)

    def setstring(self, row, col, s):
        """Set item s op col, row als string."""
        if row >= self.rows():
            self.enlarge(row)

        self.data[row][col] = str(s)

    def write(self, sheetname, left, bottom, insert = False, erase = False):
        """Schrijft de data naar een sheet sheetname.

        left is de linkse hoek, bottom het laagste rijnummer.
        Als insert = False, dat wordt eventuele data overschreven. Is insert True, dan worden er rijen ingevoegd.
        Als erase = True, dat wordt alle data met rijen hoger dan rows() verwijdert.
        """

        if not sheetname.endswith('.csv'):
            sheetname += '.csv'

        sheet = getsheetbyname(sheetname)
        if sheet:
            cols = self.columns()
        else:
            cols = len(sheet[0])

        if insert:
            it = bottom
            for i in self.data:
                sheet.insert(it, ['']*cols)
                sheet[it][left: left + self.columns()] = i
                it += 1
        else:
            for r in range(self.rows()):
                s = bottom + r
                
                while s >= len(sheet):
                    sheet.append(['']*cols)
                    
                sheet[s][left: left + self.columns()] = self.data[r]
                    
        if erase:
            sheet = sheet[:bottom + self.rows()]
            
        try:
            f = open(sheetname, 'wb')
            writer = csv.writer(f)
            writer.writerows(sheet)
            f.close()
        except:
            raise Exception('Kon sheet \'%s\' niet schrijven.' % sheetname)

class Sheet_ro(Sheet):
    pass

def layout_journaalstyle(sheet):
    """Layout volgens journaalstyle."""
    raise Exception('Dit is niet beschikbaar in CSV.')
  
def layout_balansstyle(sheet):
    """Layout volgens balansstyle."""
    raise Exception('Dit is niet beschikbaar in CSV.')
  
def layout_extrakortedc(sheet):
    """Layout extra korte dc."""
    raise Exception('Dit is niet beschikbaar in CSV.')

def createsheet(name):
    """Maak een nieuw sheet."""
    if not name.endswith('.csv'):
        name += '.csv'
    
    f = open(name, 'w')
    f.write(',,,,,,,,,\n,,,,,,,,,\n')
    f.close()

def enablekeys():
    raise Exception('Dit kan niet in CSV')
