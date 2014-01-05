from debcred import *


class MaakBeginDC(Debcred):
    """Maak een debiteuren- en crediteurenlijst-samenvatting"""

    def __init__(self, journaal, begindc):
        """Initialiseer.

        De parameters journaal en begindc zijn Sheet_jr_ro van Journaal en BeginDC.
        """
        Debcred.__init__(self, journaal, begindc)
        self.dclijstkort = [] # dclijstkort is een list met Kortedcregels
        self.wegstrepen_true = self.conf.getvar('debcredkort:wegstrepen')
        self.verwijder_dubieus = self.conf.getvar('maakbegindc:verwijder_Dubieuze_Debiteuren')

    def header(self, it, b):
        """Hulpfunctie.Dit maakt de headers.
        Als regel b de datum begindatum - 1 is, is het een regel van de begindc.
        """
        self.dclijst.setboekregel(it, Boekregel(rekening = b.rekening,
                                            omschrijving = ""))
        it += 1
        self.dclijst.setboekregel(it, Boekregel())
        it += 1
        self.dclijst.setboekregel(it, b)
        it += 1
        return it

    def footer(self, it, r, w):
        self.dclijst.setboekregel(it, Boekregel(0,
                                                "",
                                                0,
                                                '',
                                                '',
                                                0,
                                                0,
                                                w.counterpart(),
                                                'Begin balans volgend jaar'))
        self.dclijst.setstring(it, 0, 'Eind')
        it += 1
        self.dclijst.setboekregel(it, Boekregel())
        it += 1
        self.dclijst.setboekregel(it, Boekregel())
        it += 1
        return it


    def bdatumfix(self, b):
        if b.datum == self.bdatum:
            b.datum = self.bdatum - 1
        return b

    def maak(self):
        """Maak de handel."""
        regels = self.begindc_fix() + self.journaal_fix()

        if self.wegstrepen_true:
            regels = self.wegstrepen(regels)
            regels = self.verwijder_nul(regels)

        regels = sorter(regels, sorter_rodn)
        if not regels: #stoppen bij lege boekhouding
            return

        rel = regels.pop(0)
        it = self.header(0, rel)
        waarde = rel.waarde
        om2 = ''

        for r in regels:
            if self.check and not self.rel.exist(r.omschrijving):
                raise Fout('\'%s\' is niet bekend in het relatiebestand.' % r.omschrijving)

            if self.verwijder_dubieus and r.omschrijving == "Dubieuze Debiteuren":
                continue
            if r.rekening != rel.rekening:
                it = self.footer(it,r, waarde)
                it = self.header(it, r)
                rel = r
                waarde = r.waarde
                om2 = ''
             # het is nog het huidge boekstuk
             #dus += waarde en extra boekregel
            else:
                self.dclijst.setboekregel(it, r)
                it += 1
                waarde += r.waarde
                om2 += ', ' + r.omschrijving2
        self.footer(it,r, waarde)

    def write(self):
        """Wie schrijft die blijft."""
        rel = Relaties()

        # maak deb/cred lijst
        createsheet('BeginDC_NEW')

        tmp = Sheet('BeginDC_NEW', 0, 0, 9, 0)
        tmp.setstring(0, 4, 'Debiteuren / Crediteuren Samenvatting')

        tmp.setstring(1, 0, 'Bknr.')
        tmp.setstring(1, 1, 'Datum')
        tmp.setstring(1, 2, 'rek.')
        tmp.setstring(1, 3, 'ctr.')
        tmp.setstring(1, 4, 'Naam')
        tmp.setstring(1, 5, 'tegr2')
        tmp.setstring(1, 6, 'tegr1')
        tmp.setstring(1, 7, 'debet')
        tmp.setstring(1, 8, 'credit')
        tmp.setstring(1, 9, 'Omschrijving')

        tmp.write('BeginDC_NEW', 0, 0)
        self.dclijst.write('BeginDC_NEW', erase = True)

        try:
            layout_journaalstyle('DebCredKort')
        except:
            pass

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
            while it < len(bdc) and b.omschrijving == bdc[it].omschrijving:
                b.omschrijving2 += ', ' + bdc[it].omschrijving2
                b.waarde += bdc[it].waarde
                del bdc[it]

        return bdc

    def journaal_fix(self):
        regels = filter(lambda b: self.rel.isrelatierekening(self.conf.getrekening(b.rekening)), self.journaal)
        # if self.conf.getvar('debcredkort:negeerafgehandeld'):
            # regels = filter(lambda b: 'AFGEHANDELD' not in b.omschrijving2, regels)
        return regels

    def wegstrepen(self, regels):
        """Wegstrepen."""

        #print 'wegstrepen'
        regels.sort(sorter_rodn)

        it = 0
        while it < len(regels):
            rek = regels[it].rekening
            naam = regels[it].omschrijving
            waarde = regels[it].waarde

            it2 = it + 1

            while it2 < len(regels) and regels[it2].omschrijving == naam and regels[it2].rekening == rek:
                if regels[it2].waarde == waarde and regels[it2].waarde.dc != waarde.dc:
                    #print regels[it]
                    #print regels[it2]
                    del regels[it2]
                    del regels[it]
                    it -= 1
                    break
                it2 += 1
            it += 1
        return regels

    def verwijder_nul(self, regels):

        regels.sort(sorter_rodn)

        include = []
        it = 0
        # bereken eerst totale bedrag / relatie
        # als True(dus niet 0) zet deze rekening*omschrijving combinatie
        # dan in lijst include.
        # geburik vervolgends deze lijst om nog keer door alles heen te loopen
        # maar nu alleen koppieren ales de relatie in include lijst zit
        while it < len(regels):
            rek = regels[it].rekening
            naam = regels[it].omschrijving
            waarde = Euro()

            while (it < len(regels) and regels[it].omschrijving == naam and
                    regels[it].rekening == rek):

                waarde += regels[it].waarde
                it += 1
            if waarde.true():
                include.append(str(rek)+naam)

        regels_new = []
        it = 0
        while it < len(regels):
            rek = str(regels[it].rekening)
            naam = regels[it].omschrijving

            if (rek + naam) in include:
                regels_new.append(regels[it])
            it += 1
        return regels_new

if __name__ == "__main__":
    journaal = Sheet_jr_ro('Journaal')
    begindc = Sheet_jr_ro('BeginDC')
    dc = MaakBeginDC(journaal, begindc)
    dc.maak()
    dc.write()




