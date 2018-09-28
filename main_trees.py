#!/usr/bin/env python3

import sys
import sqlite3 as sqlite

from code         import interact
from PyQt4        import uic
from PyQt4.QtCore import *
from PyQt4.QtGui  import *
from PyQt4.QtSql  import *

Ui_MainWindow, QtBaseClass = uic.loadUiType('ctrack.ui')

db_name = "ctrack.db"
# act:   id, name, description, closed, user_status, developer
# cs:    id, ver_id, idx, dev, date, time, name, versioning, status
# ps_ver: id, ver, build
# rel:   id, changeset_id, module, file, comment
# tc:    id, changeset_id, test_id, platforms, dev_notes, qa_notes
# tests: id, type, suite, name


class MyApp(QMainWindow):
    def __init__(self):
        super(MyApp, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.keyboardShortcuts()

        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName(db_name)
        self.db.open()

        # set up developer dropdown
        self.models = {}
        self.models["devs"] = QSqlQueryModel()
        self.models["devs"].setQuery("SELECT release_name FROM developers ORDER BY release_name")
        self.ui.devComboBox.setModel(self.models["devs"])

        # initialise value of dev selector
        for i in range(self.models["devs"].rowCount()):
            if self.models["devs"].record(i).value("release_name") == "simonb":
                self.ui.devComboBox.setCurrentIndex(i)
                break
        self.ui.devComboBox.activated.connect(self.updateActivities)
       
        # activities table
        self.models["acts"] = QSqlTableModel()
        self.models["acts"].setTable("activities")
        self.updateActivities()

        self.ui.activitiesTable.setModel(self.models["acts"])
        self.ui.activitiesTable.setColumnHidden(0, True)
        self.ui.activitiesTable.setColumnHidden(self.models["acts"].fieldIndex("id"), True)
        self.ui.activitiesTable.setColumnHidden(self.models["acts"].fieldIndex("developer"), True)
        self.ui.activitiesTable.setColumnHidden(self.models["acts"].fieldIndex("closed"), True)
        self.ui.activitiesTable.setColumnHidden(self.models["acts"].fieldIndex("user_status"), True)
        self.ui.activitiesTable.clicked.connect(self.updateChangesets)
        
        self.models["csets"] = QStandardItemModel()
        self.models["csets_sql"]  = QSqlQueryModel()
        self.csets_query = "SELECT changesets.date, changesets.time, ps_versions.version, ps_versions.build, changesets.name, releases.module, releases.file, releases.comment FROM (((activities JOIN activity_changesets ON activities.id=activity_changesets.activity_id) JOIN changesets ON activity_changesets.changeset_id=changesets.id) JOIN releases ON releases.changeset_id=changesets.id) JOIN ps_versions ON ps_versions.id=changesets.version_id  WHERE activities.id IS '{}'"
        #self.models["csets"].update(self.ui.activitiesTable)
        self.ui.changesetsTable.setModel(self.models["csets"])
        self.ui.activitiesTable.setCurrentIndex(self.models["acts"].index(1, 0))
        self.updateChangesets()
        """
        env = globals().copy()
        loc = locals()
        env.update(loc)
        interact(local=env)
        """


    def updateActivities(self):
        self.models["acts"].setFilter("developer is '{}'".format(self.ui.devComboBox.currentText()))
        self.models["acts"].select()

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

            
if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MyApp()
    win.show()
    #interact()

    sys.exit(app.exec_())
