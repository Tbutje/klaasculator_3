'''
Created on 25 nov. 2013

@author: Timo
'''
import unittest
from klaasculator.euro import Euro


class TestEuro(unittest.TestCase):

    def testadd(self):
        euro = Euro(5)
        result = euro.floatt()
        self.assertEqual(result, (5.0, 0.0), "addition failed")

class TestBoekregel(unittest.TestCase):
    pass

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



# if __name__ == "__main__":
#     #import sys;sys.argv = ['', 'Test.testName']
#     unittest.main()