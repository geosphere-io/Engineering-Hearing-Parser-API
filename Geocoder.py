##Based on code by Marc
#!/usr/bin/python
import psycopg2
import re
import sys
# -*- coding: utf8 -*-

# sys.setdefaultencoding() does not exist, here!
#reload(sys)  # Reload does the trick!
#sys.setdefaultencoding('UTF8')

class geocoder{
    def __init(self,dbname,dbusername,dbpassword):
        self.project_range= 2640
        self.conn = psycopg2.connect(dbname="elect", user="elect",password="elect")
        cur = conn.cursor()
        self.streets = {}
        self.streets_regexen = {}
        self.street_bits = {}
        self.item = ''
        self.words = []
    def nearest_neighbor(points, k):
        shortest = 999999
        a = point[k]
        for k in points:
            b = points[k];
            sql = "select st_distance(a1.the_geom,b2.the_geom) from stintersections a1, stintersections b1, stintersections a2, stintersections b2 where a1.the_geom=b1.the_geom and a1.st_name='{0}' and a1.st_type='{1}' and b1.st_name='{2}' and b1.st_type='{3}' and a2.the_geom=b2.the_geom and a2.st_name='{4}' and a2.st_type='{5}' and b2.st_name='{6}' and b2.st_type='{7}' and a1.the_geom=b1.the_geom and a2.the_geom=b2.the_geom".  format( a['a_street'].upper(),a['a_st_type'].upper(),a['b_street'].upper(),a['b_st_type'], b['a_street'].upper(),b['a_st_type'].upper(),b['b_street'].upper(),b['b_st_type'])
            cur = self.conn.cursor();
            cur.execute(sql)
            res = cur.fetchone();
            if res is not None and len(res) > 0 and res[0] > 0 and res[0] < shortest:
                shortest = res[0]
         if shortest == 999999:
             shortest = 0
         return(shortest)


}
