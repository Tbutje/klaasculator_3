from boekregel import *

class Boekstuk:
    """Deze class beschrijft een boekstuk.

    Een boekstuk is feitelijk een list van Boekregels. Daarbij houdt het het boeknummer en datum bij in self.nummer en
    self.datum. Het zorgt er ook voor dat alle boekregels het goede nummer en datum krijgen. Om die reden is het niet de
    bedoeling dat je zelf in self.regels gaat kloten.
    """

    def __init__(self, nummer = 0, datum = 0):
        """Initialiseer een boekstuk."""
        self.nummer = nummer
        self.datum = datum
        self.regels = []

    def __len__(self):
        """Voor len()-functie."""
        return len(self.regels)

    def __getitem__(self, i):
        """Operator []."""
        return self.regels[i]

    def __setitem__(self, i, value):
        """Operator[]."""
        value.nummer = self.nummer
        value.datum = self.datum
        self.regels[i] = value

    def __delitem__(self, i):
        """Voor del()-functie."""
        del self.regels[i]

    def __iter__(self):
        """Geeft een iterator."""
        return iter(self.regels)

    def append(self, boekregel):
        """Voeg een boekregel toe."""
        boekregel.nummer = self.nummer
        boekregel.datum = self.datum

        self.regels.append(boekregel)

    def extend(self, boekregels):
        """Voeg een list van boekregels toe."""

        for b in boekregels:
            b.nummer = self.nummer
            b.datum = self.datum

        self.regels.extend(boekregels)

    def setnummer(self, nummer):
        """Verander het nummer."""
        self.nummer = nummer
        for r in self.regels:
            r.nummer = nummer

    def setdatum(self, datum):
        """Verander de datum."""
        self.datum = datum
        for r in self.regels:
            r.datum = datum

    def tegenregel(self):
        """Maak een tegenregel.

        Deze maakt een tegenregel van de laatste boekregel.
        """
        o = self.regels[-1]
        b = Boekregel(self.nummer,
                      self.datum,
                      o.tegen,
                      '',
                      o.omschrijving,
                      o.tegen2,
                      o.rekening,
                      o.waarde.counterpart(),
                      o.omschrijving2)
        self.regels.append(b)

    def balanceer(self):
        """Balanceer het boekstuk.

        Dit doet bijna hetzelfde als tegenregel, met het verschil dat het het boekstuk in balans brengt i.p.v. dom een
        tegenregel te maken.
        """
        w = self.balanswaarde()
        if w.true():
            o = self.regels[-1]
            b = Boekregel(self.nummer,
                          self.datum,
                          o.tegen,
                          '',
                          o.omschrijving,
                          o.tegen2,
                          o.rekening,
                          self.balanswaarde(),
                          o.omschrijving2)
            self.regels.append(b)

    def balanswaarde(self):
        """Geeft dde balanserende Euro terug.

        Dit houdt in dat het een Euro terug geeft die het boekstuk in balans zou brengen.
        """
        w = Euro()
        for r in self.regels:
            w += r.waarde
        w.switchdc()
        return w

    def inbalans(self):
        """Geeft True als het boekstuk in balans is."""
        return not self.balanswaarde().true()

    def __str__(self):
        """String-representatie."""
        s = ''
        for r in self.regels:
            s += str(r) + '\n'
        return s


