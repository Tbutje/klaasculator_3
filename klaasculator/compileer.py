from debcred import *
from debcredkort import *
from debcredkort_leden import *
from grootboek import *
from maakbegindc import *
from powertools import *


def sorteerjournaal():
    """Sorteer het journaal."""

    # lees het bestaande journaal uit en zet de boekregels in een list
    journaal_oud = Sheet_jr_ro('Journaal')


    boekregels = sorter(journaal_oud, sorter_dn) # sorteren

    if not boekregels: # afbreken als er geen boekregels zijn
        return

    # en weer in journaal zetten
    journaal = Sheet_jr(None)

    nummer = boekregels[0].nummer
    datum = boekregels[0].datum

    it = 0 # iterator
    for b in boekregels:
        if b.nummer != nummer or b.datum != datum: # lege regel invoegen
            journaal.setboekregel(it, Boekregel())
            nummer = b.nummer
            datum = b.datum
            it += 1
        journaal.setboekregel(it, b)
        it += 1

    # en schrijven
    journaal.write('Journaal', erase = True)

def mooiebeginbalans():
    """Deze functie schoont de beginbalans op."""
    oud = Sheet_bl_ro('Beginbalans')
    reks = Config().balansrekeningen()
    reks.sort()

    nieuw = Sheet_bl(None)
    it = 0
    for r in reks:
        w = oud.getwaarde(r.nummer)
        nieuw.setbalansregel(it, Balansregel(r.nummer, r.naam, w))
        it += 1

    nieuw.write('Beginbalans')

def autowinst():
    """Maakt automatisch het resultaten-boekstuk."""

    jr = Sheet_jr_ro('Journaal')
    conf = Config()
    edatum = getcellint('Info', 'C8')
    ev = conf.getrekening('Eigen Vermogen').nummer

    w = Euro()

    idstring = 'Automatisch gegenereerd boekstuk, aanpassen op eigen risico!'

    for b in jr:
        if conf.getrekening(b.rekening).soort == BALANSREKENING:
            if ev != b.rekening or b.datum != edatum or b.omschrijving2 != idstring:
                w += b.waarde

    row = jr.find(999, edatum)
    if row > 2:
        b = jr.getboekregel(row - 2)
        if b.nummer == 999 and b.datum == edatum and b.rekening == ev and b.omschrijving2 == idstring:
            row -= 2
        else:
            row += 1
    row += 2

    jrn = Sheet_jr(None, row)
    jrn.setboekregel(0, Boekregel(999,
                                  edatum,
                                  ev,
                                  '',
                                  'Resultaat',
                                  0,
                                  conf.getrekening('Resultaat').nummer,
                                  w.counterpart(),
                                  idstring))
    jrn.setboekregel(1, Boekregel(999,
                                  edatum,
                                  conf.getrekening('Resultaat').nummer,
                                  '',
                                  'Resultaat',
                                  0,
                                  ev,
                                  w,
                                  idstring))
    jrn.write('Journaal')

def maakgrootboek():
    """Maak het grootboek."""

    if Config().getvar('idiotproof:autowinst'):
        autowinst()

    journaal = Sheet_jr_ro('Journaal')
    beginbalans = Sheet_bl_ro('Beginbalans')
    g = Grootboek(journaal, beginbalans)
    g.maak()
    g.write()

def maakdebcred():
    """Maak de debiteuren-crediteurenlijst."""
    journaal = Sheet_jr_ro('Journaal')
    begindc = Sheet_jr_ro('BeginDC')
    dc = Debcred(journaal, begindc)
    dc.maak()
    dc.write()

def maakdebcredkort():
    """Maak de debiteuren-crediteuren samenvatting."""
    journaal = Sheet_jr_ro('Journaal')
    begindc = Sheet_jr_ro('BeginDC')
    dc = DebcredKort(journaal, begindc)
    dc.maak()
    dc.write()

def maakdebcredkortleden():
    """Maak de debiteuren-crediteuren samenvatting."""
    journaal = Sheet_jr_ro('Journaal')
    begindc = Sheet_jr_ro('BeginDC')
    dc = DebcredKortLeden(journaal, begindc)
    dc.maak()
    dc.write()

def maakbegindc():
    journaal = Sheet_jr_ro('Journaal')
    begindc = Sheet_jr_ro('BeginDC')
    dc = MaakBeginDC(journaal, begindc)
    dc.maak()
    dc.write()

def compileeralles():
    """Compileert alles."""
    if Config().getvar('idiotproof:autowinst'):
        autowinst()

    sorteerjournaal()
    mooiebeginbalans()

    journaal = Sheet_jr_ro('Journaal')
    beginbalans = Sheet_bl_ro('Beginbalans')
    begindc = Sheet_jr_ro('BeginDC')

    g = Grootboek(journaal, beginbalans)
    g.maak()
    g.write()

    d = Debcred(journaal, begindc)
    d.maak()
    d.write()

    dc = DebcredKort(journaal, begindc)
    dc.maak()
    dc.write()

    # dl = DebcredKortLeden(journaal, begindc)
    # dl.maak()
    # dl.write()


if __name__ == "__main__":
    compileeralles()
