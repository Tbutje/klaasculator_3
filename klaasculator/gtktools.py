"""Handige functies die verband houden met gtk (de grafische interface dingen.)"""

import gtk

from datetime import date

def gtkdelete(widget, event, data = None):
    return False

def gtkdestroy(widget, data = None):
    gtk.main_quit()

def gtkwindow(title = ''):
    """Retourneert een gtk.Window.

    Het idee is dat als je dat via deze functie doet i.p.v. gtk.Window(), dat dan de layout simpel en uniform is.
    """
    w = gtk.Window(gtk.WINDOW_TOPLEVEL)
    w.set_position(gtk.WIN_POS_CENTER)
    w.set_border_width(10)
    w.set_title(title)
    w.connect('delete_event', gtkdelete)
    w.connect('destroy', gtkdestroy)

    return w

def boxspacing(b):
    """Huplmethode voor functies hieronder (gtkhbox etc.)."""
    b.set_spacing(5)

def gtkhbox():
    """Zie gtkwindow(), maar nu voor gtk.HBox()."""
    b = gtk.HBox()
    boxspacing(b)
    return b

def gtkvbox():
    """Zie gtkwindow(), maar nu voor gtk.VBox()."""
    b = gtk.VBox()
    boxspacing(b)
    return b

def gtkhbuttonbox():
    """Zie gtkwindow(), maar nu voor gtk.HBox()."""
    b = gtk.HButtonBox()
    boxspacing(b)
    return b

def gtkvbuttonbox():
    """Zie gtkwindow(), maar nu voor gtk.VBox()."""
    b = gtk.VButtonBox()
    boxspacing(b)
    return b

def gtktable(r, c):
    """Zie gtkwindow(), maar nu voor gtk.Table()."""
    t = gtk.Table(r, c)
    t.set_row_spacings(5)
    t.set_col_spacings(5)
    return t

INT, FLOAT, STRING, DATUM = range(4) # enum voor makegtkentry

def dottocomma(widget, event):
    """Kleine hek voor makegtkentry met FLOAT.

    De reden hiervoor is dat bij Nederlandse instellingen de komma als decimaalseperator wordt gebruikt, terwijl je ook de
    punt wilt gebruiken (die zit namelijk wel op je numpad).
    """
    v = event.keyval
    if v == 44 or v == 46 or event.keyval == 65454:
        pos = widget.get_position()
        s = widget.get_text()
        if s == '0.00' or s == '0,00':
            widget.set_text('0')
            pos = 1            
        widget.insert_text(',', pos)
        widget.insert_text('.', pos)
        widget.set_position(pos + 1)
        return True
    return False

def gtkentry(soort, lower = -999999999, upper = 999999999):
    """Hulpfunctie voor makegtkentry.

    Dit is in een aparte functie gezet omdat je het in sommige gevallen ook afzonderlijk van een table wilt hebben.
    """
    if soort == INT:
        spin = gtk.SpinButton()
        spin.set_numeric(True)
        spin.set_range(lower, upper)
        spin.set_increments(1, 10)
        return spin
    elif soort == FLOAT:
        spin = gtk.SpinButton(None, 0.0, 2)
        spin.set_numeric(True)
        spin.set_range(lower, upper)
        spin.set_increments(0.01, 1)
        spin.connect('key-press-event', dottocomma)
        return spin
    elif soort == STRING:
        entry = gtk.Entry()
        return entry
    elif soort == DATUM:
        dag = gtk.SpinButton(gtk.Adjustment(1, 1, 31, 1), 0, 0)
        dag.set_wrap(True)
        maand = gtk.SpinButton(gtk.Adjustment(1, 1, 12, 1), 0, 0)
        maand.set_wrap(True)
        y = date.today().year
        jaar = gtk.SpinButton(gtk.Adjustment(y, y - 100, y + 100, 1), 0, 0)
        jaar.set_wrap(True)
        return dag, maand, jaar
    return None

def makegtkentry(table, row, label, soort):
    """Dit is een hulpfunctie voor entrys.

    Het is de bedoeling dit te gebruiken als je data van de gebruiker wilt hebben, zoals een bedrag of een datum.
    table is de gtk.Table waar het in komt, dit moet 2 kolommen hebben en tenminste row rijen.
    row is de rij waar het in komt.
    label is hoe we de variabele noemen (zoals 'Omzet groep 1').
    soort is het soort data, dit moet INT, FLOAT, STRING, of DATUM zijn.
    Het retourneert de widget die in de table is geplaatst en waar je daarna data uit kunt lezen. In het geval van DATUM
    is dit een tuple van drie widgets, te weten dag, maand en jaar.
    """

    if row >= table.get_property('n-rows'):
        table.resize(row + 1, table.get_property('n-columns'))

    gtklabel = gtk.Label()
    gtklabel.set_text(label)
    gtklabel.set_alignment(1, 0.5)
    table.attach(gtklabel, 0, 1, row, row + 1)

    entry = gtkentry(soort)

    if soort == DATUM:
        box = gtk.HBox()
        box.pack_start(entry[0])
        box.pack_start(entry[1])
        box.pack_start(entry[2])
        table.attach(box, 1, 2, row, row + 1)
    else:
        table.attach(entry, 1, 2, row, row + 1)

    return entry
