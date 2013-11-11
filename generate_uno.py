import sys

### dit generate aan de hand van menu_def  stuff
## output --> klaasculator_oo.py + *.xcu

def indenteer(f, i):
    f.write('    '*i)

class XML:
    def __init__(self, tag, args = []):
        self.tag = tag
        self.args = args
        self.body = []

    def set(self, body):
        self.body.append(body)
        return body

    def write(self, fd, i = 0):
        indenteer(fd, i)

        fd.write('<%s' % self.tag)
        
        if self.args:
            fd.write(' ')
            fd.write(' '.join(self.args))
        
        if len(self.body) == 0:
            fd.write('/>\n')
        elif len(self.body) == 1 and type(self.body[0]) == str:
            fd.write('>%s</%s>\n' % (self.body[0], self.tag))
        else:
            fd.write('>\n')
            for b in self.body:
                if type(b) == str:
                    indenteer(fd, i + 1)
                    fd.write('%s\n' % b)
                else:
                    b.write(fd, i + 1)
            indenteer(fd, i)
            fd.write('</%s>\n' % self.tag)

class Menuitem:
    def __init__(self, line):
        if len(line) == 2:
            self.name = line[0]
            self.target = line[1]
        else:
            self.name = line[0]
            self.target = [Menuitem(line[1:])]

    def add(self, line):
        self.target.append(Menuitem(line))

    def gnumeric_topy(self, f):
        r = []
        if type(self.target) == str:
            r.append([self.name, 'gnumeric_%s' % self.name])
            f.write('''
def gnumeric_%s(e):
    try:
        Config()
        Relaties()
    except Fout, f:
        f.settraceback(gettraceback())
        f.show(False)
    except Exception, e:
        f = Fout(str(e) + '\\nDit is misschien een bug en moet je Klaas erbij halen.', gettraceback())
        f.show(True)

    try:
        %s()
    except Fout, f:
        f.settraceback(gettraceback())
        f.show(False)
    except Exception, e:
        f = Fout(str(e) + '\\nDit is misschien een bug en moet je Klaas erbij halen.', gettraceback())
        f.show(True)
''' % (self.name, self.target))
        else:
            for t in self.target:
                r.extend(t.gnumeric_topy(f))
        return r

    def gnumeric_toxml(self, xml):
        if type(self.target) == str:
            xml.set(XML('menuitem', ['action="%s"' % self.name]))
        else:
            m = xml.set(XML('menu', ['name="%s"' % self.name.replace('_', ' '), 'action="%s_menu"' % self.name]))
            
            for t in self.target:
                t.gnumeric_toxml(m)

    def gnumeric_pluginxml(self, xml):
        if type(self.target) == str:
            xml.set(XML('action', ['name="%s"' % self.name, 'label="%s"' % self.name.replace('_', ' ')]))
        else:
            act = xml.set(XML('action', ['name="%s_menu"' % self.name, 'label="%s"' % self.name.replace('_', ' ')]))
            
            for t in self.target:
                t.gnumeric_pluginxml(xml)

    def topy(self, f):
        r = []
        if type(self.target) == str:
            r.append(self.name)
            f.write('''
            if functie == '%s':
                %s()
                return
''' % (self.name, self.target))
        else:
            for t in self.target:
                r.extend(t.topy(f))
        return r

    def toxcu(self, xml, count):
        node = xml.set(XML('node', ['oor:name="m%02i"' % count, 'oor:op="replace"']))
        count += 1
        prop = node.set(XML('prop', ['oor:name="URL"', 'oor:type="xs:string"']))
        val = prop.set(XML('value'))

        if type(self.target) == str:
            val.set('service:klaasculator_oo.Verkeersregelaar?%s' % self.name)

        prop = node.set(XML('prop', ['oor:name="Title"', 'oor:type="xs:string"']))
        val = prop.set(XML('value', ['xml:lang="en-US"']))
        val.set(self.name.replace('_', ' '))
        val = prop.set(XML('value', ['xml:lang="nl"']))
        val.set(self.name.replace('_', ' '))

        prop = node.set(XML('prop', ['oor:name="Target"', 'oor:type="xs:string"']))
        val = prop.set(XML('value'))
        val.set('_self')

        if type(self.target) == str:
            prop = node.set(XML('prop', ['oor:name="Context"', 'oor:type="xs:string"']))
            val = prop.set(XML('value'))
            val.set('com.sun.star.sheet.SpreadsheetDocument')
        else:
            node = node.set(XML('node', ['oor:name="Submenu"']))
            
            for t in self.target:
                count = t.toxcu(node, count)
            
            node = xml.set(XML('node', ['oor:name="%02i"' % count, 'oor:op="replace"']))
            count += 1
            prop = node.set(XML('prop', ['oor:name="URL"', 'oor:type="xs:string"']))
            val = prop.set(XML('value'))
            val.set('private:separator')

        return count
 
    def __str__(self, indent = 0):
        s = ' '*indent
        s += self.name
        if type(self.target) == str:
            s += ' : ' + self.target
        else:
            for t in self.target:
                s += t.__str__(indent + 1) + '\n'
        return s

class Menu:
    def __init__(self):
        self.items = []

    def add(self, line):
        for i in self.items:
            if i.name == line[0]:
                i.add(line[1:])
                break
        else:
            self.items.append(Menuitem(line))

    def gnumeric_topy(self, f):
        f.write('''import sys

if not hasattr(sys, 'argv'):
    sys.argv = ['gnumeric']
else:
    sys.argv.append('gnumeric')

from klaasculator import *

def nietgeimplementeerd():
    raise Fout('Deze functie is (nog) niet geimplementeerd.')

''')
        impl = []
        for i in self.items:
            impl.extend(i.gnumeric_topy(f))

        f.write('klaasculator_ui_actions = {')
        for i in impl:
            f.write('\'%s\' : %s,\n                           ' % (i[0], i[1]))
        f.write('}\n')

    def gnumeric_toxml(self, f):
        xml = XML('ui')
        t = xml.set(XML('menubar'))
        t = t.set(XML('menu', ['name="Tools"', 'action="MenuTools"']))
        t = t.set(XML('menu', ['name="klaasculator_menu"', 'action="dummy_menu"']))

        for it in self.items:
            it.gnumeric_toxml(t)
        
        xml.write(f)
        
    def gnumeric_pluginxml(self, f):
        f.write('<?xml version="1.0"?>\n')
        xml = XML('plugin', ['id="Klaasculator"'])
        
        info = xml.set(XML('information'))
        name = info.set(XML('name'))
        name.set('Klaasculator nu ook in Gnumeric')
        desc = info.set(XML('description'))
        desc.set('Klaasculator 3 is dus ook redelijk portable.')
        load = xml.set(XML('loader', ['type="Gnumeric_PythonLoader:python"']))
        load.set(XML('attribute', ['name="module_name"', 'value="klaasculator_gnumeric"']))
        serv = xml.set(XML('services'))
        serv = serv.set(XML('service', ['type="ui"', 'id="klaasculator"', 'file="menu.xml"']))
        acts = serv.set(XML('actions'))
        acts.set(XML('action', ['name="dummy_menu"', 'label="Klaasculator"']))
        
        for it in self.items:
            it.gnumeric_pluginxml(acts)

        xml.write(f)
        
    def header(self, f):
        f.write(r'''
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
''')

    def topy(self, f):
        impl = []
        self.header(f)

        f.write(r'''
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
''')

        for i in self.items:
            i.topy(f)

        f.write('''
            raise Fout('Onbekende funcie \\'%s\\'' % functie)
        except Fout, f:
            f.settraceback(gettraceback())
            f.show(False)
        except Exception, e:
            f = Fout(str(e) + '\\nDit is misschien een bug en moet je Klaas erbij halen.', gettraceback())
            f.show(True)

g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(Verkeersregelaar, 'klaasculator_oo.Verkeersregelaar', ('com.sun.star.task.Job',))
''')
    def toxcu(self, f, f2):
        f.write('<?xml version=\'1.0\' encoding=\'UTF-8\'?>\n')

        xml = XML('oor:component-data', ['oor:name="Addons"',
                                         'oor:package="org.openoffice.Office"',
                                         'xmlns:oor="http://openoffice.org/2001/registry"',
                                         'xmlns:xs="http://www.w3.org/2001/XMLSchema"'])
                                         
        node = xml.set(XML('node', ['oor:name="AddonUI"']))
        node = node.set(XML('node', ['oor:name="OfficeMenuBar"']))
        node = node.set(XML('node', ['oor:name="klaasculator_3"', 'oor:op="replace"']))
        
        prop = node.set(XML('prop', ['oor:name="Title"', 'oor:type="xs:string"']))
        prop.set(XML('value'))
        val = prop.set(XML('value', ['xml:lang="en-US"']))
        val.set('Klaasculator_3')
        val = prop.set(XML('value', ['xml:lang="nl"']))
        val.set('Klaasculator_3')

        prop = node.set(XML('prop', ['oor:name="Target"', 'oor:type="xs:string"']))
        val = prop.set(XML('value'))
        val.set('_self')

        node = node.set(XML('node', ['oor:name="Submenu"']))

        count = 1
        for t in self.items:
            count = t.toxcu(node, count)
           
        xml.write(f)
        
        f2.write('<?xml version=\'1.0\' encoding=\'UTF-8\'?>\n')
        xml = XML('oor:component-data', ['oor:name="ProtocolHandler"',
                                         'oor:package="org.openoffice.Office"',
                                         'xmlns:oor="http://openoffice.org/2001/registry"',
                                         'xmlns:xs="http://www.w3.org/2001/XMLSchema"',
                                         'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'])
        node = xml.set(XML('node', ['oor:name="HandlerSet"']))
        node = node.set(XML('node', ['oor:name="klaasculator_3"', 'oor:op="replace"']))
        prop = node.set(XML('prop', ['oor:name="Protocols"', 'oor:type="oor:string-list"']))
        val  = prop.set(XML('value'))
        val.set('klaasculator_3:*')

        xml.write(f2)

      
    def __str__(self):
        s = ''
        for i in self.items:
            s += str(i) + '\n'
        return s

def main(menu_def, py, xcu):
    f = open(menu_def)

    m = Menu()
    for line in f.readlines():
        if line.startswith('#'):
            continue
        l = line.split()
        if len(l) >= 2:
            m.add(l)
        
    f.close()

    f = open(py, 'w')
    m.topy(f)
    f.close()

    f = open(xcu, 'w')
    f2 = open('unopkg/klaasculator_3.xcu', 'w')
    m.toxcu(f, f2)
    f.close()

def gnumeric(menu_def, py, menu_xml, plugin_xml):
    f = open(menu_def)
    m = Menu()
    for line in f.readlines():
        if line.startswith('#'):
            continue
        l = line.split()
        if len(l) >= 2:
            m.add(l)
    f.close()

    f = open(py, 'w')
    m.gnumeric_topy(f)
    f.close()

    f = open(menu_xml, 'w')
    m.gnumeric_toxml(f)
    f.close()

    f = open(plugin_xml, 'w')
    m.gnumeric_pluginxml(f)
    f.close()

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print 'Gebruik: %s <definitebestand> <output-py> <output-xcu>' % sys.argv[0]
        print 'Bijvoorbeeld: %s menu_def klaasculator_oo.py menu.xcu' % sys.argv[0]
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3])

