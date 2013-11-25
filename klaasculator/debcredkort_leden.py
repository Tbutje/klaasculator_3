from debcred import *

class DebcredKortLeden(Debcred):
    """Maak een debiteuren- en crediteurenlijst-samenvatting"""

    def __init__(self, journaal, begindc):
        """Initialiseer.

        De parameters journaal en begindc zijn Sheet_jr_ro van Journaal en BeginDC.
        """
        Debcred.__init__(self, journaal, begindc)
        self.wegstrepen_true = self.conf.getvar('debcredkort:wegstrepen')


    def bdatumfix(self, b):
        if b.datum == self.bdatum:
            b.datum = self.bdatum - 1
        return b

    def maak(self):
        """Maak de handel."""
        regels = sorter(self.begindc_fix() + self.journaal_fix(), sorter_odn)
        if self.wegstrepen_true:
            regels = self.wegstrepen(regels)

        # remove als niet in self.rel.leden
        for line in regels:
            if line.omschrijving in self.rel.leden:
                continue
            else:
                regels.remove(line)


        it = 0

        for r in regels:
            if self.check and not self.rel.exist(r.omschrijving):
                raise Fout('\'%s\' is niet bekend in het relatiebestand.' % r.omschrijving)

            self.dclijst.setboekregel(it, r)
            it += 1


    def write(self):
        """Wie schrijft die blijft."""

        # maak deb/cred lijst leten
        createsheet('DebCredKortLeden')

        tmp = Sheet('DebCredKortLeden', 0, 0, 9, 0)
        tmp.setstring(0, 4, 'Debiteuren / Crediteuren Samenvatting Leden')

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

        tmp.write('DebCredKortLeden', 0, 0)
        self.dclijst.write('DebCredKortLeden', erase = True)

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


#         if self.wegstrepen_true:
#             bdc = self.wegstrepen(bdc)
#             bdc.sort(sorter_rodn)

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
#         if self.wegstrepen_true:
#             regels = self.wegstrepen(regels)
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
                    del regels[it2]
                    del regels[it]
                    it -= 1
                    break
                it2 += 1
            it += 1
        return regels

if __name__ == "__main__":
    journaal = Sheet_jr_ro('Journaal')
    begindc = Sheet_jr_ro('BeginDC')
    dc = DebcredKortLeden(journaal, begindc)
    dc.maak()
    dc.write()




