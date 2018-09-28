import re
import sqlite3 as sqlite
import urllib3
import requests
import difflib
from requests_ntlm import HttpNtlmAuth
from bs4 import BeautifulSoup
from PyParasolid.build import PSBuildsOfVersion, PSBuildNumber
from code import interact


if __name__ == "__main__":
    ver_i   = "290"
    # ver_i   = "300"
    version = PSBuildNumber(version=ver_i, build=1)

    # db  = sqlite.connect("test.db")
    # cur = db.cursor()

    done = False
    while not done:
        bov = PSBuildsOfVersion(version.regime()).getAllBuilds()
        #print("{}: {}".format(version.full(), bov))

        for b in bov:
            cs = b.getChangesets()
            for c in cs:
                # set name
                date = c.date.strftime("%d/%m/%y")
                time = c.date.strftime("%H:%M:%S")
                name = "{}_{}".format(c.date.strftime("%y_%m_%d_%H_%M_%S"), c.user)
                print(name)

                pat = "(?<!---)(?<!#ver)((?:VER|DS)_(?:from_|before_|in_|\d)[^\s(-]+)"

                for (src, sav) in zip(c.getSrc(), c.getSav()):
                    print(src, sav)
                    with open(src) as src_f, open(sav) as sav_f:
                        for l in src_f:
                            m = re.search(pat, re.subn("\s*", "", l)[0])
                            if m:
                                interact(local=locals())

        done = bov[-1].as_devel()
        version.incrementVersion()

    # db.commit()
