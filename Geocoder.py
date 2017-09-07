import parse_engr as geoparse
import psycopg2
import re
import sys

class Geocoder:
    def parse_text(self,instr):
        #switched to function on a sinle string line.
        item = ''
        words = []
        item = item + instr.replace(',','').replace('\n',' ')
        words.extend(instr.replace("'","").replace(',',' ').replace('.',' ').split())
        return item,words
    def report_matches(self,points,project_radius):
        #similar to original, but returns result matrix instead of prinitng.
        result = [];
        for point in points:
            # filter out intersections too far afield probable noise
            p = points[point]
            if p['shortest'] < project_radius:
                #instead adds to results array
                result.append(p)
        return result
    def geocode(self,str):
        ##mostly just runs marc's code in parse_engr.py, but with a couple small modifications to work with singe line items
        #and return the points.
        project_radius = 2640
        item, words =self.parse_text(str)
        verb, subject = geoparse.get_verb_subject(item)
        conn = psycopg2.connect(dbname="engr", user="engr",password="engr")
        street_bits, streets_regexen = geoparse.get_street_bits(words,conn)

        streets = geoparse.search_item_for_streets(item,streets_regexen)

        points = geoparse.get_intersections(streets,street_bits,conn)

        geoparse.nearest_neighbors(points,conn)
        resultpoints = self.report_matches(points,project_radius)
        return resultpoints
def main():
    gc = Geocoder();
    rp = gc.geocode("Action: ESTABLISH; Object:  STOP SIGNS ; description: Balboa Street, eastbound and westbound, at 11th Avenue, making this intersection an all-way  STOP")
    print(rp)
if __name__ == '__main__':
    main()
