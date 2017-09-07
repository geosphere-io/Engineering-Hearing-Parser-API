#!/usr/bin/python
import psycopg2
import re
import sys
# -*- coding: utf8 -*-

project_radius = 2640

def distance_between_points(a,b,conn):
    ##Executes the gsi query to find the distanct between two points.
   sql = "select st_distance(a1.the_geom,b2.the_geom) from stintersections a1, stintersections b1, stintersections a2, stintersections b2 where a1.the_geom=b1.the_geom and a1.st_name='{0}' and a1.st_type='{1}' and b1.st_name='{2}' and b1.st_type='{3}' and a2.the_geom=b2.the_geom and a2.st_name='{4}' and a2.st_type='{5}' and b2.st_name='{6}' and b2.st_type='{7}' and a1.the_geom=b1.the_geom and a2.the_geom=b2.the_geom".  format( a['a_street'].upper(),a['a_st_type'].upper(),a['b_street'].upper(),a['b_st_type'], b['a_street'].upper(),b['a_st_type'].upper(),b['b_street'].upper(),b['b_st_type'])
   cur = conn.cursor()
   cur.execute(sql)
   res = cur.fetchone()
   if res is not None and len(res) > 0:
       return(res[0])

def nearest_neighbor(points, j, conn):
    ##finds the distance to the nearest nearest_neighboring point
    shortest = 999999
    a = points[j]
    for k in points:
       b = points[k]
       distance = distance_between_points(a,b,conn)
       if distance > 0 and distance < shortest:
           shortest = distance

    if shortest == 999999:
        shortest = 0
    return(shortest)

def parse_text():
    item = ''
    words = []
    e = open (sys.argv[1],'r')
# break words into an array
    for line in e:
        item = item + line.replace(',','').replace('\n',' ')
        words.extend(line.replace("'","").replace(',',' ').replace('.',' ').split())
    return item,words

def get_verb_subject(item):
    a = '\xe2\x80\x93'
    res = re.findall('^[A-Z]\.[\s]*([A-Z^\-]+)[\s]*[\-'+a+']+[\s]*(.*) \- .*$',item)
    verb = ''
    subject = ''

    if res is not None and len(res) == 1:
        verb = res[0][0]
        subject = res[0][1]
    return verb,subject

def get_max_street_len(conn):
    sql = "select max(length(street)) from stclines_streets"
    cur = conn.cursor()
    cur.execute(sql)
    return cur.fetchone()[0]

def get_street_bits(words,conn):
    street_bits = {}
    max_street_len = get_max_street_len(conn)
    # iterate over words, checking (n), (n n+1) and (n n+1 n+2)
    cur = conn.cursor()
    streets_regexen = {}
    words_seen = {}
    for n in range(0,len(words)):
        for a in range(1,5):
            street_words = []
            # don't run off the end
            if n+a == len(words):
                break
            for b in range(n,n+a):
                 street_words.append(words[b])
            word = ' '.join(street_words)
            # don't do any unncessary db lookups
            if len(word) > max_street_len or word in words_seen:
                continue
            words_seen[word] = 1
            sql = "select street,st_type from stclines_streets where street ilike '{0}' and length(street) > 2".format(word)
            cur.execute(sql)
            # if this token is a street name, include it in the regex
            res = cur.fetchall()
            if len(res) > 0 and res[0][0] is not None and res[0][1] is not None:
                reg = "{0}[\\s]+{1}".format(res[0][0],res[0][1])
                streets_regexen[reg] = 1
                if res[0][1] == 'ST':
                    streets_regexen[reg] = 1
                if res[0][1] == 'AV' or res[0][1] == 'AVE':
                    streets_regexen[reg] = 1
                # save fields for disambiguation
                bits = {}
                bits['street'] = res[0][0]
                bits['st_type'] = res[0][1]
                street_bits[bits['street'] + ' ' + bits['st_type']] = bits
    return street_bits,streets_regexen

def search_item_for_streets(item,streets_regexen):
    streets = {}
    # assemble regular expression
    item = re.sub(r'\n',' ',item)
    regex = '^.*(' + '|'.join(streets_regexen.keys()) + ')+.*$'
    regex = '(' + '|'.join(streets_regexen.keys()) + ')+'

    # iterate across matches from street db of <street name>[spaces]<street type>
    for res in re.findall(regex,item,re.IGNORECASE):
        streets[res] = 1
    return streets

def get_intersections(streets,street_bits,conn):
    # iterate over matches, deduping, geocoding
    seen = {}
    points = {}
    cur = conn.cursor()
    for a in streets.keys():
        try:
            a_bits = street_bits[a.upper()]
        except KeyError:
            continue

        for b in streets.keys():
            try:
                b_bits = street_bits[b.upper()]
            except KeyError:
                continue

            # if this street is that street, ignore
            if a == b:
                continue

            key1 = str(a_bits) + ' ' + str(b_bits)
            key2 = str(b_bits) + ' ' + str(a_bits)

            # check to see if we've reported this intersection
            if key1 in seen or key2 in seen:
                continue

            # mark as seen
            seen[key1] = 1
            seen[key2] = 1

            # spatial query to check for existence of intersection
            # transform SRID to 4674 and pull lat/lon
            sql = "select ST_X(ST_TRANSFORM(a.the_geom,4674)) AS LONG, ST_Y(ST_TRANSFORM(a.the_geom,4674)) AS LAT from stintersections a, stintersections b where a.the_geom=b.the_geom and a.st_name='{0}' and a.st_type='{1}' and b.st_name='{2}' and b.st_type='{3}'".format(a_bits['street'].upper(),a_bits['st_type'].upper(),b_bits['street'].upper(),b_bits['st_type'])
            cur.execute(sql)
            res = cur.fetchall()
            if res is None or len(res) <= 0:
                continue

            d = { "lat" : res[0][0], "lon" : res[0][1] , "a_street" : a_bits['street'].upper(), "a_st_type" : a_bits['st_type'].upper(), "b_street" : b_bits['street'].upper() , "b_st_type" : b_bits['st_type'].upper()}
            points[str(d)] = d
    return points


def nearest_neighbors(points,conn):
    # calculate nearest neighbor of two intersections
    for point in points:
        points[point]['shortest'] = nearest_neighbor(points, point, conn)

def report_matches(points,project_radius):
    # report matches
    for point in points:
        # filter out intersections too far afield probable noise
        p = points[point]
        if p['shortest'] < project_radius:
            print "{0} {1} + {2} {3} {4} - {5} : {6}\n".format(p['a_street'],p['a_st_type'],p['b_street'],p['b_st_type'],p['lat'],p['lon'],p['shortest'])

def main():

    item, words = parse_text()

    verb, subject = get_verb_subject(item)

    conn = psycopg2.connect(dbname="engr", user="engr",password="engr")

    street_bits, streets_regexen = get_street_bits(words,conn)

    streets = search_item_for_streets(item,streets_regexen)

    points = get_intersections(streets,street_bits,conn)

    nearest_neighbors(points,conn)

    print "{0} - {1}:\n".format(verb,subject)

    report_matches(points,project_radius)

if __name__ == '__main__':

   main()
