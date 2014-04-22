from StringIO import StringIO
import csv
import re
from powertools import *


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
                        f = open(loc)
                    except:
                        raise Fout('Kon bestand of sheet \'%s\' niet lezen.' % loc)

            self.leden = []
            self.leden_codes = set() # deze gaat alleen ficos opslaan.
            self.ficos = []
            self.olv = set()
            self.extern = set()
            self.ledenrek = set()
            self.olvrek = set()
            # added for excluding values
            self.exclude_rek = set()
            self.externrek = set()
            self.alias = {}

            reader = csv.reader(f)
            rownum = 0
            for l in reader:
                try :
                    key = l[0].strip('"')
                except:
                    raise Fout('fout bij inlezen relaties op RIJ %i, misschien \
                    staat er een lege enter of een regel?' % (rownum + 1))
                try :
                    value = l[1].strip('"')
                except:
                    raise Fout('fout bij inlezen relaties op RIJ %i, misschien \
                     staat er een lege enter of een regel?' % (rownum + 1))

                if key == 'lid':
                    try:
                        naam = l[2].strip('"')
                    except:
                        naam = ""
                    try :
                        woonplaats = l[3].strip('"')
                    except:
                        woonplaats = ""
                    try:
                        reknr = str(l[4])

                    except:
                        reknr = ""
                    self.leden.append((value, naam, woonplaats, reknr))

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

                rownum +=1

            # versimpelde list maken van rel.leden met alleen fico.
            for line in self.leden:
                if line[0] in self.leden_codes:
                    raise Fout("fico niet uniek %s" % line[0])
                self.leden_codes.add(line[0])

            # maak lijst met ficos en check if uniek
            for line in self.leden:
                fico = line[0][:4]

                #check if geen naam
                if not fico.isupper():
                    raise Fout("naam ipv fico %s" % line[0])

                # check if dubbel
                if fico in self.ficos:
                    raise Fout("FICO dubbel %s" % line[0])

                self.ficos.append(fico)

            # loop door olvers
            for line in self.olv:
                fico = line[0][:4]

                #check if geen naam
                if not fico.isupper():
                    raise Fout("naam ipv fico %s" % line[0])

                # check if dubbel
                if fico in self.ficos:
                    raise Fout("FICO dubbel %s" % line[0])

                self.ficos.append(fico)


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
                return naam in self.leden_codes
            elif soort == OLV:
                return naam in self.olv
            elif soort == EXTERN:
                return naam in self.extern
            return naam in self.leden_codes or naam in self.olv or naam in self.extern

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
            s = Sheet_ro(loc, 0, 0, 4, laatsteboeking(loc))
            f = StringIO()
            for r in s.data:
                if r[0] == "lid":
                    try:

                        try:
                            naam = r[2].strip('"')
                        except:
                            naam = ""
                        try:
                            woonplaats = r[3].strip('"')
                        except:
                            woonplaats = ""
                        try:
                            reknr = int(r[4])
                        except:
                            reknr = str(r[4])


                        f.write('%s,%s,%s,%s,%s\n' % \
                                (r[0], r[1], naam, woonplaats,reknr))
                    except Exception, e:
                        print e
                        raise Fout("mogelijk probleem met missende rijen in relatie bestand")
                else:
                    try:
                        f.write('%s,%s\n' % (r[0], r[1]))
                    except Exception, e:
                        print e
                        raise Fout("mogelijk probleem met missende rijen in relatie bestand")
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
    print "print rel.leden"
    print rel.leden_codes
    print rel.exist("TIWO - Tineke Wolting ")
    print "TIWO - Tineke Wolting " in rel.leden_codes

# self.leden, self.olv en self.extern, d
    # self.ledenrek, self.olvrek en self.externrek.