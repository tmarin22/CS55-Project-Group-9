from gedcom.element.individual import IndividualElement
from gedcom.parser import Parser
from gedcom.element.element import Element

def getElems(elements):
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
    indis = []
    for elem in elements:
        tag = elem.get_tag()
        if (tag == "INDI"):
            ## GET ALL INDIVIDUALS AND IDS
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
            if(isDeceased):
                deathDate = elem.get_death_data()
                infoArr.append(deathDate[0])
            else:
                infoArr.append("N/A")
            indis.append(infoArr)
    ##SORT INDIVIDUALS

  
    
    return indis

def getFams(elements, indis):
    fams = []
    for elem in elements:
        tag = elem.get_tag()
        if(tag == "FAM"):
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
                if(fTag == "MARR"):
                    dateMarrElem = famElem.get_child_elements()
                    dateMarr = dateMarrElem[0].get_value()
                    famInfo[1] = dateMarr
                if(fTag == "DIV"):
                    dateDivElem = famElem.get_child_elements()
                    dateDiv = dateDivElem[0].get_value()
                    famInfo[2] = dateDiv
                if(fTag == "HUSB"):
                    for indi in indis:
                        if(indi[0] == fEPtr):
                            famInfo.append(indi[0])
                            famInfo.append(indi[1])
                if(fTag == "WIFE"):
                   for indi in indis:
                        if(indi[0] == fEPtr):
                            famInfo.append(indi[0])
                            famInfo.append(indi[1])
                if(fTag == "CHIL"):
                    children.append(fEPtr)
            famInfo.append(children)
            fams.append(famInfo)
    ##SORT FAMILIES

            
    return fams
            
def main():
    file_path = 'ProjectSampleGedcom.ged'

    accepted_tags = ["INDI", "NAME", "SEX", "BIRT", "DEAT", "FAMC", "FAMS",
                        "FAM", "MARR", "HUSB", "WIFE", "CHIL", "DIV", "DATE",
                         "HEAD", "TRLR", "NOTE"]


    lines = []

    gedcom_parser = Parser()
    gedcom_parser.parse_file(file_path)
    elements = gedcom_parser.get_element_list()
    indis = getIndis(elements)
    fams = getFams(elements, indis)

    indiStrings = []

    for indi in indis:
        string = "ID: " + indi[0] + " | Name: " + indi[1] + " | Gender: " + indi[2] + " | Birthdate: " + indi[3] + " | Age: " + str(indi[4]) + " | Alive: " + str(indi[5]) + " | Death Date: " + indi[6] + "\n"
        indiStrings.append(string)

    famStrings = []

    for fam in fams:
        listStr = "[ "
        children = fam[7]
        for i in range(len(children)):
            listStr = listStr + children[i]
            if(i != len(children)-1):
               listStr = listStr + ", "
        listStr = listStr + " ]"
        string = "ID: " + fam[0] + " | Married: " + fam[1] + " | Divorced: " + fam[2] + " | Husband ID: " + fam[3] + " | Husband Name: " + fam[4] + " | Wife ID: " + fam[5] + " | Wife Name: " + fam[6] + " | Children: " + listStr + "\n"
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





    
    
    
