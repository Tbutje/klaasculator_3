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

        # remove als niet in self.rel.leden
        regels_new = []
        for line in regels:
            if self.rel.exist(line.omschrijving, soort = LID):
                regels_new.append(line)
            else:
                pass

        if self.wegstrepen_true:
            regels_new = self.wegstrepen(regels_new)

#         regels = sorter(regels, sorter_odn)
        regels_new = sorter(regels_new, sorter_odn)
        it = 0

        for r in regels_new:
            if self.check and not self.rel.exist(r.omschrijving):
                raise Fout('\'%s\' is niet bekend in het relatiebestand.' % r.omschrijving)
            # alleen maar appenden als het daadwerkelijk een waarde heeft.
            if r.waarde.true():
                self.dclijst.setboekregel(it, r)
                it += 1
            else:
                continue



    def write(self):
        """Wie schrijft die blijft."""

        # maak deb/cred lijst leten
        createsheet('DebCredIncassoLeden')

        tmp = Sheet('DebCredIncassoLeden', 0, 0, 9, 0)
        tmp.setstring(0, 4, 'Debiteuren / Crediteuren Incasso Leden')

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

        # lelijk wegens getallen in centen ipv de normale float euro's
        c = 2
        for r in self.dclijst:
            tmp.setstring(c, 0, r.nummer)
            tmp.setint(c, 1, r.datum)
            tmp.setint(c, 2, r.rekening)
            tmp.setstring(c, 3, r.kascie)
            tmp.setstring(c, 4, r.omschrijving)
            tmp.setint(c, 5, r.tegen2)
            tmp.setint(c, 6, r.tegen)

            if r.waarde.dc == DEBET:
                # beetje hak; intern houd Euro() de waarde bij in self.value
                #    in centen. Komt nu goed van pas ;)
                tmp.setint(c, 7, r.waarde.value)
                tmp.setint(c, 8, 0)
            else:
                tmp.setint(c, 7, 0)
                tmp.setint(c, 8, r.waarde.value)
            tmp.setstring(c, 9, r.omschrijving2)
            c += 1

        tmp.write('DebCredIncassoLeden', 0, 0)

        try:
            layout_journaalstyle('DebCredKort')
        except:
            pass

    def begindc_fix(self):
        """ Omdat dit later van pas komt worden alle date vervangen door de begindatum - 1
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
#             while it < len(bdc) and b.omschrijving == bdc[it].omschrijving:
#                 b.omschrijving2 += ', ' + bdc[it].omschrijving2
#                 b.waarde += bdc[it].waarde
#                 del bdc[it]

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




