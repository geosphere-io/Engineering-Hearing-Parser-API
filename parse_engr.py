#!/usr/bin/python
import psycopg2
import re
import sys
# -*- coding: utf8 -*-

# sys.setdefaultencoding() does not exist, here!
#reload(sys)  # Reload does the trick!
#sys.setdefaultencoding('UTF8')
project_range = 2640

e = open (sys.argv[1],'r')
conn = psycopg2.connect(dbname="elect", user="elect", password="elect")
cur = conn.cursor()
streets = {}
streets_regexen = {}
street_bits = {}
item = ''
words = []

def nearest_neighbor(points, k):
    shortest = 999999
    a = points[k]
    for k in points:
       b = points[k]
       sql = "select st_distance(a1.geom,b2.geom) from stintersections a1, stintersections b1, stintersections a2, stintersections b2 where a1.geom=b1.geom and a1.st_name='{0}' and a1.st_type='{1}' and b1.st_name='{2}' and b1.st_type='{3}' and a2.geom=b2.geom and a2.st_name='{4}' and a2.st_type='{5}' and b2.st_name='{6}' and b2.st_type='{7}' and a1.geom=b1.geom and a2.geom=b2.geom".  format( a['a_street'].upper(),a['a_st_type'].upper(),a['b_street'].upper(),a['b_st_type'], b['a_street'].upper(),b['a_st_type'].upper(),b['b_street'].upper(),b['b_st_type'])
       cur = conn.cursor()
       cur.execute(sql)
       res = cur.fetchone()
       if res is not None and len(res) > 0 and res[0] > 0 and res[0] < shortest:
           shortest = res[0]
    if shortest == 999999:
        shortest = 0
    return(shortest)

# break words into an array
for line in e:
    item = item + line.replace(',','').replace('\n',' ')
    words.extend(line.replace("'","").replace(',',' ').replace('.',' ').split())
a = '\xe2\x80\x93'
res = re.findall('^[A-Z]\.[\s]*([A-Z^\-]+)[\s]*[\-'+a+']+[\s]*(.*) \- .*$',item)
#verb = res[0][0]
#subject = res[0][1]

# iterate over words, checking (n), (n n+1) and (n n+1 n+2)
for n in range(0,len(words)):
    for a in range(1,5):
        street_words = []
        # don't run off the end
        if n+a == len(words):
            break
        for b in range(n,n+a):
             street_words.append(words[b])
        word = ' '.join(street_words)
        sql = "select street,st_type from stclines where street ilike '{0}' and length(street) > 2".format(word)
        cur.execute(sql)
        # if this token is a street name, include it in the regex
        res = cur.fetchall()
        if len(res) > 0 and res[0][0] is not None and res[0][1] is not None:
            reg = "{0}[\\s]+{1}".format(res[0][0],res[0][1])
            streets_regexen[reg] = 1
            if res[0][1] == 'ST':
                reg = "{0}[\\s]+STREET".format(res[0][0])
            if res[0][1] == 'AV' or res[0][1] == 'AVE':
                reg = "{0}[\\s]+AVENUE".format(res[0][0])
            # save fields for disambiguation
            bits = {}
            bits['street'] = res[0][0]
            bits['st_type'] = res[0][1]
            street_bits[bits['street'] + ' ' + bits['st_type']] = bits


# assemble regular expression
item = re.sub(r'\n',' ',item)
regex = '^.*(' + '|'.join(streets_regexen.keys()) + ')+.*$'
regex = '(' + '|'.join(streets_regexen.keys()) + ')+'

# iterate across matches from street db of <street name>[spaces]<street type>
for res in re.findall(regex,item,re.IGNORECASE):
    streets[res] = 1

# iterate over matches, deduping, geocoding
seen = {}
points = {}
for a in streets.keys():
    a_bits = street_bits[a.upper()]

    for b in streets.keys():
        b_bits = street_bits[b.upper()]

        # if this street is that street, ignore
        if a == b:
            continue

        key1 = str(a_bits) + ' ' + str(b_bits)
        key2 = str(b_bits) + ' ' + str(a_bits)
        # check to see if we've reported this intersection
        if key1 in seen or key2 in seen:
            continue
        seen[key1] = 1
        seen[key2] = 1

        sql = "select ST_X(ST_TRANSFORM(a.geom,4326)) AS LONG, ST_Y(ST_TRANSFORM(a.geom,4326)) AS LAT from stintersections a, stintersections b where a.geom=b.geom and a.st_name='{0}' and a.st_type='{1}' and b.st_name='{2}' and b.st_type='{3}'".format(a_bits['street'].upper(),a_bits['st_type'].upper(),b_bits['street'].upper(),b_bits['st_type'])
        cur.execute(sql)
        res = cur.fetchall()
        if res is None or len(res) <= 0:
            continue

        d = { "lat" : res[0][0], "lon" : res[0][1] , "a_street" : a_bits['street'].upper(), "a_st_type" : a_bits['st_type'].upper(), "b_street" : b_bits['street'].upper() , "b_st_type" : b_bits['st_type'].upper()}
        points[str(d)] = d

# calculate nearest neighbor
for point in points:
    points[point]['shortest'] = nearest_neighbor(points, point)

#print "{0} - {1}:\n".format(verb,subject)
# report matches
for point in points:
    if points[point]['shortest'] < project_range:
        p = points[point]
        print "{0} {1} + {2} {3} {4} - {5} : {6}\n".format(p['a_street'],p['a_st_type'],p['b_street'],p['b_st_type'],p['lat'],p['lon'],p['shortest'])
