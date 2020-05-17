from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    file_path = ""
    level = ""  # 16
    patch_size = ""  # 1080

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(591, 353)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setGeometry(QtCore.QRect(240, 250, 118, 23))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(220, 103, 59, 16))
        self.label_2.setObjectName("label_2")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(220, 51, 29, 16))
        self.label.setObjectName("label")
        self.lineEditLevel = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEditLevel.setGeometry(QtCore.QRect(220, 74, 137, 22))
        self.lineEditLevel.setObjectName("lineEditLevel")
        self.pushButtonBrowse = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonBrowse.setGeometry(QtCore.QRect(220, 155, 141, 28))
        self.pushButtonBrowse.setObjectName("pushButtonBrowse")
        self.lineEditPatchSize = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEditPatchSize.setGeometry(QtCore.QRect(220, 126, 137, 22))
        self.lineEditPatchSize.setObjectName("lineEditPatchSize")
        self.pushButtonMakePatches = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonMakePatches.setGeometry(QtCore.QRect(180, 190, 221, 51))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.pushButtonMakePatches.setFont(font)
        self.pushButtonMakePatches.setObjectName("pushButtonMakePatches")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.centralwidget.setStyleSheet("QToolButton\n"
                                         "{\n"
                                         "    outline:0px;\n"
                                         "    background-color:rgb(143, 143, 143);\n"
                                         "    color: rgb(255, 255, 255);\n"
                                         "    border-width:2px;\n"
                                         "    border-style:solid;\n"
                                         "    border-color: rgb(127, 127, 127);\n"
                                         "    border-radius:5px;\n"
                                         "}\n"
                                         "QLineEdit\n"
                                         "{\n"
                                         "    border-width:2px;\n"
                                         "    border-style:solid;\n"
                                         "    border-color: rgb(127, 127, 127);\n"
                                         "    outline:0px;\n"
                                         "    background-color:rgb(255, 255, 255);\n"
                                         "    padding-right: 40px;\n"
                                         "}\n"
                                         "")


        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label_2.setText(_translate("MainWindow", "Patch Size"))
        self.label.setText(_translate("MainWindow", "Level"))
        self.pushButtonBrowse.setText(_translate("MainWindow", "Browse"))
        self.pushButtonMakePatches.setText(_translate("MainWindow", "Make Patches"))

        self.pushButtonBrowse.clicked.connect(self.browse)
        self.pushButtonMakePatches.clicked.connect(self.makePatches)


    def browse(self):
        from PyQt5.QtWidgets import QFileDialog

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(MainWindow, "QFileDialog.getOpenFileName()", "",
                                                  "All Files (*);;Python Files (*.py)", options=options)
        if fileName == "":
            self.displayErrorMessage("File Not Chosen")

        elif not fileName.endswith(".svs"):
            self.displayErrorMessage(".svs File Not Chosen")
        else:
            self.file_path = fileName

    def displayErrorMessage(self, text="Error", informative_text="", window_title="Error"):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setText(text)
        msg.setInformativeText(informative_text)
        msg.setWindowTitle(window_title)
        msg.exec_()

    def makePatches(self):
        level = self.lineEditLevel.text()
        patch_size = self.lineEditPatchSize.text()
        file_path = self.file_path
        if level is not "" and patch_size is not "" and file_path is not "":
            self.level = int(level)
            self.patch_size = int(patch_size)

            from threading import Thread
            Thread(target=self.createPatches).start()

        else:
            self.displayErrorMessage("Enter Required Fields")

    def createPatches(self):
        import save_patches
        import os

        file_dir = os.path.dirname(self.file_path)
        file_name = os.path.basename(self.file_path)

        # Patches Directory Path
        db_location = file_dir + "/"+file_name[:-4]+"_patches_"+str(self.patch_size)+"_"+str(self.level)+"/"
        if not os.path.isdir(db_location): # If no directory create one
            mode = 0o666
            os.mkdir(db_location, mode)

        patch = save_patches.Patch(self.file_path, db_location)
        patch.print_tile_dimensions(self.patch_size)

        self.progressBar.setValue(0)
        patch.sample_and_store_patches(self.patch_size, self.level, self.progressBar)
        self.progressBar.setValue(100)
        print("Finsihed...")


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())


