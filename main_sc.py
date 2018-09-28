#!/usr/bin/env python3

import sys
import sqlite3 as sqlite

from code         import interact
from PyQt4        import uic
from PyQt4.QtCore import QAbstractTableModel, QAbstractItemModel, Qt, QVariant, QModelIndex
from PyQt4.QtGui  import QMainWindow, QApplication, QStandardItem, QStandardItemModel
from PyQt4.QtSql  import *

Ui_MainWindow, QtBaseClass = uic.loadUiType('ctrack.ui')

db_name = "ctrack.db"
# act:   id, name, description, closed, user_status, developer
# cs:    id, name, versioning, status, activity_id
# rel:   id, changeset_id, module, file, comment
# tc:    id, changeset_id, test_id, platforms, dev_notes, qa_notes
# tests: id, type, suite, name

class ActivityTableModel(QAbstractTableModel):
    def __init__(self, data, parent = None, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.activities = data
        self.header = ("Name", "Description")

    def rowCount(self, parent):
        return len(self.activities)

    def columnCount(self, parent):
        return len(self.activities[1:])

    def data(self, index, role):
        if role in (Qt.DisplayRole, Qt.EditRole):
            #print("{}:{}".format(index.row(), index.column()+1))
            return self.activities[index.row()][index.column()+1]
        else:
            return None#QVariant()

    def headerData(self, section, orientation, role):
        if section <= 1 and orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[section]
        else:
            return None#QVariant()

class ChangesetsModel(QAbstractItemModel):
    class csItem():
        def __init__(self, parent = None, data = []):
            self._parent   = parent
            self._data     = data
            self._children = []

        def row(self):
            if self._parent:
                return self._parent._children.index(self)
            else:
                return 0

        def nCols(self):
            print("<< {}".format(self._data))
            return len(self._data)

        def nChildren(self):
            return len(self._children)

        def addChild(self, kid):
            self._children.append(kid)

        def getValue(self, col):
            return self._data[col]

        def getChild(self, i):
            return self._children[i] if i < self.nChildren() else None

        def getParent(self):
            return self._parent

    def __init__(self, parent = None, *args):
        QAbstractItemModel.__init__(self, parent, *args)

        self._query  = "SELECT changesets.date, changesets.time, changesets.name, releases.module, releases.file, releases.comment FROM ((activities JOIN activity_changesets ON activities.id=activity_changesets.activity_id) JOIN changesets ON activity_changesets.changeset_id=changesets.id) JOIN releases ON releases.changeset_id=changesets.id  WHERE activities.id IS '{}'"
        self._act_id = None
        self._model  = QSqlQueryModel()
        self._data   = self.csItem()

        self.header = ("Date", "Time", "Name", "Module", "File", "Comment")

    def update(self, activity):
        self.beginResetModel()

        self._data   = self.csItem()
        self._act_id = activity
        self._model.setQuery(self._query.format(self._act_id))

        i    = 0
        cs0  = None
        curr = None
        print(self._model.rowCount())
        while i < self._model.rowCount():
            rec = self._model.record(i)
            cs  = rec.value(2)
            if cs != cs0:
                curr = self.csItem(self._data, [cs])
                self._data.addChild(curr)
                cs0 = cs

            kid = self.csItem(curr, [rec.value(i) for i in range(rec.count())])
            curr.addChild(kid)
            i += 1
        #self.dataChanged.emit(QModelIndex(), QModelIndex())
        self.endResetModel()
        self.layoutChanged.emit()
        print("updated")

    def hasIndex(self, row, col, parent = QModelIndex()):
        if not parent or not parent.isValid():
            print("no parent")
            return row == 0 and col == 0
        else:
            p = parent.internalPointer()
            c = p.getChild(row)
            return c and col < c.nCols()

    def index(self, row, col, parent = QModelIndex()):
        if not self.hasIndex(row, col, parent):
            print("has not")
            return QModelIndex()

        if not parent or not parent.isValid():
            parentItem = self._data
        else:
            parentItem = parent.internalPointer()

        child = parentItem.getChild(row)
        if child:
            return self.createIndex(row, col, child)
        else:
            print("no child")
            return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        child = index.internalPointer()
        parent = child.getParent()

        if parent is self._data:
           return QModelIndex()
        else:
            return self.createIndex(parent.row(), 0, parent)

    def rowCount(self, parent):
        if not parent.isValid():
            parentItem = self._data
        else:
            parentItem = parent.internalPointer()
        return parentItem.nChildren()

    def columnCount(self, parent):
        if not parent.isValid():
            return self._data.nCols()
        else:
            return parent.internalPointer().nCols()#len(self._data[parent.row()][0])

    def data(self, index, role):
        if not index.isValid():
            print("invalid")
            return None#QVariant()

        if not role is Qt.DisplayRole:
            print("not display")
            return None#QVariant()

        return index.internalPointer().getValue(index.column())

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[section]
        else:
            return None#QVariant()

    def hasChildren(self, index):
        if not index.internalPointer():
            return 0
        else:
            return index.internalPointer().nChildren()


class MyApp(QMainWindow):
    def __init__(self):
        super(MyApp, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

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
        
        self.models["csets"] = ChangesetsModel()
        #self.models["csets"].update(self.ui.activitiesTable)
        self.ui.changesetsTable.setModel(self.models["csets"])
        self.ui.activitiesTable.setCurrentIndex(self.models["acts"].index(1, 0))
        self.updateChangesets()
        env = globals().copy()
        loc = locals()
        env.update(loc)
        interact(local=env)

    def printAll(self, idx = None, prefix = ""):
        if not idx:
            idx = self.models["csets"].index(0, 0)
        d = []
        while idx.column() < self.models["csets"].columnCount():
            d.append(self.models["csets"].data(idx, Qt.DisplayRole))
            idx = idx.sibling()


    def updateActivities(self):
        self.models["acts"].setFilter("developer is '{}'".format(self.ui.devComboBox.currentText()))
        self.models["acts"].select()

    def updateChangesets(self):
        idx = self.ui.activitiesTable.currentIndex()
        if idx.isValid():
            idx = self.models["acts"].index(idx.row(), 0)
            actID = self.models["acts"].data(idx)
            self.models["csets"].update(actID)
        #self.ui.changesetsTable.dataChanged()

            
if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MyApp()
    win.show()
    #interact()

    sys.exit(app.exec_())
