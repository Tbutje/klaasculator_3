"""Hier staat de functies die afhankelijk zijn van openoffice.

Deze oo-afhankelijke functies zouden idealiter tot een minimum
beperkt moeten blijven, en wel in dit bestand voor overzicht.
"""

import uno
import unohelper


from com.sun.star.table import XCellRange
from com.sun.star.sheet import XSpreadsheet
from com.sun.star.sheet import XCellRangeData
from com.sun.star.table import XColumnRowRange
from com.sun.star.table import XTableRows
from com.sun.star.beans import PropertyValue
from com.sun.star.awt   import KeyEvent

import sys
import os

from time import sleep
from commands import getoutput
from threading import Lock

class OOContext:
    """Singleton class voor de openoffice context.

    Onderstaande functies hebben dat nodig. Roep voor dat je een van onderstaande functies gebruikt OOContext(ctx) in.
    Als het goed is, gebeurt dit al in unopkg/klaasculator_oo.py, wat het menutje in de balk regelt.
    """

    class ding:
        def __init__(self, ctx = None):
            self.ctx = ctx
            self.lock = Lock()
            
        def get(self):
            return self.ctx

        def activate(self):
            self.lock.acquire()
            print 'activate'

        def deactivate(self):
            self.lock.release()
            print 'deactivate'

    instance = None

    def __init__(self, ctx = None):
        if ctx != None:
            OOContext.instance = OOContext.ding(ctx)

    def __getattr__(self, attr):
        return getattr(self.instance, attr)

    def __setattr__(self, attr, value):
        return setattr(self.instance, attr, value)

def getoopath():
    """Probeert uit te zoeken waar OpenOffice is geinstalleerd.

    Misschien moet iemand met verstand van windows hier iets mooiers van maken door het pad uit de registry te halen.
    """
    if sys.platform.startswith('win'):
	for d in os.listdir('C:\\Program Files'):
            if d.startswith('OpenOffice.org 2'):
                return 'C:\\Program Files\\' + d + '\\program'
        return ''
    else:
        e = getoutput('which soffice')
        p = os.readlink(e)
        return os.path.dirname(os.path.abspath(os.path.dirname(e) + '/' + p))

def connect(args = [], path = '', wait = 0):
    """Deze functie maakt het mogelijk om openoffice vanaf de python-interpeter te starten en te bedienen.
    
    path is het pad naar OpenOffice en args een list van command-line argumenten.
    wait is het aantal seconden dat deze functie wacht met retourneren wanneer hij klaar is. Dit is handig wanneer je
    bestanden aan het laden bent, wat de OOConext is pas bruikbaar wanneer dat bestand geladen is.
    """
    if not path:
        path = getoopath()

    exe = os.path.join(path, 'scalc')
    if sys.platform.startswith('win'):
        exe += '.exe'

    command = [exe, '-accept=pipe,name=unopipe;urp;']
    command.extend(args)
    os.spawnv(os.P_NOWAIT, exe, command)

    xlc = uno.getComponentContext()
    resolver = xlc.ServiceManager.createInstanceWithContext('com.sun.star.bridge.UnoUrlResolver', xlc)

    con = 'uno:pipe,name=unopipe;urp;StarOffice.ComponentContext'
    for i in range(20):
        try:
            print 'Poging %i' % i
            ctx = resolver.resolve(con)
            OOContext(ctx)
            if wait:
                print 'Even wachten...'
                sleep(wait)
            print 'Gelukt'
            return
        except:
            sleep(0.5)
    print 'Mislukt'

  
def getactivecell():
    """Geeft de geselecteerde cel terug.

    Gewijzigd: retourneert nu niet de interne openoffice-representatie, maar de coordintaten (bv C5 als (2, 4)).
    """
    ctx = OOContext()
    desktop = ctx.get().ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', ctx.get() )
    doc = desktop.getCurrentComponent()

    select = doc.getCurrentSelection()
    cell = select.getCellAddress()
    return cell.Row, cell.Column

def getactivesheet(): # is dit nodig?
    """Geeft het geselecteerde sheet terug.

    Gewijzigd: retourneert nu de naam van het sheet i.p.v. de internte openoffice representatie.
    """
    ctx = OOContext()
    desktop = ctx.get().ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', ctx.get() )
    doc = desktop.getCurrentComponent()

    controller = doc.getCurrentController()
    sheet = controller.getActiveSheet()
    return sheet.Name

def getsheetbyname(name):
    """Retourneer het sheet 'name'."""
    ctx = OOContext()
    desktop = ctx.get().ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', ctx.get())
    doc = desktop.getCurrentComponent()

    sheets = doc.getSheets()
  
    try:
        return sheets.getByName(name)
    except:
        raise Exception('Er is geen sheet getiteld \'%s\'' % name)

def laatsteboeking(sheet):
    """Geeft het laagste index terug waarop nog dingen staan in een sheet.

    sheet kan een string zijn (de naam van een sheet), of een openoffice-sheet.
    """
    if type(sheet) == str or type(sheet) == unicode:
        sheet = getsheetbyname(sheet)
    
    c = sheet.createCursor()
    c.gotoEndOfUsedArea(False)
    return c.getRangeAddress().EndRow

class Sheet_abstract:
    """Abstrace class.

    Deze class is om code die Sheet en Sheet_ro delen in te zetten. Het is niet geschikt om direct te gebruiken.
    """
    def columns(self):
        """Het aantal kolommen."""
        return len(self.data[0])


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
            return unicode(self.data[row][col])
        except:
            return unicode('')

    def rows(self):
        """Het aantal rijen."""
        return len(self.data)

class Sheet(Sheet_abstract):
    """Deze class representeert de data op een sheet.

    Deze data kan gelezen en geschreven worden. Wanneer je de data alleen hoeft te lezen, en niet bewerken, gebruik dan
    Sheet_ro, dat is efficienter.
    """
    
    def __init__(self, sheetname, left, bottom, right, top):
        """Maak de sheet van de sheet sheetname, in de range left, bottom, right, top.
        
        Voor de goede orde: left staat voor de linker kolom, right voor de rechter, bottom voor de laagste rij (dus die
        bovenin je scherm staat) en top voor de hoogste rij (ondering je scherm). Deze zijn 0-gebasseerd.
        Dus bijvoorbeeld Sheet('Journaal', 2, 4, 5, 8) selecteerd de range C5:F9.
        """
        
        if top - bottom < 0:
            self.data = [[u'']*(right - left + 1)]
        else:

            sheet = getsheetbyname(sheetname)
            cellrange = sheet.getCellRangeByPosition(left, bottom, right, top)
            dataarray = cellrange.getDataArray()

            self.data = []
            for r in dataarray:
                self.data.append(list(r))

    def enlarge(self, newrows):
        """Maak het aantal rijen op de sheet groter tot newrows."""
        while self.rows() <= newrows:
            self.data.append([u'']*self.columns())

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

        self.data[row][col] = unicode(s)

    def write(self, sheetname, left, bottom, insert = False, erase = False):
        """Schrijft de data naar een sheet sheetname.

        left is de linkse hoek, bottom het laagste rijnummer.
        Als insert = False, dat wordt eventuele data overschreven. Is insert True, dan worden er rijen ingevoegd.
        Als erase = True, dat wordt alle data met rijen hoger dan rows() verwijdert.
        """

        sheet = getsheetbyname(sheetname)
        if insert:
            tr = sheet.getRows()
            tr.insertByIndex(bottom, self.rows())

        d = []
        for i in self.data:
            d.append(tuple(i))
            
        t = tuple(d)

        cellrange = sheet.getCellRangeByPosition(left, bottom, left + self.columns() - 1, bottom + self.rows() - 1)
        cellrange.setDataArray(t)

        if erase:
            tr = sheet.getRows()
            tr.removeByIndex(bottom + self.rows(), laatsteboeking(sheet))

class Sheet_ro(Sheet_abstract):
    """Deze class representeert de data op een sheet.

    Dit is read-only. De reden dat dit bestaat is dat OpenOffice de data
    op een sheet als tuple geeft, wat een read-only datatype is. Om ook de data te kunnen bewerken moet dus de data in
    lists worden omgezet, wat tijd kost. Op het moment dat je de data vervolgens naar het daadwerkelijke sheet wilt
    schrijven moet het weer terug naar tuples. Een hoop onnodig gekopieer dus wanneer je alleen wilt kunnen lezen.
    Gebruik dit dus als je alleen data wilt kunnen lezen van een sheet.
    """
    
    def __init__(self, sheetname, left, bottom, right, top):
        """Maak de sheet van de sheet sheetname, in de range left, bottom, right, top.
        
        Voor de goede orde: left staat voor de linker kolom, right voor de rechter, bottom voor de laagste rij (dus die
        bovenin je scherm staat) en top voor de hoogste rij (ondering je scherm). Deze zijn 0-gebasseerd.
        Dus bijvoorbeeld Sheet('Journaal', 2, 4, 5, 8) selecteerd de range C5:E9.
        """
        if top - bottom < 0:
            self.data = ((u'',)*(right - left + 1),)
        else:
            sheet = getsheetbyname(sheetname)
            cellrange = sheet.getCellRangeByPosition(left, bottom, right, top)
            self.data = cellrange.getDataArray()

    def write(self, sheetname, left, bottom, insert = False, erase = False):
        """Schrijft de data naar een sheet sheetname.

        left is de linkse hoek, bottom het laagste rijnummer.
        Als insert = False, dat wordt eventuele data overschreven. Is insert True, dan worden er rijen ingevoegd.
        Als erase = True, dat wordt alle data met rijen hoger dan rows() verwijdert.
        """
        sheet = getsheetbyname(sheetname)
        if insert:
            tr = sheet.getRows()
            tr.insertByIndex(bottom, self.rows())

        cellrange = sheet.getCellRangeByPosition(left, bottom, left + self.columns() - 1, bottom + self.rows() - 1)
        cellrange.setDataArray(self.data)

        if erase:
            tr = sheet.getRows()
            tr.removeByIndex(bottom + self.rows(), laatsteboeking(sheet))

def layout_journaalstyle(sheet):
    """Layout volgens journaalstyle."""
    if type(sheet) == str or type(sheet) == unicode:
        sheet = getsheetbyname(sheet)

    sheet.setPropertyValue('CharFontFamily', 5)
    sheet.setPropertyValue('CharHeight', 10)
    sheet.setPropertyValue('CharWeight', 100)
    sheet.setPropertyValue('CharPosture', 0)
    sheet.setPropertyValue('HoriJustify', 0)
    sheet.setPropertyValue('VertJustify', 2)

    for c in range(10):
        width = 1500
        numberformat = 0

        if c == 1:
            width = 2000
            numberformat = 39
        elif c == 3:
            width = 1000
        elif c == 4:
            width = 8000
        elif c == 7:
            width = 3000
            numberformat = 4
        elif c == 8:
            width = 3000
            numberformat = 4
        elif c == 9:
            width = 8000

        col = sheet.getColumns().getByIndex(c)
        col.setPropertyValue('NumberFormat', numberformat)
        col.setPropertyValue('Width', width)

    for r in range(2):
        row = sheet.getRows().getByIndex(r)
        row.setPropertyValue('CharWeight', 150)
        row.setPropertyValue('HoriJustify', 2)

def layout_balansstyle(sheet):
    """Layout volgens balansstyle."""
    if type(sheet) == str or type(sheet) == unicode:
        sheet = getsheetbyname(sheet)

    sheet.setPropertyValue('CharFontFamily', 5)
    sheet.setPropertyValue('CharHeight', 10)
    sheet.setPropertyValue('CharWeight', 100)
    sheet.setPropertyValue('CharPosture', 0)
    sheet.setPropertyValue('HoriJustify', 0)
    sheet.setPropertyValue('VertJustify', 2)

    for c in range(8):
        width = 1500
        numberformat = 0

        if c == 2:
            width = 500
        elif c == 3:
            width = 8000
        elif c == 4:
            width = 500
        elif c == 5:
            width = 500
        elif c == 6:
            width = 3000
            numberformat = 4
        elif c == 7:
            width = 3000
            numberformat = 4

        col = sheet.getColumns().getByIndex(c)
        col.setPropertyValue('NumberFormat', numberformat)
        col.setPropertyValue('Width', width)

    for r in range(4):
        row = sheet.getRows().getByIndex(r)
        row.setPropertyValue('CharWeight', 150)
        row.setPropertyValue('HoriJustify', 2)

def layout_extrakortedc(sheet):
    """Layout extra korte dc."""
    if type(sheet) == str or type(sheet) == unicode:
        sheet = getsheetbyname(sheet)

    sheet.setPropertyValue('CharFontFamily', 5)
    sheet.setPropertyValue('CharHeight', 10)
    sheet.setPropertyValue('CharWeight', 100)
    sheet.setPropertyValue('CharPosture', 0)
    sheet.setPropertyValue('HoriJustify', 0)
    sheet.setPropertyValue('VertJustify', 2)

    for c in range(4):
        width = 8000
        numberformat = 0

        if c == 1 or c == 2:
            width = 3000
            numberformat = 2

        col = sheet.getColumns().getByIndex(c)
        col.setPropertyValue('NumberFormat', numberformat)
        col.setPropertyValue('Width', width)

def createsheet(name):
    """Maak een nieuw sheet."""
    ctx = OOContext()
    desktop = ctx.get().ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', ctx.get())
    doc = desktop.getCurrentComponent()
    sheets = doc.getSheets()

    try:
        getsheetbyname(name)
        sheets.removeByName(name)
    except:
        pass

    sheets.insertNewByName(name, sheets.Count)

# oud en niet meer gebruikt, maar laat even staan in het kader 'nooit code weggooien'
class EnableKeys:
    """Dit regelt sneltoetsen.

    Het leest eerst eventueel bestaande definities en schrijft nieuwe eroverheen.
    Voor het gemak begint alles met shift-alt (want die gebruikt openoffice zelf nog niet.

    Als idee: zou je hier met een grafische interface dit dynamisch aan kunnen passen?
    """

    def __init__(self):
        """Lees bestaande."""
        ctx = OOContext()
        inst = ctx.get().ServiceManager.createInstance('com.sun.star.comp.framework.PathSubstitution')

        userdir = inst.getSubstituteVariableValue('$(user)')
        lang = inst.getSubstituteVariableValue('$(vlang)')

        sdirs = ('config', 'soffice.cfg', 'modules', 'scalc', 'accelerator', lang)

        d = uno.fileUrlToSystemPath(userdir)
        for sd in sdirs:
            d = os.path.join(d, sd)
            if not os.path.exists(d):
                print 'mkdir', d
                os.mkdir(d)

        self.fname = os.path.join(d, 'current.xml')

        self.head = ['<?xml version="1.0" encoding="UTF-8"?>\n', '<accel:acceleratorlist xmlns:accel="http://openoffice.org/2001/accel" xmlns:xlink="http://www.w3.org/1999/xlink">\n']
        self.tail = ['</accel:acceleratorlist>\n']
        self.lines = []

        try:
            f = open(self.fname, 'r')
            for line in f.readlines():
                if line.strip().startswith('<accel:item') and not 'klaasculator' in line:
                    self.lines.append(line + '')
            f.close()
        except Exception, e:
            print e
            print 'geen bestaande regels gelezen.'

        self.addkeys()
        self.write()

    def addkeys(self):
        keys = {'T' : 'Tegenregel',
                'R' : 'Selecteer een relatie',
                'C' : 'Compileer Alles',
                'D' : 'Debug',
                'O' : 'Baromzet',
                'N' : 'NICO',
                'X' : 'TCS',
                'L' : 'Levering',
                'B' : 'BTW',
                'P' : 'Python Console'}
        for k, v in keys.iteritems():
            self.addkey(k, v)                    

    def addkey(self, key, function):
        self.lines.append('\t<accel:item accel:code="KEY_%s" accel:shift="true" accel:mod2="true" xlink:href="service:klaasculator_oo.Verkeersregelaar?%s"/>\n' % (key.upper()[0], function.replace(' ', '_')))

    def write(self):
        f = open(self.fname, 'w')
        for l in self.head:
            f.write(l)
        for l in self.lines:
            f.write(l)
        for l in self.tail:
            f.write(l)
        f.close()

# reference: http://wiki.services.openoffice.org/wiki/Framework/Tutorial/Accelerators
def enablekeys():
    ctx = OOContext()
    cfg = ctx.get().ServiceManager.createInstance('com.sun.star.ui.GlobalAcceleratorConfiguration')

    # magic numbers:
    SHIFT = 1
    CNTRL = 2
    ALT   = 4

    keys = {'T' : 'Tegenregel',
            'R' : 'Selecteer een relatie',
            'C' : 'Compileer Alles',
            'D' : 'Debug',
            'O' : 'Baromzet',
            'N' : 'NICO',
            'P' : 'Python Console'}

    # meer magic numbers:
    keycode = lambda k: ord(k) - ord('A') + 512
    
    for key, name in keys.iteritems():
        kevent = KeyEvent()
        print  key, keycode(key)
        kevent.KeyCode = keycode(key)
        kevent.Modifiers = SHIFT | ALT

        cfg.setKeyEvent(kevent, 'service:klaasculator_oo.Verkeersregelaar?%s' % name.replace(' ', '_'))

    cfg.store()
   
