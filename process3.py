#!/usr/bin/env python3

import re
#import regex
from code import interact

patterns = {
            "generic": " *([^:]+):",
            "pr":      " *(?:(?:perf(?:_| )*)?pr)? *\d{6,8}(?:_\w+)?",
            "project": " *p(?:roj(?:ect)?|id)? *\d{5,}",
            #"projid":  " *p(?:id)? *\d{5,}",
            "apic":    " *apic *\d{4,}",
            "test":    " *[a-z]+(?:_[a-z0-9]+)*_[0-9]+"
           }

db = {}
breaks = False
with open("comments3.txt") as f:
     vers = f.readline().strip()
     while vers:
         print (vers)
         cs = f.readline().strip()
         while cs[0] == ">":
             print(cs)

             user = cs[3:].split("_")[-1]
             if not user in db:
                 db[user] = []
                  
             l = "<"
             r = []
             while l[0] == "<":
                 r.append(l.split(",")[-1].strip())
                 l = f.readline().strip()

             acts = []
             for rel in r[1:]:
                 print(rel)
                 if   re.search(patterns["project"], rel, re.I):
                     for m in re.findall(patterns["project"], rel, re.I):
                         for n in re.findall("\d{5,}", m, re.I):
                             acts.append("pid"+n)
                 elif re.search(patterns["pr"], rel, re.I):
                     for m in re.findall(patterns["pr"], rel, re.I):
                         acts.append(re.subn(" ", "_", m))
                 elif re.search(patterns["apic"], rel, re.I):
                 elif re.search(patterns["generic"], rel, re.I):
                 else:

                 for p in patterns:
                     m = re.findall(p[3:], rel, re.I)
                     print("  {}: {}".format(p, m))
                     acts += m

                 if re.findall("60856", rel):
                     breaks = True


             if breaks:
                 interact(local=locals())

             cs = l

         vers = l
         
         
