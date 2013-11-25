from StringIO import StringIO
from code import InteractiveConsole
import sys
from textwrap import wrap, fill

import gtk
import pango

from gtktools import *


class Console:
    """Een python-console.

    Dit ding geeft een interactive console voor de nerds. Dat is dik!
    Voor het gemak wordt 'from klaasculator import *' standaard uitgevoerd.
    """
    def __init__(self):
        self.out = StringIO()
        sys.stdout = self.out
        sys.stderr = self.out
        
        self.console = InteractiveConsole()
        self.console.push('from klaasculator import *')
        
        self.window = gtkwindow('Klaasculator Python Console')

        self.output = gtk.TextView()
        self.output.modify_font(pango.FontDescription('Monospace'))
        self.output.set_editable(False)
        self.output.set_wrap_mode(gtk.WRAP_CHAR)
     
        self.buffer = self.output.get_buffer()

        self.entry = gtk.Entry()
        self.entry.set_width_chars(80)
        self.entry.modify_font(pango.FontDescription('Monospace'))
        self.entry.connect('activate', self.enter, self.entry)
        self.entry.connect('key-press-event', self.tab)

        self.completion = gtk.EntryCompletion()
        self.cstore = gtk.ListStore(str)

        self.completion.set_model(self.cstore)
        self.completion.set_text_column(0)
        self.entry.set_completion(self.completion)

        self.prompt = gtk.Label()
        self.prompt.set_width_chars(4)
        self.prompt.modify_font(pango.FontDescription('Monospace'))
        self.prompt.set_text('>>>')
     
        self.hbox = gtk.HBox()
        self.hbox.pack_start(self.prompt, expand = False)
        self.hbox.pack_start(self.entry, expand = True)

        self.scroll = gtk.ScrolledWindow(None, gtk.Adjustment(value = 0, lower = 0, upper = 1000))
        self.scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.scroll.add_with_viewport(self.output)
        self.scroll.get_vscrollbar().set_range(0, 1)
       
        self.box = gtkvbox()
        self.box.pack_start(self.scroll, expand = True)
        self.box.pack_start(self.hbox, expand = False)
        self.window.add(self.box)
        self.scroll.set_size_request(100, 300)
        self.entry.grab_focus()
        self.window.show_all()

        self.history = []
        self.history_iter = 0

        self.window.show_all()
        gtk.main()

     

    def __del__(self):
        self.out.close()
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    def tab(self, widget, event):
        """Kleine hek om ook tabs etc in de entry mogelijk te maken."""
        if event.keyval == 65289: # dit getal is kennelijk een tab
            pos = self.entry.get_position()
            self.entry.insert_text('    ', pos)
            self.entry.set_position(pos + 4)
            return True
        elif event.keyval == 65362: # pijltje omhoog
            self.history_iter -= 1
            if self.history_iter >= 0 and self.history_iter < len(self.history):
                self.entry.set_text(self.history[self.history_iter])
            return True
        elif event.keyval == 65364: # pijltje omlaag
            self.history_iter += 1
            if self.history_iter < len(self.history) and self.history_iter >= 0:
                self.entry.set_text(self.history[self.history_iter])
            return True
        return False
            
    def enter(self, widget, entry):
        command = entry.get_text()

        self.history.append(command)
        self.history_iter = len(self.history)

        if command not in [r[0] for r in self.cstore]:
            self.cstore.append([command])
        

        # We willen hier exit() en quit() afvangen, want die maken naast je console ook je openoffice stuk.
        if command == 'exit()' or command == 'quit()': 
            self.window.destroy()
            return

        print self.prompt.get_text() + ' ' + command
        
        if self.console.push(command):
            self.prompt.set_text('...')
        else:
            self.prompt.set_text('>>>')
        entry.set_text('')

        self.buffer.set_text(self.out.getvalue())
        self.scroll.get_vadjustment().set_value(99999999) # belachelijk hoog getal
                

def console():
    """Roept de class Console aan."""
    Console()
    
