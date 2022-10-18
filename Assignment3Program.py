import time
from gedcom.element.individual import IndividualElement
from gedcom.parser import Parser
from gedcom.element.element import Element
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def getDate(var):
    return datetime.strptime(var, '%d %b %Y').date()


errors = []

def compareDates(laterDate, earlierDate, errorMsg):
    if(laterDate < earlierDate):
        errors.append(errorMsg)
        return False
    return True

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
    errOut = True
    for fam in fams:
        marriedDate = getDate(fam[1])
        husbID = fam[3]
        wifeID = fam[5]
        for indi in indis:
            ID = indi[0]
            if (ID == husbID):
                if (not indi[5]):
                    deathdate = getDate(indi[6])
                    errorMsg = 'Error: Husband named ' + indi[1] + ' of family ' + fam[0] + ' has a death date before marriage || Death Date: ' + indi[6] + ' | Marriage Date: ' + fam[1] + '\n'
                    errOut = compareDates(deathdate, marriedDate, errorMsg)
            if (ID == wifeID):
                if (not indi[5]):
                    deathdate = getDate(indi[6])
                    errorMsg = "Error: Wife named " + indi[1] + " of family " + fam[0] + " has a death date before marriage || Death Date: " + indi[6] + " | Marriage Date: " + fam[1] + "\n"
                    errOut = compareDates(deathdate, marriedDate, errorMsg)
    return errOut


def divorceBeforeDeath(fams, indis):
    errOut = True
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
                            errors.append(
                                "Error: Husband named " + indi[1] + " of family " + fam[0] + " has a death date before divorce || ")
                            errors.append("Death Date: " +
                                  indi[6] + " | Divorce Date: " + fam[2] + "\n")
                            errOut = False
                if (ID == wifeID):
                    if (not indi[5]):
                        deathdate = datetime.strptime(
                            indi[6], '%d %b %Y').date()
                        if (deathdate < divorcedDate):
                            errors.append(
                                "Error: Wife named " + indi[1] + " of family " + fam[0] + " has a death date before divorce || ")
                            errors.append("Death Date: " +
                                  indi[6] + " | Divorce Date: " + fam[2] + "\n")
                            errOut = False
    return errOut


def noBigamy(fams, indis):
    """If two families share one spouse, they must have been married and divorced"""
    errOut = True
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
                            errors.append(
                                "Error: Individual " + indi[1] + " is married to multiple people at the same time\n")
                            errOut = False
                        elif (famsOfIndi[i][2] > famsOfIndi[j][1]):
                            errors.append(
                                "Error: Individual " + indi[1] + " is married to multiple people at the same time\n")
                            errOut = False
    return errOut


def unique_ID(indis, fams):
    errOut = True
    for i in range(len(indis)):
        indi = indis[i]
        for j in range(i+1, len(indis)):
            nextIndi = indis[j]
            if (indi[0] == nextIndi[0]):
                errors.append(indi[1] + " has the same individual ID as " + nextIndi[1] + "\n")
                errorOut = False
    for i in range(len(fams)):
        fam = fams[i]
        for j in range(i+1, len(fams)):
            nextFam = fams[j]
            if(fam[0] == nextFam[0]):
                errors.append("Family with husband ID " + fam[3] + " and wife ID " + fam[5] + " has same ID as family with husband ID " + nextFam[3] + "and wife ID " + nextFam[5] + "\n")
                errOut = False
    return errOut

# birth before date


def birthBeforeDeath(indis):
    errOut = True
    for indi in indis:
        if (indi[3] != "N/A"):
            birthdate = datetime.strptime(indi[3], '%d %b %Y').date()
        if (indi[6] != "N/A"):
            deathdate = datetime.strptime(indi[6], '%d %b %Y').date()
            if (deathdate < birthdate):
                errors.append(
                    "Error: " + indi[1] + " has death date before being birth date \n")
                errOut = False
    return errOut

def datesBeforeCurrent(fams, indis):
    currentDate = datetime.now().date()
    for fam in fams:
        marDate = datetime.strptime(fam[1], '%d %b %Y').date()
        if(marDate > currentDate):
            print("Family with ID " + fam[0] + " has a marriage date after current date")
            return False
        if(fam[2] != "N/A"):
            divDate = datetime.strptime(fam[2], '%d %b %Y').date()
            if(divDate > currentDate):
                print("Family with ID " + fam[0] + " has a divorce date after current date")
                return False
    for indi in indis:
        birthDate = datetime.strptime(indi[3], '%d %b %Y').date()
        if(birthDate > currentDate):
            print("Individual with ID " + indi[0] + " has a birth date after current date")
            return False
        if(indi[6]!= "N/A"):
            deathDate = datetime.strptime(indi[6], '%d %b %Y').date()
            if(deathDate > currentDate):
                print("Individual with ID " + indi[0] + " has a death date after current date")
                return False
    print("All dates occur before current time")
    return True

def birthBeforeDeathofParents(fams, indis):
    for fam in fams:
        for child in fam[7]:
            for indi in indis:
                if(indi[0] == child):
                    childBDate = datetime.strptime(indi[3], '%d %b %Y').date()
                    for parents in indis:
                        if(parents[0] == fam[3]):
                            if(parents[6] != "N/A"):
                                fatherDDate = datetime.strptime(parents[6], '%d %b %Y').date()
                                adjustedDate = fatherDDate + relativedelta(months = 9)
                                if(adjustedDate < childBDate):
                                    print("Father died more than 9 months before child was born")
                                    return False
                        if(parents[0] == fam[5]):
                            if(parents[6] != "N/A"):
                                motherDDate = datetime.strptime(parents[6], '%d %b %Y').date()
                                if(motherDDate < childBDate):
                                    print("Mother died beofre child was born")
                                    return False            
    print("All parents death make sense in respect to childs birth")
    return True

# US10	Marriage after 14


def marriageAfter14(fams, indis):
    errOut = True
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
                    errors.append("The individual" + indi[0] + "was married before 14\n")
                    errOut = False
    return errOut


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
    marrBefore14 = marriageAfter14(fams, indis)
    bBD = birthBeforeDeath(indis)
    birthBeforeParentsDeath = birthBeforeDeathofParents(fams, indis)
    beforeCurrent = datesBeforeCurrent(fams, indis)

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

        f.write("\n")

        if(mbD):
            f.write("All Marriage dates are before Death dates of spouses\n")
        if(uniqueIDs):
            f.write("All IDs are unique\n")
        if(dbD):
            f.write("All Divorce dates are before Death dates of spouses\n")
        if(bigamy):
            f.write("No bigamy\n")
        if(marrBefore14):
            f.write("No individuals were married before 14\n")
        if(bBD):
            f.write("All birth dates are before death dates\n")
        if(len(errors)>0):
            f.writelines(errors)


if __name__ == "__main__":
    main()
