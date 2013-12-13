from StringIO import StringIO
import csv
# from urllib import urlopen
from tools import *


BALANSREKENING, RESULTATENREKENING = range(2) # enum

class Rekening:
    """Class die informatie over een rekening opslaat.

    self.nummer is het nummer van de rekening (bv 100), self.naam de naam (bv 'Kas algemeen'). self.soort is het type
    rekening. dit moet BALANSREKENING of RESULTATENREKENING zijn.
    """
    def __init__(self, nummer, naam, soort):
        """Initialiseer."""
        self.nummer = nummer
        self.naam = naam
        self.soort = soort

    def __cmp__(self, other):
        return cmp(self.nummer, other.nummer)

class Config:
    """Singleton class voor de configuratie.

    Roep voor je je functies uitvoert (maar na een OOContext()!) Config() aan. Als het goed is, gebeurt dit al in
    unopkg/klaasculator_oo.py.
    Deze Config leest het veld C10 op de sheet Info uit voor de url naar het configuratiebestand. Als toevoeging is het ook
    mogelijk hier de naam van een blad in je bestand in te vullen.
    Het houdt intern naast een dict (hashmap) self.variabelen ook de hashmaps self.rekening en self.rekening2 bij. Met de
    eerste kun je een rekenin opzoeken gegeven een naam, met de tweede kun je een rekening opzoeken gegeven een int.
    """

    class ding:
        def __init__(self, filename = ''):
            """Initialiseer.

            Leest het veld ('Info, 'C10') uit. Als hier de naam van een bestaande sheet in staat, dan wordt die sheet als
            configuratie gebruikt. Anders wordt dit als een url naar het configuratiebestand geinterpeteerd.
            """
            self.configure(filename)

        def configure(self, filename = ''):
            """Het daadwerkelijke configureren."""
            if filename:
                try:
                    f = open(filename, 'rb')
                except:
                    raise Fout('Kon bestand \'%s\' niet lezen' % filename)
            else:
                try:
                    loc = getcellstring('Info', 'C10')
                except:
                    raise Fout('Kon cell C10 op de sheet \'Info\' niet lezen.')
                try: # gooit een exceptie als sheet in kwestie niet bestaat
                    f = self.leessheet(loc)
                except Exception:
                    try:
#                         f = urlopen(loc)
                        f = open(loc)
                    except:
                        raise Fout('Kon bestand of sheet \'%s\' niet lezen.' % loc)

            self.rekening = {}
            self.rekening2 = {}
            self.variabelen = {}

            reader = csv.reader(f)
            rownum = 0
            for l in reader:
                try:
                    key = l[0].strip('"')
                except IndexError:
                    raise Fout("fout bij inlezen config op RIJ %i, misschien staat er een lege enter of een regel?" % (rownum + 1))
                try:
                    value = int(l[1])
                except IndexError:
                    raise Fout("fout bij inlezen config op RIJ %i , misschien is heeft een variabele op een regel geen waarde? " % (rownum + 1))

                if key.startswith('balansrekening:'):
                    naam = key[key.find(':') + 1:]
                    self.rekening[naam] = Rekening(value, naam, BALANSREKENING)
                    self.rekening2[value] = Rekening(value, naam, BALANSREKENING)
                elif key.startswith('resultatenrekening'):
                    naam = key[key.find(':') + 1:]
                    self.rekening[naam] = Rekening(value, naam, RESULTATENREKENING)
                    self.rekening2[value] = Rekening(value, naam, RESULTATENREKENING)
                else:
                    self.variabelen[key] = value
                rownum +=1

            f.close()

        def getvar(self, key, default = None):
            """Geef de waarde van de variabele key. Optioneel kan er een default waarde meegegeven worden."""
            try:
                return self.variabelen[key]
            except:
                if default != None:
                    return default
                raise Fout('Variabele \'%s\' key is niet opgegeven in het configuratiebestand.' % key)

        def getrekening(self, key, soort = None):
            """Geef de rekening.

            key kan een int zijn of een string. Met een string kan efficienter gezocht worden. Voor soort kun je
            BALANSREKENING of RESULTATENREKENING opgeven. Als dat is opgegeven, zal de functie alleen een rekening
            teruggeven als de soort klopt.
            """
            try:
                if type(key) == str or type(key) == unicode:
                    r = self.rekening[key]
                else:
                    r = self.rekening2[key]

                if soort != None and r.soort != soort:
                    raise Fout()
                return r
            except:
                raise Fout('Kon geen rekening \'' + str(key) + '\' vinden of deze had het verkeerde type.')

        def getbalansrekening(self, key):
            """Shortcut."""
            return self.getrekening(key, BALANSREKENING)

        def getresultrekening(self, key):
            """Shortcut."""
            return self.getrekening(key, RESULTATENREKENING)

        def rekeninglist(self):
            """Retourneert een list met rekeningen."""
            return self.rekening.values()

        def balansrekeningen(self):
            """Retourneert een list met balanrekeningen."""
            return filter(lambda x: x.soort == BALANSREKENING, self.rekening.values())

        def resultrekeningen(self):
            """Retourneert een list met resultatenrekeningen."""
            return filter(lambda x: x.soort == RESULTATENREKENING, self.rekening.values())

        def leessheet(self, loc):
            """Lees de data uit een sheet.

            Dit leest de configuratie uit het sheet loc. retourneert een filepointer-achtige StringIO(). Dit is op zich
            een overbodige kopie, maarach. Het idee is toch dat deze funcie maar een keert wordt uitgevoerd.
            """
            s = Sheet_ro(loc, 0, 0, 1, laatsteboeking(loc))
            f = StringIO()
            for r in s.data:
                f.write('"%s",%i\n' % (r[0], r[1]))
            f.seek(0)
            return f

    instance = None

    def __init__(self, filename = ''):
        if Config.instance == None:
            Config.instance = Config.ding(filename)

    def __getattr__(self, attr):
        return getattr(self.instance, attr)

    def __setattr__(self, attr, value):
        return setattr(self.instance, attr, value)

if __name__ == "__main__":
    Config()