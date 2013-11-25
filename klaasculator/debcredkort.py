from debcred import *

class DebcredKort(Debcred):
    """Maak een debiteuren- en crediteurenlijst-samenvatting"""

    def __init__(self, journaal, begindc):
        """Initialiseer.

        De parameters journaal en begindc zijn Sheet_jr_ro van Journaal en BeginDC.
        """
        Debcred.__init__(self, journaal, begindc)
        self.dclijstkort = [] # dclijstkort is een list met Kortedcregels
        self.wegstrepen_true = self.conf.getvar('debcredkort:wegstrepen')

    def header(self, it, b):
        """Hulpfunctie.Dit maakt de headers.
        Als regel b de datum begindatum - 1 is, is het een regel van de begindc.
        """
        self.dclijst.setboekregel(it, Boekregel(rekening = 0, omschrijving = b.omschrijving))
        it += 1
        self.dclijst.setboekregel(it, Boekregel())
        it += 1
        if b.datum == self.bdatum - 1:
            self.dclijst.setboekregel(it, Boekregel(0, self.bdatum, b.rekening, '', 'Van beginbalans', 0, 0, b.waarde, b.omschrijving2))
            self.dclijst.setstring(it, 0, 'Begin')
            it += 1
        else:
            self.dclijst.setboekregel(it, Boekregel(0, self.bdatum, b.rekening, '', 'Van beginbalans', 0, 0, Euro(), ''))
            self.dclijst.setstring(it, 0, 'Begin')
            it += 1
            self.dclijst.setboekregel(it, b)
            it += 1
        return it

    def footer(self, it, w):
        return Debcred.footer(self, it, Boekregel(), w)

    def bdatumfix(self, b):
        if b.datum == self.bdatum:
            b.datum = self.bdatum - 1
        return b

    def maak(self):
        """Maak de handel."""

        regels = self.begindc_fix() + self.journaal_fix()

        # dit haalt alle deb/cred weg die op 0 eindigen op eindbalans
        # houd alles nog een beetje overzichtelijk
        # wel extreem trage functie aangezien die 2x door de boekhouding gaat
        if self.wegstrepen_true:
            regels = self.wegstrepen(regels)
            regels = self.verwijder_nul(regels)

        regels = sorter(regels, sorter_odn)


        if not regels: #stoppen bij lege boekhouding
            return

        rel = regels.pop(0)
        it = self.header(0, rel)
        waarde = rel.waarde
        om2 = ''
        datum = rel.datum

        for r in regels:
            if self.check and not self.rel.exist(r.omschrijving):
                raise Fout('\'%s\' is niet bekend in het relatiebestand.' % r.omschrijving)

            # verwijder lege boekstukken
            if not r.waarde.true():
                continue

            if r.omschrijving != rel.omschrijving:
                self.dclijstkort.append(Kortedcregel(rel.omschrijving, waarde, om2, datum))

                it = self.footer(it, waarde)
                it = self.header(it, r)
                rel = r
                waarde = rel.waarde
                om2 = ''
                datum = rel.datum
             # het is nog het huidge boekstuk
             #dus += waarde en extra boekregel
            else:
                if datum > r.datum:
                    datum = r.datum
                self.dclijst.setboekregel(it, r)
                it += 1
                waarde += r.waarde
                om2 += ', ' + r.omschrijving2
        self.footer(it, waarde)
        self.dclijstkort.append(Kortedcregel(rel.omschrijving, waarde, om2))



    def write(self):
        """Wie schrijft die blijft."""

        # maak deb/cred lijst leten
        createsheet('DebCredKort')

        tmp = Sheet('DebCredKort', 0, 0, 9, 0)
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

        tmp.write('DebCredKort', 0, 0)

        self.dclijstkort = sorter(self.dclijstkort, sorter_dckort_w)
        # for line in tmp:
            # print line.waarde


        self.dclijst.write('DebCredKort', erase = True)

        # maak extra korte lijst
        createsheet('DebCredSamenvatting')

        kort = Sheet('DebCredSamenvatting', 0, 0, 4, 0)
        # timo edit
        kort.setstring(0, 3, 'DebCredSamenvatting')

        kort.setstring(1, 0, 'naam.')
        kort.setstring(1, 1, "Oudste datum")
        kort.setstring(1, 2, 'Debet')
        kort.setstring(1, 3, 'Credit')
        kort.setstring(1, 4, 'omschrijving.')

        # kort.write('DebCredSamenvatting', 0, 0)

        # split in extern en leden
        # line.omschrijving in self.rel.leden
        # eerst extern schrijven
        # dan leden, inefficient maar is maar klein lijstje anyway
        kort.setstring(2,0, "EXTERNEN")
        c = 3
        # print self.rel.extern
        for r in self.dclijstkort:
            if r.waarde.true():
                if r.naam in self.rel.extern:
                    kort.setstring(c, 0, r.naam)
                    kort.setint(c, 1, r.datum)

                    if r.waarde.dc == DEBET:
                        kort.setfloat(c, 2, float(r.waarde))
                        kort.setfloat(c, 3, 0.0)
                    else:
                        kort.setfloat(c, 2, 0.0)
                        kort.setfloat(c, 3, float(r.waarde))
                    kort.setstring(c, 4, r.omschrijving)
                    c += 1
                else:
                    continue



        c += 3
        kort.setstring(c-1,0, "LEDEN")

        for r in self.dclijstkort:
            if r.waarde.true():
                if not r.naam in self.rel.extern:
                    kort.setstring(c, 0, r.naam)
                    kort.setint(c, 1, r.datum)

                    if r.waarde.dc == DEBET:
                        kort.setfloat(c, 2, float(r.waarde))
                        kort.setfloat(c, 3, 0.0)
                    else:
                        kort.setfloat(c, 2, 0.0)
                        kort.setfloat(c, 3, float(r.waarde))
                    kort.setstring(c, 4, r.omschrijving)
                    c += 1
                else:
                    continue



        kort.write('DebCredSamenvatting', 0, 0, erase = True)

        # def write(self, sheetname, left, bottom, insert = False, erase = False):
        # """Schrijft de data naar een sheet sheetname.

        # left is de linkse hoek, bottom het laagste rijnummer.
        # Als insert = False, dat wordt eventuele data overschreven. Is insert True, dan worden er rijen ingevoegd.
        # Als erase = True, dat wordt alle data met rijen hoger dan rows() verwijdert.
        # """



        try:
            layout_journaalstyle('DebCredKort')
            layout_extrakortedc('DebCredSamenvatting')
        except:
            pass

    def begindc_fix(self):
        """Deze methode verwijdert dubbele entrys in de begindc.

        Dus wanneer iemand twee keer op dezelfde rekening in de begindc iets heeft, wordt dit samengevat tot een.
        Retourneert een lijst met boekregels zoals ze horen.
        Omdat dit later van pas komt worden alle date vervangen door de begindatum - 1
        """
        bdc = sorter(self.begindc, sorter_rodn)


#         if self.conf.getvar('debcredkort:wegstrepen'):
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
#         if self.conf.getvar('debcredkort:wegstrepen'):
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
    dc = DebcredKort(journaal, begindc)
    dc.maak()
    dc.write()




