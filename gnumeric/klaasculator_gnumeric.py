import sys

if not hasattr(sys, 'argv'):
    sys.argv = ['gnumeric']
else:
    sys.argv.append('gnumeric')

from klaasculator import *

def nietgeimplementeerd():
    raise Fout('Deze functie is (nog) niet geimplementeerd.')


def gnumeric_Tegenregel(e):
    try:
        Config()
        Relaties()
    except Fout, f:
        f.settraceback(gettraceback())
        f.show(False)
    except Exception, e:
        f = Fout(str(e) + '\nDit is misschien een bug en moet je Klaas erbij halen.', gettraceback())
        f.show(True)

    try:
        tegenregel()
    except Fout, f:
        f.settraceback(gettraceback())
        f.show(False)
    except Exception, e:
        f = Fout(str(e) + '\nDit is misschien een bug en moet je Klaas erbij halen.', gettraceback())
        f.show(True)

def gnumeric_Layout(e):
    try:
        Config()
        Relaties()
    except Fout, f:
        f.settraceback(gettraceback())
        f.show(False)
    except Exception, e:
        f = Fout(str(e) + '\nDit is misschien een bug en moet je Klaas erbij halen.', gettraceback())
        f.show(True)

    try:
        layout()
    except Fout, f:
        f.settraceback(gettraceback())
        f.show(False)
    except Exception, e:
        f = Fout(str(e) + '\nDit is misschien een bug en moet je Klaas erbij halen.', gettraceback())
        f.show(True)

def gnumeric_Debug(e):
    try:
        Config()
        Relaties()
    except Fout, f:
        f.settraceback(gettraceback())
        f.show(False)
    except Exception, e:
        f = Fout(str(e) + '\nDit is misschien een bug en moet je Klaas erbij halen.', gettraceback())
        f.show(True)

    try:
        Debug()
    except Fout, f:
        f.settraceback(gettraceback())
        f.show(False)
    except Exception, e:
        f = Fout(str(e) + '\nDit is misschien een bug en moet je Klaas erbij halen.', gettraceback())
        f.show(True)

def gnumeric_Importeer_CSV(e):
    try:
        Config()
        Relaties()
    except Fout, f:
        f.settraceback(gettraceback())
        f.show(False)
    except Exception, e:
        f = Fout(str(e) + '\nDit is misschien een bug en moet je Klaas erbij halen.', gettraceback())
        f.show(True)

    try:
        importeer_csv()
    except Fout, f:
        f.settraceback(gettraceback())
        f.show(False)
    except Exception, e:
        f = Fout(str(e) + '\nDit is misschien een bug en moet je Klaas erbij halen.', gettraceback())
        f.show(True)

def gnumeric_Boekstuk_Editor(e):
    try:
        Config()
        Relaties()
    except Fout, f:
        f.settraceback(gettraceback())
        f.show(False)
    except Exception, e:
        f = Fout(str(e) + '\nDit is misschien een bug en moet je Klaas erbij halen.', gettraceback())
        f.show(True)

    try:
        boekstukeditor()
    except Fout, f:
        f.settraceback(gettraceback())
        f.show(False)
    except Exception, e:
        f = Fout(str(e) + '\nDit is misschien een bug en moet je Klaas erbij halen.', gettraceback())
        f.show(True)

def gnumeric_Kascie_Helper(e):
    try:
        Config()
        Relaties()
    except Fout, f:
        f.settraceback(gettraceback())
        f.show(False)
    except Exception, e:
        f = Fout(str(e) + '\nDit is misschien een bug en moet je Klaas erbij halen.', gettraceback())
        f.show(True)

    try:
        kasciehelper()
    except Fout, f:
        f.settraceback(gettraceback())
        f.show(False)
    except Exception, e:
        f = Fout(str(e) + '\nDit is misschien een bug en moet je Klaas erbij halen.', gettraceback())
        f.show(True)

def gnumeric_Selecteer_een_relatie(e):
    try:
        Config()
        Relaties()
    except Fout, f:
        f.settraceback(gettraceback())
        f.show(False)
    except Exception, e:
        f = Fout(str(e) + '\nDit is misschien een bug en moet je Klaas erbij halen.', gettraceback())
        f.show(True)

    try:
        KiesRelatie()
    except Fout, f:
        f.settraceback(gettraceback())
        f.show(False)
    except Exception, e:
        f = Fout(str(e) + '\nDit is misschien een bug en moet je Klaas erbij halen.', gettraceback())
        f.show(True)

def gnumeric_Compileer_Alles(e):
    try:
        Config()
        Relaties()
    except Fout, f:
        f.settraceback(gettraceback())
        f.show(False)
    except Exception, e:
        f = Fout(str(e) + '\nDit is misschien een bug en moet je Klaas erbij halen.', gettraceback())
        f.show(True)

    try:
        compileeralles()
    except Fout, f:
        f.settraceback(gettraceback())
        f.show(False)
    except Exception, e:
        f = Fout(str(e) + '\nDit is misschien een bug en moet je Klaas erbij halen.', gettraceback())
        f.show(True)

def gnumeric_Sorteer_Journaal(e):
    try:
        Config()
        Relaties()
    except Fout, f:
        f.settraceback(gettraceback())
        f.show(False)
    except Exception, e:
        f = Fout(str(e) + '\nDit is misschien een bug en moet je Klaas erbij halen.', gettraceback())
        f.show(True)

    try:
        sorteerjournaal()
    except Fout, f:
        f.settraceback(gettraceback())
        f.show(False)
    except Exception, e:
        f = Fout(str(e) + '\nDit is misschien een bug en moet je Klaas erbij halen.', gettraceback())
        f.show(True)

def gnumeric_Maak_Grootboek(e):
    try:
        Config()
        Relaties()
    except Fout, f:
        f.settraceback(gettraceback())
        f.show(False)
    except Exception, e:
        f = Fout(str(e) + '\nDit is misschien een bug en moet je Klaas erbij halen.', gettraceback())
        f.show(True)

    try:
        maakgrootboek()
    except Fout, f:
        f.settraceback(gettraceback())
        f.show(False)
    except Exception, e:
        f = Fout(str(e) + '\nDit is misschien een bug en moet je Klaas erbij halen.', gettraceback())
        f.show(True)

def gnumeric_debCred_leden(e):
    try:
        Config()
        Relaties()
    except Fout, f:
        f.settraceback(gettraceback())
        f.show(False)
    except Exception, e:
        f = Fout(str(e) + '\nDit is misschien een bug en moet je Klaas erbij halen.', gettraceback())
        f.show(True)

    try:
        maakdebcredkortleden()
    except Fout, f:
        f.settraceback(gettraceback())
        f.show(False)
    except Exception, e:
        f = Fout(str(e) + '\nDit is misschien een bug en moet je Klaas erbij halen.', gettraceback())
        f.show(True)

def gnumeric_begin_dc(e):
    try:
        Config()
        Relaties()
    except Fout, f:
        f.settraceback(gettraceback())
        f.show(False)
    except Exception, e:
        f = Fout(str(e) + '\nDit is misschien een bug en moet je Klaas erbij halen.', gettraceback())
        f.show(True)

    try:
        maakbegindc()
    except Fout, f:
        f.settraceback(gettraceback())
        f.show(False)
    except Exception, e:
        f = Fout(str(e) + '\nDit is misschien een bug en moet je Klaas erbij halen.', gettraceback())
        f.show(True)

def gnumeric_Baromzet(e):
    try:
        Config()
        Relaties()
    except Fout, f:
        f.settraceback(gettraceback())
        f.show(False)
    except Exception, e:
        f = Fout(str(e) + '\nDit is misschien een bug en moet je Klaas erbij halen.', gettraceback())
        f.show(True)

    try:
        baromzet()
    except Fout, f:
        f.settraceback(gettraceback())
        f.show(False)
    except Exception, e:
        f = Fout(str(e) + '\nDit is misschien een bug en moet je Klaas erbij halen.', gettraceback())
        f.show(True)

def gnumeric_NICO(e):
    try:
        Config()
        Relaties()
    except Fout, f:
        f.settraceback(gettraceback())
        f.show(False)
    except Exception, e:
        f = Fout(str(e) + '\nDit is misschien een bug en moet je Klaas erbij halen.', gettraceback())
        f.show(True)

    try:
        nico()
    except Fout, f:
        f.settraceback(gettraceback())
        f.show(False)
    except Exception, e:
        f = Fout(str(e) + '\nDit is misschien een bug en moet je Klaas erbij halen.', gettraceback())
        f.show(True)

def gnumeric_Configuratie_Aanpassen(e):
    try:
        Config()
        Relaties()
    except Fout, f:
        f.settraceback(gettraceback())
        f.show(False)
    except Exception, e:
        f = Fout(str(e) + '\nDit is misschien een bug en moet je Klaas erbij halen.', gettraceback())
        f.show(True)

    try:
        EditConfig()
    except Fout, f:
        f.settraceback(gettraceback())
        f.show(False)
    except Exception, e:
        f = Fout(str(e) + '\nDit is misschien een bug en moet je Klaas erbij halen.', gettraceback())
        f.show(True)

def gnumeric_Relaties_Aanpassen(e):
    try:
        Config()
        Relaties()
    except Fout, f:
        f.settraceback(gettraceback())
        f.show(False)
    except Exception, e:
        f = Fout(str(e) + '\nDit is misschien een bug en moet je Klaas erbij halen.', gettraceback())
        f.show(True)

    try:
        EditRelaties()
    except Fout, f:
        f.settraceback(gettraceback())
        f.show(False)
    except Exception, e:
        f = Fout(str(e) + '\nDit is misschien een bug en moet je Klaas erbij halen.', gettraceback())
        f.show(True)

def gnumeric_Selecteer_Configuratiebestand(e):
    try:
        Config()
        Relaties()
    except Fout, f:
        f.settraceback(gettraceback())
        f.show(False)
    except Exception, e:
        f = Fout(str(e) + '\nDit is misschien een bug en moet je Klaas erbij halen.', gettraceback())
        f.show(True)

    try:
        selectconfig()
    except Fout, f:
        f.settraceback(gettraceback())
        f.show(False)
    except Exception, e:
        f = Fout(str(e) + '\nDit is misschien een bug en moet je Klaas erbij halen.', gettraceback())
        f.show(True)

def gnumeric_Selecteer_Relatiebestand(e):
    try:
        Config()
        Relaties()
    except Fout, f:
        f.settraceback(gettraceback())
        f.show(False)
    except Exception, e:
        f = Fout(str(e) + '\nDit is misschien een bug en moet je Klaas erbij halen.', gettraceback())
        f.show(True)

    try:
        selectrelaties()
    except Fout, f:
        f.settraceback(gettraceback())
        f.show(False)
    except Exception, e:
        f = Fout(str(e) + '\nDit is misschien een bug en moet je Klaas erbij halen.', gettraceback())
        f.show(True)

def gnumeric_Sneltoetsen_activeren(e):
    try:
        Config()
        Relaties()
    except Fout, f:
        f.settraceback(gettraceback())
        f.show(False)
    except Exception, e:
        f = Fout(str(e) + '\nDit is misschien een bug en moet je Klaas erbij halen.', gettraceback())
        f.show(True)

    try:
        enablekeys()
    except Fout, f:
        f.settraceback(gettraceback())
        f.show(False)
    except Exception, e:
        f = Fout(str(e) + '\nDit is misschien een bug en moet je Klaas erbij halen.', gettraceback())
        f.show(True)

def gnumeric_Python_Console(e):
    try:
        Config()
        Relaties()
    except Fout, f:
        f.settraceback(gettraceback())
        f.show(False)
    except Exception, e:
        f = Fout(str(e) + '\nDit is misschien een bug en moet je Klaas erbij halen.', gettraceback())
        f.show(True)

    try:
        console()
    except Fout, f:
        f.settraceback(gettraceback())
        f.show(False)
    except Exception, e:
        f = Fout(str(e) + '\nDit is misschien een bug en moet je Klaas erbij halen.', gettraceback())
        f.show(True)
klaasculator_ui_actions = {'Tegenregel' : gnumeric_Tegenregel,
                           'Layout' : gnumeric_Layout,
                           'Debug' : gnumeric_Debug,
                           'Importeer_CSV' : gnumeric_Importeer_CSV,
                           'Boekstuk_Editor' : gnumeric_Boekstuk_Editor,
                           'Kascie_Helper' : gnumeric_Kascie_Helper,
                           'Selecteer_een_relatie' : gnumeric_Selecteer_een_relatie,
                           'Compileer_Alles' : gnumeric_Compileer_Alles,
                           'Sorteer_Journaal' : gnumeric_Sorteer_Journaal,
                           'Maak_Grootboek' : gnumeric_Maak_Grootboek,
                           'debCred_leden' : gnumeric_debCred_leden,
                           'begin_dc' : gnumeric_begin_dc,
                           'Baromzet' : gnumeric_Baromzet,
                           'NICO' : gnumeric_NICO,
                           'Configuratie_Aanpassen' : gnumeric_Configuratie_Aanpassen,
                           'Relaties_Aanpassen' : gnumeric_Relaties_Aanpassen,
                           'Selecteer_Configuratiebestand' : gnumeric_Selecteer_Configuratiebestand,
                           'Selecteer_Relatiebestand' : gnumeric_Selecteer_Relatiebestand,
                           'Sneltoetsen_activeren' : gnumeric_Sneltoetsen_activeren,
                           'Python_Console' : gnumeric_Python_Console,
                           }
