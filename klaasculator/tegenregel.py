from powertools import *


def tegenregel():
    """Maak een tegenregel."""

    # lees eerst het bestaande boekstuk

    row = getactivecell()[0] - 2
    sheetname = getactivesheet()

    sheet = Sheet_jr_ro(sheetname)
    boekstuk, row = sheet.getboekstuk_local(row)
    origsize = len(boekstuk)

    # en tegenregel/balanceren

    if Config().getvar('tegenregel:balanceer'):
        boekstuk.balanceer()
    else:
        boekstuk.tegenregel()

    # en schrijven:

    appendboekstuk(boekstuk[origsize:], row + 3, sheetname)
    
        
