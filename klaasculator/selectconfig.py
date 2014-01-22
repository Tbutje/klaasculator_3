from os.path import dirname
import os

from powertools import *


def selectconfig(field = 'C10', titel = 'Selecteer het configuratiebestand'):
    """Selecteer het configuratiebestand.

    De field en titel argumenten zijn een trucje om voor selectrelaties dezelfde code te kunnen gebruiken.
    """

    dialog = gtk.FileChooserDialog(titel,
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

    try:
        path = getcellstring('Info', field)
        if (".csv" in path):
            dialog.set_current_folder(dirname(path))
    except:
        pass

    result = dialog.run()
    if result == gtk.RESPONSE_OK:
        npath = dialog.get_filename()
        npath =  os.path.abspath(npath)

        setcellstring('Info', field, npath)
        if field == 'C10':
            Config().configure()
        elif field == 'C11':
            Relaties().configure()
    dialog.destroy()

def selectrelaties():
    """Zie selectconfig()."""
    selectconfig('C11', 'Selecteer het relatiebestand')

if __name__ == "__main__":
    selectconfig()
    selectrelaties()

