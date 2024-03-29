from PyQt5.QtWidgets import QMainWindow, QApplication, QAction, QWidgetAction, QFileDialog, QColorDialog, QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QImage, QClipboard
from PyQt5.QtCore import Qt, QSize
from brushsettingslider import BrushSettingSlider
from checkboxsetting import CheckboxSetting
from imagefromweb import ImageFromWeb
from imageviewer import ImageViewer
from drawing import *
import sys


class PaintApplication(QMainWindow):

    def __init__(self):
        super().__init__()

        title = 'Paint Application'

        self.setAcceptDrops(True)
        self.setWindowTitle(title)

        self.imageViewer = ImageViewer()
        self.imageViewer.update.connect(self.updateSize)
        self.hdr = {'User-Agent': 'Mozilla/5.0'}
        self.setStyleSheet("QWidget {background-color: rgb(239, 235, 230);}")
        self.clipboardImage = None
        QApplication.clipboard().dataChanged.connect(self.copy)

        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu("File")
        modify = mainMenu.addMenu("Modify")
        brushStyle = mainMenu.addMenu("Brush Style")
        brushSetting = mainMenu.addMenu("Brush Setting")
        colorPicker = QAction('Color Picker', self)
        drawingMenu = mainMenu.addMenu("Drawing")
        imageSearch = QAction('Image Search', self)

        fileMenuSetting = [{'name': 'Save', 'shortcut': 'Ctrl+S', 'callback': self.save},
                           {'name': 'Load', 'shortcut': 'Ctrl+O', 'callback': self.load},
                           {'name': 'Clear', 'shortcut': 'Ctrl+C', 'callback': self.imageViewer.clear},
                           {'name': 'Undo', 'shortcut': 'Ctrl+Z', 'callback': self.imageViewer.undoAndRedo},
                           {'name': 'Redo', 'shortcut': 'Ctrl+Shift+Z', 'callback': self.imageViewer.undoAndRedo},
                           {'name': 'Paste', 'shortcut': 'Ctrl+V', 'callback': self.paste}]

        for setting in fileMenuSetting:
            action = QAction(setting['name'], self)
            action.setShortcut(setting['shortcut'])
            action.triggered.connect(setting['callback'])
            fileMenu.addAction(action)

        modifyMenuSetting = [{'name': 'Rotate 90', 'shortcut': 'Ctrl+R', 'callback': self.imageViewer.rotateImage},
                             {'name': 'Rotate 180', 'shortcut': None, 'callback': self.imageViewer.rotateImage},
                             {'name': 'Rotate 270', 'shortcut': None, 'callback': self.imageViewer.rotateImage},
                             {'name': 'Flip Vertically', 'shortcut': 'Ctrl+Down', 'callback': self.imageViewer.flip},
                             {'name': 'Flip Horizontally', 'shortcut': 'Ctrl+Right', 'callback': self.imageViewer.flip},
                             {'name': 'Invert Color', 'shortcut': 'Ctrl+I', 'callback': self.imageViewer.invertColor}]

        for setting in modifyMenuSetting:
            action = QAction(setting['name'], self)
            if setting['shortcut']:
                action.setShortcut(setting['shortcut'])
            action.triggered.connect(setting['callback'])
            modify.addAction(action)

        brushMenuSetting = [{'name': 'Pen', 'shortcut': 'Ctrl+P'},
                            {'name': 'Fountain Pen', 'shortcut': 'Ctrl+F'},
                            {'name': 'Spray', 'shortcut': 'Ctrl+Y'},
                            {'name': 'Paint Bucket', 'shortcut': 'Ctrl+B'},
                            {'name': 'Eraser', 'shortcut': 'Ctrl+E'},
                            {'name': 'Move', 'shortcut': 'Ctrl+M'}]

        for setting in brushMenuSetting:
            action = QAction(setting['name'], self)
            action.setShortcut(setting['shortcut'])
            action.triggered.connect(self.imageViewer.changeBrush)
            brushStyle.addAction(action)

        drawingMenu.aboutToHide.connect(self.getDrawingOption)
        optionSettingAction = QWidgetAction(self)
        checkboxSetting = CheckboxSetting('Full Fill')
        optionSettingAction.setDefaultWidget(checkboxSetting)
        drawingMenu.addAction(optionSettingAction)
        self.drawingOption = checkboxSetting

        figureSetting = [{'name': 'Rectangle', 'shortcut': 'Shift+R'},
                         {'name': 'Circle', 'shortcut': 'Shift+C'},
                         {'name': 'Line', 'shortcut': 'Shift+L'}]

        for setting in figureSetting:
            action = QAction(setting['name'], self)
            action.setShortcut(setting['shortcut'])
            action.triggered.connect(self.imageViewer.changeBrush)
            drawingMenu.addAction(action)

        sliderSetting = [{'name': 'Brush Size', 'min': 1, 'max': 200, 'base': 2},
                         {'name': 'Brush Opacity', 'min': 1, 'max': 100, 'base': 100}]

        brushSetting.aboutToHide.connect(self.getSetting)
        self.settingWidget = {}
        for setting in sliderSetting:
            settingPickAction = QWidgetAction(self)
            settingWidget = BrushSettingSlider(setting['min'], setting['max'], setting['base'], setting['name'])
            settingPickAction.setDefaultWidget(settingWidget)
            self.settingWidget[setting['name']] = settingWidget
            brushSetting.addAction(settingPickAction)

        colorPicker.triggered.connect(self.pickColor)
        mainMenu.addAction(colorPicker)

        imageSearch.triggered.connect(self.searchImage)
        mainMenu.addAction(imageSearch)

        image = self.imageViewer.image()
        self.statusBar = QLabel('Width=' + str(image.width()) + ', Height=' + str(image.height()) + ', (0, 0)')
        self.imageViewer.mouseMoved.connect(self.updateStatus)

        vBox = QVBoxLayout()
        vBox.addWidget(self.imageViewer)
        vBox.addWidget(self.statusBar)

        widget = QWidget()
        widget.setLayout(vBox)
        self.setCentralWidget(widget)
        self.updateSize()

    def save(self):
        filePath, type = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG(*.png);;JPEG(*.jpg *.jpeg);;All Files(*.*) ")
        if filePath == "":
            return
        image = self.imageViewer.image()
        if '.' not in filePath:
            filePath += '.png'
        image.save(filePath)

    def load(self):
        filePath, type = QFileDialog.getOpenFileName(self, "Import Image", "", "PNG(*.png);;JPEG(*.jpg *.jpeg);;All Files(*.*) ")
        if filePath == "":
            return
        newImage = QImage(filePath)
        self.imageViewer.setNewImage(newImage)

    def copy(self):
        self.clipboardImage = QApplication.clipboard().image(QClipboard.Clipboard)

    def paste(self):
        if self.clipboardImage and not self.clipboardImage.isNull():
            self.imageViewer.setNewImage(self.clipboardImage)

    def getDrawingOption(self):
        fullFill = self.drawingOption.getSetting()
        self.imageViewer.setFullFill(fullFill)

    def getSetting(self):
        self.imageViewer.setBrushSize(self.settingWidget['Brush Size'].getValue())
        self.imageViewer.setBrushOpacity(self.settingWidget['Brush Opacity'].getValue())

    def pickColor(self):
        self.imageViewer.setBrushColor(QColorDialog.getColor())

    def searchImage(self):
        imgSearchDialog = ImageFromWeb()
        imgSearchDialog.exec_()
        searchedImage = imgSearchDialog.image
        if searchedImage:
            self.image = searchedImage
            while self.image.width() >= 1920 or self.image.height() >= 1080:
                self.image = self.image.scaled(self.image.width() // 2, self.image.height() // 2, Qt.KeepAspectRatio)
            self.imageViewer.setNewImage(self.image)

    def updateSize(self):
        if not self.isMaximized():
            self.resize(self.sizeHint())

    def updateStatus(self, x, y):
        image = self.imageViewer.image()
        width = str(image.width())
        height = str(image.height())
        self.statusBar.setText('Width=' + width + ', Height=' + height + ', (' + str(x) + ', ' + str(y) + ')')

    def sizeHint(self):
        screen = self.imageViewer.image()
        width, height = screen.width(), screen.height()
        return QSize(width + 24, height + 65)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PaintApplication()
    window.show()
    app.exec()