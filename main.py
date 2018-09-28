#!/usr/bin/env python3

import sys
import sqlite3 as sqlite

from code         import interact
from PyQt4        import uic
from PyQt4.QtCore import *
from PyQt4.QtGui  import *
from PyQt4.QtSql  import *

Ui_MainWindow, QtBaseClass = uic.loadUiType('ctrack3.ui')

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

        self.ui.activitiesView.setModel(self.models["acts"])
        self.ui.activitiesView.setColumnHidden(0, True)
        self.ui.activitiesView.setColumnHidden(self.models["acts"].fieldIndex("id"), True)
        self.ui.activitiesView.setColumnHidden(self.models["acts"].fieldIndex("developer"), True)
        self.ui.activitiesView.setColumnHidden(self.models["acts"].fieldIndex("closed"), True)
        self.ui.activitiesView.setColumnHidden(self.models["acts"].fieldIndex("user_status"), True)
        self.ui.activitiesView.clicked.connect(self.updateChangesets)
        
        # changesets
        self.models["csets"]  = QSqlQueryModel()
        self.csets_query = "SELECT changesets.id, changesets.date || ' ' || changesets.time AS 'date', ps_versions.version, ps_versions.build, changesets.name, group_concat(DISTINCT releases.module) AS 'modules', changesets.versioning FROM (((activities JOIN activity_changesets ON activities.id=activity_changesets.activity_id) JOIN changesets ON activity_changesets.changeset_id=changesets.id) JOIN ps_versions ON ps_versions.id=changesets.version_id) JOIN releases ON releases.changeset_id=changesets.id WHERE activities.id IS '{}' GROUP BY changesets.id"
        self.models["csets_sort"] = QSortFilterProxyModel()
        self.models["csets_sort"].setSourceModel(self.models["csets"])
        self.ui.changesetsView.setModel(self.models["csets_sort"])
        self.ui.changesetsView.clicked.connect(self.updateReleases)

        # releases
        self.models["rels"]  = QSqlQueryModel()
        self.rels_query = "SELECT module, file, comment FROM releases WHERE changeset_id='{}'"
        self.models["rels_sort"] = QSortFilterProxyModel()
        self.models["rels_sort"].setSourceModel(self.models["rels"])
        self.ui.releasesView.setModel(self.models["rels_sort"])

        # select intial rows
        self.ui.activitiesView.setCurrentIndex(self.models["acts"].index(0, 0))
        self.updateChangesets()
        self.ui.changesetsView.setCurrentIndex(self.models["csets"].index(0, 0))
        self.updateReleases()
        self.ui.releasesView.setCurrentIndex(self.models["rels"].index(0, 0))

        # tweak columns
        self.ui.changesetsView.setColumnHidden(0, True)
        self.ui.changesetsView.setColumnHidden(4, True)

        self.ui.activitiesView.resizeColumnToContents(1)
        for i in range(self.models["csets"].columnCount()):
            self.ui.changesetsView.resizeColumnToContents(i)
        for i in range(self.models["rels"].columnCount()):
            self.ui.releasesView.resizeColumnToContents(i)

        # relabel buttons
        self.ui.activitiesButtonBox.children()[-1].setText("&Add")
        self.ui.activitiesButtonBox.children()[-2].setText("&Remove")
        self.ui.changesetsButtonBox.children()[-1].setText("A&ssociate")
        self.ui.changesetsButtonBox.children()[-2].setText("&Disassociate")
        self.ui.detailsButtonBox.children()[-1].setText("&Add")
        self.ui.detailsButtonBox.children()[-2].setText("&Remove")
        self.ui.detailsButtonBox.setEnabled(False)
        self.ui.regressionsTab.parent().parent().currentChanged.connect(self.toggleButtons)

        self.inter()


    def toggleButtons(self, i):
        self.ui.detailsButtonBox.setEnabled(i != 0)

    def inter(self):
        env = globals().copy()
        loc = locals()
        env.update(loc)
        interact(local=env)

    def updateActivities(self):
        self.models["acts"].setFilter("developer is '{}'".format(self.ui.devComboBox.currentText()))
        self.models["acts"].select()

    def updateChangesets(self):
        idx = self.ui.activitiesView.currentIndex()
        if idx.isValid():
            idx = self.models["acts"].index(idx.row(), 0)
            actID = self.models["acts"].data(idx)
            self.models["csets"].setQuery(self.csets_query.format(actID))

    def updateReleases(self):
        idx = self.ui.changesetsView.currentIndex()
        # print(str(idx))
        if idx.isValid():
            idx = self.models["csets"].index(idx.row(), 0)
            csID = self.models["csets"].data(idx)
            # print(csID)
            self.models["rels"].setQuery(self.rels_query.format(csID))
        for i in range(self.models["rels"].columnCount()):
            self.ui.releasesView.resizeColumnToContents(i)

    def keyboardShortcuts(self):
        QShortcut(QKeySequence("Ctrl+Q"), self, self.destroy)

            
if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MyApp()
    win.show()
    #interact()

    sys.exit(app.exec_())
