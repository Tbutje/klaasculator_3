from compileer import compileeralles
from debcred import *
from powertools import *
from relaties import *


class Debug:
    def __init__(self):
        self.conf = Config()
        self.rel = Relaties()
        self.bdatum = getbegindatum()
        self.edatum = geteinddatum()
        self.begindc = Sheet_jr_ro('BeginDC')

        self.verder = True
        ok = True
        self.error = ''
        # ok returned FALSE als er ergens iets niet ok is
        # optioneel kan self.verder aangeven dat het al klaar is
        # probleem is dat als er een fout gevonden wordt ok False blijft
        # ook nadat je verberterd hebt
        # misschien dubbele check doen? beetje loos. dan maar geen berichtje
        # als je alles goed verbeterd hebt.

        if self.verder:
            ok = self.check_beginbalans(ok)

        if self.verder:
            ok = self.check_begindc(ok)

        # maak check voor totaal begin dc / post == beginbalans
        if self.verder:
            ok = self.check_begindc_x_beginbalans(ok)

        if self.verder:
            ok = self.check_journaal(ok)

        # even een schermpje als er geen fouten waren
        if ok:
            title = 'Gefeliciteerd'
            text = 'Geen fouten gevonden.'

            window = gtkwindow(title)
            vbox = gtkvbox()
            vbox.pack_start(gtk.Label(text))
            button = gtk.Button(stock = gtk.STOCK_OK)
            button.connect('clicked', self.sluiten, window)
            vbox.pack_start(button)
            window.add(vbox)
            window.show_all()
            gtk.main()

    def check_balansregel(self, balansregel):
        """Controleert een balansregel."""
        # bestaat de rekening als blanansrekening, gooit Fout als het niet zo is
        try:
            rek = self.conf.getrekening(balansregel.rekening, BALANSREKENING)

            if rek.naam != balansregel.naam:
                self.error = 'De naam van rekening %i komt niet overeen met die in het configuratiebestand (\'%s\' vs\' %s\')' % (balansregel.rekening, balansregel.naam, rek.naam)
                return False
        except Fout, f: # rekening bestaat niet afvangen
            self.error = str(f)
            return False
        return True

    def check_begindcregel(self, begindc):
        """Controleert een regel uit de begindc-lijst."""
        try:
            rek = self.conf.getrekening(begindc.rekening, BALANSREKENING)

            if not self.rel.isrelatierekening(rek.naam):
                self.error = '%i is geen relatierekening.' % rek.nummer
                return False
        except Fout, f:
            self.error = str(f)
            return False

        if not self.rel.exist(begindc.omschrijving):
            self.error = '\'%s\' staat niet in het relatiebestand.' % begindc.omschrijving
            return False

        if begindc.datum > self.bdatum:
            d = inttodate(self.bdatum)
            self.error = 'De datum is voor na de begindatum (%i-%i-%i)' % (d[0], d[1], d[2])
            return False

        return True

    def check_boekstuk(self, boekstuk):
        """Check of een boekstuk deugt.

        Geeft True als het deugt, anders False.
        """

        # is het in balans:
        if not boekstuk.inbalans():
            self.error = 'Dit boekstuk is niet in balans.'
            return False

        # ligt de datum tussen begin- en einddatum
        if boekstuk.datum < self.bdatum:
            self.error = 'De datum is voor de begindatum (%i-%i-%i).' % inttodate(self.bdatum)
            return False
        elif boekstuk.datum > self.edatum:
            self.error = 'De datum is na de einddatum (%i-%i-%i).' % inttodate(self.edatum)
            return False

        # afzonderlijke regels
        for b in boekstuk:
            try:
                # controleer of de rekening bestaat (gooit exceptie als dat niet zo is)
                r = self.conf.getrekening(b.rekening).naam

                if self.rel.isrelatierekening(r) and not self.rel.exist(b.omschrijving):
                    self.error = '%s is niet gedefinieerd in het relatiebestand.' % b.omschrijving
                    return False

            except Fout: # exceptie voor als de rekening niet bestaat afvangen
                self.error = 'Rekening %i is niet gedefinieerd.' % b.rekening
                return False

            # heeft het een tegenrekening
            if not b.tegen:
                self.error = 'Tegenrekening ontbreekt.'
                return False
        return True

    def check_beginbalans(self, ok):
        """Checkt de beginbalans."""
        s = Sheet_bl_ro('Beginbalans')
        si = iter(s)
        w = Euro()
        try:
            while self.verder:
                b = si.next()
                w += b.waarde
                while self.check_balansregel(b):
                    b = si.next()
                    w += b.waarde
                ok = False
                self.error_balansregel(b)
        except StopIteration:
            pass
        if w.true() and self.verder:
            ok = False
            window = gtkwindow('Fout')
            vbox = gtkvbox()
            vbox.pack_start(gtk.Label('De beginbalans is niet in balans'))
            bbox = gtkhbuttonbox()
            verder = gtk.Button(stock = gtk.STOCK_GO_FORWARD)
            verder.connect('clicked', self.verder_bl, window)
            sluiten = gtk.Button(stock = gtk.STOCK_CLOSE)
            sluiten.connect('clicked', self.sluiten, window)
            bbox.pack_start(verder)
            bbox.pack_start(sluiten)
            vbox.pack_start(bbox)
            window.add(vbox)
            window.show_all()
            gtk.main()
        return ok

    def check_begindc(self, ok):
        """Checkt de beginlijst debiteuren/crediteuren."""
        s = Sheet_jr_ro('BeginDC')

        bdciter = iter(s)
        try:
            while self.verder:
                b = bdciter.next()
                while self.check_begindcregel(b):
                    b = bdciter.next()
                ok = False
                self.error_begindc(b, bdciter.i)
        except StopIteration:
            pass
        return ok

    def check_journaal(self, ok):
        """Checkt het Journaal."""

        # iterator over het journaal
        biter = iter(BoekstukIter())
        # writer heeft nog wat review nodig
        writer = BoekstukWriter('Journaal')
        try:
            # zolang we verder willen
            while self.verder:
                b = biter.next()
                while self.check_boekstuk(b): # controlleer
                    b = biter.next()
                ok = False
                # er is een fout
                self.error_boekstuk(b, writer, biter.row)
        except StopIteration:
            pass
        return ok

    def error_boekstuk(self, boekstuk, writer, row):
        """Dit is om een error in een boekstuk te laten zien."""
        # print self.error
        # print boekstuk

        d = inttodate(boekstuk.datum)
        window = gtkwindow('Fout in boekstuk %i op %i-%i-%i' % (boekstuk.nummer, d[0], d[1], d[2]))

        vbox = gtkvbox()

        label = gtk.Label('Fout:\n\n%s' % self.error)
        vbox.pack_start(label, expand = False)

        bw = BoekstukWidget()
        bw.set_editable(True)
        bw.set_boekstuk(boekstuk)
        vbox.pack_start(bw.widget)

        bbox = gtkhbuttonbox()
        volgende = gtk.Button(stock = gtk.STOCK_GO_FORWARD)
        volgende.connect('clicked', self.volgende_boekstuk, bw, row, writer, window)
        bbox.pack_start(volgende)

        sluiten = gtk.Button(stock = gtk.STOCK_CLOSE)
        sluiten.connect('clicked', self.sluiten, window)
        bbox.pack_start(sluiten)

        vbox.pack_start(bbox, expand = False)

        window.add(vbox)
        window.maximize()
        window.show_all()
        gtk.main()

    def error_begindc(self, regel, row):
        """Errorscherm als er iets mis is in de begindc."""

        window = gtkwindow('Fout in de Debiteuren/Crediteuren-beginlijst')

        vbox = gtkvbox()
        vbox.pack_start(gtk.Label(self.error))

        # we vatten een regel op als een boekstuk met een regel
        #
        # Het zou mooier zijn om dit aan te passen / vervagen zodat het omschrijvings-veld de relatiewidget is.
        # 'This is left as an excercise to the reader.'
        bw = BoekstukWidget()
        bw.set_editable(True)
        bw.widget.remove(bw.buttons) # kleine hek, ik heb even geen behoeft aan knopjes

        boekstuk = Boekstuk(regel.nummer, regel.datum)
        boekstuk.append(regel)
        bw.set_boekstuk(boekstuk)

        vbox.pack_start(bw.widget)

        bbox = gtkhbuttonbox()
        volgende = gtk.Button(stock = gtk.STOCK_GO_FORWARD)
        volgende.connect('clicked', self.volgende_begindc, bw, row, window)
        bbox.pack_start(volgende)

        sluiten = gtk.Button(stock = gtk.STOCK_CLOSE)
        sluiten.connect('clicked', self.sluiten, window)
        bbox.pack_start(sluiten)

        vbox.pack_start(bbox)

        window.add(vbox)
        window.show_all()
        gtk.main()

    def error_balansregel(self, regel):
        """Errorscherm voor als er iest mis is in de beginbalans."""
        # print self.error
        # print regel

        window = gtkwindow('Fout in beginbalans.')

        vbox = gtkvbox()

        rw = BalansregelWidget()
        rw.set_balansregel(regel)

        vbox.pack_start(gtk.Label(self.error))
        vbox.pack_start(rw.widget)

        bbox = gtkhbuttonbox()
        volgende = gtk.Button(stock = gtk.STOCK_GO_FORWARD)
        volgende.connect('clicked', self.volgende_balansregel, rw, window)
        bbox.pack_start(volgende)

        sluiten = gtk.Button(stock = gtk.STOCK_CLOSE)
        sluiten.connect('clicked', self.sluiten, window)
        bbox.pack_start(sluiten)

        vbox.pack_start(bbox, expand = False)

        window.add(vbox)
        window.show_all()
        gtk.main()

    # hulpfuncties voor error_(boekstuk/balansregel/begindc):
    def volgende_boekstuk(self, button, bw, row, writer, window):
        writer.write(bw.get_boekstuk(), row)
        window.destroy()

    def volgende_balansregel(self, button, rw, window):
        s = Sheet_bl('Beginbalans')
        regel = rw.get_balansregel()

        size = s.rows()
        for i in range(size):
            if s.getbalansregel(i).rekening == regel.rekening:
                s.setbalansregel(i, regel)
                s.write('Beginbalans')
                window.destroy()
                return
        s.setbalansregel(size, regel)
        s.write('Beginbalans')
        window.destroy()

    def volgende_begindc(self, button, bw, row, window):
        row += 2
        s = Sheet_jr(None, row)
        s.setboekregel(0, bw.get_boekstuk()[0])
        s.write('BeginDC')
        window.destroy()

    def sluiten(self, button, window):
        self.verder = False
        window.destroy()

    def verder_bl(self, button, window):
        window.destroy()

    def check_begindc_x_beginbalans(self, ok):
        dc = self.begindc_fix()
        totals = {}
        reks = self.conf.balansrekeningen()
        reks.sort()

        for line in reks:
            if line.nummer > 129 and line.nummer < 150:
                # haal Relates().exclude rek rekening eruit
                # we nemen aan dat dit geen normale deb/cred zijn
                # zoals bv btw
                if not (self.conf.getrekening(line.nummer).naam in self.rel.exclude_rek):
                    totals[line.nummer] = 0

        for line in dc:
            if line.waarde.dc == 0: # debet
                totals[line.rekening] += line.waarde.value/100
            elif line.waarde.dc == 1: # credit
                totals[line.rekening] -= line.waarde.value/100

        beginbalans = Sheet_bl_ro('Beginbalans')
        ok = True
        foute_nummers = []
        for key,value in totals.iteritems():
            if beginbalans.getwaarde(key).dc == 0: # bebet
                if beginbalans.getwaarde(key).value/100 != value:
                    foute_nummers.append( key)
            if beginbalans.getwaarde(key).dc == 1: # credit
                if (beginbalans.getwaarde(key).value/-100) != value:
                    foute_nummers.append( key)

        if len(foute_nummers) > 0:
            text = " ".join(str(x) for x in foute_nummers)
            text = "Het totaal van de volgende begin DC posten is niet gelijk aan de beginbalans : " + text
            ok = False
            window = gtkwindow('Begin DC fout')
            vbox = gtkvbox()
            vbox.pack_start(gtk.Label(text))
            bbox = gtkhbuttonbox()
            verder = gtk.Button(stock = gtk.STOCK_GO_FORWARD)
            verder.connect('clicked', self.verder_bl, window)
            sluiten = gtk.Button(stock = gtk.STOCK_CLOSE)
            sluiten.connect('clicked', self.sluiten, window)
            bbox.pack_start(verder)
            bbox.pack_start(sluiten)
            vbox.pack_start(bbox)
            window.add(vbox)
            window.show_all()
            gtk.main()

        return ok

    def begindc_fix(self):
        """Deze methode verwijdert dubbele entrys in de begindc.

        Dus wanneer iemand twee keer op dezelfde rekening in de begindc iets heeft, wordt dit samengevat tot een.
        Retourneert een lijst met boekregels zoals ze horen.
        Omdat dit later van pas komt worden alle date vervangen door de begindatum - 1
        """
        bdc = sorter(self.begindc, sorter_rodn)

        it = 0
        while it < len(bdc):
            b = bdc[it]
            it += 1
            b.datum = self.bdatum - 1
            while it < len(bdc) and b.rekening == bdc[it].rekening and b.omschrijving == bdc[it].omschrijving:
                b.omschrijving2 += ', ' + bdc[it].omschrijving2
                b.waarde += bdc[it].waarde
                del bdc[it]

#         for line in bdc:
#             print line
        return bdc





if __name__ == "__main__":
    Debug()






