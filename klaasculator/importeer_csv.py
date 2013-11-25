import csvtools
from powertools import *


def importeer_csvfilelist(files, sheetname = 'Journaal'):
    """Importeer de csvbestanden in de lijst filelist."""
    for f in files:
        # dit moet een beetje vuil omdat mogelijk ootools is geladen ipv csvtools
        jr = Sheet_jr(None)
        jr.data = csvtools.getsheetbyname(f)[2:]
        
        boekstuk = Boekstuk(0, 0)
        
        for b in jr:
            if b.datum != boekstuk.datum or b.nummer != boekstuk.nummer:
                if len(boekstuk):
                    writeboekstuk(boekstuk, sheetname)
                boekstuk = Boekstuk(b.nummer, b.datum)
            boekstuk.append(b)
        if len(boekstuk):
            writeboekstuk(boekstuk, sheetname)

def importeer_csv():
    """Importeer een tcs-boekstuk.

    Dit laad de boekstukken zoals in het csv-bestand dat is opgegeven.
    """
    # Eerst csv-bestand of directory
    dialog = gtk.FileChooserDialog('Selecteer het tcs-bestand of directory',
                                   None,
                                   gtk.FILE_CHOOSER_ACTION_OPEN,
                                   (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
    
    
    dialog.set_default_response(gtk.RESPONSE_OK)
    
    filter = gtk.FileFilter()
    filter.set_name('csv-bestanden')
    filter.add_pattern('*.csv')
    dialog.add_filter(filter)
    
    filter = gtk.FileFilter()
    filter.set_name('Alle bestanden')
    filter.add_pattern('*')
    dialog.add_filter(filter)
    
    dialog.set_select_multiple(True)
    
    result = dialog.run()
    files = []
    if result == gtk.RESPONSE_OK:
        files = dialog.get_filenames()
    dialog.destroy()

    importeer_csvfilelist(files)
   
