import re
import sqlite3 as sqlite
import urllib3
import requests
from requests_ntlm import HttpNtlmAuth
from bs4 import BeautifulSoup
from PyParasolid.build import PSBuildsOfVersion, PSBuildNumber
from code import interact

dms_url  = "http://cbrx64i72/dmssqlserver/ProjectsDisc.aspx?id={}"
apic_url = "http://otws.cbr.ugs.com/APIC_New/View.aspx?N={}"
tac_url  = "http://www-assem.net.plm.eds.com/cgi-bin/tac_pr.pl?number={}#query"
headers  = urllib3.util.make_headers(basic_auth="qd8zve:But#51m5")

def getPage(url, http):
    page = http.get(url)
    # print("Got {}".format(page.status))
    return BeautifulSoup(page.text, "html.parser")

def lookup(actID, http):

    name = ""
    try:
        if   actID[:3] == "pid":
            page = getPage(dms_url.format(actID[3:]), http)
            # soup = BeautifulSoup(page, "html.parser")
            titleBox = page.find("textarea", attrs={"name": "ctl00$CPHDMS$txtProjectTitle"})
            print("pid")
            if titleBox:
                name = titleBox.text.strip()

        elif actID[:2] == "pr":
            page = getPage(tac_url.format(re.sub("_.*", "", actID[2:])), http)
            # soup = BeautifulSoup(page, "html.parser")
            td = page.findAll("td", attrs={"align": "center"})[-1]
            print("pr")
            # interact(local=locals())
            if td:
                name = td.text.strip()

        elif actID[:4] == "apic":
            page = getPage(apic_url.format(actID[4:]), http)
            # soup = BeautifulSoup(page, "html.parser")
            titleBox = page.find("span", attrs={"id": "ContentPlacePageSubTitle_TitleView"})
            if titleBox:
                name = re.subn("APIC \d+ : ", "", titleBox.text.strip())[0]
            print("apic")
            # interact(local=locals())

    except Exception as e:
        interact(local=locals())

    print(safestr(name))
    return name

def safestr(text):
    return re.sub(r'[^\x00-\x7F]+',' ', text)

def insert(db, table, fields, vals):
    curs = db.cursor()
    sql  = "INSERT INTO {}({}) VALUES ({})".format(table, ",".join(fields), ("?,"*len(fields))[:-1])
    # print("INSERT INTO {}({}) VALUES ({})".format(table, ",".join(fields), ",".join([str(v) for v in vals])))
    curs.execute(sql, vals)
    return curs.lastrowid

def insertDev(db, dev):
    fields = ("release_name")
    return insert(db, "developers", fields, dev)

def insertActCSLink(db, act_cs):
    fields = ("activity_id", "changeset_id")
    return insert(db, "activity_changesets", fields, act_cs)

def insertCS(db, cs):
    fields = ("developer", "version_id", "idx", "date", "time", "name")
    return insert(db, "changesets", fields, cs)

def insertRelease(db, release):
    fields = ("changeset_id", "module", "file", "comment")
    return insert(db, "releases", fields, release)

def insertActivity(db, activity):
    fields = ("name", "developer")
    return insert(db, "activities", fields, activity)

def insertVersion(db, ver):
    fields = ("version", "build")
    return insert(db, "ps_versions", fields, ver)

def getExistingActivity(db, name, developer):
    curs = db.cursor()
    sql  = "SELECT id FROM activities WHERE name IS \"{}\" AND developer IS \"{}\"".format(name, developer)
    print(sql)
    curs.execute(sql)
    res = curs.fetchall()
    if res:
        return res[0][0]

def tryPattern(pattern, comment):
    x = re.search(pattern, comment[:-1], re.I)
    if x:
        return x.groups(0)[0].strip()
    else:
        return None

def extractActivity(comment):
    patterns = {
                # "project": " *(?:p(?:roj(?:ect)?|id))? *\d{5,5}",
                "project": " *(?:p(?:roj(?:ect)?|id)?)? *(?<!\d)(?<!flt)(?<!pr)(?<!apic)\d{5}(?!\d)",
                "pr":      " *(?:(?:perf(?:_| )*)?pr)? *\d{6,8}(?:_\w+)?",
                "apic":    " *apic *\d{4,}",
                "test":    " *[a-z]+(?:_[a-z0-9]+)*_[0-9]+",
                "generic": " *([^:]+):",
               }

    acts = []
    if re.search(patterns["project"], comment, re.I):
        # assume first project is the principal one
        for m in re.findall(patterns["project"], comment, re.I):#.group(0)
            # print(m)
            n = re.search("\d{5,}", m, re.I).group(0)
            print("Add project {}".format(n))
            acts.append("pid"+n)
    elif re.search(patterns["pr"], comment, re.I):
        # store all mentioned PRs
        for m in re.findall(patterns["pr"], comment, re.I):
            # num = re.subn(" ", "_", m.strip())[0].lower() 
            # num = re.subn("^([0-9])", "pr\\1", num)[0]
            # interact(local=locals())
            # acts.append(num)
            n = re.search("\d{6,7}", m, re.I).group(0)
            print("Add pr {}".format(n))
            acts.append("pr"+n)
    elif re.search(patterns["apic"], comment, re.I):
        # assume only one apic!
        # m = re.search(patterns["apic"], comment, re.I).group(0)
        # n = re.search("\d{4,}", m, re.I).group(0)
        # acts.append("apic"+n)
        for m in re.findall(patterns["apic"], comment, re.I):
            # num = re.subn(" ", "_", m.strip())[0].lower() 
            # num = re.subn("^([0-9])", "pr\\1", num)[0]
            # interact(local=locals())
            # acts.append(num)
            n = re.search("\d{4}", m, re.I).group(0)
            print("Add apic {}".format(n))
            acts.append("apic"+n)
    elif re.search(patterns["generic"], comment, re.I):
        # store
        acts.append(re.search(patterns["generic"], comment, re.I).group(0)[:-1])
    elif re.search(patterns["test"], comment, re.I):
        # store all mentioned tests
        acts += re.findall(patterns["test"], comment, re.I)
    else:
        pass

    return [y.strip() for y in acts]



if __name__ == "__main__":
    ver_i   = "290"
    # ver_i   = "300"
    version = PSBuildNumber(version=ver_i, build=1)

    db  = sqlite.connect("test.db")
    cur = db.cursor()

    # urllib3.disable_warnings()
    # http = urllib3.PoolManager()
    # urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    # urllib3.disable_warnings(urllib3.exceptions.HTTPError)
    # ua   = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"
    # cert = False
    # http.verify = cert
    # http.headers.update({"User-Agent": ua})

    user = "plm\qd8zve"
    pw   = "But#51m5"
    http = requests.Session()
    http.auth = HttpNtlmAuth(user, pw)

    done = False
    while not done:
        bov = PSBuildsOfVersion(version.regime()).getAllBuilds()
        #print("{}: {}".format(version.full(), bov))

        for b in bov:
            ver_id = insertVersion(db, (b.major()+b.minor(), b.buildn()))

            cs = b.getChangesets()
            for c in cs:
                # set name
                date = c.date.strftime("%d/%m/%y")
                time = c.date.strftime("%H:%M:%S")
                name = "{}_{}".format(c.date.strftime("%y_%m_%d_%H_%M_%S"), c.user)
                print(name)

                # find activities
                names = []
                activities = []
                for f in c.getReleaseComments():
                    print("  {}: {}".format(f[0], f[1].strip().encode("utf-8")))
                    for a in extractActivity(safestr(f[1]).strip()):
                        if not a in names:
                            names.append(a)
                print(names)
                for n in names:
                    print(n)
                    lookup(n, http)

                for n in names:
                    # find existing activities
                    actID = getExistingActivity(db, n, c.user) or insertActivity(db, (n, c.user))
                    print(">> ",actID)
                    if not actID in activities:
                        activities.append(actID)
                print(activities)

                vals  = (c.user, ver_id, c.index(), date, time, name) 
                cs_id = insertCS(db, vals)

                for a in activities:
                    insertActCSLink(db, (a, cs_id))

                for f in c.getReleaseComments():
                    # insert releases
                    (mod, filen) = f[0].split("\\")
                    vals = (cs_id, mod, filen, safestr(f[1]).strip())
                    insertRelease(db, vals)
            # interact(local=locals())

        done = bov[-1].as_devel()
        version.incrementVersion()

    db.commit()
