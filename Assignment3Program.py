from gedcom.element.individual import IndividualElement
from gedcom.parser import Parser
from gedcom.element.element import Element
from datetime import datetime
from dateutil.relativedelta import relativedelta


def getElems(elements):
    accepted_tags = ["INDI", "NAME", "SEX", "BIRT", "DEAT", "FAMC", "FAMS",
                     "FAM", "MARR", "HUSB", "WIFE", "CHIL", "DIV", "DATE",
                     "HEAD", "TRLR", "NOTE"]
    lines = []
    for elem in elements:
        lines.append(elem.to_gedcom_string())
        level = elem.get_level()
        tag = elem.get_tag()
        accepted = "N"

        if tag in accepted_tags:
            accepted = "Y"

        value = elem.get_value()
        string = str(level) + "|" + tag + "|" + accepted + "|" + value + "\n"
        lines.append(string)


def getIndis(elements):
    # Returns an array of arrays with information for all individuals in a gedcom file.
    # Contents of Inner Array: [Individual ID (String), Name (String), Gender (String), Birth Date (String), Age (Int), Alive (Boolean), Death Date (String)]
    indis = []
    for elem in elements:
        tag = elem.get_tag()
        if (tag == "INDI"):
            # GET ALL INDIVIDUALS AND IDS
            ptr = elem.get_pointer()
            infoArr = []
            nameTup = elem.get_name()
            name = nameTup[0] + " " + nameTup[1]
            gender = elem.get_gender()
            birthdate = elem.get_birth_data()
            bornYear = elem.get_birth_year()
            age = 2022 - bornYear
            isChild = elem.is_child()
            isDeceased = elem.is_deceased()

            infoArr.append(ptr)
            infoArr.append(name)
            infoArr.append(gender)
            infoArr.append(birthdate[0])
            infoArr.append(age)
            infoArr.append(not isDeceased)
            if (isDeceased):
                deathDate = elem.get_death_data()
                infoArr.append(deathDate[0])
            else:
                infoArr.append("N/A")
            indis.append(infoArr)
    # SORT INDIVIDUALS

    return indis


def getFams(elements, indis):
    # Returns an array of arrays with information for all families in a GEDCOM file
    # Contents of inner array: [Family ID (String), Married Date (String), Divorce Date (String), Husband ID (String), Husband Name (String), Wife ID (String), Wife Name (String), Array of Children IDs ([Strings])]
    fams = []
    for elem in elements:
        tag = elem.get_tag()
        if (tag == "FAM"):
            famInfo = []
            ptr = elem.get_pointer()
            famInfo.append(ptr)
            family = elem.get_child_elements()
            children = []
            dateMarr = "N/A"
            dateDiv = "N/A"
            famInfo.append(dateMarr)
            famInfo.append(dateDiv)
            for famElem in family:
                fEPtr = famElem.get_value()
                fTag = famElem.get_tag()
                if (fTag == "MARR"):
                    dateMarrElem = famElem.get_child_elements()
                    dateMarr = dateMarrElem[0].get_value()
                    famInfo[1] = dateMarr
                if (fTag == "DIV"):
                    dateDivElem = famElem.get_child_elements()
                    dateDiv = dateDivElem[0].get_value()
                    famInfo[2] = dateDiv
                if (fTag == "HUSB"):
                    for indi in indis:
                        if (indi[0] == fEPtr):
                            famInfo.append(indi[0])
                            famInfo.append(indi[1])
                if (fTag == "WIFE"):
                    for indi in indis:
                        if (indi[0] == fEPtr):
                            famInfo.append(indi[0])
                            famInfo.append(indi[1])
                if (fTag == "CHIL"):
                    children.append(fEPtr)
            famInfo.append(children)
            fams.append(famInfo)
    # SORT FAMILIES

    return fams


def marriageBeforeDeath(fams, indis):
    for fam in fams:
        marriedDate = datetime.strptime(fam[1], '%d %b %Y').date()
        husbID = fam[3]
        wifeID = fam[5]
        for indi in indis:
            ID = indi[0]
            if (ID == husbID):
                if (not indi[5]):
                    deathdate = datetime.strptime(indi[6], '%d %b %Y').date()
                    if (deathdate < marriedDate):
                        print('Error: Husband named ' +
                              indi[1] + ' of family ' + fam[0] + ' has a death date before marriage \n')
                        print("Death Date: " +
                              indi[6] + " | Marriage Date: " + fam[1])
                        return False
            if (ID == wifeID):
                if (not indi[5]):
                    deathdate = datetime.strptime(indi[6], '%d %b %Y').date()
                    if (deathdate < marriedDate):
                        print("Error: Wife named " + indi[1] + " of family " +
                              fam[0] + " has a death date before marriage \n")
                        print("Death Date: " +
                              indi[6] + " | Marriage Date: " + fam[1])
                        return False
    print("All Marriage dates are before Death dates of spouses")
    return True


def parentsNotTooOld(fams, indis):
    """Mother should be less than 60 years older than her children and father should be less than 80 years older than his children"""
    for fam in fams:
        children = fam[7]
        for child in children:
            for indi in indis:
                if (indi[0] == child):
                    childAge = indi[4]
                    motherID = fam[5]
                    fatherID = fam[3]
                    for indi in indis:
                        if (indi[0] == motherID):
                            motherAge = indi[4]
                            ageDiff = childAge - motherAge
                            if (ageDiff > 60):
                                print("Error: Mother named " + indi[1] + " of family " +
                                      fam[0] + " is more than 60 years older than her child \n")
                                print("Mother's Age: " + str(motherAge) +
                                      " | Child's Age: " + str(childAge))
                                return False
                        if (indi[0] == fatherID):
                            fatherAge = indi[4]
                            ageDiff = childAge - fatherAge
                            if (ageDiff > 80):
                                print("Error: Father named " + indi[1] + " of family " +
                                      fam[0] + " is more than 80 years older than his child \n")
                                print("Father's Age: " + str(fatherAge) +
                                      " | Child's Age: " + str(childAge))
                                return False
    print("All parents are not too old")
    return True


def divorceBeforeDeath(fams, indis):
    for fam in fams:
        if (fam[2] != "N/A"):
            divorcedDate = datetime.strptime(fam[2], '%d %b %Y').date()
            husbID = fam[3]
            wifeID = fam[5]
            for indi in indis:
                ID = indi[0]
                if (ID == husbID):
                    if (not indi[5]):
                        deathdate = datetime.strptime(
                            indi[6], '%d %b %Y').date()
                        if (deathdate < divorcedDate):
                            print(
                                "Error: Husband named " + indi[1] + " of family " + fam[0] + " has a death date before divorce \n")
                            print("Death Date: " +
                                  indi[6] + " | Divorce Date: " + fam[2])
                            return False
                if (ID == wifeID):
                    if (not indi[5]):
                        deathdate = datetime.strptime(
                            indi[6], '%d %b %Y').date()
                        if (deathdate < divorcedDate):
                            print(
                                "Error: Wife named " + indi[1] + " of family " + fam[0] + " has a death date before divorce \n")
                            print("Death Date: " +
                                  indi[6] + " | Divorce Date: " + fam[2])
                            return False
    print("All Divorce dates are before Death dates of spouses")
    return True


def noBigamy(fams, indis):
    """If two families share one spouse, they must have been married and divorced"""
    for indi in indis:
        famsOfIndi = []
        for fam in fams:
            if (indi[0] == fam[3] or indi[0] == fam[5]):
                famsOfIndi.append(fam)
        if (len(famsOfIndi) > 1):
            for i in range(len(famsOfIndi)):
                for j in range(i+1, len(famsOfIndi)):
                    if (famsOfIndi[i][1] < famsOfIndi[j][1]):
                        if (famsOfIndi[i][2] == "N/A" or famsOfIndi[j][2] == "N/A"):
                            print(
                                "Error: Individual " + indi[1] + " is married to multiple people at the same time")
                            return False
                        elif (famsOfIndi[i][2] > famsOfIndi[j][1]):
                            print(
                                "Error: Individual " + indi[1] + " is married to multiple people at the same time")
                            return False
    print("No Bigamy")
    return True


def unique_ID(indis, fams):
    for i in range(len(indis)):
        indi = indis[i]
        for j in range(i+1, len(indis)):
            nextIndi = indis[j]
            if (indi[0] == nextIndi[0]):
                print(indi[1] + " has the same individual ID as " + nextIndi[1])
                return False
    for i in range(len(fams)):
        fam = fams[i]
        for j in range(i+1, len(fams)):
            nextFam = fams[j]
            if (fam[0] == nextFam[0]):
                return False
    print("All IDs are unique")
    return True

# birth before date


def birthBeforeDeath(indis):
    for indi in indis:
        if (indi[3] != "N/A"):
            birthdate = datetime.strptime(indi[3], '%d %b %Y').date()
        if (indi[6] != "N/A"):
            deathdate = datetime.strptime(indi[6], '%d %b %Y').date()
            if (deathdate < birthdate):
                print(
                    "Error:" + indi[1] + "was death before being born \n")
                return False
    print("All birth dates are before death dates")
    return True

# US10	Marriage after 14


def marriageAfter14(fams, indis):

    for indi in indis:
        marriages = []
        age = []
        for fam in fams:
            if (indi[0] == fam[3] or indi[0] == fam[5]):
                married = datetime.strptime(fam[1], '%d %b %Y')
                # print(married)
                bornDate = datetime.strptime(indi[3], '%d %b %Y')
                # print(bornDate)
                #print("individual " + indi[1] + " was married on " + fam[1])
                #difference = (married - bornDate).days
                difference = relativedelta(married, bornDate)
                differenceinYears = difference.years
                # print(differenceinYears)
                if (differenceinYears < 14):
                    print("The individual" + indi[0] + "was married before 14")
    print("No individuals were married before 14")
    return True


def main():
    file_path = 'ProjectSampleGedcom.ged'
    # file_path = 'C:\ProjectSampleGedcom.ged' # for PDS to run in her PC

    lines = []

    gedcom_parser = Parser()
    gedcom_parser.parse_file(file_path)
    elements = gedcom_parser.get_element_list()
    indis = getIndis(elements)
    fams = getFams(elements, indis)
    mbD = marriageBeforeDeath(fams, indis)
    uniqueIDs = unique_ID(indis, fams)
    dbD = divorceBeforeDeath(fams, indis)
    bigamy = noBigamy(fams, indis)
    parents_not_too_old = parentsNotTooOld(fams, indis)

    indiStrings = []

    for indi in indis:
        string = "ID: " + indi[0] + " | Name: " + indi[1] + " | Gender: " + indi[2] + " | Birthdate: " + \
            indi[3] + " | Age: " + str(indi[4]) + " | Alive: " + \
            str(indi[5]) + " | Death Date: " + indi[6] + "\n"
        indiStrings.append(string)

    famStrings = []

    for fam in fams:
        listStr = "[ "
        children = fam[7]
        for i in range(len(children)):
            listStr = listStr + children[i]
            if (i != len(children)-1):
                listStr = listStr + ", "
        listStr = listStr + " ]"
        string = "ID: " + fam[0] + " | Married: " + fam[1] + " | Divorced: " + fam[2] + " | Husband ID: " + fam[3] + \
            " | Husband Name: " + fam[4] + " | Wife ID: " + fam[5] + \
            " | Wife Name: " + fam[6] + " | Children: " + listStr + "\n"
        famStrings.append(string)

    with open("Result.txt", 'w') as f:
        f.write("Individuals: \n")
        f.write("\n")
        f.writelines(indiStrings)
        f.write("\n")
        f.write("Families: \n")
        f.write("\n")
        f.writelines(famStrings)


if __name__ == "__main__":
    main()
