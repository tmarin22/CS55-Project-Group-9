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

    def testUniqueIDs(self):
        self.assertTrue(unique_ID(indis, fams))

    def testBirthBeforeDeath(self):
        self.assertTrue(birthBeforeDeath(indis))

    def testMarriageAfter14(self):
        self.assertTrue(marriageAfter14(fams, indis))

    def testParentsNotTooOld(self):
        self.assertTrue(parentsNotTooOld(fams, indis))

    def testBirthBeforeDeathOfParents(self):
        self.assertTrue(birthBeforeDeathofParents(fams, indis))

    def testDatesBeforeCurrent(self):
        self.assertTrue(datesBeforeCurrent(fams, indis))

    def testHasFatherLastname(self):
        self.assertTrue(hasFatherLastname(fams, indis))

    def testCheckSiblingNumber(self):
        self.assertTrue(checkSiblingNumber(fams))

    def testNoIllegitimateDateFormats(self):
        self.assertTrue(noIllegitimateDateFormats(indis, fams))

    def testBirthBeforeMarriage(self):
        self.assertTrue(birthBeforeMarriage(fams, indis))

    def testLessThan150YearsOld(self):
        self.assertTrue(lessThan150YearsOld(fams, indis))
        
    def testsortSibligs(self):
        self.assertTrue(sortSibligs(fams, indis))

    def testlistDeads(self):
        self.assertTrue(listDeads(indis))


if __name__ == '__main__':
    unittest.main()
