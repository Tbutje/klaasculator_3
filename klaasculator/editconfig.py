from powertools import *
from selectconfig import *


class EditConfig:
    def __init__(self):
        self.conf = Config()

        self.window = gtkwindow('Wijzig de configuratie')

        ## om data in op te stlaan
        self.balansrekeningen = []
        self.resultatenrekeningen = []
        self.opties = []

        ## knopjes

        # file selecteren
        tmp = gtk.Button(stock = gtk.STOCK_OPEN)
        filechooser = gtk.Button('Selecteer configuratiebestand')
        filechooser.set_image(tmp.get_image())
        filechooser.connect('clicked', self.selectfile)

        # annuleren
        annuleren = gtk.Button(stock = gtk.STOCK_CANCEL)
        annuleren.connect('clicked', self.annuleren)
        try:
            self.origfile = getcellstring('Info', 'C10')
        except:
            self.origfile = ''

        # ok
        ok = gtk.Button(stock = gtk.STOCK_OK)
        ok.connect('clicked', self.ok)

        # in doos stoppen
        buttonbox = gtkhbuttonbox()
        buttonbox.pack_start(filechooser)
        buttonbox.pack_start(annuleren)
        buttonbox.pack_start(ok)

        # label bovenaan
        self.label = gtk.Label(self.origfile)

        ## paginas maken
        self.notebook = gtk.Notebook()

        self.maak()

        ## in elkaar zetten:

        vbox = gtkvbox()
        vbox.pack_start(self.label, expand = False)
        vbox.pack_start(self.notebook, expand = True)
        vbox.pack_start(buttonbox, expand = False)

        self.window.add(vbox)
        self.window.maximize()#notebook.set_size_request(100, 300)
        self.window.show_all()
        gtk.main()

    def maak(self):
        while self.notebook.get_n_pages():
            self.notebook.remove_page(0)

        self.balansrekeningen = []
        self.resultatenrekeningen = []
        self.opties = []

        # balansrekening
        vbox, table, button = self.rekeningframe()
        self.balansrekeningen.extend(self.rekeningen_set(table, sorter(self.conf.balansrekeningen())))
        button.connect('clicked', self.brekadd, table)

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scroll.add_with_viewport(vbox)
        self.notebook.append_page(scroll, gtk.Label('Balansrekeningen'))

        # resulatenrekening
        vbox, table, button = self.rekeningframe()
        self.resultatenrekeningen.extend(self.rekeningen_set(table, sorter(self.conf.resultrekeningen())))
        button.connect('clicked', self.rrekadd, table)

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scroll.add_with_viewport(vbox)
        self.notebook.append_page(scroll, gtk.Label('Resultatenrekeningen'))

        # opties
        vbox, table, button = self.optieframe()
        self.opties.extend(self.opties_set(table, sorter(self.conf.variabelen.items())))
        button.connect('clicked', self.optieadd, table)

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scroll.add_with_viewport(vbox)
        self.notebook.append_page(scroll, gtk.Label('Opties'))

        # instructies:
        help = gtk.TextView()
        help.set_editable(False)
        help.set_wrap_mode(gtk.WRAP_CHAR)
        buff = help.get_buffer()
        buff.set_text("""\
Instructies:
* Wanneer je de naam of het nummer van een rekening wilt wijzigen:
  Precies zoals je denkt dat het gaat, gewoon wijzigen. Pas wel op dat sommige functies niet meer correct kunnen werken als
  je de naam wijzigt.
* Wanneer je een rekening toe wilt voegen:
  Klik op 'toevoegen' bij het juiste type rekening. Onderin de tabel komt een nieuw veld wat je kunt bewerken.
* Wanneer je een optie toe wilt voegen:
  Zelfde als met rekening.
* Wanneer je een optie wilt wijzigen:
  Verander het vinkje achter de betreffende optie.
* Wanneer je een rekening of optie wilt verwijderen:
  Maak het betrefende veld leeg.
""")
        self.notebook.append_page(help, gtk.Label('Instructies'))

        self.window.show_all()

    def selectfile(self, b):
        selectconfig()
        self.label.set_text(getcellstring('Info', 'C10'))
        self.maak()

    def annuleren(self, b):
        setcellstring('Info', 'C10', self.origfile)
        self.conf.configure()
        self.window.destroy()

    def ok(self, b):
        self.write()
        self.conf.configure()
        self.window.destroy()

    def write(self):

        fname = self.label.get_text()
        fname = fname.lstrip("file:///")
        fname = fname.replace("C|", "")

        try:
            # setcellstring('Info', 'C10', self.label.get_text())
            f = open(fname, 'wb')

            for r in self.balansrekeningen:
                s = r[0].get_text().strip()
                if s:
                    f.write('"balansrekening:%s",%i\n' % (s, r[1].get_value_as_int()))

            for r in self.resultatenrekeningen:
                s = r[0].get_text().strip()
                if s:
                    f.write('"resultatenrekening:%s",%i\n' % (s, r[1].get_value_as_int()))

            for o in self.opties:
                s = o[0].get_text().strip()
                if s:
                    f.write('"%s",%i\n' % (s, o[1].get_value_as_int()))

            f.close()
        except Exception, e:
            print e
            raise Fout('Kon niet naar bestand \'%s\' schrijven.' % fname)

    # Allerlij hulpfuncties:

    def rekeningframe(self):
        vbox = gtkvbox()

        table = gtktable(1, 2)
        table.set_homogeneous(False)
        table.attach(gtk.Label('Naam:'), 0, 1, 0, 1)
        table.attach(gtk.Label('Nummer:'), 1, 2, 0, 1)

        button = gtk.Button(stock = gtk.STOCK_ADD)
        bbox = gtkhbuttonbox()
        bbox.pack_start(button)

        vbox.pack_start(table, expand = False)
        vbox.pack_start(bbox, expand = False)

        return vbox, table, button

    def rekeningframe_append(self, table):
        row = table.get_property('n-rows')
        table.resize(row + 1, 2)

        e = gtkentry(STRING)
        i = gtkentry(INT, 1, 999)
        table.attach(e, 0, 1, row, row + 1)
        table.attach(i, 1, 2, row, row + 1)
        self.window.show_all()
        return e, i

    def brekadd(self, b, table):
        self.balansrekeningen.append(self.rekeningframe_append(table))

    def rekeningen_set(self, table, reks):
        ret = []
        for r in reks:
            e, i = self.rekeningframe_append(table)
            e.set_text(r.naam)
            i.set_value(r.nummer)
            ret.append([e, i])
        return ret

    def rrekadd(self, b, table):
        self.resultatenrekeningen.append(self.rekeningframe_append(table))

    def optieframe(self):
        vbox = gtkvbox()

        table = gtktable(1, 2)
        table.attach(gtk.Label('Optie:'), 0, 1, 0, 1)
        table.attach(gtk.Label('Waarde (voor booleanse waarden: 0 is uit, 1 is aan):'), 1, 2, 0, 1)

        button = gtk.Button(stock = gtk.STOCK_ADD)
        bbox = gtkhbuttonbox()
        bbox.pack_start(button)

        vbox.pack_start(table, expand = False)
        vbox.pack_start(bbox, expand = False)

        return vbox, table, button

    def optieframe_append(self, table):
        row = table.get_property('n-rows')
        table.resize(row + 1, 2)

        e = gtkentry(STRING)
        i = gtkentry(INT, 0, 999999)
        table.attach(e, 0, 1, row, row + 1)
        table.attach(i, 1, 2, row, row + 1)
        self.window.show_all()
        return e, i

    def optieadd(self, b, table):
        self.opties.append(self.optieframe_append(table))

    def opties_set(self, table, opties):
        ret = []
        for o in opties:
            e, i = self.optieframe_append(table)
            e.set_text(o[0])
            i.set_value(o[1])
            ret.append([e, i])
        return ret

if __name__ == "__main__":
    EditConfig()

