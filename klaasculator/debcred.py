from powertools import *

class Debcred:
    """Maak een debiteuren- en crediteurenlijst."""

    def __init__(self, journaal, begindc):
        """Initialiseer.

        De parameters journaal en begindc zijn Sheet_jr_ro van Journaal en BeginDC.
        """

        self.journaal = journaal
        self.begindc = begindc
        self.dclijst = Sheet_jr(None)
        self.check = False
        self.conf = Config()
        self.rel = Relaties()
        if self.conf.getvar('debcred:checknaam'):
            self.check = True

        self.bdatum = getcellint('Info', 'C6')
        self.edatum = getcellint('Info', 'C8')

    def header(self, it, b):
        """Hulpfunctie.

        Dit maakt de headers. Als regel b de datum begindatum - 1 is, is het een regel van de begindc.
        """
        self.dclijst.setboekregel(it, Boekregel(rekening = b.rekening, omschrijving = b.omschrijving))
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

    def footer(self, it, r, w):
        self.dclijst.setboekregel(it, Boekregel(0,
                                                self.edatum,
                                                r.rekening,
                                                '',
                                                'Naar eindbalans',
                                                0,
                                                0,
                                                w.counterpart(),
                                                ''))
        self.dclijst.setstring(it, 0, 'Eind')
        it += 1
        self.dclijst.setboekregel(it, Boekregel())
        it += 1
        self.dclijst.setboekregel(it, Boekregel())
        it += 1                                  
        return it

    def maak(self):
        """Maak de handel."""

        beg = self.begindc_fix()
        # dit checked of het in een van de Relaties.rek is; extern, leden, olv
        beg.extend(filter(lambda b: self.rel.isrelatierekening(self.conf.getrekening(b.rekening)), self.journaal))
        regels = sorter(beg, sorter_rodn)

        if not regels: #stoppen bij lege boekhouding
            return

        rel = regels.pop(0)
        it = self.header(0, rel)
        waarde = rel.waarde
        
        for r in regels:
            if self.check and not self.rel.exist(r.omschrijving):
                raise Fout('\'%s\' is niet bekend in het relatiebestand.' % r.omschrijving)                
            
            if r.omschrijving != rel.omschrijving or r.rekening != rel.rekening:
                it = self.footer(it, rel, waarde)
                it = self.header(it, r)
                rel = r
                waarde = r.waarde
            else:
                self.dclijst.setboekregel(it, r)
                it += 1
                waarde += r.waarde
        self.footer(it, rel, waarde)

    def write(self):
        """Wie schrijft die blijft."""
        self.dclijst.write('DebCred', erase = True)
            
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

        return bdc
        
    

if __name__ == "__main__":
    journaal = Sheet_jr_ro('Journaal')
    beginbalans = Sheet_bl_ro('Beginbalans')
    begindc = Sheet_jr_ro('BeginDC')
    d = Debcred(journaal, begindc)
    d.maak()
    d.write()
    
