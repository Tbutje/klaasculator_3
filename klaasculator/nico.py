from powertools import *


class Nico:

    def __init__(self):
        """Maakt het Nico-schermpje."""

        # de window
        self.window = gtkwindow('Nico')

        # tabel met variabelen erin
        table = gtktable(6, 2)

        # zet de dingen in de tabel, zie makegtkentry
        self.dag, self.maand, self.jaar = makegtkentry(table, 0, 'Datum:', DATUM)
        self.eters = makegtkentry(table, 1, 'Aantal eters:', INT)
        self.kas = makegtkentry(table, 2, 'Kasomzet:', FLOAT)
        self.verbruik = makegtkentry(table, 3, 'Kosten:', FLOAT)
        self.ppe = makegtkentry(table, 4, 'Prijs Per Eter:', FLOAT)

        # automatisch opzoeken van de gebruikelijke prijs per eter
        self.ppe.set_value(Config().getvar('nico:Prijs per eter') / 100.0)



    #eetkorting

        self.eetkorting = gtkentry(FLOAT)

        #label
        eklabel = gtk.Label()
        eklabel.set_text('Eetkorting:')
        eklabel.set_alignment(1, 0.5)

        #en zo zet je het in de table:
        ekbox = gtkhbox()
        eetkorting = gtk.Button('Berekenen')
        eetkorting.connect('clicked', self.berekeneetkorting)

        #in de tabel zetten
        ekbox.pack_start(eetkorting)
        ekbox.pack_start(self.eetkorting)
        table.attach(eklabel, 0, 1, 5, 6)
        table.attach(ekbox, 1, 2, 5, 6)


    #zwarteters
        self.zwarteters = []

        self.zwarteter = relatiewidget(True, False, False)

        #label
        zelabel = gtk.Label()
        zelabel.set_text('Zwarteter:')
        zelabel.set_alignment(1, 0.5)

        self.zelabel = zelabel

        #en zo zet je het in de table:
        zebox = gtkhbox()
        zwartetertoevoegen = gtk.Button('Zwarteter Toevoegen')
        zwartetertoevoegen.connect('clicked', self.voegzwartetertoe)

        #in de tabel zetten
        zebox.pack_start(zwartetertoevoegen)
        zebox.pack_start(self.zwarteter)
        table.attach(zelabel, 0, 1, 6, 7)
#        table.attach(ekbox, 1, 2, 6, 7)

        # knopjes
        hbox = gtkhbuttonbox()

        volgende = gtk.Button(stock = gtk.STOCK_GO_FORWARD)
        volgende.connect('clicked', self.volgende)

        klaar = gtk.Button(stock = gtk.STOCK_APPLY)
        klaar.connect('clicked', self.klaar)

        annuleren = gtk.Button(stock = gtk.STOCK_CANCEL)
        annuleren.connect('clicked', self.annuleren)

        hbox.pack_start(volgende)
        hbox.pack_start(klaar)
        hbox.pack_start(annuleren)

        # alles in elkaar zetten
        vbox = gtkvbox()
        vbox.pack_start(table)
#        vbox.pack_start(ekbox)
        vbox.pack_start(zebox)
        vbox.pack_start(hbox)
        self.window.add(vbox)
        self.window.show_all()
        gtk.main()




    def maak(self):
        """Deze functie maakt het boekstuk en schrijft het naar het journaal."""
        # boekstuk met datum maken, nummer komt later wel
        datum = datetoint(self.dag.get_value_as_int(), self.maand.get_value_as_int(), self.jaar.get_value_as_int())
        boekstuk = Boekstuk(0, datum)

        # configuratie erbij pakken
        conf = Config()

        # omschrijving
        omschrijving = 'Nico'

        # hoog en laag btw
     #   btw_hoog = conf.getvar('btw:hoog') /100.0 #21 / 100.0
        btw_laag = conf.getvar('btw:laag') / 100.0 # 6 / 100.0

        # kasomzet
        kas = Euro(self.kas.get_value(), DEBET)
        if kas.true():
            boekstuk.append(Boekregel(0,
                                      0,
                                      conf.getrekening('Kas Algemeen').nummer,
                                      '',
                                      omschrijving,
                                      conf.getrekening('Verbruik NICO').nummer,
                                      conf.getrekening('Omzet NICO').nummer,
                                      kas,
                                        ''))

        # omzet nico
        eters = float(self.eters.get_value())
        ppe = self.ppe.get_value()
        eetkorting = self.eetkorting.get_value()
        omzet = ((eters * ppe)- eetkorting)

        omzetinc = Euro(omzet, CREDIT)
        exc, btwafdracht = btw_inctoexc(omzetinc, btw_laag)
        if exc.true():
            boekstuk.append(Boekregel(0,
                                      0,
                                      conf.getrekening('Omzet NICO').nummer,
                                      '',
                                      omschrijving,
                                      conf.getrekening('Af te dragen BTW over verkopen').nummer,
                                      conf.getrekening('Kas Algemeen').nummer,
                                      exc,
                                      '(inc. BTW: %.2f)' % float(omzetinc)))

        # af te dragen BTW
        if btwafdracht.true():
            boekstuk.append(Boekregel(0,
                                      0,
                                      conf.getrekening('Af te dragen BTW over verkopen').nummer,
                                      '',
                                      omschrijving,
                                      conf.getrekening('Kas Algemeen').nummer,
                                      conf.getrekening('Omzet NICO').nummer,
                                      btwafdracht,
                                      ''))

        # verbruik nico
        verbruik = Euro(self.verbruik.get_value(), DEBET)
        exc, btwterug = btw_inctoexc(verbruik, btw_laag)
        if exc.true():
            boekstuk.append(Boekregel(0,
                                      0,
                                      conf.getrekening('Verbruik NICO').nummer,
                                      '',
                                      omschrijving,
                                      conf.getrekening('Kasverschillen').nummer,
                                      conf.getrekening('Kas Algemeen').nummer,
                                      exc,
                                      '(inc. BTW: %.2f)' % float(verbruik)))
        # af te dragen BTW
        if btwterug.true():
            boekstuk.append(Boekregel(0,
                                      0,
                                      conf.getrekening('Te vorderen BTW over inkopen').nummer,
                                      '',
                                      omschrijving,
                                      conf.getrekening('Kas Algemeen').nummer,
                                      conf.getrekening('Verbruik NICO').nummer,
                                      btwterug,
                                      ''))

        # Zwarteters
        administratiekosten = Euro(conf.getvar('nico:administratiekosten') / 100.0, CREDIT)   ## dit moet ook een config komen!
        totaal = Euro()
        adminkostenppe = Euro((conf.getvar('nico:administratiekosten') / 100.0) + self.ppe.get_value(), DEBET)
        for lidx in self.zwarteters:
            totaal += administratiekosten
            boekstuk.append(Boekregel(0,
                                      0,
                                      conf.getrekening('Debiteuren Intern').nummer,
                                      '',
                                      lidx,
                                      conf.getrekening('Administratie zwarteters').nummer,
                                      conf.getrekening('Omzet NICO').nummer,
                                      adminkostenppe,
                                      'Zwarteter'))


        # Admistratie kosten Zwarteters
        if totaal.true():
            boekstuk.append(Boekregel(0,
                                      0,
                                      conf.getrekening('Administratie zwarteters').nummer,
                                      '',
                                      'Nico',
                                      conf.getrekening('Kas Algemeen').nummer,
                                      conf.getrekening('Debiteuren Intern').nummer,
                                      totaal,
                                      'Administratiekosten zwarteters'))


        # kasverschil
        verschil = boekstuk.balanswaarde()
        if verschil.true():
            boekstuk.append(Boekregel(0,
                                      0,
                                      conf.getrekening('Kasverschillen').nummer,
                                      '',
                                      omschrijving,
                                      0,
                                      conf.getrekening('Kas Algemeen').nummer,
                                      verschil,
                                      ''))
        # naar journaal schrijven
        writeboekstuk(boekstuk)


    def berekeneetkorting(self, button):
        """Berekent de eetkorting aan de hand van aantal eters en prijs per eter"""
##      conf = Config()
##      self.eetkorting = conf.geteetkorting(self.eters,self.ppe)
        #voorlopig zo maar dit willen we ook uit een config file halen , iets met data en code scheiden

        n = self.eters.get_value_as_int()
        p = self.ppe.get_value()

        if n < 13:
            self.eetkorting.set_value(1 + (2 * 1.5))
        elif n < 18:
            self.eetkorting.set_value(1 + (2 * p))
        else:
            self.eetkorting.set_value(1 + (3 * p))

    def voegzwartetertoe(self, button):
        #voegt een zwarteter toe aan de lijst van zwarteters
        naam = self.zwarteter.child.get_text()
        if naam not in self.zwarteters: # voorkom domme ongelukken
            self.zwarteters.append(naam)
        self.zwarteter.set_active(0)
        self.zwarteter.child.set_text('Selecteer een naam:')

        label = 'Zwarteters:'
        for naam in self.zwarteters:
            label += '\n' + naam
        self.zelabel.set_label(label)

    def volgende(self, button):
        """Maakt het boekstuk en geeft alle velden hun defaults terug."""
        self.maak()
        self.dag, self.maand, self.jaar = makegtkentry(self.table, 0, 'Datum:', DATUM)
        self.eters = 0
        self.kas = 0.0
        self.ppe = 0.0

    def klaar(self, button):
        """Maakt het boekstuk en maakt het scherm stuk."""
        self.maak()
        self.annuleren(button)

    def annuleren(self, button):
        self.window.destroy()

def nico():
    Nico()

if __name__ == "__main__":
    nico()






