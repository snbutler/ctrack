#!/usr/bin/env python3

import re
import sys

from code         import interact
from PyQt4        import uic
from PyQt4.QtCore import *
from PyQt4.QtGui  import *
from PyQt4.QtSql  import *

    def updateChangesets(self):
        idx = self.ui.activitiesTable.currentIndex()
        if idx.isValid():
            idx = self.models["acts"].index(idx.row(), 0)
            actID = self.models["acts"].data(idx)

            self.models["csets_sql"].setQuery(self.csets_query.format(actID))
            self.models["csets"].clear()
            self.models["csets"].setColumnCount(6)
            root = self.models["csets"].invisibleRootItem()

            i    = 0
            cs0  = None
            curr = None
            print("{} records".format(self.models["csets_sql"].rowCount()))
            while i < self.models["csets_sql"].rowCount():
                rec = self.models["csets_sql"].record(i)
                cs  = rec.value(4)
                if cs != cs0:
                    print("add {} to root".format(cs))
                    cols = []
                    for j in range(4):
                        col = QStandardItem(str(rec.value(j)))
                        col.setEditable(False)
                        cols.append(col)
                    root.appendRow(cols)
                    curr = cols[0]
                    cs0 = cs

                cols = []
                print( "add {} to cs".format([rec.value(j) for j in range(rec.count())]))
                for j in range(5,rec.count()):
                    col = QStandardItem(rec.value(j))
                    col.setEditable(False)
                    cols.append(col)
                #rel = QStandardItem(cols)
                curr.appendRow(cols)
                i += 1

    def keyboardShortcuts(self):
        QShortcut(QKeySequence("Ctrl+Q"), self, self.destroy)

def appendFold():
    pass
            
if __name__ == '__main__':
    with open(sys.argv[1]) as f:
        tree = QStandardItemModel()
        root = tree.invisibleRootItem()
        
        parent = root
        for l in f:
            if re.match("\s*\\\\{{{", l):
                fold = QStandardItem(re.subn("\s*\\\\{{{\s*", "", l))
                parent.append([fold])
                parent = fold
            elif re.match("\s*\\\\}}}", l):
                parent = fold.parent()
            else:
                fold = QStandardItem(l)
                parent.append([fold])

