import sys
import os

"""Handige functies.

In dit bestand staan die functies die je vaker zult willen gebruiken. Zie ook powertools.py voor funcies die op een hoger
niveau opereren.
"""

# Zo bepalen we in welk spreadsheetprogramma we zitten: door de naam aan sys.argv toe te voegen
if 'gnumeric' in sys.argv:
    from gnumerictools import *
    print 'Gnumeric loaded'
elif 'openoffice' in sys.argv:
    from ootools import *
    print 'OpenOffice loaded'
else:
    from csvtools import *
    print 'CSV loaded'
    

from gtktools import *

from datetime import date
from traceback import print_exc
from StringIO import StringIO

def gettraceback():
    """ Genereert de traceback van de laatste Exception, handig voor debuggen. """
    s = StringIO()
    print_exc(10, s)
    trace = '\n%s' % s.getvalue()
    s.close()
    return trace

class Fout(Exception):
    """Foutmelding.

    Wanneer je een fout hebt waar je rekening mee wilt houden, gooi dan deze exceptie. Deze wordt afgevangen. Andere
    excepties worden ook afgevangen, maar worden als bugs behandeld.
    """
    def __init__(self, msg = '', traceback = ''):
        self.traceback = traceback
        Exception.__init__(self, msg)

    def settraceback(self, traceback):
        """Handig."""
        self.traceback = traceback

    def show(self, show_tr = False):
        print str(self)
        w = gtkwindow('Oei')
        b = gtk.Button(stock = gtk.STOCK_OK)
        b.connect_object('clicked', gtk.Widget.destroy, w)
        t = gtk.ToggleButton('Traceback')
        t.connect('toggled', self.tr)

        # raar, maar even nodig voor het plaatje
        temp = gtk.Button(stock = gtk.STOCK_PREFERENCES)
        t.set_image(temp.get_image())

        msg = str(self)

        if show_tr:
            msg = '\n\n'.join((msg, self.traceback))
            self.label = gtk.Label()
            t.set_active(True)
            
        self.label = gtk.Label(msg)
        box = gtkvbox()
        box.pack_start(self.label)
        box2 = gtkhbuttonbox()
        box2.pack_start(b)
        box2.pack_start(t)
        box.pack_start(box2)
        w.add(box)
        w.show_all()
        gtk.main()

    def tr(self, button):
        if button.get_active():
            self.label.set_text('\n\n'.join((str(self), self.traceback)))
        else:
            self.label.set_text(str(self))
        
def coord(s):
    """Dit vertaalt een string als 'A1' in coordinaten-tuple.

    'A1' wordt dus (0, 0) en B3 wordt (1, 2).
    """
    if s[0].isupper(): #hoofdletter
        return (ord(s[0]) - 65, int(s[1:]) - 1)
    else: # kleine letter
        return (ord(s[0]) - 97, int(s[1:]) - 1)

def getcellint(sheetname, cr):
    """Geef de inhoud van een cell als int.

    Dus bijvoorbeeld getcellstring('Info', 'C10') geeft de url naar het configuratiebestand.
    """
    c, r = coord(cr)
    sheet = Sheet_ro(sheetname, c, r, c, r)
    return sheet.getint(0, 0)

def getcellfloat(sheetname, cr):
    """Geef de inhoud van een cell als float.

    Dus bijvoorbeeld getcellstring('Info', 'C10') geeft de url naar het configuratiebestand.
    """
    c, r = coord(cr)
    sheet = Sheet_ro(sheetname, c, r, c, r)
    return sheet.getfloat(0, 0)

def getcellstring(sheetname, cr):
    """Geef de inhoud van een cell als string.

    Dus bijvoorbeeld getcellstring('Info', 'C10') geeft de url naar het configuratiebestand.
    """
    c, r = coord(cr)
    sheet = Sheet_ro(sheetname, c, r, c, r)
    return sheet.getstring(0, 0)

def setcellint(sheetname, cr, i, allow_zero = False):
    """Zet de inhoud van een cell als int.

    Als allow_zero == True, dan wordt een 0 omgezet in een lege string
    """
    c, r = coord(cr)
    sheet = Sheet(sheetname, c, r, c, r)
    sheet.setint(0, 0, i, allow_zero)
    sheet.write(sheetname, c, r)

def setcellfloat(sheetname, cr, f, allow_zero = False):
    """Zet de inhoud van een cell als float.

    Als allow_zero == True, dan wordt een 0 omgezet in een lege string.
    """
    c, r = coord(cr)
    sheet = Sheet(sheetname, c, r, c, r)
    sheet.setfloat(0, 0, f, allow_zero)
    sheet.write(sheetname, c, r)

def setcellstring(sheetname, cr, s):
    """Zet de inhoud van een cell als string."""
    c, r = coord(cr)
    sheet = Sheet(sheetname, c, r, c, r)
    sheet.setstring(0, 0, s)
    sheet.write(sheetname, c, r)

def datetoint(dag, maand, jaar):
    """Geef de int-representatie van een datum.

    De int hoort het aantal dagen sinds 30 december 1899 te zijn (waarom niet 1-1-1900 weet ik ook niet).
    """
    datum = date(jaar, maand, dag)
    epoch = date(1899, 12, 30)
    return datum.toordinal() - epoch.toordinal()

def inttodate(d):
    """Analoog aan datetoint.

    Geeft een (dag, maand, jaar) tuple.
    """
    epoch = date(1899, 12, 30)
    datum = date.fromordinal(d + epoch.toordinal())
    return datum.day, datum.month, datum.year

def btw_inctoexc(euro_inc, tarief):
    """Maakt van een bedrag inclusief btw een bedrag exlusief btw.

    Dit geeft een tuple, waarvan het eerste element het bedrag exclusief btw is en het tweede de btw. tarief is het 
    btw-tarief (dus 0.19 of 0.06).
    """
    exc = euro_inc / (1.0 + tarief)
    btw = euro_inc - exc
    return exc, btw

def btw_exctoinc(euro_exc, tarief):
    """Analoog aan btw_inctoexc."""
    btw = euro_exc * tarief
    inc = euro_exc + btw
    return inc, btw

def sorter(iterable, cmpfunc = None):
    """Hek voor windoows.

    De windows-versie van OpenOffice zit nog met python 2.3, en dat heeft kennelijk geen sorted-functie. Daarom maar
    zelf implementeren.
    """
    try:
        return sorted(iterable, cmpfunc)
    except:
        copy = map(None, iterable)
        copy.sort(cmpfunc)
        return copy

def getbegindatum():
    return getcellint('Info', 'C6')

def geteinddatum():
    return getcellint('Info', 'C8')


