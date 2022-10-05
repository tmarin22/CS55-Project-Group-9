import unittest
from Assignment3Program import *

file_path = "./ProjectSampleGedcom.ged"
gedcom_parser = Parser()
gedcom_parser.parse_file(file_path)
elements = gedcom_parser.get_element_list()
indis = getIndis(elements)
fams = getFams(elements, indis)


class TestGedcom(unittest.TestCase):
    def testNoBigamy(self):
        self.assertTrue(noBigamy(fams, indis))

    def testMarriageBeforeDeath(self):
        self.assertTrue(marriageBeforeDeath(fams, indis))

    def testDivorceBeforeDeath(self):
        self.assertTrue(divorceBeforeDeath(fams, indis))

    def testNoBigamy(self):
        self.assertTrue(noBigamy(fams, indis))

    def testUniqueIDs(self):
        self.assertTrue(unique_ID(indis, fams))

    def testBirthBeforeDeath(self):
        self.assertTrue(birthBeforeDeath(indis))

    def testMarriageAfter14(self):
        self.assertTrue(marriageAfter14(fams, indis))


if __name__ == '__main__':
    unittest.main()
