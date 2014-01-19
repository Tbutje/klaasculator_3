from powertools import *
from euro import *


class Baromzet:
    def __init__(self):
        """Maakt het baromzet-schermpje."""

        self.conf = Config()
        # hoog en laag btw
        self.btw_hoog = self.conf.getvar('btw:hoog') /100.0 #21 / 100.0
        self.btw_laag = self.conf.getvar('btw:laag') / 100.0 # 6 / 100.0
        #Rekening check
        # gooit een error als deze rekeningen niet gevonden kunnen worden
        self.rek_keuk = self.conf.getrekening('Omzet Groep 1 - Keuken')
        self.rek_bier = self.conf.getrekening('Omzet Groep 2 - Bier')
        self.rek_fris = self.conf.getrekening('Omzet Groep 3 - Fris')
        self.rek_alc = self.conf.getrekening('Omzet Groep 4 - Alcohol+')
        self.rek_kasvr = self.conf.getrekening('Kasverschillen')
        self.rek_kas = self.conf.getrekening('Kas Algemeen')
        self.rek_btw = self.conf.getrekening('Af te dragen BTW over verkopen')



        self.window = gtkwindow('Baromzet')
        # de window

        # tabel met variabelen erin
        table = gtktable(7, 2)

        # zet de dingen in de tabel, zie makegtkentry
        self.znr = makegtkentry(table, 0, 'Z-nr:', STRING)
        self.dag, self.maand, self.jaar = makegtkentry(table, 1, 'Datum:', DATUM)
        self.kas = makegtkentry(table, 2, 'Kasomzet:', FLOAT)
        self.omzet1 = makegtkentry(table, 3, 'Omzet Groep 1:', FLOAT)
        self.omzet2 = makegtkentry(table, 4, 'Omzet Groep 2:', FLOAT)
        self.omzet3 = makegtkentry(table, 5, 'Omzet Groep 3:', FLOAT)
        self.omzet4 = makegtkentry(table, 6, 'Omzet Groep 4:', FLOAT)

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

        # omschrijving
        omschrijving = 'Omzet Z-nr.%s' % self.znr.get_text()

        # kasomzet
        kas = Euro(self.kas.get_value(), DEBET)
        if kas.true():
            boekstuk.append(Boekregel(0,
                                      0,
                                      self.rek_kas.nummer,
                                      '',
                                      omschrijving,
                                      self.rek_keuk.nummer,
                                      self.rek_bier.nummer,
                                      kas,
                                        ''))

        # we moeten btw bijhouden
        btw = Euro()


        # groep 1
        omzet1 = Euro(self.omzet1.get_value(), CREDIT)
        exc, b = btw_inctoexc(omzet1, self.btw_laag)
        btw += b
        if exc.true():
            boekstuk.append(Boekregel(0,
                                      0,
                                      self.rek_keuk.nummer,
                                      '',
                                      omschrijving,
                                      self.rek_kasvr.nummer,
                                      self.rek_kas.nummer,
                                      exc,
                                      '(inc. BTW: %.2f)' % float(omzet1)))
        # groep 2
        omzet2 = Euro(self.omzet2.get_value(), CREDIT)
        exc, b = btw_inctoexc(omzet2, self.btw_hoog)
        btw += b
        if exc.true():
            boekstuk.append(Boekregel(0,
                                      0,
                                      self.rek_bier.nummer,
                                      '',
                                      omschrijving,
                                      self.rek_kasvr.nummer,
                                      self.rek_kas.nummer,
                                      exc,
                                      '(inc. BTW: %.2f)' % float(omzet2)))
        # groep 3
        omzet3 = Euro(self.omzet3.get_value(), CREDIT)
        exc, b = btw_inctoexc(omzet3, self.btw_laag)
        btw += b
        if exc.true():
            boekstuk.append(Boekregel(0,
                                      0,
                                      self.rek_fris.nummer,
                                      '',
                                      omschrijving,
                                      self.rek_kasvr.nummer,
                                      self.rek_kas.nummer,
                                      exc,
                                      '(inc. BTW: %.2f)' % float(omzet3)))
        # groep 4
        omzet4 = Euro(self.omzet4.get_value(), CREDIT)
        exc, b = btw_inctoexc(omzet4, self.btw_hoog)
        btw += b
        if exc.true():
            boekstuk.append(Boekregel(0,
                                      0,
                                      self.rek_alc.nummer,
                                      '',
                                      omschrijving,
                                      self.rek_kasvr.nummer,
                                      self.rek_kas.nummer,
                                      exc,
                                      '(inc. BTW: %.2f)' % float(omzet4)))

        # btw
        if btw.true():
            boekstuk.append(Boekregel(0,
                                      0,
                                      self.rek_btw.nummer,
                                      '',
                                      omschrijving,
                                      self.rek_kasvr.nummer,
                                      self.rek_kas.nummer,
                                      btw,
                                      ''))

        # kasverschil
        verschil = boekstuk.balanswaarde()
        if verschil.true():
            boekstuk.append(Boekregel(0,
                                      0,
                                      self.rek_kasvr.nummer,
                                      '',
                                      omschrijving,
                                      0,
                                      self.rek_kas.nummer,
                                      verschil,
                                      ''))
        # naar journaal schrijven
        writeboekstuk(boekstuk)


    def volgende(self, button):
        """Maakt het boekstuk en geeft alle velden hun defaults terug."""
        self.maak()
        self.znr.set_text('')
        self.kas.set_value(0.0)
        self.omzet1.set_value(0.0)
        self.omzet2.set_value(0.0)
        self.omzet3.set_value(0.0)
        self.omzet4.set_value(0.0)

    def klaar(self, button):
        """Maakt het boekstuk en maakt het scherm stuk."""
        self.maak()
        self.annuleren(button)

    def annuleren(self, button):
        self.window.destroy()

def baromzet():
    Baromzet()



if __name__ == "__main__":
    baromzet()



