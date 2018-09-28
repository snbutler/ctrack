#!/usr/bin/env python3

import sys
import sqlite3 as sqlite

from code            import interact
from PyQt5           import uic
from PyQt5.QtCore    import QAbstractTableModel, Qt, QVariant
from PyQt5.QtWidgets import QMainWindow, QApplication

Ui_MainWindow, QtBaseClass = uic.loadUiType('ctrack.ui')

db_name = "test.db"
# act:   id, name, description, closed, user_status, developer
# cs:    id, regime, build, name, versioning, status, activity_id
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
        #print(role, Qt.DisplayRole)
        if role in (Qt.DisplayRole, Qt.EditRole):
            return self.activities[index.row()][index.column()+1]
        else:
            return QVariant()

    def headerData(self, section, orientation, role):
        #print(orientation, role)
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            print("yes")
            return self.header[section]
        else:
            return QVariant()



class MyApp(QMainWindow):
    def __init__(self):
        super(MyApp, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        #self.ui.calc_tax_button.clicked.connect(self.CalculateTax)

        self.db = sqlite.connect(db_name)
        cursor  = self.db.cursor()

        cursor.execute("SELECT id, name, description from activities")
        res = cursor.fetchall()
        
        activityModel = ActivityTableModel(res)
        self.ui.activitiesTable.setModel(activityModel)
        #for x in dir(self.ui):
            #print(x)


"""
def CalculateTax(self):
    price = int(self.ui.price_box.toPlainText())
    tax = (self.ui.tax_rate.value())
    total_price = price + ((tax / 100) * price)
    total_price_string = ‘The total price with tax is: ‘ + str(total_price)
    self.ui.results_window.setText(total_price_string)
"""

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MyApp()
    win.show()
    #interact()

    sys.exit(app.exec_())

