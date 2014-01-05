DEBET, CREDIT = range(2) # enum
from tools import Fout

class Euro:
    """Deze class beschrijft valuta, i.t.t. floating-point getallen.

    Gebruik dit in plaats van een float als het om geld gaat. Daarnaast houdt deze class in self.dc bij of het debet of
    credit is. In de interne representatie wordt self.value als bedrag in centen en self.dc als type gebruikt.
    """

    def __init__(self, value = 0, dc = DEBET, value_in_centen = False):
        """Initialiseer de Euro met waarde value (float) en type dc.

        Als je value_in_centen = True meegeeft, wordt value geinterpeteerd als een bedrag in centen i.p.v. euros.
        """
        self.dc = dc
        if value_in_centen:
            self.value = int(value)
        else:
            self.value = int(round(value * 100))

        self.fixate()

    def fixate(self):
        """Corrigeer voor een negatieve waarde door het teken en dc om te slaan.

        Dit dient te worden aangeroepen na elke member-functie waarna de waarde mogelijk negatief is.
        """

        if self.value < 0:
            self.value = -self.value
            self.switchdc()

    def balanced(self, other):
        """Retourneert True als other dezelfde waarde heeft maar een omgekeerd tegen, False in andere gevallen."""
        if self.dc != other.dc:
            return self.value == other.value
        return False

    def switchdc(self):
        """Draait het type (DEBET of CREDIT) van deze Euro om."""
        self.dc = (self.dc + 1) % 2

    def counterpart(self):
        """Retourneert een Euro met dezelfde waarde maar omgedraait type."""
        return Euro(self.value, (self.dc + 1) % 2, True)

    def __copy__(self):
        """Geeft een kopie."""
        return Euro(self.value, self.dc, True)

    def true(self):
        """Truth-operator."""
        return self.value != 0

    def __iadd__(self, other):
        """Operator +=, other moet een Euro zijn."""
        try:
            if self.dc == other.dc:
                self.value += other.value
            else:
                self.value -= other.value
                self.fixate()
            return self
        except:
            raise Fout("Kan alleen maar een Euro() class optellen")

    def __isub__(self, other):
        """Operator -=, other moet een Euro zijn."""
        try:
            if self.dc == other.dc:
                self.value -= other.value
                self.fixate()
            else:
                self.value += other.value
            return self
        except:
            raise Fout("Kan alleen maar een Euro() class aftrekken")

    def __imul__(self, other):
        """Operator *= operator, other moet een float zijn."""
        try:
            self.value *= other
            self.value = int(round(self.value))
            self.fixate()
            return self
        except:
            raise Fout("moet vermenigvuldigen met een float")

    def __idiv__(self, other):
        """Operator /=, other moet een float zijn."""
        try:
            self.value /= other
            self.value = int(round(self.value))
            self.fixate()
            return self
        except:
            raise Fout("moet delen met een float")

    def __add__(self, other):
        """Operator +, other moet een Euro zijn."""
        e = self.__copy__()
        e += other
        return e

    def __sub__(self, other):
        """Operator -, other moet een Euro zijn."""
        e = self.__copy__()
        e -= other
        return e

    def __mul__(self, other):
        """Operator *, other moet een float zijn."""
        e = self.__copy__()
        e *= other
        return e

    def __div__(self, other):
        """Operator /, other moet een float zijn."""
        e = self.__copy__()
        e /= other
        return e

    def __cmp__(self, other):
        """Vergelijk twee euros.

        Let op dat dit alleen de value in acht neemt.
        """
        return self.value.__cmp__(other.value)

    def __lt__(self, other):
        """Operator <, neemt dc niet mee in bereking."""
        return self.value < other.value

    def __le__(self, other):
        """Operator <=, neemt dc nier mee in bereking."""
        return self.value <= other.value

    def __eq__(self, other):
        """Operator ==, neemt dc niet mee in bereking."""
        return self.value == other.value

    def __ne__(self, other):
        """Operator != operator, neemt dc nier mee in bereking."""
        return self.value != other.value

    def __gt__(self, other):
        """Operator > operator, neemt dc mee niet in bereking."""
        return self.value > other.value

    def __ge__(self, other):
        """Operator <, neemt dc niet mee in bereking."""
        return self.value >= other.value

    def __float__(self):
        """Floating point representatie."""
        return self.value / 100.0

    def floatt(self):
        """Als tuple.

        Geeft (3.14, 0.00) voor debet en (0.00, 3.14) voor credit. Handig.
        """
        if self.dc == DEBET:
            return float(self), 0.00
        else:
            return 0.00, float(self)

    def __str__(self):
        """String representatie."""
        if self.dc == CREDIT:
            return '0.00, %.2f' % float(self)
        return '%.2f, 0.00' % float(self)


