from gedcom.element.individual import IndividualElement
from gedcom.parser import Parser
from gedcom.element.element import Element

file_path = 'Marin_Tayler_Tree.ged'

accepted_tags = ["INDI", "NAME", "SEX", "BIRT", "DEAT", "FAMC", "FAMS",
                    "FAM", "MARR", "HUSB", "WIFE", "CHIL", "DIV", "DATE",
                     "HEAD", "TRLR", "NOTE"]

lines = []

gedcom_parser = Parser()
gedcom_parser.parse_file(file_path)
elements = gedcom_parser.get_element_list()

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

print(lines)
with open("Result.txt", 'w') as f:
    f.writelines(lines)
    
    
    
