# -*- coding: utf-8 -*-

import csv
class Categorizer:
    #initialize and train the Categorizer
    def __init__(self, reference_file):
        fp = open(reference_file, "r");
        entries=csv.reader(fp)
        type_dict={}
        for row in entries:
            print(row[6]+row[5])
            type = row[6].upper()
            category = row[5].title()
            if(type in type_dict):
                if(category in type_dict[type]):
                    type_dict[type][category] +=1
                else:
                    type_dict[type][category] = 1
            else:
                type_dict[type]={category:1}
        for type in type_dict:
            type_dict[type] = max(type_dict[type], key = type_dict[type].get)
        self.reference_dict= type_dict;
    def categorize(self,type):
        if(type in self.reference_dict):##Test to see if we already have this category
            return self.reference_dict[type]
        ##Switch to keyword test)
        ##todo: find better way of generating keyword lists than by hand
        if(self.wordTest(['ZONE','LOADING','PARKING','TOW-AWAY'],type)):
            return "Parking"
        if(self.wordTest(['BIKE','BICYCLE'],type)):
            return "Biking"
        if(self.wordTest(['SIGNAL','TURN','SIGNS',],type)):
            return "Traffic"
        if(self.wordTest(['BOARDING'],type)):
            return "Transit"
        return "BLANK"
    #Helper to test if any of words in string are in the wordList
    def wordTest(self,wordList,string):
        return any(word in string for word in wordList)

def main():
    c = Categorizer("Resolution-Detail-of-08_02_2017.csv");
    print(c.reference_dict)
    print(c.categorize("RED ZONE"))
    print(c.categorize("CLASS II BIKE LANE"))


if __name__ == '__main__':
    main()
