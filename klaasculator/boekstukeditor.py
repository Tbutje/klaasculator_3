from powertools import *

class BoekstukEditor:
    def __init__(self, sheetname = 'Journaal'):
        self.window = gtkwindow('Boekstuk Editor')

        hbox = gtkvbox()

        self.zoek = BoekstukZoekerWidget(sheetname)
        self.boekstuk = BoekstukWidget()

        self.zoek.set_callback(self.boekstuk.set_boekstuk)
        self.boekstuk.set_editable(True)

        bbox = gtkhbuttonbox()
        annuleren = gtk.Button(stock = gtk.STOCK_CANCEL)
        annuleren.connect('clicked', self.annuleren)

        volgende = gtk.Button(stock = gtk.STOCK_GO_FORWARD)
        volgende.connect('clicked', self.volgende)

        ok = gtk.Button(stock = gtk.STOCK_APPLY)
        ok.connect('clicked', self.ok)

        bbox.pack_start(annuleren)
        bbox.pack_start(volgende)
        bbox.pack_start(ok)
        
        hbox.pack_start(gtk.Label('Zoek het boekstuk:'), expand = False)
        hbox.pack_start(self.zoek.widget, expand = False)
        hbox.pack_start(gtk.HSeparator(), expand = False)
        hbox.pack_start(gtk.HSeparator(), expand = False)
        hbox.pack_start(gtk.Label('Wijzig het boekstuk:'), expand = False)
        hbox.pack_start(self.boekstuk.widget)
        hbox.pack_start(gtk.HSeparator(), expand = False)
        hbox.pack_start(gtk.HSeparator(), expand = False)
        hbox.pack_start(bbox, expand = False)

        self.writer = BoekstukWriter(sheetname)
        self.window.add(hbox)
        self.window.maximize()

    def run(self):
        self.window.show_all()
        gtk.main()

    def maak(self):
        b = self.boekstuk.get_boekstuk()
        self.writer.write(b, self.zoek.bkiter.row)

    def annuleren(self, b):
        self.window.destroy()

    def volgende(self, b):
        self.maak()
        self.zoek.zoek(None)

    def ok(self, b):
        self.maak()
        self.window.destroy()

def boekstukeditor():
    b = BoekstukEditor()
    b.run()

def kasciehelper():
    k = BoekstukEditor()
    k.window.set_title('Kascie Helper')
    k.boekstuk.set_editable(False)
    k.boekstuk.set_kascie(True)
    k.run()
    
if __name__ == "__main__":
    kasciehelper()