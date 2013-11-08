from powertools import *

class Grootboek:
    def __init__(self, journaal, beginbalans):
        self.journaal = journaal
        self.beginbalans = beginbalans
        self.grootboek = Sheet_jr(None)
        self.eindbalans = Sheet_bl(None)
        self.resultaten = Sheet_bl(None)
        self.conf = Config()
        self.bdatum = getcellint('Info', 'C6')
        self.edatum = getcellint('Info', 'C8')

    def header(self, it, rekening, waarde):
        """Maakt de headers in het grootboek."""
        self.grootboek.setboekregel(it, Boekregel(rekening = rekening.nummer, omschrijving = rekening.naam))
        it += 1
        self.grootboek.setboekregel(it, Boekregel())
        it += 1
        if rekening.soort == BALANSREKENING:
            self.grootboek.setboekregel(it, Boekregel(0,
                                                      self.bdatum,
                                                      rekening.nummer,
                                                      '',
                                                      'Van beginbalans',
                                                      0,
                                                      0,
                                                      waarde,
                                                      ''))
            self.grootboek.setstring(it, 0, 'Begin')
            it += 1

        return it

    def footer(self, it, it_eb, it_rs, rekening, waarde):
        """Maakt de footers in het grootboek en schrijft naar eindbalans/resultaten."""
        if rekening.soort == BALANSREKENING:
            self.eindbalans.setbalansregel(it_eb, Balansregel(rekening.nummer, rekening.naam, waarde))
            it_eb += 1

            self.grootboek.setboekregel(it, Boekregel(0,
                                                      self.edatum,
                                                      rekening.nummer,
                                                      '',
                                                      'Naar eindbalans',
                                                      0,
                                                      0,
                                                      waarde.counterpart(),
                                                      ''))
                                                                  
        else:
            self.resultaten.setbalansregel(it_rs, Balansregel(rekening.nummer, rekening.naam, waarde))
            it_rs += 1
            self.grootboek.setboekregel(it, Boekregel(0,
                                                      self.edatum,
                                                      rekening.nummer,
                                                      '',
                                                      'Naar resulatenrekening',
                                                      0,
                                                      0,
                                                      waarde.counterpart(),
                                                      ''))
        self.grootboek.setstring(it, 0, 'Eind')
        it += 1
        self.grootboek.setboekregel(it, Boekregel())
        it += 1
        self.grootboek.setboekregel(it, Boekregel())
        it += 1
        return it, it_eb, it_rs

    def nextrek(self, rekeningen, check = 0):
        """Hulpfunctie."""
        if not rekeningen:
            if not check:
                raise Fout('Er zijn geen rekeningen gedefinieerd.')
            else:
                raise Fout('Rekening %i is niet gedefinieerd.' % check)

        rek = rekeningen.pop(0)
        if rek.soort == BALANSREKENING:
            waarde = self.beginbalans.getwaarde(rek.nummer)
        else:
            waarde = Euro()

        return rek, waarde

    def maak(self):
        """Maak het grootboek.

        journaal en beginbalans zijn de Sheet_jr_ro en Sheet_bl_ro voor journaal en beginbalans.
        """
        boekregels = sorter(self.journaal, sorter_rdn) # sorteren

        rekeningen = self.conf.rekeninglist() # rekeningnummers krijgen
        rekeningen.sort()

        if not rekeningen:
            raise Fout('Er zijn geen rekeningen gedefinieerd.')

        rek, waarde = self.nextrek(rekeningen)

        it, it_eb, it_rs = 0, 0, 0 # iterator

        # het daadwerkelijke bouwen:
        it = self.header(it, rek, waarde)

        for b in boekregels:
            while rek.nummer != b.rekening:
                it, it_eb, it_rs = self.footer(it, it_eb, it_rs, rek, waarde)
                rek, waarde = self.nextrek(rekeningen, b.rekening)

                it = self.header(it, rek, waarde)

            self.grootboek.setboekregel(it, b)
            it += 1
            waarde += b.waarde
        it, it_eb, it_rs = self.footer(it, it_eb, it_rs, rek, waarde)

        # opruimen, misschien zijn er nog rekeningen over.
        while rekeningen:
            rek, waarde = self.nextrek(rekeningen)
            it = self.header(it, rek, waarde)
            it, it_eb, it_rs = self.footer(it, it_eb, it_rs, rek, waarde)

    def write(self):
        """Schrijven."""
        self.grootboek.write('Grootboek', erase = True)
        self.eindbalans.write('Eindbalans')
        self.resultaten.write('Resultaten')
    
