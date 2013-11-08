from powertools import *

class KiesRelatie:
    def __init__(self):
        self.window = gtkwindow('Selecteer een relatie')

        conf = Config()
        self.entry = relatiewidget(conf.getvar('selectrelatie:incleden'),
                                   conf.getvar('selectrelatie:incolv'),
                                   conf.getvar('selectrelatie:incextern'))

        ok = gtk.Button(stock = gtk.STOCK_OK)
        ok.connect('clicked', self.ok)
        
        annuleren = gtk.Button(stock = gtk.STOCK_CANCEL)
        annuleren.connect('clicked', self.annuleren)

        bbox = gtkhbuttonbox()
        bbox.pack_start(annuleren)
        bbox.pack_start(ok)

        vbox = gtkvbox()
        vbox.pack_start(self.entry)
        vbox.pack_start(bbox)

        self.window.add(vbox)
        self.window.show_all()
        gtk.main()

    def ok(self, b):
        r, c = getactivecell()
        coord = '%c%i' % (chr(65 + c), r + 1)
        setcellstring(getactivesheet(), coord, self.entry.child.get_text())
        self.window.destroy()

    def annuleren(self, b):
        self.window.destroy()

