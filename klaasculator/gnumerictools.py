"""Hier staat de functies die afhankelijk zijn van gnumeric.

Om even aan te tonen dat het kan, werkt de klaasculator namelijk ook in gnumeric.
"""

from Gnumeric import *

import sys
import os

def getactivecell(): # is dit nodig?
    """Geeft de geselecteerde cel terug."""
    raise Exception('Dit kan helaas niet in Gnumeric.')

def getactivesheet(): # is dit nodig?
    """Geeft het geselecteerde sheet terug."""
    raise Exception('Dit kan helaas niet in Gnumeric.')

def getsheetbyname(name):
    """Retourneer het sheet 'name'."""
    wb = workbooks()[0]
    for s in wb.sheets():
        if s.get_name_unquoted() == name:
            return s
    raise Exception('Er is geen sheet getitels \'%s\'' % name)

def laatsteboeking(sheet):
    """Geeft het laagste index terug waarop nog dingen staan in een sheet.

    sheet kan een string zijn (de naam van een sheet), of een gnumeric-sheet.
    """
    if type(sheet) == str or type(sheet) == unicode:
        sheet = getsheetbyname(sheet)

    ran = sheet.get_extent()
    return ran.get_tuple()[3]

class Sheet:
    """Deze class representeert de data op een sheet."""
    
    def __init__(self, sheetname, left, bottom, right, top):
        """Maak de sheet van de sheet sheetname, in de range left, bottom, right, top.
        
        Voor de goede orde: left staat voor de linker kolom, right voor de rechter, bottom voor de laagste rij (dus die
        bovenin je scherm staat) en top voor de hoogste rij (ondering je scherm). Deze zijn 0-gebasseerd.
        Dus bijvoorbeeld Sheet('Journaal', 2, 4, 5, 8) selecteerd de range C5:E9.
        """
        if top - bottom < 0:
            self.data = [[u'']*(right - left + 1)]
        else:
            sheet = getsheetbyname(sheetname)
            self.data = []
            rows = top - bottom
            cols = right - left
            for r in range(rows + 1):
                row = []
                for c in range(cols + 1):
                    cell = sheet.cell_fetch(left + c, bottom + r)
                    v = cell.get_value()
                    if v == 'None':
                        row.append(u'')
                    else:
                        row.append(v)
                self.data.append(row)

    def columns(self):
        """Het aantal kolommen."""
        return len(self.data[0])

    def enlarge(self, newrows):
        """Maak het aantal rijen op de sheet groter tot newrows."""
        while self.rows() <= newrows:
            self.data.append([u'']*self.columns())

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
            self.data[row][col] = u''
        else:
            self.data[row][col] = float(f)

    def setint(self, row, col, i, allow_zero = False):
        """Set item i op col, row als int.

        Als allow_zero = False, dan word een 0 omgezet in een lege string.
        """
        if row >= self.rows():
            self.enlarge(row)

        if not allow_zero and not i:
            self.data[row][col] = u''
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

        sheet = getsheetbyname(sheetname)

        if insert: # inefficient
            size = laatsteboeking(sheetname)
            if size < bottom + self.rows():
                size = bottom + self.rows()
            temp = Sheet(sheetname, 0, 0, self.columns() - 1, size)
            it = bottom
            for i in self.data:
                temp.data.insert(it, i)
                it += 1
            temp.write(sheetname, 0, 0, False, erase)
            return
                
        for r in range(self.rows()):
            for c in range(self.columns()):
                cell = sheet.cell_fetch(left + c, bottom + r)
                s = self.data[r][c]
                if type(s) == float:
                    cell.set_text('%.2f' % s)
                elif type(s) == int:
                    cell.set_text('%i' % s)
                elif s == None:
                    cell.set_text('')
                else:
                    cell.set_text(str(s))

        if erase:
            for r in range(bottom + self.rows(), laatsteboeking(sheet)):
                for c in range(self.columns()):
                    cell = sheet.cell_fetch(left + c, r)
                    cell.set_text('')

class Sheet_ro(Sheet):
    def __init__(self, sheetname, left, bottom, right, top):
        Sheet.__init__(self, sheetname, left, bottom, right, top)

def layout_journaalstyle(sheet):
    """Layout volgens journaalstyle."""
    raise Exception('Dit is niet beschikbaar in Gnumeric')

def layout_balansstyle(sheetname):
    """Layout volgens balansstyle."""
    raise Exception('Dit is niet beschikbaar in Gnumeric')
    
def layout_extrakortedc(sheet):
    """Layout extra korte dc."""
    raise Exception('Dit is niet beschikbaar in Gnumeric')

def createsheet(name):
    """Maak een nieuw sheet."""
    try:
        s = getsheetbyname(name)
        r = s.get_extent().get_tuple()
        sh = Sheet(name, 0, 0, r[2], 0)
        sh.write(name, 0, 0, erase = True)
    except Exception, e:
        print e
        wb = workbooks()[0]
        s = wb.sheet_add()
        s.rename(name)

def enablekeys():
    raise Exception('Dit kan niet in Gnumeric')
