from powertools import *

from StringIO import StringIO
from urllib import urlopen

import csv, re

LID, OLV, EXTERN = range(3) # enum

class Relaties:
    """Singleton class voor de relaties.

    Roep voor je je functies uitvoert (maar na een OOContext()! en Config()) Relaties() aan. Als het goed is, gebeurt dit
    al in unopkg/klaasculator_oo.py.
    Deze Relaties leest het veld C11 op de sheet Info uit voor de url naar het configuratiebestand.
    De data zijn self.leden, self.olv en self.extern, dit zijn respectievelijk de leden, olvers en externen.
    Daarnaast zijn er de data-members self.ledenrek, self.olvrek en self.externrek. Dit zijn namen van rekeningen die
    als 'relatierekeningen' moeten worden beschouwd bij het maken van debiteuren-crediteurenlijsten.
    """

    class ding:
        def __init__(self, filename = ''):
            """Initialiseer.

            Leest het veld ('Info, 'C11') uit. Als hier de naam van een bestaande sheet in staat, dan wordt die sheet als
            configuratie gebruikt. Anders wordt dit als een url naar het configuratiebestand geinterpeteert.
            """
            self.configure(filename)

        def configure(self, filename = ''):
            """Het daadwerkelijke configureren."""
            if filename:
                try:
                    f = open(filename, 'rb')
                except:
                    raise Fout('Kon bestand \'%s\' niet lezen.' % filename)
            else:
                try:
                    loc = getcellstring('Info', 'C11')
                except:
                    raise Fout('Kon de cell C11 op het sheet \'Info\' niet lezen.')
                try: # gooit een exceptie als sheet in kwestie niet bestaat
                    f = self.leessheet(loc)
                except Exception:
                    try:
                        f = urlopen(loc)
                    except:
                        raise Fout('Kon bestand of sheet \'%s\' niet lezen.' % loc)

            self.leden = set()
            self.olv = set()
            self.extern = set()
            self.ledenrek = set()
            self.olvrek = set()
            # added for excluding values
            self.exclude_rek = set()
            self.externrek = set()
            self.alias = {}

            reader = csv.reader(f)
            for l in reader:
                try : 
                    key = l[0].strip('"')
                except:
                     raise Fout('Kon regel \'%s\' niet lezen in relatie bestand' % l)
                try :  
                    value = l[1].strip('"')
                except:
                     raise Fout('Kon regel \'%s\' niet lezen in relatie bestand' % l)

                if key == 'lid':
                    self.leden.add(value)
                elif key == 'olv':
                    self.olv.add(value)
                elif key == 'extern':
                    self.extern.add(value)
                elif key == 'ledenrekening':
                    self.ledenrek.add(value)
                elif key == 'olvrekening':
                    self.olvrek.add(value)
                elif key == 'exclude':
                    self.exclude_rek.add(value)
                elif key.startswith('alias:'):
                    self.alias[key[key.find(':') + 1:]] = value
                    
            # maak hier iets dat alle rekeningde die niet olv of extern zijn
            # add in self.extern; behalve als in exclude_rek
            reks = Config().balansrekeningen()
            reks.sort()
            deb_cred_list = []
            for line in reks:
                if line.nummer > 129 and line.nummer < 150:
                    deb_cred_list.append( Config().getrekening(line.nummer).naam)
                  
            for line in deb_cred_list:
                if line in self.ledenrek:
                    continue
                elif line in self.exclude_rek:
                    continue
                else:
                    self.externrek.add(line)
                  
            f.close()

        def alias_regex(self, string):
            """Zoek in de alias'es als reguliere expressie.

            Dit geeft de bijbehorende list met namen die de reguliere expressie (wat de key van self.alias is), matcht met
            string.
            Stel, je hebt:
            self.alias = {'Klaas' : 'Klaas de Vries', '(tok){2}' : Michiel Bosma}
            en je doet
            rel = Relaties()
            print rel.alias_regex('Meneer Klaas was hier.')
            print rel.alias_regex('hij zei altijd toktok')
            print rel.alias_regex('hij zei altijd tok')
            print rel.alias_regex('dit komt niet voor')
            print rel.alias_regex('') # lege string matcht alles

            geeft als output:
            ['Klaas de Vries']
            ['Michiel Bosma']
            []
            []
            ['Klaas de Vries', 'Michiel Bosma']

            Meer informatie over reguliere expressies, zie de Python library reference hoofdstuk 4.2 (voor mij zien
            reguliere expressies er verder ook maar uit als Donald Duck die aan het schelden is).
            """
            r = []
            for key, value in self.alias.iteritems():
                if re.search(key, string):
                    r.append(value)
            return r

        def exist(self, naam, soort = None):
            """Geeft True als er een relatie 'naam' bestaat van een zekere soort.

            soort moet LID, OLV, of EXTERN zijn. Als soort niet is opgegeven, dan wordt alles uitgeprobeerd.
            """
            if soort == LID:
                return naam in self.leden
            elif soort == OLV:
                return naam in self.olv
            elif soort == EXTERN:
                return naam in self.extern
            return naam in self.leden or naam in self.olv or naam in self.extern

        def isrelatierekening(self, rekening):
            """Geeft True als rekening een relatierekening is.

            rekening kan een string of een Rekening zijn.
            """
            if type(rekening) == str or type(rekening) == unicode:
                return rekening in self.ledenrek or rekening in self.olvrek or rekening in self.externrek
            return rekening.naam in self.ledenrek or rekening.naam in self.olvrek or rekening.naam in self.externrek

        def leessheet(self, loc):
            """Lees de data uit een sheet.

            Dit leest de configuratie uit het sheet loc. retourneert een filepointer-achtige StringIO(). Dit is op zich
            een overbodige kopie, maarach. Het idee is toch dat deze funcie maar een keert wordt uitgevoerd.
            """
            s = Sheet_ro(loc, 0, 0, 1, laatsteboeking(loc))
            f = StringIO()
            for r in s.data:
                f.write('"%s",%s\n' % (r[0], r[1]))
            f.seek(0)
            return f

    instance = None

    def __init__(self, filename = ''):
        if Relaties.instance == None:
             Relaties.instance = Relaties.ding(filename)

    def __getattr__(self, attr):
        return getattr(self.instance, attr)

    def __setattr__(self, attr, value):
        return setattr(self.instance, attr, value)
        
if __name__ == "__main__":
    rel = Relaties()
    print "LEDENREKNNG"
    print rel.ledenrek
    print rel.olvrek
    print "EXTERN"
    print rel.externrek
    print "EXLCIDE"
    print rel.exclude_rek
    
# self.leden, self.olv en self.extern, d
    # self.ledenrek, self.olvrek en self.externrek.