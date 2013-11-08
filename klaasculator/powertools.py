from boekstuk import *
from tools import *
from sheet import *
from config import *
from relaties import *

import re

"""Powertools.

In dit bestand staan handige functies, vergelijkbaar met tools.py. Deze staan echter in een apart bestand om circulaire
dependencies te voorkomen. Dit zijn namelijk functies op een hoger niveau en zijn zelf ook ergens afhankelijk van.
Bijvoorbeeld: veel van deze functies zijn afhankelijk van config.py, maar config.py is zelf ook afhankelijk van tools.py,
daarom moeten deze functies in een apart bestand.
"""
   
def appendboekstuk(boekstuk_tail, row = 0, sheetname = 'Journaal'):
    """Dit voegt de regels in boekstuk_tail toe aan het journaal.

    Dit is voor die gevallen dat het boekstuk al gedeeltelijk bestaat. Als row != 0, wordt het op die regel bijgeschreven,
    anders wordt het zelf uitgezocht.
    """
    if row:
        row -= 1
    else:
        journaal = Sheet_jr_ro(sheetname)
        row = journaal.find(boekstuk_tail.nummer, boekstuk_tail.datum) + 2

    journaal = Sheet_jr(None, row)
    i = 0
    for b in boekstuk_tail:
        journaal.setboekregel(i, b)
        i += 1

    journaal.write(sheetname, True, False)

def replaceboekstuk(boekstuk, row, sheetname = 'Journaal'):
    s = Sheet_jr_ro(sheetname)

    while s.getint(row, 0) and s.getint(row, 1):
        row -= 1
        if row == -1:
            break

    count = 0
    row += 1
        
    while s.getint(row + count, 0) and s.getint(row + count, 1):
        count += 1

    s = Sheet_jr(None, row + 2)
    for i in range(count):
        if i < len(boekstuk):
            s.setboekregel(i, boekstuk[i])
        else:
            s.setboekregel(i, Boekregel())
    s.write(sheetname, False, False)
    if boekstuk[count:]:
        appendboekstuk(boekstuk[count:], row + 2 + count, sheetname)
    return len(boekstuk) - count

class BoekstukIter:
    """Dit maakt het mogelijk om over een Journaal te itereren, maar dan als Boekstukken i.p.v. Boekregels.

    Gebruiksvoorbeeld:
    boekstukiter = BoekstukIter('Journaal')
    for boekstuk in boekstukiter:
        print boekstuk # of doe iets anders met het boekstuk.
    """
    def __init__(self, naam = 'Journaal'):
        self.sheet = Sheet_jr_ro(naam)

    def __iter__(self):
        self.i = iter(self.sheet)
        self.row = self.i.i
        return self

    def next(self):
        regel = self.i.next() # raist StopIteration als er niets meer is
        self.row = self.i.i
        boekstuk = Boekstuk(regel.nummer, regel.datum)
        boekstuk.append(regel)

        try:
            regel = self.i.next()
            while regel.nummer == boekstuk.nummer and regel.datum == boekstuk.datum:
                boekstuk.append(regel)
                regel = self.i.next()
            self.i.i -= 1 # we hebben 1 teveel gelezen.
        except StopIteration: # dit is het laatste boekstuk, pas de volgende next moeten we zelf StopIteration raisen
            pass
        return boekstuk

def matchrelatie(completion, estr, iter):
    """Hulpfunctie voor relatiewidget."""
    mstr = completion.get_model()[iter][0]
    return estr.lower() in mstr.lower()

def relatiewidget(incleden = True, incolv = False, incextern = False):
    """Relatiewidget.

    Even buiten de class gezet omdat ik vermoed dat dit te hergebruiken is.
    """
    completion = gtk.EntryCompletion()
    store = gtk.ListStore(str)

    rel = Relaties()
    if incleden:
        for r in sorter(rel.leden):
            store.append([r])
    if incolv:
        for r in sorter(rel.olv):
            store.append([r])
    if incextern:
        for r in sorter(rel.extern):
            store.append([r])
    
    completion.set_model(store)
    completion.set_text_column(0)
    completion.set_match_func(matchrelatie)

    entry = gtk.combo_box_entry_new_text()
    entry.set_model(store)
    
    entry.set_active(0)
    entry.child.set_completion(completion)
    entry.child.set_text('Selecteer een naam:')
    entry.child.set_width_chars(30)
    return entry

def writeboekstuk(boekstuk, sheetname = 'Journaal'):
    """Deze functie schrijft een boekstuk naar het journaal.

    Het nummer wordt hier ook bepaald. Als 'idiotproof:autosort' is opgegeven in de configuratie, dan wordt het op de
    juiste plek in het journaal gezet (gaat er wel van uit dat het journaal als gesorteerd is). Ander komt het achteraan.
    """
    conf = Config()
    if conf.getvar('idiotproof:autosort'):
        journaal = Sheet_jr_ro(sheetname)
        row = journaal.find(0, boekstuk.datum + 1)

        if row < 2:
            row = -1
            boekstuk.setnummer(1)
        elif journaal.getint(row - 2, 1) == boekstuk.datum:
            nummer = journaal.getint(row - 2, 0) + 1
            boekstuk.setnummer(nummer)
        else:
            boekstuk.setnummer(1)

        journaal = Sheet_jr(None, row + 3)

        i = 0
        for b in boekstuk:
            journaal.setboekregel(i, b)
            i += 1
        journaal.setboekregel(i, Boekregel())
        journaal.write(sheetname, True, False)
    else:
        journaal = Sheet_jr_ro(sheetname)
        row = journaal.rows() + 3

        if journaal.getint(row - 4, 1) == boekstuk.datum:
            nummer = journaal.getint(row - 4, 0) + 1
            boekstuk.setnummer(nummer)
        else:
            boekstuk.setnummer(1)

        if row < 5:
            row = 2
        
        journaal = Sheet_jr(None, row)
        i = 0
        for b in boekstuk:
            journaal.setboekregel(i, b)
            i += 1

        journaal.write(sheetname)

class BoekstukWidget:
    """Gtk-widget voor een boekstuk.

    Ga er maar even voor zitten, want het is een berg code, maar het is dik! Dit maakt het mogelijk om boekstukken te laten
    zien in gtk. Met de widget-member kun je die krijgen, voorbeeld:
    window = gtkwindow()
    bw = BoekstukWidget()
    bw.set_editable(True)
    bw.set_boekstuk(Boekstuk())
    window.add(bw.widget) # <= dit is belangrijk
    window.show_all()
    gtk.main()
    Nu heb je al een window met een (leeg) boekstuk erin. Belangrijkste functies:
    
    (get/set)_editable, hiermee regel je of het boekstuk bewerkt kan worden (behalve het kascie-veld). Ook laat dit de
      bewerk-knoptjes zien.
    (get/set)_kascie, hiermee regel je of het kascie-veld beschreven kan worden en laat kascieknopjes zien.
    (get/set)_boekstuk spreekt voor zich.
    """
    
    def __init__(self):
        self.widget = gtkvbox() # de widget zelf in een vbox

        # nummer en datum:
        nummerdatum = gtkhbox()

        nummerlabel = gtk.Label('Nummer:')
        self.nummer = gtkentry(INT)
        datumlabel  = gtk.Label('Datum:')
        self.datum  = gtkentry(DATUM)

        # nummer en datum op niet-editable zetten:
        self.nummer.set_editable(False)
        self.nummer.configure(gtk.Adjustment(0, 0, 0), 0, 0)
        for d in self.datum:
            d.set_editable(False)

        v = self.datum[0].get_value_as_int()
        self.datum[0].configure(gtk.Adjustment(v, v, v), 0, 0)
        v = self.datum[1].get_value_as_int()
        self.datum[1].configure(gtk.Adjustment(v, v, v), 0, 0)
        v = self.datum[2].get_value_as_int()
        self.datum[2].configure(gtk.Adjustment(v, v, v), 0, 0)
        
        nummerdatum.pack_start(nummerlabel)
        nummerdatum.pack_start(self.nummer)
        nummerdatum.pack_start(datumlabel)

        hbox = gtkhbox()
        hbox.pack_start(self.datum[0])
        hbox.pack_start(self.datum[1])
        hbox.pack_start(self.datum[2])
        nummerdatum.pack_start(hbox)

        self.widget.pack_start(nummerdatum, expand = False)

        # De tabel. Hier worden alleen de labels ingevuld, de regel gaan met set_boekregel
        self.table = gtktable(1, 8)
        self.table.attach(gtk.Label('Rekening:'), 0, 1, 0, 1)
        self.table.attach(gtk.Label('Kascie:'), 1, 2, 0, 1)
        self.table.attach(gtk.Label('Hoofdomschrijving:'), 2, 3, 0, 1)
        self.table.attach(gtk.Label('Tegenrekening 2:'), 3, 4, 0, 1)
        self.table.attach(gtk.Label('Tegenrekening 1:'), 4, 5, 0, 1)
        self.table.attach(gtk.Label('Debet:'), 5, 6, 0, 1)
        self.table.attach(gtk.Label('Credit:'), 6, 7, 0, 1)
        self.table.attach(gtk.Label('Extra Omschrijving:'), 7, 8, 0, 1)

        # lists om references naar de velden de houden.
        self.rekening = []
        self.kascie = []
        self.hoofdomschrijving = []
        self.tegenrekening2 = []
        self.tegenrekening1 = []
        self.debet = []
        self.credit = []
        self.extraomschrijving = []

        # table in een scrollwindow zetten
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        tmp = gtk.VBox()
        tmp.pack_start(self.table, expand = False)
        scroll.add_with_viewport(tmp)
        self.widget.pack_start(scroll, expand = True)

        # bewerk-knopjes. merk op dat deze nog niet in self.widget worden gezet
        self.buttons = gtkhbuttonbox()
        tmp = gtk.Button(stock = gtk.STOCK_ADD)
        add = gtk.Button('Regel toevoegen')
        add.set_image(tmp.get_image())
        add.connect('clicked', self.add)
        self.buttons.pack_start(add)

        tmp = gtk.Button(stock = gtk.STOCK_PREFERENCES)

        balanceer = gtk.Button('Balanceer')
        balanceer.set_image(tmp.get_image())
        balanceer.connect('clicked', self.balanceer)
        self.buttons.pack_start(balanceer)

        tmp = gtk.Button(stock = gtk.STOCK_PREFERENCES)
        tegenregel = gtk.Button('Tegenregel')
        tegenregel.set_image(tmp.get_image())
        tegenregel.connect('clicked', self.tegenregel)
        self.buttons.pack_start(tegenregel)

        # kascieknopjes. merk op dat deze nog niet in self.widget worden gezet
        self.kasciebuttons = gtkhbuttonbox()

        tmp = gtk.Button(stock = gtk.STOCK_NO)
        ok = gtk.Button('Afkeuren')
        ok.set_image(tmp.get_image())
        ok.connect('clicked', self.afkeuren)
        self.kasciebuttons.pack_start(ok)

        tmp = gtk.Button(stock = gtk.STOCK_YES)
        nee = gtk.Button('Goedkeuren')
        nee.set_image(tmp.get_image())
        nee.connect('clicked', self.goedkeuren)
        self.kasciebuttons.pack_start(nee)

        # per default is het niet editable en niet kascie
        self.iseditable = False
        self.iskascie = False
        
    def add(self, b):
        """Voor het bewerk-knopje 'regel toevoegen'."""
        self.set_boekregel(Boekregel())
        self.widget.show_all()

    def afkeuren(self, b):
        """Voor het kascie-knopje 'afkeuren'."""
        for k in self.kascie:
            k.set_text('y')

    def balanceer(self, b):
        """Voor het bewer-knopje 'balanceer'."""
        bk = self.get_boekstuk()
        if not bk.inbalans():
            bk.balanceer()
            self.set_boekregel(bk[-1])
        self.widget.show_all()

    def get_boekstuk(self):
        boekstuk = Boekstuk(self.nummer.get_value_as_int(),
                            datetoint(self.datum[0].get_value_as_int(),
                                      self.datum[1].get_value_as_int(),
                                      self.datum[2].get_value_as_int()))

        for i in range(len(self.rekening)):
            boekstuk.append(Boekregel(0, 0,
                                      self.rekening[i].get_value_as_int(),
                                      self.kascie[i].get_text(),
                                      self.hoofdomschrijving[i].get_text(),
                                      self.tegenrekening2[i].get_value_as_int(),
                                      self.tegenrekening1[i].get_value_as_int(),
                                      Euro(self.debet[i].get_value() - self.credit[i].get_value()),
                                      self.extraomschrijving[i].get_text()))
        return boekstuk

    def get_editable(self):
        return self.iseditable

    def goedkeuren(self, b):
        """Voor het kascie-knopje 'goedkeuren'."""
        for k in self.kascie:
            k.set_text('x')

    def set_editable(self, e):
        if e:
            # knopjes verwijderen:
            if not self.iseditable:
                self.widget.pack_start(self.buttons, expand = False)
                self.widget.show_all()
            
            self.iseditable = True

            # nummer en datum (merk op dat voor spinbuttons je ook de adjustment aan moet passen met configure)
            self.nummer.set_editable(True)
            self.nummer.configure(gtk.Adjustment(self.nummer.get_value_as_int(), 1, 999, 1, 10), 0, 0)
            for d in self.datum:
                d.set_editable(True)
            self.datum[0].configure(gtk.Adjustment(self.datum[0].get_value_as_int(), 1, 31, 1, 10), 0, 0)
            self.datum[1].configure(gtk.Adjustment(self.datum[1].get_value_as_int(), 1, 12, 1, 10), 0, 0)
            v = self.datum[2].get_value_as_int()
            self.datum[2].configure(gtk.Adjustment(v, v - 100, v + 100, 1, 10), 0, 0)

            # de regels:
            for i in range(len(self.rekening)):
                self.rekening[i].set_editable(True)
                self.rekening[i].configure(gtk.Adjustment(self.rekening[i].get_value_as_int(), 0, 999, 1, 10), 0, 0)
                self.hoofdomschrijving[i].set_editable(True)
                self.tegenrekening2[i].set_editable(False)
                self.tegenrekening2[i].configure(gtk.Adjustment(self.tegenrekening2[i].get_value_as_int(), 0, 999, 1, 10),
                                                 0, 0)
                self.tegenrekening1[i].set_editable(False)
                self.tegenrekening1[i].configure(gtk.Adjustment(self.tegenrekening1[i].get_value_as_int(), 0, 999, 1, 10),
                                                 0, 0)
                self.debet[i].set_editable(True)
                self.debet[i].configure(gtk.Adjustment(self.debet[i].get_value(), 0, 999999999, 0.01, 1), 0.0, 2)
                self.credit[i].set_editable(True)
                self.credit[i].configure(gtk.Adjustment(self.credit[i].get_value(), 0, 999999999, 0.01, 1), 0.0, 2)
                self.extraomschrijving[i].set_editable(True)
        else:
            # knopjes toevoegen
            if self.iseditable:
                self.widget.remove(self.buttons)
                self.widget.show_all()
            
            self.iseditable = False

            # nummer en datum (merk op dat voor spinbuttons je ook de adjustment aan moet passen met configure)
            self.nummer.set_editable(False)
            v = self.nummer.get_value_as_int()
            self.nummer.configure(gtk.Adjustment(v, v, v), 0, 0)
            for d in self.datum:
                d.set_editable(False)

            v = self.datum[0].get_value_as_int()
            self.datum[0].configure(gtk.Adjustment(v, v, v), 0, 0)
            v = self.datum[1].get_value_as_int()
            self.datum[1].configure(gtk.Adjustment(v, v, v), 0, 0)
            v = self.datum[2].get_value_as_int()
            self.datum[2].configure(gtk.Adjustment(v, v, v), 0, 0)

            # de regels:
            for i in range(len(self.rekening)):
                self.rekening[i].set_editable(False)
                v = self.rekening[i].get_value_as_int()
                self.rekening[i].configure(gtk.Adjustment(v, v, v), 0, 0)
                self.hoofdomschrijving[i].set_editable(False)
                self.tegenrekening2[i].set_editable(False)
                v = self.tegenrekening2[i].get_value_as_int()
                self.tegenrekening2[i].configure(gtk.Adjustment(v, v, v), 0, 0)
                self.tegenrekening1[i].set_editable(False)
                v = self.tegenrekening1[i].get_value_as_int()
                self.tegenrekening1[i].configure(gtk.Adjustment(v, v, v), 0, 0)
                v = self.debet[i].get_value()
                self.debet[i].set_editable(False)
                self.debet[i].configure(gtk.Adjustment(v, v, v), 0, 2)
                self.credit[i].set_editable(False)
                v = self.credit[i].get_value()
                self.credit[i].configure(gtk.Adjustment(v, v, v), 0, 2)
                self.extraomschrijving[i].set_editable(False)

    def get_kascie(self):
        return self.iskascie

    def set_kascie(self, k):
        if k:
            # de knopjes:
            if not self.iskascie:
                self.widget.pack_start(self.kasciebuttons, expand = False)
                self.widget.show_all()
            self.iskascie = True
        else:
            if self.iskascie:
                self.widget.remove(self.kasciebuttons)
                self.widget.show_all()
            self.iskascie = False

        # de regels:
        for i in self.kascie:
            i.set_editable(self.iskascie)
            
    def set_boekregel(self, b):
        """Zet een nieuwe boekregel in de tabel.

        Een hoop code, maar spreek grotendeels voor zich.
        """
        # tabel vergroten:
        row = self.table.get_property('n-rows')
        self.table.resize(row + 1, 2)

        # entrys maken
        rekening          = gtkentry(INT, 0, 999)
        kascie            = gtkentry(STRING)
        hoofdomschrijving = gtkentry(STRING)
        tegenrekening2    = gtkentry(INT, 0, 999)
        tegenrekening1    = gtkentry(INT, 0, 999)
        debet             = gtkentry(FLOAT, 0)
        credit            = gtkentry(FLOAT, 0)
        extraomschrijving = gtkentry(STRING)

        kascie.set_width_chars(5)

        # waarden invullens
        rekening.set_value(b.rekening)
        kascie.set_text(b.kascie)
        hoofdomschrijving.set_text(b.omschrijving)
        tegenrekening2.set_value(b.tegen2)
        tegenrekening1.set_value(b.tegen)
        debet.set_value(b.waarde.floatt()[0])
        credit.set_value(b.waarde.floatt()[1])
        extraomschrijving.set_text(b.omschrijving2)

        # eventueel kascie en editable uitzetten:
        if not self.iskascie:
            kascie.set_editable(False)

        if not self.iseditable:
            rekening.set_editable(False)
            rekening.configure(gtk.Adjustment(b.rekening, b.rekening, b.rekening), 0, 0)
            hoofdomschrijving.set_editable(False)
            tegenrekening2.set_editable(False)
            tegenrekening2.configure(gtk.Adjustment(b.tegen2, b.tegen2, b.tegen2), 0, 0)
            tegenrekening1.set_editable(False)
            tegenrekening1.configure(gtk.Adjustment(b.tegen, b.tegen, b.tegen), 0, 0)
            w = b.waarde.floatt()
            debet.set_editable(False)
            debet.configure(gtk.Adjustment(w[0], w[0], w[0]), 0, 2)
            credit.set_editable(False)
            credit.configure(gtk.Adjustment(w[1], w[1], w[1]), 0, 2)
            extraomschrijving.set_editable(False)

        # in table zetten
        self.table.attach(rekening, 0, 1, row, row + 1, gtk.SHRINK)
        self.table.attach(kascie, 1, 2, row, row + 1, gtk.SHRINK)
        self.table.attach(hoofdomschrijving, 2, 3, row, row + 1)
        self.table.attach(tegenrekening2, 3, 4, row, row + 1, gtk.SHRINK)
        self.table.attach(tegenrekening1, 4, 5, row, row + 1, gtk.SHRINK)
        self.table.attach(debet, 5, 6, row, row + 1)
        self.table.attach(credit, 6, 7, row, row + 1)
        self.table.attach(extraomschrijving, 7, 8, row, row + 1)

        # references in lists zetten
        self.rekening.append(rekening)
        self.kascie.append(kascie)
        self.hoofdomschrijving.append(hoofdomschrijving)
        self.tegenrekening2.append(tegenrekening2)
        self.tegenrekening1.append(tegenrekening1)
        self.debet.append(debet)
        self.credit.append(credit)
        self.extraomschrijving.append(extraomschrijving)
        self.table.show()

    def set_boekstuk(self, boekstuk):
        """Set een boekstuk."""

        # als self.nummer en self.datum niet editable zijn, moet dit even
        if not self.iseditable:
            self.nummer.set_editable(True)
            self.nummer.configure(gtk.Adjustment(self.nummer.get_value_as_int(), 1, 999, 1, 10), 0, 0)
            for d in self.datum:
                d.set_editable(True)
            self.datum[0].configure(gtk.Adjustment(self.datum[0].get_value_as_int(), 1, 31, 1, 10), 0, 0)
            self.datum[1].configure(gtk.Adjustment(self.datum[1].get_value_as_int(), 1, 12, 1, 10), 0, 0)
            self.datum[2].configure(gtk.Adjustment(0, 0, 3000, 1, 10), 0, 0) # dit gaat ons nog een milleniumbug opleveren

        self.nummer.set_value(boekstuk.nummer)
        d, m, j = inttodate(boekstuk.datum)
        self.datum[0].set_value(d)
        self.datum[1].set_value(m)
        self.datum[2].set_value(j)

        # en weer terug zetten
        if not self.iseditable:
            self.nummer.set_editable(False)
            v = self.nummer.get_value_as_int()
            self.nummer.configure(gtk.Adjustment(v, v, v), 0, 0)
            for d in self.datum:
                d.set_editable(False)

            v = self.datum[0].get_value_as_int()
            self.datum[0].configure(gtk.Adjustment(v, v, v), 0, 0)
            v = self.datum[1].get_value_as_int()
            self.datum[1].configure(gtk.Adjustment(v, v, v), 0, 0)
            v = self.datum[2].get_value_as_int()
            self.datum[2].configure(gtk.Adjustment(v, v, v), 0, 0)

        # ouwe dingen weghalen
        s = len(self.rekening)
        for i in range(s):
            self.table.remove(self.rekening[i])
            self.table.remove(self.kascie[i])
            self.table.remove(self.hoofdomschrijving[i])
            self.table.remove(self.tegenrekening2[i])
            self.table.remove(self.tegenrekening1[i])
            self.table.remove(self.debet[i])
            self.table.remove(self.credit[i])
            self.table.remove(self.extraomschrijving[i])

        self.rekening = []
        self.kascie = []
        self.hoofdomschrijving = []
        self.tegenrekening2 = []
        self.tegenrekening1 = []
        self.debet = []
        self.credit = []
        self.extraomschrijving = []

        self.table.resize(1, 8)

        # en nieuwe erin zetten
        for b in boekstuk:
            self.set_boekregel(b)
        self.table.show_all()

    def tegenregel(self, b):
        """Voor de bewerk-knop 'tegenregel'."""
        bk = self.get_boekstuk()
        bk.tegenregel()
        self.set_boekregel(bk[-1])
        self.widget.show_all()

class BoekstukZoekerWidget:
    """Gtk-widget om boekstukken te zoeken.

    Wederom, is wat code maar het is dik! Dit geeft je de mogelijkheid om een journaal te doorzoeken op boekstukken met
    of (inclusief):
    * een gegeven nummer en datum
    * een gegeven rekening
    * een reguliere expressie voor de omschrijving

    De widget kun je gebruiken door de BoekstukZoekerWidget.widget te gebruiken.
    Vergeet ook niet de callback met set_callback te gebruiken, voor wat er uiteindelijk met het gevonden boekstuk
    moet gebeuren.
    """
    def __init__(self, sheetname = 'Journaal'):
        self.widget = gtkvbox()
        self.callback = None

        table = gtktable(3, 2)

        # vinkjes voor het type zoeken
        self.doenummerdatum = gtk.CheckButton('Nummer en datum:')
        self.doerekening = gtk.CheckButton('Rekening:')
        self.doeomschrijving = gtk.CheckButton('Omschrijving (regex):')

        # nummer en datum
        self.nummer = gtkentry(INT, 1, 999)
        self.datum = gtkentry(DATUM)

        nummerdatum = gtkhbox()
        nummerdatum.pack_start(gtk.Label('Nummer:'))
        nummerdatum.pack_start(self.nummer)
        nummerdatum.pack_start(gtk.Label('Datum:'))
        for d in self.datum:
            nummerdatum.pack_start(d)

        # rekening, omschrijving
        self.rekening = gtkentry(INT, 1, 999)
        self.omschrijving = gtkentry(STRING)

        # in table zetten
        table.attach(self.doenummerdatum, 0, 1, 0, 1)
        table.attach(nummerdatum, 1, 2, 0, 1)

        table.attach(self.doerekening, 0, 1, 1, 2)
        table.attach(self.rekening, 1, 2, 1, 2)

        table.attach(self.doeomschrijving, 0, 1, 2, 3)
        table.attach(self.omschrijving, 1, 2, 2, 3)

        # status en zoeken
        bbox = gtkhbox()
        self.status = gtk.Label('')
        tmp = gtk.Button(stock = gtk.STOCK_FIND)
        self.next = gtk.Button('Volgende zoeken')
        self.next.set_image(tmp.get_image())
        self.next.connect('clicked', self.zoek)
        bbox.pack_start(self.status)
        bbox.pack_start(self.next, expand = False)

        # in widget stoppen
        self.widget.pack_start(table, expand = False)
        self.widget.pack_start(bbox, expand = False)

        # iterator initialiseren
        self.sheetname = sheetname
        self.reset(sheetname)

    def get_callback(self):
        return self.callback

    def get_nummerdatum(self):
        return self.doenummerdatum.get_active()

    def get_rekening(self):
        return self.doerekening.get_active()

    def get_doeomchrijving(self):
        return self.doeomschrijving.get_active()

    def match_nummerdatum(self, boekstuk):
        """Functie die True geeft als het nummer en datum matcht."""
        return boekstuk.nummer == self.nummer.get_value_as_int() and boekstuk.datum == datetoint(self.datum[0].get_value_as_int(), self.datum[1].get_value_as_int(), self.datum[2].get_value_as_int())

    def match_rekening(self, boekstuk):
        """Functie die True geeft als de rekening matcht."""
        r = self.rekening.get_value_as_int()
        for b in boekstuk:
            if b.rekening == r:
                return True
        return False

    def match_omschrijving(self, boekstuk):
        """Functie die True geeft als de omschrijving matcht."""
        pattern = self.omschrijving.get_text()

        for b in boekstuk:
            if re.search(pattern, b.omschrijving):
                return True
        return False

    def reset(self, sheetname = 'Journaal'):
        """Reset de iterator."""
        tmp = BoekstukIter(sheetname)
        self.bkiter = iter(tmp)

    def set_callback(self, functie):
        """Zet de callback functie.

        Dit moet een functie zijn die 1 argument (een boekstuk) heeft.
        """
        self.callback = functie

    def set_nummerdatum(self, e):
        self.doenummerdatum.set_active(e)

    def set_rekening(self, e):
        self.doerekening.set_active(e)

    def set_doeomchrijving(self, e):
        self.doeomschrijving.set_active(e)

    def zoek(self, b):
        """Zoek."""
        try:
            self.status.set_text('Zoekende ...')
            while True:
                boekstuk = self.bkiter.next()

                if self.doenummerdatum.get_active() and self.match_nummerdatum(boekstuk):
                    self.status.set_text('Gevonden.')
                    if self.callback:
                        self.callback(boekstuk)
                    break
                if self.doerekening.get_active() and self.match_rekening(boekstuk):
                    self.status.set_text('Gevonden.')
                    if self.callback:
                        self.callback(boekstuk)
                    break
                if self.doeomschrijving.get_active() and self.match_omschrijving(boekstuk):
                    self.status.set_text('Gevonden.')
                    if self.callback:
                        self.callback(boekstuk)
                    break
                    
        except StopIteration: # StopIteration afvangen
            self.status.set_text('Einde document.')
            self.bkiter = iter(self.bkiter)
            self.reset(self.sheetname)
            if self.callback:
                self.callback(Boekstuk())

class BoekstukWriter:
    """Class om boekstukken de schrijven die al bestaan.

    Het idee is dat dit in self.mod het aantal ingevoegde regels bijhoud. Review is gewenst.
    """
    def __init__(self, sheetname):
        self.sheetname = sheetname
        self.mod = 0
        self.lr = 0

    def write(self, boekstuk, row):
        if row < self.lr:
            self.mod = 0
        self.lr = row
        m = replaceboekstuk(boekstuk, row + self.mod, self.sheetname)
        self.mod += m

    def reset(self):
        self.mod = 0

class BalansregelWidget:
    """Widget voor een balansregel.

    Wederom, gebruik dit met self.widget.
    """
    def __init__(self):
        self.widget = gtktable(2, 4)

        self.widget.attach(gtk.Label('Rekening:'), 0, 1, 0, 1)
        self.widget.attach(gtk.Label('Naam:'), 1, 2, 0, 1)
        self.widget.attach(gtk.Label('Debet:'), 2, 3, 0, 1)
        self.widget.attach(gtk.Label('Credit:'), 3, 4, 0, 1)

        self.rekening = gtkentry(INT, 1, 999)
        self.naam = gtkentry(STRING)
        self.debet = gtkentry(FLOAT, 0)
        self.credit = gtkentry(FLOAT, 0)

        self.widget.attach(self.rekening, 0, 1, 1, 2)
        self.widget.attach(self.naam, 1, 2, 1, 2)
        self.widget.attach(self.debet, 2, 3, 1, 2)
        self.widget.attach(self.credit, 3, 4, 1, 2)

    def get_balansregel(self):
        return Balansregel(self.rekening.get_value_as_int(),
                           self.naam.get_text(),
                           Euro(self.debet.get_value()- self.credit.get_value()))

    def set_balansregel(self, regel):
        self.rekening.set_value(regel.rekening)
        self.naam.set_text(regel.naam)
        w = regel.waarde.floatt()
        self.debet.set_value(w[0])
        self.credit.set_value(w[1])
