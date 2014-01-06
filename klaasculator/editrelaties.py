from powertools import *
from selectconfig import *


class EditRelaties:
    def __init__(self):
        self.conf = Config()
        self.rel = Relaties()

        self.window = gtkwindow('Wijzig het relatiebestand')

        ## knopjes

        # file selecteren
        tmp = gtk.Button(stock = gtk.STOCK_OPEN)
        filechooser = gtk.Button('Selecteer relatiebestand')
        filechooser.set_image(tmp.get_image())
        filechooser.connect('clicked', self.selectfile)

        # annuleren
        annuleren = gtk.Button(stock = gtk.STOCK_CANCEL)
        annuleren.connect('clicked', self.annuleren)
        try:
            self.origfile = getcellstring('Info', 'C11')
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

        self.leden = []
        self.olv = []
        self.extern = []
        self.ledenrek = []
        self.olvrek = []
        self.externrek = []
        self.excluderek = []
        # self.alias = []

        # leden
        vbox, table, button = self.ledenframe()
        self.leden.extend(self.leden_set(table))
        button.connect('clicked', self.ledenadd, table)

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scroll.add_with_viewport(vbox)
        self.notebook.append_page(scroll, gtk.Label('Leden'))

        # olv
        vbox, table, button = self.naamframe()
        self.olv.extend(self.olv_set(table))
        button.connect('clicked', self.olvadd, table)

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scroll.add_with_viewport(vbox)
        self.notebook.append_page(scroll, gtk.Label('OLV-ers'))

        # extern
        vbox, table, button = self.naamframe()
        self.extern.extend(self.extern_set(table))
        button.connect('clicked', self.externadd, table)

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scroll.add_with_viewport(vbox)
        self.notebook.append_page(scroll, gtk.Label('Externen'))

        # alias
        # vbox, table, button = self.aliasframe()
        # self.alias.extend(self.alias_set(table))
        # button.connect('clicked', self.aliasadd, table)

        # scroll = gtk.ScrolledWindow()
        # scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        # scroll.add_with_viewport(vbox)
        # self.notebook.append_page(scroll, gtk.Label('Alias'))

        # ledenrek
        table = self.rekeningframe()
        self.ledenrek.extend(self.ledenrek_set(table))
        button.connect('clicked', self.ledenrekadd, table)

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scroll.add_with_viewport(table)
        self.notebook.append_page(scroll, gtk.Label('Ledenrekeningen'))

        # olvrek
        table = self.rekeningframe()
        self.olvrek.extend(self.olvrek_set(table))
        button.connect('clicked', self.olvrekadd, table)

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scroll.add_with_viewport(table)
        self.notebook.append_page(scroll, gtk.Label('OLVrekeningen'))

        # extern rek
        table = self.rekeningframe()
        self.externrek.extend(self.externrek_set(table))
        button.connect('clicked', self.externrekadd, table)

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scroll.add_with_viewport(table)
        self.notebook.append_page(scroll, gtk.Label('Externrekeningen'))

        # exclude rek
        table = self.rekeningframe()
        self.excluderek.extend(self.excluderek_set(table))
        button.connect('clicked', self.excluderekadd, table)

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scroll.add_with_viewport(table)
        self.notebook.append_page(scroll, gtk.Label('Excluded rekeningen'))

        # instructies:
        help = gtk.TextView()
        help.set_editable(False)
        help.set_wrap_mode(gtk.WRAP_CHAR)
        buff = help.get_buffer()
        buff.set_text("""\
Instructies:
* Alle rekeningen tussen 129 en 150 worden automatisch als extern rek gemarkeerd als ze niet in leden rek of exclude rek staan
* exclude rek wordt niet meegenomen bij de deb/cred lijst.
* Om namen aan te passen:
  Ga rustig typen. Bij leden kan automatisch een fico code gemaakt worden.
* Om namen toe te voegen:
  Klik op 'toevoegen' in de juiste lijst, ondering verschijnt een nieuwe regel waar je een naam kunt typen,
* Om relaties te verwijderen:
  Maak het veld met de naam leeg.
* Om een rekening als 'relatierekening' aan te merken.
  Dit houdt in dat ze worden meegenomen bij het maken van debiteuren/crediteurenlijsten. Zet een vinkje achter de rekening.
* De rekening die ik als relatierekening wil aanmerken bestaat niet.
  Voeg de rekening eerst toe met 'Configuratie aanpassen' als balansrekening.

""")
        self.notebook.append_page(help, gtk.Label('Instructies'))

        self.window.show_all()

    def selectfile(self, b):
        selectrelaties()
        self.label.set_text(getcellstring('Info', 'C11'))
        self.maak()

    def annuleren(self, b):
        setcellstring('Info', 'C11', self.origfile)
        self.rel.configure()
        self.window.destroy()

    def ok(self, b):
        self.write()
        self.rel.configure()
        self.window.destroy()

    def write(self):

        fname = self.label.get_text()
        fname = fname.lstrip("file:///")
        # doordat klaas een urlparser gebruikt ipv dirparser vervangt die
        #  : door |. Nu dus weer omdraaien
        fname = fname.replace("|", ":")

        try:
            # setcellstring('Info', 'C11', self.label.get_text())
            f = open(fname, 'wb')

            for r in self.leden:
                code = r[0].get_text().strip()
                naam = r[1].get_text().strip()

                if naam:
                    f.write('"lid","%s - %s"\n' % (code, naam))

            for r in self.olv:
                naam = r.get_text().strip()

                if naam:
                    f.write('"olv","%s"\n' % naam)

            for r in self.extern:
                naam = r.get_text().strip()

                if naam:
                    f.write('"extern","%s"\n' % naam)


            for r in self.ledenrek:
                s = r[0].get_text().strip()
                if r[1].get_active() and s:
                    f.write('"ledenrekening","%s"\n' % s)

            for r in self.olvrek:
                s = r[0].get_text().strip()
                if r[1].get_active() and s:
                    f.write('"olvrekening","%s"\n' % s)

            for r in self.externrek:
                s = r[0].get_text().strip()
                if r[1].get_active() and s:
                    f.write('"externrekening","%s"\n' % s)

            for r in self.excluderek:
                s = r[0].get_text().strip()
                if r[1].get_active() and s:
                    f.write('"exclude","%s"\n' % s)


            # for r in self.alias:
                # a = r[0].get_text().strip()
                # if a:
                    # f.write('"alias:%s","%s"\n' % (a.replace('"', r'\"'), r[1].child.get_text()))
            f.close()
        except Exception, e:

            ## probeer te schrijven naar een sheet
            ## TODO: mogelijk onverwacht resultaat bij rare pathname?
            try: # gooit een exceptie als sheet in kwestie niet bestaat
                rel_sheet = Sheet(fname, 0, 0, 1, 0)
                idx = 0

                for r in self.leden:
                    code = r[0].get_text().strip()
                    naam = r[1].get_text().strip()

                    if naam:
                        rel_sheet.setstring(idx, 0, "lid")
                        rel_sheet.setstring(idx, 0, '"%s - %s"' % (code, naam))
                        idx +=1

                for r in self.olv:
                    naam = r.get_text().strip()

                    if naam:
                        f.write('"olv","%s"\n' % naam)

                for r in self.extern:
                    naam = r.get_text().strip()

                    if naam:
                        f.write('"extern","%s"\n' % naam)


                for r in self.ledenrek:
                    s = r[0].get_text().strip()
                    if r[1].get_active() and s:
                        f.write('"ledenrekening","%s"\n' % s)

                for r in self.olvrek:
                    s = r[0].get_text().strip()
                    if r[1].get_active() and s:
                        f.write('"olvrekening","%s"\n' % s)

                for r in self.externrek:
                    s = r[0].get_text().strip()
                    if r[1].get_active() and s:
                        f.write('"externrekening","%s"\n' % s)

                for r in self.excluderek:
                    s = r[0].get_text().strip()
                    if r[1].get_active() and s:
                        f.write('"exclude","%s"\n' % s)











                for r in self.balansrekeningen:
                    s = r[0].get_text().strip()
                    if s:
                        conf_sheet.setstring(idx, 0,"balansrekening:" + s)
                        conf_sheet.setint(idx,1,r[1].get_value_as_int() )
                        idx +=1

                conf_sheet.write(fname, 0, 0, erase = True)

            except Exception:
                print e
                raise Fout('Kon niet naar bestand \'%s\' schrijven.' % fname)


    ## allerlij hulpfuncties: #################################################

    # leden

    def ledenframe(self):
        vbox = gtkvbox()

        table = gtktable(1, 2)
        table.attach(gtk.Label('Code:'), 0, 1, 0, 1, gtk.SHRINK)
        table.attach(gtk.Label('Naam:'), 1, 2, 0, 1)

        button = gtk.Button(stock = gtk.STOCK_ADD)
        bbox = gtkhbuttonbox()
        bbox.pack_start(button)

        vbox.pack_start(table, expand = False)
        vbox.pack_start(bbox, expand = False)

        return vbox, table, button

    def ledenframe_append(self, table):
        row = table.get_property('n-rows')
        table.resize(row + 1, 2)

        code = gtkentry(STRING)
        naam = gtkentry(STRING)

        table.attach(code, 0, 1, row, row + 1, gtk.SHRINK)
        table.attach(naam, 1, 2, row, row + 1)

        naam.connect('changed', self.maakfico, code, naam)
        self.window.show_all()
        return code, naam

    def maakfico(self, b, code, naam):
        l = naam.get_text().split()
        code.set_text(l[0][:2].upper() + l[-1][:2].upper())

    def ledenadd(self, b, table):
        self.leden.append(self.ledenframe_append(table))

    def leden_set(self, table):
        ret = []
        for l in sorter(self.rel.leden):
            code, naam = self.ledenframe_append(table)
            sp = l.split(' - ')
            code.set_text(sp[0].strip())
            naam.set_text((' - '.join(sp[1:])).strip())
            ret.append([code, naam])
        return ret

    # naam
    def naamframe(self):
        vbox = gtkvbox()

        table = gtktable(1, 1)
        table.attach(gtk.Label('Naam:'), 0, 1, 0, 1)

        button = gtk.Button(stock = gtk.STOCK_ADD)
        bbox = gtkhbuttonbox()
        bbox.pack_start(button)

        vbox.pack_start(table, expand = False)
        vbox.pack_start(bbox, expand = False)

        return vbox, table, button

    def naamframe_append(self, table):
        row = table.get_property('n-rows')
        table.resize(row + 1, 1)

        naam = gtkentry(STRING)

        table.attach(naam, 0, 1, row, row + 1)
        self.window.show_all()
        return naam

    def olvadd(self, b, table):
        self.olv.append(self.naamframe_append(table))

    def externadd(self, b, table):
        self.extern.append(self.naamframe_append(table))

    def olv_set(self, table):
        ret = []
        for l in sorter(self.rel.olv):
            naam = self.naamframe_append(table)
            naam.set_text(l)
            ret.append(naam)
        return ret

    def extern_set(self, table):
        ret = []
        for l in sorter(self.rel.extern):
            naam = self.naamframe_append(table)
            naam.set_text(l)
            ret.append(naam)
        return ret

    # alias

    def aliasframe(self):
        vbox = gtkvbox()

        table = gtktable(1, 2)
        table.attach(gtk.Label('Alias:'), 0, 1, 0, 1)
        table.attach(gtk.Label('Naam:'), 1, 2, 0, 1)

        button = gtk.Button(stock = gtk.STOCK_ADD)
        bbox = gtkhbuttonbox()
        bbox.pack_start(button)

        vbox.pack_start(table, expand = False)
        vbox.pack_start(bbox, expand = False)
        return vbox, table, button

    def aliasframe_append(self, table):
        row = table.get_property('n-rows')
        table.resize(row + 1, 2)

        alias = gtkentry(STRING)
        naam = relatiewidget(True, True, True)

        table.attach(alias, 0, 1, row, row + 1)
        table.attach(naam, 1, 2, row, row + 1)
        table.show_all()
        return alias, naam

    def aliasadd(self, b, table):
        self.alias.append(self.aliasframe_append(table))

    def alias_set(self, table):
        ret = []
        for key in sorter(self.rel.alias.iterkeys()):
            alias, naam = self.aliasframe_append(table)
            alias.set_text(key)
            naam.child.set_text(self.rel.alias[key])
            ret.append([alias, naam])
        return ret

    # rekeningen

    def rekeningframe(self):
        table = gtktable(1, 2)
        table.attach(gtk.Label('Naam:'), 0, 1, 0, 1)
        table.attach(gtk.Label('Aan/Uit:'), 1, 2, 0, 1)

        return table

    def rekeningframe_append(self, table):
        row = table.get_property('n-rows')
        table.resize(row + 1, 2)

        naam = gtkentry(STRING)
        check = gtk.CheckButton()

        table.attach(naam, 0, 1, row, row + 1)
        table.attach(check, 1, 2, row, row + 1)
        self.window.show_all()
        return naam, check

    def ledenrekadd(self, b, table):
        self.ledenrek.append(self.rekeningframe_append(table))

    def olvrekadd(self, b, table):
        self.olvrek.append(self.rekeningframe_append(table))

    def externrekadd(self, b, table):
        self.externrek.append(self.rekeningframe_append(table))

    def excluderekadd(self, b, table):
        self.excluderek.append(self.rekeningframe_append(table))


    def ledenrek_set(self, table):
        ret = []
        for l in sorter(self.conf.balansrekeningen()):
            naam, check = self.rekeningframe_append(table)
            naam.set_text(l.naam)
            check.set_active(l.naam in self.rel.ledenrek)

            ret.append([naam, check])
        return ret

    def olvrek_set(self, table):
        ret = []
        for l in sorter(self.conf.balansrekeningen()):
            naam, check = self.rekeningframe_append(table)
            naam.set_text(l.naam)
            check.set_active(l.naam in self.rel.olvrek)

            ret.append([naam, check])
        return ret

    def externrek_set(self, table):
        ret = []
        for l in sorter(self.conf.balansrekeningen()):
            naam, check = self.rekeningframe_append(table)
            naam.set_text(l.naam)
            check.set_active(l.naam in self.rel.externrek)

            ret.append([naam, check])
        return ret

    def excluderek_set(self, table):
        ret = []
        for l in sorter(self.conf.balansrekeningen()):
            naam, check = self.rekeningframe_append(table)
            naam.set_text(l.naam)
            check.set_active(l.naam in self.rel.exclude_rek)

            ret.append([naam, check])
        return ret

if __name__ == "__main__":
    EditRelaties()