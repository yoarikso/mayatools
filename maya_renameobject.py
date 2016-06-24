## Maya Rename Object Dialog
## As seen at: https://www.youtube.com/watch?v=BmhA5jBf8xc
## Johannes Pagwiwoko
## http://yoarikso.tumblr.com

from PyQt4 import QtCore
from PyQt4 import QtGui

import maya.cmds as cmds

import maya.OpenMayaUI as omu
import sip

# helper function
# get a pointer to the Maya Main Window
# use sip to wrap it to what PyQt understands
def getMayaMainWindow():
    ptr = omu.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QtCore.QObject)

class RenamingDialog(QtGui.QDialog):
    
    def __init__(self, parent=getMayaMainWindow()):
        # attached to maya main window so that it stays "On top" as child
        QtGui.QDialog.__init__(self, parent)
        
        self.setWindowTitle("Renaming Dialog")
        self.setFixedSize(250, 200)
        
        self.createLayout()
        self.createConnection()
        
        # force refresh at init to get all selection right at the start
        self.refresh()
        
    def createLayout(self):
        
        # create selection list
        self.selection_list = QtGui.QListWidget()
        
        # create buttons
        self.refresh_button = QtGui.QPushButton("Refresh")
        self.cancel_button = QtGui.QPushButton("Cancel")
        
        # horizontal layout
        button_layout = QtGui.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.cancel_button)
        
        # make layout and attach all layout and itself to it
        # it's always top down: selection will be on top, then button next
        main_layout = QtGui.QVBoxLayout()
        main_layout.setSpacing(5)
        main_layout.setMargin(5)
        
        main_layout.addWidget(self.selection_list)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
            
    def createConnection(self):
        # hook the UI and the logic, event handler
        self.connect(self.refresh_button, QtCore.SIGNAL("clicked()"), self.refresh)
        self.connect(self.cancel_button, QtCore.SIGNAL("clicked()"), self.closeDialog)
        
        # for when current item is changed, setCurrentItem
        self.connect(self.selection_list, 
                     QtCore.SIGNAL("currentItemChanged(QListWidgetItem*, QListWidgetItem*)"),
                     self.setCurrentItem)
        
        # for when item itself has been renamed/changed, update its name
        self.connect(self.selection_list,
                     QtCore.SIGNAL("itemChanged(QListWidgetItem*)"),
                     self.updateName)
    
    def updateSelectionList(self):
        self.selection_list.clear()
        
        # get all selected and add to the list
        selected = cmds.ls(selection=True)
        for sel in selected:
            item = QtGui.QListWidgetItem(sel)
            # make item editable by using flags with appending flag (smart...)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
            self.selection_list.addItem(item)        
        
    def refresh(self):
        self.updateSelectionList()
        
    def closeDialog(self):
        self.close()
        
    # takes in QtWidgetItem
    def setCurrentItem(self, item):
        # if the item exist
        if (item):
            self.currentItemName = str(item.text())
        else:
            self.currentItemName = ""
            
    # takes in QtWidgetItem
    def updateName(self, item):
        # store the newname
        newName = str(item.text())
        
        # if it's the same, we are done
        if newName == self.currentItemName:
            return
        
        # if newname is just empty string ??? 
        if not newName:
            item.setText(self.currentItemName)
            return
        
        # it's a valid new name, apply to scene
        name = cmds.rename(self.currentItemName, newName)
        
        # might aswell apply to the widgetitem aswell
        self.currentItemName = str(name)
        item.setText(self.currentItemName);        
        
# only run in the __main__ namespace
if __name__ == "__main__":
    dialog = RenamingDialog()
    dialog.show()
    


