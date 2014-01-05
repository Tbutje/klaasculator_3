
import uno
import unohelper
import platform
import sys
import threading

from com.sun.star.task import XJobExecutor

if not hasattr(sys, 'argv'):
    sys.argv = ['openoffice']
else:
    sys.argv.append('openoffice')

if platform.system().startswith('Win'):
    try:
        import _winreg
        k = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\klaasculator')
        kpath = _winreg.QueryValueEx(k, 'Path')[0]
        sys.path.insert(0, kpath)
        sys.path.insert(0, os.path.join(kpath, 'gtkbin'))
        import pygtk
        sys.path.insert(0, pygtk._pygtk_2_0_dir)
        k.Close()
    except:
        pass
else: # toevoeging van Klaas, omdat ik graag de klaasculator in mijn $HOME zet
    import os
    home = os.getenv('HOME')
    sys.path.insert(0, '%s/lib/python%d.%d/site-packages' % (home, sys.version_info[0], sys.version_info[1]))

status = 'ok'
try:
    from klaasculator import *
except Exception, e:
    status = str(e)

def nietgeimplementeerd():
    raise Fout('Deze functie is (nog) niet geimplementeerd.')

# als klaasculator niet kan importeren, moeten we een foutmelding geven met die belachelijke ingebouwde gui toolkit
# http://codesnippets.services.openoffice.org/Office/Office.MessageBoxWithTheUNOBasedToolkit.snip

from com.sun.star.awt import WindowDescriptor
from com.sun.star.awt.VclWindowPeerAttribute import OK
from com.sun.star.awt.WindowClass import MODALTOP

def messagebox(tekst, ctx):
    desktop = ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', ctx)
    doc = desktop.getCurrentComponent()
    c = doc.getCurrentController()
    pw = c.Frame.ContainerWindow

    d = WindowDescriptor()
    d.Type = MODALTOP
    d.WindowServiceName = 'messbox'
    d.ParentIndex = -1
    d.Parent = pw
    d.WindowAttributes = OK

    tk = pw.getToolkit()

    mb = tk.createWindow(d)
    mb.setMessageText(tekst)
    mb.setCaptionText('Oei')
    return mb.execute()

class Verkeersregelaar(unohelper.Base, XJobExecutor):
    def __init__(self, ctx):
        self.ctx = ctx
        if status == 'ok':
            try:
                OOContext(ctx)
                Config()
                Relaties()
            except Fout, f:
                f.settraceback(gettraceback())
                f.show(False)
            except Exception, e:
                f = Fout(str(e) + '\nDit is misschien een bug en moet je Klaas erbij halen.', gettraceback())
                f.show(True)

    def trigger(self, args):
        if status != 'ok':
            try:
                messagebox('Er ging iets mis met het importeren van de klaasculator, contolleer je installatie.\n\n%s\n\n%s' % (sys.path, status), self.ctx)
            except Exception, e:
                print e
            return
        try:
            functie = args

            if functie == 'Tegenregel':
                tegenregel()
                return

            if functie == 'Layout':
                layout()
                return

            if functie == 'Debug':
                Debug()
                return

            if functie == 'Boekstuk_Editor':
                boekstukeditor()
                return

            if functie == 'Kascie_Helper':
                kasciehelper()
                return

            if functie == 'Selecteer_een_relatie':
                KiesRelatie()
                return

            if functie == 'Refresh_Config_relaties':
                refresh_conf_rel()
                return

            if functie == 'Compileer_Alles':
                compileeralles()
                return

            if functie == 'Sorteer_Journaal':
                sorteerjournaal()
                return

            if functie == 'Maak_Grootboek':
                maakgrootboek()
                return

            if functie == 'debCred_leden':
                maakdebcredkortleden()
                return

            if functie == 'begin_dc':
                maakbegindc()
                return

            if functie == 'Baromzet':
                baromzet()
                return

            if functie == 'NICO':
                nico()
                return

            if functie == 'Configuratie_Aanpassen':
                EditConfig()
                return

            if functie == 'Relaties_Aanpassen':
                EditRelaties()
                return

            if functie == 'Selecteer_Configuratiebestand':
                selectconfig()
                return

            if functie == 'Selecteer_Relatiebestand':
                selectrelaties()
                return

            if functie == 'Sneltoetsen_activeren':
                enablekeys()
                return

            if functie == 'Python_Console':
                console()
                return

            raise Fout('Onbekende funcie \'%s\'' % functie)
        except Fout, f:
            f.settraceback(gettraceback())
            f.show(False)
        except Exception, e:
            f = Fout(str(e) + '\nDit is misschien een bug en moet je Klaas erbij halen.', gettraceback())
            f.show(True)

g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(Verkeersregelaar, 'klaasculator_oo.Verkeersregelaar', ('com.sun.star.task.Job',))
