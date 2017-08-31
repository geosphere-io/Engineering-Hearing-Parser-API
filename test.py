# -*- coding: utf-8 -*-
import re
line="<a>hello</a> bak bak <a>bye</a>"
regex = re.compile("<a>(\w*)</a>.*<a>(\w*)</a>")
m = regex.match(line)
if m:
    print(m.group(1))
else:
    print("no match")
