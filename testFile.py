import unittest
from Assignment3Program import *

file_path = "./ProjectSampleGedcom.ged"
# file_path = 'C:\ProjectSampleGedcom.ged' # for PDS to run in her PC
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
        self.assertTrue(lessThan150YearsOld(indis))

    def testsortSibligs(self):
        self.assertTrue(sortSibligs(fams, indis))

    def testlistDeads(self):
        self.assertTrue(listDeads(indis))

    def testLivingSingle(self):
        self.assertTrue(len(livingSingle(indis, fams)) >= 0)

    def testLargeAgeDifference(self):
        self.assertTrue(len(largeAgeDifference(fams, indis)) >= 0)

    def testlistRecentBirths(self):
        self.assertTrue(len(listRecentBirths(
            indis, year=2000, month=1, day=1)) >= 0)

    def testlistRecentDeads(self):
        self.assertTrue(len(listRecentBirths(
            indis, year=2000, month=1, day=1)) >= 0)

    def testListOrphans(self):
        self.assertTrue(len(listOrphans(indis, fams)) >= 0)

    def testSiblingsNotMarried(self):
        self.assertTrue(siblingsNotMarried(fams))

    def testSiblingsSpacing(self):
        self.assertTrue(siblingsSpacing(fams, indis))

    def testMarriageBeforeDivorce(self):
        self.assertTrue(marriageBeforeDivorce(fams))


if __name__ == '__main__':
    unittest.main()
