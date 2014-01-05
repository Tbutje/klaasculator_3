'''
Created on 25 nov. 2013

@author: Timo
'''
import unittest
from tools import Fout
from euro import Euro
from boekregel import Boekregel


class TestEuro(unittest.TestCase):

    def testcenten(self):
        self.assertEqual(Euro(5), Euro(500, value_in_centen = True), "Centen failed")

    def testadd(self):
        euro = Euro(5)
        result = euro.floatt()
        self.assertEqual(result, (5.0, 0.0), "addition failed")

    def testexceptionadd(self):
#         self.assertRaises(Exception, self.number, "")
        # optellen
        with self.assertRaises(Exception) as e_cm:
            Euro(6) + 5
        exception = e_cm.exception
        self.assertEqual(exception.args,
                          ("Kan alleen maar een Euro() class optellen", ),
                          "Exception failed")
    def testexceptionsubstract(self):
        # aftrekken
        with self.assertRaises(Fout) as e_cm:
            Euro(6) - 5
        exception = e_cm.exception
        self.assertEqual(exception.args,
                          ("Kan alleen maar een Euro() class aftrekken", ),
                          "Exception failed")
    def testexceptionvivide(self):
        # delen
        with self.assertRaises(Fout) as e_cm:
            Euro(6) / Euro(1)
        exception = e_cm.exception
        self.assertEqual(exception.args,
                          ("moet delen met een float", ),
                          "Exception failed")

    def testexceptionmultiply(self):
        # vermenigvuldigen
        with self.assertRaises(Fout) as e_cm:
            Euro(6) * Euro(2)
        exception = e_cm.exception
        self.assertEqual(exception.args,
                          ("moet vermenigvuldigen met een float", ),
                          "Exception failed")

    def testusecase(self):
        value = Euro(5)
        value += Euro(1) # 6
        value -= Euro(2) # 4
        value = value * 2 # 8
        self.assertEqual(value.floatt(), (8.0, 0.0), "use case failed")
        value = value - Euro(10)
        self.assertEqual(value.floatt(), (0.0, 2.0), "use case failed")

class TestBoekregel(unittest.TestCase):

    def testinit(self):
        with self.assertRaises(Fout) as e_cm:
            Boekregel(waarde = 5)
        exception = e_cm.exception
        self.assertEqual(exception.args,
                          ("Waarde moet type Euro() zijn", ),
                          "Exception failed")


class TestDebCred(unittest.TestCase):
    pass

class testDebCredkort(unittest.TestCase):
    pass

class testDebCredKortLeden(unittest.TestCase):
    pass

class TestBoekstuk(unittest.TestCase):
    pass

class TestSheet(unittest.TestCase):
    pass

class TestTegenregel(unittest.TestCase):
    pass
