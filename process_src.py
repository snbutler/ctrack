#!/usr/bin/env python3

import re
import sys

from code         import interact
from PyQt4        import uic
from PyQt4.QtCore import *
from PyQt4.QtGui  import *

Ui_MainWindow, QtBaseClass = uic.loadUiType('ps.ui')

class MyApp(QMainWindow):
    def __init__(self, filen):
        super(MyApp, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.tree = QStandardItemModel()
        self.root = self.tree.invisibleRootItem()

        with open(filen) as f:
            parent = self.root
            for l in f:
            #print(parent, parent is self.root, parent.parent() is self.root if parent else None)
            #print(parent, parent.parent() if parent else None)
                if re.match("\s*\/\/{{{", l):
                    #print("nest", l.strip())
                    fold = QStandardItem(re.subn("\s*\/\/{{{\s*", "", l.strip())[0])
                    parent.appendRow(fold)
                    parent = fold
                elif re.match("\s*\/\/}}}", l):
                    #print("un-nest", l.strip())
                    parent = parent.parent() if parent else self.root
                    if not parent:
                        parent = self.root
                else:
                    #print("append", l.strip())
                    fold = QStandardItem(l.strip())
                    parent.appendRow(fold)
                    #print(parent)

        self.ui.treeView.setModel(self.tree)

        idx = self.tree.index(0, 0)
        try:
            self.printNode(self.tree.index(0, 0))
        except:
            interact(local=locals())
        interact(local=locals())

    def printNode(self, idx, level = 0):
        #print("level: {}".format(level))
        while idx.isValid() and idx.row() < self.tree.rowCount(idx.parent()):
            #print("{} ({})".format(idx.row(), self.tree.rowCount(idx.parent())))
            #interact(local=locals())
            s = str(self.tree.data(idx).toString())
            if not re.match("\s*---", s):
                print(" "*level + s)
                if self.tree.hasChildren(idx):
                    self.printNode(idx.child(0,0), level+1)
            idx = idx.sibling(idx.row()+1, 0)
            #print("  will be {}".format(str(self.tree.data(idx).toString())))
            #print("now {} {}".format(idx.row(), self.tree.rowCount(idx)))
        

            
if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MyApp(sys.argv[1])
    win.show()
    #interact()

    sys.exit(app.exec_())
