# -*- coding: utf-8 -*-

#Goal: From the converted text separate out the objects

import pdftotext
import Categorizer


class Proposal:
    def __init__(self):
        self.action = "";
        self.object = "";
        self.description = "";
        self.category = "";

class ProposalMachine:
    ## The Proposal Machine Works as follows:
    #   stage 0 : Search for the first Word of a line to be the ACTION. Add the action to current proposal
    #   add the rest of the line to object of current Proposal
    #   stage 1: Next line, Search for either an action word, then all caps. If an action word, Create secondary proposal,
    # if all caps, add line to current proposals object. if neither, move to stage 3
    #stage 2 : if the first word in the description is a "A.", go into multiple description mode.
    #else go until empty line;
    #multiple description mode, wait for double line break before stopping

    ##however, an issue is that multiple actions and objects may share a description.
    def __init__(self,training_set):
        self.total=0
        self.categorized= 0
        self.stage = 0
        self.currentProp = [Proposal()];
        self.completedProps = [];
        self.categorizer = Categorizer.Categorizer(training_set)
    def StringList(self):
        s = [];
        for prop in self.completedProps:
            if(prop.category is "BLANK"):
                currentstring = "Action: "+prop.action+"; Category: "+prop.category+"; Object: "+prop.object+"; description:"+prop.description
                s.append(currentstring)
        return s
    def emptyCurrentProposition(self):
        for p in self.currentProp:
            self.total +=1
            p.action = p.action.strip()
            p.object = p.object.strip()
            p.description = p.description.strip()
            p.category = self.categorizer.categorize(p.object)
            if(not p.category is "BLANK"):
                self.categorized +=1
            self.completedProps.append(p);
        self.currentProp = [Proposal()]
        self.stage = 0;
    def addDescription(self,section):
        for p in self.currentProp:
            p.description+=(" "+section);
    def process(self, section):
        working_section = section;
        if(self.stage == 0):
            found = self.find_action(working_section)
            return
        elif(self.stage == 1):
            #print("Checking for object at line"+str(ln))
            self.find_object(working_section)
        elif(self.stage == 2):
            #print("checking for description at line"+str(ln))
            self.find_description(working_section)



    def find_action(self,section):
        firstWord = section.split(" ")[0]
        if(firstWord=="ESTABLISH" or firstWord == "RESCIND"):
            self.currentProp[-1].action = firstWord
            self.currentProp[-1].object = section.split("–")[1];
            self.stage = 1;
            return True
        return False
    def find_object(self,section):
        firstWord = section.split(" ")[0]
        if(firstWord=="ESTABLISH" or firstWord == "RESCIND"):
            self.currentProp.append(Proposal())
            self.currentProp[-1].action = firstWord
            self.currentProp[-1].object = section.split("–")[1]
        elif(firstWord.isupper() and not firstWord == "A."):
            self.currentProp[-1].object+=(" "+section)
        else:
            self.addDescription(section)
            self.stage = 2;
    def find_description(self,section):
        firstWord = section.split(" ")[0];
        if(firstWord in ["ESTABLISH","RESCIND","be", "Items"]):
            self.emptyCurrentProposition()
            self.process(section)
        elif(not section.isspace()):
            self.addDescription(section)



def main():
    text = pdftotext.convert_pdf_to_txt("Engineering_Public_Hearing_example.pdf")
    sections = text.split("\n")
    pmachine = ProposalMachine("Resolution-Detail-of-08_02_2017.csv")
    #print(str(pmachine.categorizer.reference_dict))
    for sect in sections:
        if(pmachine.process(sect)):
            pmachine.process(sect)
    for p in pmachine.StringList():
        print(p+"\n")
    print("categorized: "+str(pmachine.categorized)+"/"+str(pmachine.total))

if __name__ == '__main__':
    main()
