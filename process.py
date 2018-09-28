import re
from code import interact

patterns = ["[^:]+:",
            "((perf *)?pr)? *\d{6,8}(_\w+)?",
            "proj(ect)? *\d{5}",
            "apic *\d{4}"
           ]

with open("comments2.txt") as f:
     cs = f.readline().strip()
     while cs:
         print(cs)
         l  = ">"
         r  = []
         while l[0] == ">":
             r.append(l)
             l = f.readline().strip()

         acts = []
         for rel in r[1:]:
             print(rel)
             for p in patterns:
                 m = re.findall(p[2:], rel, re.I)
                 print("  {}: {}".format(p, m))
                 acts += m

         interact(local=locals())
         cs = l
         
         
