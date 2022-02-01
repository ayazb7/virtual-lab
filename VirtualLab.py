# Ayaz Baig NEA Project
import os

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
import matplotlib
import math
import numpy as np

matplotlib.use('Qt5Agg')

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


# parent window class, defines the basic attributes for each window
class Window(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)

        self._x = 200
        self._y = 100
        self._height = 700
        self._width = 1000

        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)

    def _initUI(self):
        self.setWindowTitle("Virtual Lab")
        self.setGeometry(self._x, self._y, self._width, self._height)


# Main menu window, which is a subclass of the parent window class
# Includes two buttons which when pressed opens the relevant window
class MenuWindow(Window):
    def __init__(self):
        super(MenuWindow, self).__init__()

        self._initUI()

    def _initUI(self):
        super(MenuWindow, self)._initUI()
        self.setStyleSheet("background-color: white;")

        self.layout = QGridLayout()
        self.layout.setSpacing(30)

        self.label = QLabel(self)
        pix = QPixmap(resource_path("./img/logo2.png"))
        self.label.setPixmap(pix)

        # Each button given a PAG type attribute so when pressed the attribute is sent to the animation window
        pagButton1 = "Vertical"
        pagButton2 = "Planck"

        self.__option1Button = self.__initMenuButton(resource_path("./img/manualButton.png"), pagButton1)
        self.__option2Button = self.__initMenuButton(resource_path("./img/plancksConstant.png"), pagButton2)

        self.layout.addWidget(self.label, 0, 1)
        self.layout.addWidget(self.__option1Button, 1, 0)
        self.layout.addWidget(self.__option2Button, 1, 2)

        self.layout.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.centralWidget.setLayout(self.layout)
        self.show()

    # Function which creates the button, takes the PAG type and the button image as parameters
    def __initMenuButton(self, iconPath, pagType):
        button = QPushButton()
        button.clicked.connect(lambda: self.__windowClick(pagType))
        button.setIconSize(QSize(200, 150))
        button.setIcon(QIcon(iconPath))
        button.setFlat(True)

        return button

    def __windowClick(self, pagType):
        self.window = ChoiceWindow(pagType)
        self.close()
        self.window.show()


# Choice window displays window which gives the user an option to show a sample animation or to let them do the practical themselves
class ChoiceWindow(Window):
    def __init__(self, pagType):
        super(ChoiceWindow, self).__init__()

        self.__pagType = pagType
        self._initUI()

    def _initUI(self):
        super(ChoiceWindow, self)._initUI()
        self.setStyleSheet("background-color: white;")

        self.layout = QGridLayout()
        self.layout.setSpacing(30)

        self.label = QLabel(self)
        pix = QPixmap(resource_path("./img/logo2.png"))
        self.label.setPixmap(pix)

        self.__choice1 = self.__initChoiceButton(resource_path("./img/manualChoice1.png"), 1, self.__pagType)
        self.__choice2 = self.__initChoiceButton(resource_path("./img/manualChoice2.png"), 2, self.__pagType)

        self.layout.addWidget(self.label, 0, 1)
        self.layout.addWidget(self.__choice1, 1, 0)
        self.layout.addWidget(self.__choice2, 1, 2)
        self.layout.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.centralWidget.setLayout(self.layout)

    def __initChoiceButton(self, iconPath, choice, pagType):
        button = QPushButton()
        button.clicked.connect(lambda: self.windowClick(pagType, choice))
        button.setIconSize(QSize(200, 150))
        button.setIcon(QIcon(iconPath))
        button.setFlat(True)

        return button

    def windowClick(self, pagType, choice):
        if choice == 1:
            self.window = AnimationWindow(pagType, choice)
            self.close()
            self.window.show()
        else:
            self.window = DIYWindow(pagType, choice)
            self.close()
            self.window.show()


# Creates the animation view where the user can see all the graphics includes (e.g. the ball, animations of the ball etc.)
class AnimationView(QGraphicsView):
    def __init__(self):
        super().__init__()

        self._initUI()

    def _initUI(self):
        self.scene = QGraphicsScene(self)

    def drawBackground(self, painter, rect):
        sceneRect = self.scene.sceneRect()
        bg = QPixmap(resource_path("./img/background2.png"))
        bgRect = QRectF(bg.rect())
        painter.drawPixmap(sceneRect, bg, bgRect)


# Animation window where the animations are run
class AnimationWindow(Window):
    def __init__(self, pagType, choice):
        super(AnimationWindow, self).__init__()

        self.pagType = pagType
        self.choice = choice
        self.speed = 10
        self._initUI()

    # Creates the UI by creating the necessary buttons and the main graphics view where the animation is displayed
    def _initUI(self):
        super(AnimationWindow, self)._initUI()

        self.calcWindow = False
        self.animWindow = False

        # Main layout is a QHBoxLayout
        # Also includes several sub-layouts which are added to the main layout
        self.layout = QHBoxLayout()
        self.buttonLayout = QVBoxLayout()
        self.vLayout = QVBoxLayout()

        self.stack = QStackedWidget()
        self.graphicsView = AnimationView()
        self.stack.addWidget(self.graphicsView)
        self.vLayout.addWidget(self.stack)

        self.textBox = QLineEdit()
        self.textBox.setReadOnly(True)
        self.textBox.setAlignment(Qt.AlignCenter)
        self.textBox.setFixedSize(800, 80)
        self.textBox.setFont(QFont("Arial", 20))

        self.nextButton = self.__initArrow(resource_path("./img/nextArrow.png"))
        self.nextButton.clicked.connect(lambda: self.nextStep(self.pagType))
        self.nextButton.setIconSize(QSize(100, 80))

        self.prevButton = self.__initArrow(resource_path("./img/prevArrow.png"))
        self.prevButton.clicked.connect(lambda: self.prevStep(self.pagType))
        self.prevButton.setIconSize(QSize(100, 80))

        self.hLayout = QHBoxLayout()
        self.hLayout.addWidget(self.prevButton)
        self.hLayout.addWidget(self.textBox)
        self.hLayout.addWidget(self.nextButton)
        self.vLayout.addLayout(self.hLayout)

        self.layout.addLayout(self.vLayout)

        self.startButton = self.buttons("Start Example")
        self.startButton.clicked.connect(lambda: self.startAnimation(self.pagType, self.choice))

        editButton = self.buttons("Edit Animation")
        editButton.clicked.connect(self.editAnimation)

        calcButton = self.buttons("Calculate")
        calcButton.clicked.connect(lambda: self.calculations(self.pagType))

        if self.pagType != "Planck":
            self.changeButton = self.buttons("Change Type")
            self.changeButton.clicked.connect(self.changeType)

        exitButton = self.buttons("Exit")
        exitButton.clicked.connect(self.exitToMenu)

        self.layout.addLayout(self.buttonLayout)
        self.centralWidget.setLayout(self.layout)

    def __initArrow(self, iconPath):
        button = QPushButton()
        button.setIcon(QIcon(iconPath))
        button.setFlat(True)

        return button

    # Subroutine is run when the start animation button is pressed, which then starts the relevant animation depending on the PAG type
    def startAnimation(self, pagType, choice):
        self.animWindow = True
        self.calcWindow = False
        self.textBox.setFont(QFont("Arial", 20))
        if pagType == "Vertical":
            if self.startButton.text() == "Start Example":
                self.animView = VerticalFall(self.startButton, choice)
                self.graphicsView.scene.setSceneRect(-600, -20, 1100, 742)
                self.graphicsView.setScene(self.animView)
                self.stack.setCurrentWidget(self.graphicsView)
                self.animView.still(1, 250, "Distance = 0.5m")
                self.startButton.setText("Start Animation")
                self.textBox.setText("Measure the Distance of the Drop")
            elif self.startButton.text() == "Pause Animation" and (
                    self.animView.getAnimState() == 2 or self.animView.getAnimState() == 4):
                self.animView.pauseAnims()
                self.startButton.setText("Resume Animation")
            elif self.startButton.text() == "Resume Animation" and (
                    self.animView.getAnimState() == 2 or self.animView.getAnimState() == 4):
                self.animView.resumeAnims()
                self.startButton.setText("Pause Animation")
            elif self.startButton.text() == "Start Animation" and (
                    self.animView.getAnimState() == 2 or self.animView.getAnimState() == 4):
                self.animView.startAnims()
                self.startButton.setText("Pause Animation")
        elif pagType == "Ramp":
            if self.startButton.text() == "Start Example":
                self.animView = RampFall(self.startButton, choice)
                self.graphicsView.scene.setSceneRect(-400, -279, 1150, 700)
                self.graphicsView.setScene(self.animView)
                self.stack.setCurrentWidget(self.graphicsView)
                self.animView.still(1, 200, 83, "Ramp Length = 0.5m, θ = 30°")
                self.startButton.setText("Start Animation")
                self.textBox.setText("Measure the Distance of the Drop along the ramp")
            elif self.startButton.text() == "Pause Animation" and (
                    self.animView.getAnimState() == 2 or self.animView.getAnimState() == 4):
                self.animView.pauseAnims()
                self.startButton.setText("Resume Animation")
            elif self.startButton.text() == "Resume Animation" and (
                    self.animView.getAnimState() == 2 or self.animView.getAnimState() == 4):
                self.animView.resumeAnims()
                self.startButton.setText("Pause Animation")
            elif self.startButton.text() == "Start Animation" and (
                    self.animView.getAnimState() == 2 or self.animView.getAnimState() == 4):
                self.animView.startAnims()
                self.startButton.setText("Pause Animation")
        elif pagType == "Planck":
            if self.startButton.text() == "Start Example":
                self.animView = PlanckAnim(self.startButton, choice)
                self.graphicsView.setScene(self.animView)
                self.stack.setCurrentWidget(self.graphicsView)
                self.animView.still(1, 700)
                self.startButton.setText("Start Animation")
                self.textBox.setText("Set up Circuit with LED in series with a variable resistor")
            elif self.startButton.text() == "Pause Animation" and (
                    self.animView.getAnimState() == 2 or self.animView.getAnimState() == 3):
                self.animView.pauseAnims()
                self.startButton.setText("Resume Animation")
            elif self.startButton.text() == "Resume Animation" and (
                    self.animView.getAnimState() == 2 or self.animView.getAnimState() == 3):
                self.animView.resumeAnims()
                self.startButton.setText("Pause Animation")
            elif self.startButton.text() == "Start Animation" and (
                    self.animView.getAnimState() == 2 or self.animView.getAnimState() == 3):
                self.animView.startAnims()
                self.startButton.setText("Pause Animation")

    # Edit animation subroutine is executed when relevant button is pressed, displays a dialog box where the user can change the speed of the animation
    def editAnimation(self):
        self.options = QDialog(self)
        self.options.setWindowTitle("Change Practical Variables")

        dlgLayout = QVBoxLayout()

        groupBox = QGroupBox("Edit")
        grpLayout = QGridLayout()

        label = QLabel("Animation Speed:")
        grpLayout.addWidget(label, 0, 0)

        speedSlider = QSlider(Qt.Horizontal)
        speedSlider.setMinimum(1)
        speedSlider.setMaximum(10)
        speedSlider.setValue(self.speed)
        speedSlider.setTickPosition(QSlider.TicksBelow)
        speedSlider.setTickInterval(1)
        grpLayout.addWidget(speedSlider, 0, 1)

        grpLayout.addWidget(label, 1, 0)

        groupBox.setLayout(grpLayout)

        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        buttonBox = QDialogButtonBox(buttons)
        buttonBox.accepted.connect(self.options.accept)
        buttonBox.rejected.connect(self.options.reject)

        dlgLayout.addWidget(groupBox)
        dlgLayout.addWidget(buttonBox)

        self.options.setLayout(dlgLayout)
        self.options.exec_()

        self.speed = speedSlider.value()

        if self.animWindow:
            self.animView.changeSpeed(self.speed)

    # Displays the relevant calculation box, which replaces the graphics view widget
    def calculations(self, pagType):
        if pagType == "Vertical":
            self.calcWindow = True
            self.animWindow = False
            self.startButton.setText("Start Example")
            self.calcBox = CalculationVertical()
            self.stack.addWidget(self.calcBox)
            self.stack.setCurrentWidget(self.calcBox)
            self.textBox.setFont(QFont("Arial", 14))
            self.textBox.setText(
                "Repeat experiment multiple times at different heights and record all measurements in a table")
        elif pagType == "Ramp":
            self.calcWindow = True
            self.animWindow = False
            self.startButton.setText("Start Example")
            self.calcBox = CalculationRamp()
            self.stack.addWidget(self.calcBox)
            self.stack.setCurrentWidget(self.calcBox)
            self.textBox.setFont(QFont("Arial", 18))
            self.textBox.setText("Diagram shows the forces acting on the ball")
        elif pagType == "Planck":
            self.calcWindow = True
            self.animWindow = False
            self.startButton.setText("Start Example")
            self.calcBox = CalculationPlanck()
            self.stack.addWidget(self.calcBox)
            self.stack.setCurrentWidget(self.calcBox)
            self.textBox.setFont(QFont("Arial", 18))
            self.textBox.setText("Record measured P.d. in a table")

    # Runs the next step of the animation or the calculation process
    def nextStep(self, pagType):
        if pagType == "Vertical":
            if not self.calcWindow and self.animWindow:
                if self.animView.getAnimState() == 1:
                    self.textBox.setText("Drop Ball and Start Timer")
                    self.startButton.setText("Start Animation")
                    self.animView.drop(250, 2, 320, "Distance = 0.5m")
                elif self.animView.getAnimState() == 2:
                    self.animView.still(3, 0, "Distance = 1m")
                    self.textBox.setText("Repeat at different heights")
                elif self.animView.getAnimState() == 3:
                    self.animView.drop(0, 4, 450, "Distance = 1m")
                    self.startButton.setText("Start Animation")
                    self.textBox.setText("Drop Ball from second height and start Timer")
            elif not self.animWindow and self.calcWindow:
                if not self.calcBox.graphShown:
                    self.calcBox.graph()
                    self.textBox.setText(
                        "Draw a graph of Distance (y axis) against time\u00b2 (x axis), with a line of best fit")
                elif not self.calcBox.workingOutShown:
                    self.calcBox.workingOut()
                    self.textBox.setText("Calculate the value of Freefall using the graph")
        elif pagType == "Ramp":
            if not self.calcWindow and self.animWindow:
                if self.animView.getAnimState() == 1:
                    self.textBox.setText("Roll Ball and Start Timer")
                    self.animView.drop(200, 83, 2, 452, "Ramp Length = 0.5m, θ = 30°")
                elif self.animView.getAnimState() == 2:
                    self.textBox.setText("Repeat at another length up the Ramp")
                    self.startButton.setText("Start Animation")
                    self.animView.still(3, 395, -30, "Ramp Length = 1m, θ = 30°")
                elif self.animView.getAnimState() == 3:
                    self.animView.drop(395, -30, 4, 640, "Ramp Length = 1m, θ = 30°")
                    self.textBox.setText("Roll Ball from second length and start Timer")
            elif not self.animWindow and self.calcWindow:
                if not self.calcBox.getWorkingOut1Shown():
                    self.calcBox.showWorking1()
                elif not self.calcBox.getWorkingOut2Shown():
                    self.calcBox.showWorking2()
        elif pagType == "Planck":
            if not self.calcWindow and self.animWindow:
                if self.animView.getAnimState() == 1:
                    self.textBox.setText("Turn down resistance and measure voltage when LED lights up")
                    self.animView.slide(2)
                elif self.animView.getAnimState() == 2:
                    self.textBox.setText("Repeat with a different coloured LED")
                    self.animView.still(3, 450)
            elif not self.animWindow and self.calcWindow:
                if not self.calcBox.getGraphShown():
                    self.calcBox.drawGraph()
                    self.textBox.setText("Draw a graph of Voltage against 1/λ")
                elif not self.calcBox.getWorkingOutShown():
                    self.calcBox.workingOut()
                    self.textBox.setText("Calculate Planck's Constant using the gradient")

    # Runs the previous step of the animation or the calculation process
    def prevStep(self, pagType):
        if pagType == "Vertical":
            if not self.calcWindow and self.animWindow:
                if self.animView.getAnimState() == 2:
                    self.animView.still(1, 250, "Distance = 0.5m")
                    self.startButton.setText("Start Animation")
                    self.textBox.setText("Measure the Distance of the Drop")
                elif self.animView.getAnimState() == 3:
                    self.animView.drop(250, 2, 320, "Distance = 0.5m")
                    self.textBox.setText("Drop Ball and Start Timer")
                elif self.animView.getAnimState() == 4:
                    self.animView.still(3, 0, "Distance = 1m")
                    self.textBox.setText("Repeat at different heights")
            elif not self.animWindow and self.calcWindow:
                if self.calcBox.getGraphShown() and not self.calcBox.getWorkingOutShown():
                    self.calcBox.removeGraph()
                    self.textBox.setText(
                        "Repeat experiment multiple times at different heights and record all measurements in a table")
                elif self.calcBox.getWorkingOutShown():
                    self.calcBox.removeWorking()
                    self.textBox.setText(
                        "Draw a graph of Distance (y axis) against time\u00b2 (x axis), with a line of best fit")
        elif pagType == "Ramp":
            if not self.calcWindow and self.animWindow:
                if self.animView.getAnimState() == 2:
                    self.textBox.setText("Measure the Distance of the Drop along the ramp")
                    self.startButton.setText("Start Animation")
                    self.animView.still(1, 200, 83, "Ramp Length = 0.5m, θ = 30°")
                elif self.animView.getAnimState() == 3:
                    self.textBox.setText("Roll Ball and Start Timer")
                    self.animView.drop(200, 83, 2, 452, "Ramp Length = 0.5m, θ = 30°")
                elif self.animView.getAnimState() == 4:
                    self.textBox.setText("Repeat at another length up the Ramp")
                    self.startButton.setText("Start Animation")
                    self.animView.still(3, 395, -30, "Ramp Length = 1m, θ = 30°")
            elif not self.animWindow and self.calcWindow:
                if self.calcBox.getWorkingOut1Shown() and not self.calcBox.getWorkingOut2Shown():
                    self.calcBox.removeWorking1()
                elif self.calcBox.getWorkingOut2Shown():
                    self.calcBox.removeWorking2()
        elif pagType == "Planck":
            if not self.calcWindow and self.animWindow:
                if self.animView.getAnimState() == 2:
                    self.textBox.setText("Set up Circuit with LED in series with a variable resistor")
                    self.animView.still(1, 700)
                elif self.animView.getAnimState() == 3:
                    self.animView.still(2, 700)
                    self.textBox.setText("Turn down resistance and measure voltage when LED lights up")
            elif self.calcWindow and not self.animWindow:
                if self.calcBox.getGraphShown() and not self.calcBox.getWorkingOutShown():
                    self.calcBox.removeGraph()
                    self.textBox.setText("Record measured P.d. in a table")
                elif self.calcBox.getWorkingOutShown():
                    self.calcBox.removeWorking()
                    self.textBox.setText("Draw a graph of Voltage against 1/λ")

    # Displays a dialog box with 2 PAG options which changes the PAG type variable
    def changeType(self):
        self.changeBox = QDialog(self)
        self.changeBox.setWindowTitle("Change Type")

        dlgLayout = QVBoxLayout()

        groupBox = QGroupBox("Choose")
        grpLayout = QHBoxLayout()

        if self.pagType == "Vertical" or self.pagType == "Ramp":
            button1 = QRadioButton("Vertical")
            button2 = QRadioButton("Ramp")

        grpLayout.addWidget(button1)
        grpLayout.addWidget(button2)
        groupBox.setLayout(grpLayout)

        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        buttonBox = QDialogButtonBox(buttons)
        buttonBox.accepted.connect(self.changeBox.accept)
        buttonBox.rejected.connect(self.changeBox.reject)

        dlgLayout.addWidget(groupBox)
        dlgLayout.addWidget(buttonBox)

        self.changeBox.setLayout(dlgLayout)

        self.changeBox.exec_()

        if button1.isChecked():
            self.pagType = button1.text()
            self.startButton.setText("Start Example")
            self.animWindow = False
            self.textBox.setText(None)
            self.graphicsView.setScene(None)
            self.stack.setCurrentWidget(self.graphicsView)
        elif button2.isChecked():
            self.pagType = button2.text()
            self.startButton.setText("Start Example")
            self.animWindow = False
            self.textBox.setText(None)
            self.graphicsView.setScene(None)
            self.stack.setCurrentWidget(self.graphicsView)

    def buttons(self, buttonText):
        button = QPushButton(buttonText)
        button.setFixedSize(200, 130)
        button.setFont(QFont("Arial", 12))
        self.buttonLayout.addWidget(button)

        return button

    def exitToMenu(self):
        self.window = MenuWindow()
        self.close()
        self.window.show()


# Creates a new window which has a different layout including some widgets to allow the user to have control over the practical
class DIYWindow(Window):
    def __init__(self, pagType, choice):
        super(DIYWindow, self).__init__()

        self.pagType = pagType
        self.choice = choice
        self.speed = 10
        self.n = 0
        self._initUI()

    def _initUI(self):
        super(DIYWindow, self)._initUI()
        self.setGeometry(200, 100, 1350, 650)

        self.animWindow = False
        self.calcWindow = False

        self.mainLayout = QHBoxLayout()
        self.vLayout = QVBoxLayout()
        self.hLayout = QHBoxLayout()
        self.vLayout2 = QGridLayout()
        self.buttonLayout = QVBoxLayout()
        self.buttonLayout.setAlignment(Qt.AlignVCenter)

        self.startButton = self.buttons("Start Practical")
        self.editButton = self.buttons("Edit Animation")
        self.calcButton = self.buttons("Calculate")
        if self.pagType != "Planck":
            self.changeButton = self.buttons("Change Type")
            self.changeButton.clicked.connect(self.changeType)
        self.exitButton = self.buttons("Exit")

        self.stack = QStackedWidget()
        self.graphicsView = AnimationView()
        self.stack.addWidget(self.graphicsView)
        self.hLayout.addWidget(self.stack)

        self.vLayout2.setAlignment(Qt.AlignVCenter)

        # Table widget used to allow user to note down any measurements taken
        self.table = QTableWidget()
        self.table.setRowCount(7)
        self.table.setColumnCount(5)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        for i in range(7):
            for j in range(5):
                item = QTableWidgetItem("")
                self.table.setItem(i, j, item)
        self.table.setFixedSize(425, 187)
        self.tableEmpty = True
        self.vLayout2.addWidget(self.table, 1, 0)

        if self.pagType != "Planck":
            headers = ["Distance (m)", "1: time\u00b2 (s\u00b2)", "2: time\u00b2 (s\u00b2)", "3: time\u00b2 (s\u00b2)",
                       "Average time\u00b2 (s\u00b2)"]
        else:
            headers = ["Wavelength (x 10^-9 m)", "1: Voltage (V)", "2: Voltage (V)", "3: Voltage (V)",
                       "Average Voltage (V))"]
            self.table.setFixedSize(498, 188)

        self.table.setHorizontalHeaderLabels(headers)
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()

        self.hLayout.addLayout(self.vLayout2)
        self.vLayout.addLayout(self.hLayout)

        self.textBox = QLineEdit()
        self.textBox.setReadOnly(True)
        self.textBox.setAlignment(Qt.AlignCenter)
        self.textBox.setFixedSize(1150, 80)
        self.textBox.setFont(QFont("Arial", 20))
        self.vLayout.addWidget(self.textBox)

        self.startButton.clicked.connect(lambda: self.startAnimation(self.pagType, self.choice))
        self.calcButton.clicked.connect(lambda: self.calculations(self.pagType))
        self.exitButton.clicked.connect(self.exitToMenu)
        self.editButton.clicked.connect(self.editAnimation)

        self.mainLayout.addLayout(self.vLayout)
        self.mainLayout.addLayout(self.buttonLayout)

        self.centralWidget.setLayout(self.mainLayout)

    def buttons(self, buttonText):
        button = QPushButton(buttonText)
        button.setFixedSize(200, 130)
        button.setFont(QFont("Arial", 12))
        self.buttonLayout.addWidget(button)

        return button

    # Procedure is called when a value is entered into the Line Edit widget
    def firstVariableEntered(self):
        try:
            if self.pagType != "Planck":
                self.errorLabel.setText("Tip: Measure Height from the bottom of the ball")
                num = float(self.inputBox.text())
            else:
                self.errorLabel = QLabel("Tip: Enter Wavelength in x 10^-9 nanometres (nm)")
                num = float(self.inputBox.text())

            self.comboBox.addItem(str(num))
            self.inputBox.setText("")
            item = QTableWidgetItem(str(num))
            self.table.setItem(self.n, 0, item)
            self.n += 1
            self.tableEmpty = False
        except:
            if self.pagType != "Planck":
                self.errorLabel.setText("Error: Incorrect form entered, Enter height as a number in metres")
            else:
                self.errorLabel.setText(
                    "Error: Incorrect form entered, Enter wavelength as a number in x 10^-9 nanometres")

    def secondVariableEntered(self):
        try:
            if self.pagType != "Planck":
                self.errorLabel2.setText("Tip: Press Enter to add time\u00b2 (s\u00b2) into the table")
                time = float(self.inputBox2.text())
                calc = round(time ** 2, 3)
            else:
                calc = self.inputBox2.text()

            self.inputBox2.setText("")
            if not self.tableEmpty:
                for r in range(7):
                    item = self.table.item(r, 0)
                    if item.text() == self.comboBox.currentText():
                        row = r

                item = QTableWidgetItem(str(calc))

                for i in range(4):
                    test = self.table.item(row, i)
                    if test.text() == "":
                        self.table.setItem(row, i, item)
            else:
                if self.pagType != "Planck":
                    self.errorLabel2.setText("Tip: Enter some heights first")
                else:
                    self.errorLabel2.setText("Tip: Enter some wavelengths first")

        except:
            if self.pagType != "Planck":
                self.errorLabel2.setText("Error: Incorrect form entered, Enter time as a number in seconds")
            else:
                self.errorLabel2.setText("Error: Incorrect form entered, Enter voltage as a number")

    # Procedure calculates the average value of each row in the table and adds the average into the table
    def calcAverage(self):
        for r in range(7):
            total = 0
            numList = []
            for c in range(1, 4):
                num = self.table.item(r, c)
                if num.text() != "":
                    numList.append(float(num.text()))

            for item in numList:
                total = total + item

            try:
                avg = round((total / len(numList)), 3)
                avgItem = QTableWidgetItem(str(avg))
                self.table.setItem(r, 4, avgItem)
            except:
                pass

    # Function returns the data in the table as a dictionary
    def tableAsDict(self):
        rows = {}
        rowCount = self.table.rowCount()
        for r in range(rowCount):
            rowItem = self.table.item(r, 0)
            if rowItem.text() != "":
                times = []
                colCount = self.table.columnCount()
                for i in range(1, (colCount)):
                    item = self.table.item(r, i)
                    times.append(item.text())

                rows[float(rowItem.text())] = times

        return rows

    # Procedure sorts the table in ascending order based on the values in the first column
    def sortTable(self):
        if not self.tableEmpty:
            data = self.tableAsDict()
            heights = []
            for key in data.keys():
                heights.append(key)

            mergeSort(heights)
            self.clearTable(True)

            rowCount = self.table.rowCount()
            for r in range(len(heights)):
                height = heights[r]
                hItem = QTableWidgetItem(str(height))
                self.table.setItem(r, 0, hItem)
                for i, item in enumerate(data[height]):
                    nItem = QTableWidgetItem(item)
                    self.table.setItem(r, (i + 1), nItem)

    # Procedure clears all the data in the table and resets it back to default
    def clearTable(self, sorting):
        self.table.clear()
        if not sorting:
            self.comboBox.clear()
        self.n = 0
        if self.pagType != "Planck":
            headers = ["Distance (m)", "1: time\u00b2 (s\u00b2)", "2: time\u00b2 (s\u00b2)", "3: time\u00b2 (s\u00b2)",
                       "Average time\u00b2 (s\u00b2)"]
        else:
            headers = ["Wavelength (x 10^-9 m)", "1: Voltage (V)", "2: Voltage (V)", "3: Voltage (V)",
                       "Average Voltage (V))"]

        self.table.setHorizontalHeaderLabels(headers)
        for i in range(7):
            for j in range(5):
                item = QTableWidgetItem("")
                self.table.setItem(i, j, item)
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
        self.tableEmpty = True

    # Creates a group box widget which includes the input boxes used during the practical stage
    def createGroupBox1(self):
        self.grpLayout = QVBoxLayout()
        self.grpLayout.setAlignment(Qt.AlignVCenter)

        blankLabel = QLabel()
        if self.pagType != "Planck":
            self.title = QLabel("Enter Height:")
            self.title2 = QLabel("Enter Time:")
            self.errorLabel = QLabel("Tip: Measure Height from the bottom of the ball")
            self.errorLabel2 = QLabel("Tip: Press Enter to add time\u00b2 (s\u00b2) into the table")
        else:
            self.title = QLabel("Enter Wavelength:")
            self.title2 = QLabel("Enter Voltage:")
            self.errorLabel = QLabel("Tip: Enter Wavelength in x 10^-9 nanometres (nm)")
            self.errorLabel2 = QLabel("Tip: Press Enter to add threshold Voltage (V) into the table")

        self.inputBox = QLineEdit()
        self.inputBox.returnPressed.connect(self.firstVariableEntered)

        self.inputBox2 = QLineEdit()
        self.inputBox2.returnPressed.connect(self.secondVariableEntered)
        self.comboBox = QComboBox()
        self.hLayout2 = QHBoxLayout()
        self.hLayout2.addWidget(self.comboBox)
        self.hLayout2.addWidget(self.inputBox2)

        self.grpLayout.addWidget(self.title)
        self.grpLayout.addWidget(self.inputBox)
        self.grpLayout.addWidget(self.errorLabel)
        self.grpLayout.addWidget(blankLabel)
        self.grpLayout.addWidget(self.title2)
        self.grpLayout.addLayout(self.hLayout2)
        self.grpLayout.addWidget(self.errorLabel2)

        self.groupBox = QGroupBox()

        self.groupBox.setLayout(self.grpLayout)

        self.groupBox.setFixedSize(425, 200)

    # Procedure run when the start button is pressed, relevant animation is then executed
    def startAnimation(self, pagType, choice):
        self.textBox.setFont(QFont("Arial", 20))
        if pagType == "Vertical":
            if self.startButton.text() == "Start Practical":
                self.removeWidgets()

                if not self.animWindow:
                    self.createGroupBox1()

                    self.vLayout2.addWidget(self.groupBox, 0, 0)

                self.animWindow = True
                self.calcWindow = False

                self.avgButton = QPushButton("Calculate Average")
                self.avgButton.clicked.connect(self.calcAverage)

                self.sortButton = QPushButton("Sort Table")
                self.sortButton.clicked.connect(self.sortTable)

                self.clearButton = QPushButton("Clear Table")
                self.clearButton.clicked.connect(lambda: self.clearTable(False))

                self.vLayout2.addWidget(self.avgButton, 3, 0)
                self.vLayout2.addWidget(self.sortButton, 4, 0)
                self.vLayout2.addWidget(self.clearButton, 5, 0)

                self.animView = VerticalFall(self.startButton, choice)
                self.graphicsView.scene.setSceneRect(-500, -100, 900, 800)
                self.graphicsView.setScene(self.animView)
                self.stack.setCurrentWidget(self.graphicsView)
                self.startButton.setText("Start Animation")
                self.animView.DIYAnim()
                self.textBox.setText(
                    "Measure the Distance of the Drop from the bottom of the ball and enter the time measured")
            elif self.startButton.text() == "Pause Animation":
                self.animView.pauseAnims()
                self.startButton.setText("Resume Animation")
            elif self.startButton.text() == "Resume Animation":
                self.animView.resumeAnims()
                self.startButton.setText("Pause Animation")
            elif self.startButton.text() == "Start Animation":
                self.animView.startAnims()
                self.startButton.setText("Pause Animation")

        elif pagType == "Ramp":
            if self.startButton.text() == "Start Practical":
                if self.calcWindow:
                    self.vLayout2.removeWidget(self.groupBox2)
                    self.groupBox2.deleteLater()

                if not self.animWindow:
                    self.createGroupBox1()

                    self.vLayout2.addWidget(self.groupBox, 0, 0)

                self.animWindow = True
                self.calcWindow = False

                self.avgButton = QPushButton("Calculate Average")
                self.avgButton.clicked.connect(self.calcAverage)

                self.sortButton = QPushButton("Sort Table")
                self.sortButton.clicked.connect(self.sortTable)

                self.clearButton = QPushButton("Clear Table")
                self.clearButton.clicked.connect(lambda: self.clearTable(False))

                self.vLayout2.addWidget(self.avgButton, 3, 0)
                self.vLayout2.addWidget(self.sortButton, 4, 0)
                self.vLayout2.addWidget(self.clearButton, 5, 0)

                self.animView = RampFall(self.startButton, choice)
                self.graphicsView.scene.setSceneRect(-300, -150, 950, 850)
                self.graphicsView.setScene(self.animView)
                self.stack.setCurrentWidget(self.graphicsView)
                self.startButton.setText("Start Animation")
                self.animView.DIYAnim()

                self.textBox.setText(
                    "Measure the Distance of the Drop from the bottom of the ball and enter the time measured")
            elif self.startButton.text() == "Pause Animation":
                self.animView.pauseAnims()
                self.startButton.setText("Resume Animation")
            elif self.startButton.text() == "Resume Animation":
                self.animView.resumeAnims()
                self.startButton.setText("Pause Animation")
            elif self.startButton.text() == "Start Animation":
                self.animView.startAnims()
                self.startButton.setText("Pause Animation")

        elif pagType == "Planck":
            if self.startButton.text() == "Start Practical":
                if self.calcWindow:
                    self.vLayout2.removeWidget(self.groupBox2)
                    self.groupBox2.deleteLater()

                if not self.animWindow:
                    self.createGroupBox1()

                    self.vLayout2.addWidget(self.groupBox, 0, 0)

                self.removeWires = QPushButton("Remove Wires")
                self.removeWires.clicked.connect(self.sceneRemoveWires)

                self.avgButton = QPushButton("Calculate Average")
                self.avgButton.clicked.connect(self.calcAverage)

                self.sortButton = QPushButton("Sort Table")
                self.sortButton.clicked.connect(self.sortTable)

                self.clearButton = QPushButton("Clear Table")
                self.clearButton.clicked.connect(lambda: self.clearTable(False))

                self.vLayout2.addWidget(self.removeWires, 3, 0)
                self.vLayout2.addWidget(self.avgButton, 4, 0)
                self.vLayout2.addWidget(self.sortButton, 5, 0)
                self.vLayout2.addWidget(self.clearButton, 6, 0)

                self.animWindow = True
                self.calcWindow = False

                self.animView = PlanckAnim(self.startButton, choice)
                self.graphicsView.setScene(self.animView)
                self.stack.setCurrentWidget(self.graphicsView)
                self.animView.DIYAnim()
                self.startButton.setText("Start Animation")
                self.textBox.setText("Connect the circuit")
            elif self.startButton.text() == "Start Animation":
                self.circuitConnected = True
                components = self.animView.getComponents()
                for item in components:
                    length = len(item)
                    if item[length - 1] > item[length - 2]:
                        self.circuitConnected = False

                if self.circuitConnected:
                    self.animView.changeConnected(self.circuitConnected)
                    self.startButton.setText("Next")
                    self.textBox.setText(
                        "Change the resistance of the variable resistor and measure the thresold voltage")
                else:
                    self.textBox.setText("Circuit not connected, try again")

    # Removes all the wires drawn by the user when doing the "Planck's Constant" practical
    def sceneRemoveWires(self):
        self.animView.removeWires()
        self.startButton.setText("Start Animation")
        self.textBox.setText("Connect the circuit")

    # Creates and displays the relevant widgets used in the calculation stage, such as the graph
    def calculations(self, pagType):
        if not self.calcWindow and self.animWindow:
            self.startButton.setText("Start Practical")
            self.textBox.setText("Calculate Gradient from the graph to get a value for g")

            if pagType != "Planck":
                self.removeWidgets()
            else:
                self.vLayout2.removeWidget(self.groupBox)
                self.groupBox.deleteLater()

                self.vLayout2.removeWidget(self.removeWires)
                self.removeWires.deleteLater()

                self.vLayout2.removeWidget(self.avgButton)
                self.avgButton.deleteLater()

                self.vLayout2.removeWidget(self.sortButton)
                self.sortButton.deleteLater()

                self.vLayout2.removeWidget(self.clearButton)
                self.clearButton.deleteLater()

            self.calcWindow = True
            self.animWindow = False

            self.calcText = QLineEdit()
            self.calcText.setReadOnly(True)
            self.calcText.setFont(QFont("Arial", 15))

            self.groupBox2 = QGroupBox()
            self.grpLayout2 = QVBoxLayout()

            title = QLabel("Enter Calculated Gradient:")
            self.gradientEnter = QLineEdit()
            self.gradientEnter.returnPressed.connect(self.gradientEntered)
            self.errorLabel.setText("Tip: Gradient = Δy/Δx")
            blankLabel = QLabel()
            title2 = QLabel("Enter Calculated value for g:")
            self.finalValueEnter = QLineEdit()
            self.finalValueEnter.returnPressed.connect(self.finalValueEntered)
            if pagType == "Vertical":
                self.errorLabel2.setText("Tip: g = gradient × 2")
            elif pagType == "Ramp":
                self.errorLabel2.setText("Tip: g = (gradient × 2) ÷ sin(30)")
            else:
                self.errorLabel2.setText("Tip: h = (gradient × e)/c")

            self.grpLayout2.addWidget(title)
            self.grpLayout2.addWidget(self.gradientEnter)
            self.grpLayout2.addWidget(self.errorLabel)
            self.grpLayout2.addWidget(blankLabel)
            self.grpLayout2.addWidget(title2)
            self.grpLayout2.addWidget(self.finalValueEnter)
            self.grpLayout2.addWidget(self.errorLabel2)

            self.grpLayout2.setAlignment(Qt.AlignVCenter)

            self.groupBox2.setLayout(self.grpLayout2)
            self.groupBox2.setFixedSize(425, 200)

            self.vLayout2.addWidget(self.groupBox2, 0, 0)

            self.sortTable()
            self.calcAverage()
            tableData = self.tableAsDict()
            self.graphView = self.DIYGraphView(tableData)

            if self.graphView != 0:
                calcBox = QGroupBox()
                calcLayout = QVBoxLayout()
                calcLayout.addWidget(self.graphView)
                calcLayout.addWidget(self.calcText)
                calcBox.setLayout(calcLayout)
                self.stack.addWidget(calcBox)
                self.stack.setCurrentWidget(calcBox)

    # Creates a graph based on the data entered by the user in the table
    def DIYGraphView(self, data):
        try:
            graph = MplCanvas(self, width=5, height=4, dpi=100)
            x = []
            y = []
            for key in data.keys():
                y.append(key)
                a = data[key]
                x.append(float(a[len(a) - 1]))

            if self.pagType == "Planck":
                for item in y:
                    index = y.index(item)
                    newItem = 1 / (float(item) * 10 ** -9)
                    y[index] = newItem

            if self.pagType != "Planck":
                graph.axes.set_xlabel('time\u00b2 (s\u00b2)')
                graph.axes.set_ylabel('Distance (m)')
                graphX = np.array(x)
                graphY = np.array(y)
            else:
                graph.axes.set_xlabel('1/λ × 10^6')
                graph.axes.set_ylabel('Voltage (V)')
                graphX = np.array(y)
                graphY = np.array(x)

            self.m, c = np.polyfit(graphX, graphY, 1)
            graph.axes.plot(graphX, graphY, "x")
            graph.axes.plot(graphX, self.m * graphX + c)

            graph.axes.grid(b=True, which='major', color='#666666', linestyle='-')
            graph.axes.minorticks_on()
            graph.axes.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)

            graphLayout = QVBoxLayout()

            toolbar = NavigationToolbar(graph, self)

            graphLayout.addWidget(toolbar)
            graphLayout.addWidget(graph)

            graphWidget = QWidget()
            graphWidget.setLayout(graphLayout)

            return graphWidget
        except:
            self.textBox.setText("Error: No Data has been input into the table")
            return 0

    # Procedure run when a value for the gradient is entered into the relevant input box
    def gradientEntered(self):
        text = self.gradientEnter.text()
        try:
            test = float(text)
            self.calcText.setText("Gradient: " + str(text))
            self.gradientEnter.setText("")
            self.errorLabel.setText("Tip: Gradient = Δy/Δx")
        except:
            self.errorLabel.setText("Error: Enter gradient as a number")

    # Procedure run when the final calculated value is entered, the percentage error is then calculated
    def finalValueEntered(self):
        text1 = self.calcText.text()
        textSplit = text1.split(",")
        text2 = self.finalValueEnter.text()
        try:
            if self.pagType != "Planck":
                error = abs(((9.81 - float(text2)) / 9.81) * 100)
                finalError = round(error, 1)
                finalText = textSplit[0] + ", " + "Value for g: " + str(
                    text2) + "m/s\u00b2" + ", " + "Percentage Error: " + str(finalError) + "%"
            else:
                error = abs(((6.63e-34 - float(text2)) / 6.63e-34) * 100)
                finalError = round(error, 1)
                finalText = textSplit[0] + ", " + "Value for g: " + str(text2) + ", Percentage Error: " + str(
                    finalError) + "%"

            self.calcText.setText(finalText)
            self.finalValueEnter.setText("")
            if self.pagType == "Vertical":
                self.errorLabel2.setText("Tip: g = gradient × 2")
            elif self.pagType == "Ramp":
                self.errorLabel2.setText("Tip: g = (gradient × 2) ÷ sin(30)")
            else:
                self.errorLabel2.setText("Tip: h = (gradient × e)/c")
        except:
            self.errorLabel2.setText("Error: Enter the value for g as a number")

    # Removes the relevant widgets, used when switching between the practical and calculation stage
    def removeWidgets(self):
        if self.animWindow:
            self.vLayout2.removeWidget(self.groupBox)
            self.groupBox.deleteLater()

            self.vLayout2.removeWidget(self.avgButton)
            self.avgButton.deleteLater()

            self.vLayout2.removeWidget(self.sortButton)
            self.sortButton.deleteLater()

            self.vLayout2.removeWidget(self.clearButton)
            self.clearButton.deleteLater()
        elif self.calcWindow:
            self.vLayout2.removeWidget(self.groupBox2)
            self.groupBox2.deleteLater()

    # Changes the PAG type which allows the user to try a different practical
    def changeType(self):
        self.changeBox = QDialog(self)
        self.changeBox.setWindowTitle("Change Type")

        dlgLayout = QVBoxLayout()

        groupBox = QGroupBox("Choose")
        grpLayout = QHBoxLayout()

        if self.pagType == "Vertical" or self.pagType == "Ramp":
            button1 = QRadioButton("Vertical")
            button2 = QRadioButton("Ramp")

        grpLayout.addWidget(button1)
        grpLayout.addWidget(button2)
        groupBox.setLayout(grpLayout)

        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        buttonBox = QDialogButtonBox(buttons)
        buttonBox.accepted.connect(self.changeBox.accept)
        buttonBox.rejected.connect(self.changeBox.reject)

        dlgLayout.addWidget(groupBox)
        dlgLayout.addWidget(buttonBox)

        self.changeBox.setLayout(dlgLayout)

        self.changeBox.exec_()

        if button1.isChecked():
            self.pagType = button1.text()
            self.startButton.setText("Start Practical")
            self.removeWidgets()
            self.animWindow = False
            self.textBox.setText(None)
            self.graphicsView.setScene(None)
            self.clearTable(True)
            self.stack.setCurrentWidget(self.graphicsView)

        elif button2.isChecked():
            self.pagType = button2.text()
            self.startButton.setText("Start Practical")
            self.removeWidgets()
            self.animWindow = False
            self.textBox.setText(None)
            self.graphicsView.setScene(None)
            self.clearTable(True)
            self.stack.setCurrentWidget(self.graphicsView)

    # Procedure displays a Dialog box which allows the user to change parts of the animation/practical
    def editAnimation(self):
        self.options = QDialog(self)
        self.options.setWindowTitle("Change Practical Variables")

        dlgLayout = QVBoxLayout()

        groupBox = QGroupBox("Edit")
        grpLayout = QGridLayout()

        if self.pagType != "Planck":
            label = QLabel("Animation Speed:")
            grpLayout.addWidget(label, 0, 0)
            speedSlider = QSlider(Qt.Horizontal)
            speedSlider.setMinimum(1)
            speedSlider.setMaximum(10)
            speedSlider.setValue(self.speed)
            speedSlider.setTickPosition(QSlider.TicksBelow)
            speedSlider.setTickInterval(1)
            grpLayout.addWidget(speedSlider, 0, 1)
        else:
            choice = QComboBox()
            wavelengths = ["700", "630", "580", "520", "450", "420", "380"]
            choice.addItems(wavelengths)
            label = QLabel("Choose Wavelength of LED (nm):")
            grpLayout.addWidget(label, 0, 0)
            grpLayout.addWidget(choice, 0, 1)

        groupBox.setLayout(grpLayout)

        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        buttonBox = QDialogButtonBox(buttons)
        buttonBox.accepted.connect(self.options.accept)
        buttonBox.rejected.connect(self.options.reject)

        dlgLayout.addWidget(groupBox)
        dlgLayout.addWidget(buttonBox)

        self.options.setLayout(dlgLayout)
        self.options.exec_()

        if self.pagType != "Planck" and self.animWindow:
            self.speed = speedSlider.value()
            self.animView.changeSpeed(self.speed)
        elif self.pagType == "Planck" and self.animWindow:
            self.led = float(choice.currentText())
            self.animView.resetTimer()
            self.animView.changeLED(self.led)

    def exitToMenu(self):
        self.window = MenuWindow()
        self.close()
        self.window.show()


# Class definition for the graphics objects used in the animation
# Gives the object a position attribute which is then used when running the animation
class GraphicsObject(QObject):
    def __init__(self, imgPath):
        super().__init__()

        itemPixmap = QPixmap(imgPath)
        self.item = QGraphicsPixmapItem(itemPixmap)

    def setPosition(self, position):
        self.item.setPos(position)

    position = pyqtProperty(QPointF, fset=setPosition)


# Parent graphics scene class, which sets the default attributes and methods of the animation view
class AnimScene(QGraphicsScene):
    def __init__(self, button, choice):
        super(AnimScene, self).__init__()

        self.seconds = 0
        self.milli = 0
        self.animState = 1
        self.speed = 1
        self.button = button
        self.animations = []
        self.choice = choice

        self.initView()

    def initView(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateTimer)

        self.clock = QLabel()
        self.clock.setFont(QFont("Arial", 15))
        self.clock.setAlignment(Qt.AlignCenter)
        self.clock.setText("00:00")

        self.addWidget(self.clock)

    def stopAnims(self):
        for anim in self.animations:
            anim.stop()

    def animFinished(self):
        self.button.setText("Start Animation")
        self.timer.stop()

    def pauseAnims(self):
        self.timer.stop()
        for anim in self.animations:
            anim.pause()

    def resumeAnims(self):
        self.timer.start(10 * self.speed)
        for anim in self.animations:
            anim.start()

    def changeSpeed(self, speed):
        if speed == 1 or speed == 10:
            self.speed = 11 - speed
        else:
            self.speed = 10 - speed

    def getAnimState(self):
        return self.animState


# Sub class of parent graphics scene class, sets custom methods to display animation of a ball rolling down a ramp
# Also includes a procedure which defines how the animation is run in the DIY Window
class RampFall(AnimScene):
    def __init__(self, button, choice):
        super(RampFall, self).__init__(button, choice)

        self.initView()

    def initView(self):
        super(RampFall, self).initView()
        if self.choice == 1:
            self.clock.setGeometry(-200, 25, 80, 50)
        else:
            self.clock.setGeometry(-100, 125, 80, 50)
        self.createObjects()

    def createObjects(self):
        if self.choice == 1:
            self.ball = GraphicsObject(resource_path("./img/ball.png"))
            self.ramp = GraphicsObject(resource_path("./img/ramp1.png"))
        else:
            self.ball = MovableImage(40, 40, resource_path("./img/ball.png"))
            self.ruler = MovableImage(460, 505, resource_path("./img/ruler.png"))
            self.ramp = GraphicsObject(resource_path("./img/ramp1.png"))
            pix = QPixmap(resource_path("./img/ruler.png"))
            rotated = pix.transformed(QTransform().rotate(60), Qt.SmoothTransformation)
            self.ruler.setPixmap(rotated)
            self.ruler.item = QGraphicsPixmapItem(rotated)

    def createScene(self):
        if self.choice == 1:
            self.addItem(self.ball.item)
            self.addItem(self.ramp.item)
        else:
            self.addWidget(self.ruler)
            self.addItem(self.ramp.item)
            self.addWidget(self.ball)

    # Timer works by setting a 10ms timer, which when finished runs the updateTimer subroutine
    # Subroutine adds 1 to the text in the clock QLabel, repeated every time the timer is finished until the animation is completely finished or paused
    def updateTimer(self):
        self.milli += 1
        if self.milli == 100:
            self.milli = 0
            self.seconds += 1
        if self.milli >= 0 and self.milli <= 9:
            strMilli = "0" + str(self.milli)
        else:
            strMilli = str(self.milli)
        clockString = str(self.seconds) + ":" + strMilli
        self.clock.setText(clockString)

    def resetTimer(self):
        self.milli = 0
        self.seconds = 0
        self.clock.setText("00:00")

    # Creates a still image of the setup of the practical
    def still(self, state, width, height, text):
        self.createScene()
        self.resetTimer()
        self.timer.stop()
        self.heightBox = QLineEdit()
        self.heightBox.setReadOnly(True)
        self.heightBox.setAlignment(Qt.AlignCenter)
        self.heightBox.setFont(QFont("Arial", 10))
        self.heightBox.setText(text)
        self.heightBox.setGeometry(-200, 100, 200, 50)

        self.addWidget(self.heightBox)
        self.animState = state

        self.ball.item.setPos(width, height)

    # Creates the animations for the ball, setting the position of the ball at the start and at the end
    def drop(self, width, height, state, base, text):
        self.animState = state
        self.base = base
        self.heightBox.setText(text)

        self.ball.item.setPos(width, height)

        self.ballAnim = QPropertyAnimation(self.ball, b"position")
        self.ballAnim.setStartValue(QPointF(width, height))
        self.ballAnim.setEndValue(QPointF(-18, 210))
        self.ballAnim.setEasingCurve(QEasingCurve.InCubic)

        self.animations.append(self.ballAnim)

    # Creates a scene with the objects used in the practical, which can then be used by the user
    def DIYAnim(self):
        self.createScene()
        self.ballAnim = QPropertyAnimation(self.ball, b"position")

        self.ruler.move(-100, 0)
        self.ball.move(100, 250)
        self.ramp.item.setPos(-100, 243)

        self.ballAnim.setEasingCurve(QEasingCurve.InCubic)
        self.animations.append(self.ballAnim)

    # Starts the animation and starts the timer
    # For the DIY window, the procedure calculates the time taken for the ball to reach the bottom of the ramp by calculating the distance
    def startAnims(self):
        self.resetTimer()
        if self.choice == 1:
            self.ballAnim.setDuration(self.speed * self.base)
        else:
            self.ballPos = self.ball.pos()
            self.height = ((((self.ballPos.x() + 100) ** 2) + ((self.ballPos.y() - 455) ** 2)) ** (0.5)) / 503
            sinTheta = math.sin(math.pi / 6)
            self.base = (((2 * self.height) / (9.81 * sinTheta)) ** (0.5) * 1000)
            if self.base == 0:
                self.base = 1
            self.ballAnim.setDuration(self.speed * self.base)
            self.rulerPos = self.ruler.pos()

            self.ballAnim.setStartValue(self.ballPos)

            self.endPos = QPoint(-120, 455)
            self.ballAnim.setEndValue(self.endPos)

            self.ball.setHidden(True)
            self.ball.move(self.endPos)
            self.addItem(self.ball.item)
            self.ball.item.setPos(self.ballPos)

        self.ballAnim.start()
        self.timer.start(10 * self.speed)
        self.ballAnim.finished.connect(self.animFinished)

    def animFinished(self):
        super(RampFall, self).animFinished()
        if self.choice == 2:
            self.removeItem(self.ball.item)
            self.ball.setHidden(False)


# Sub class of parent graphics scene class, sets custom methods to display an animation of a ball falling vertically
class VerticalFall(AnimScene):
    def __init__(self, button, choice):
        super(VerticalFall, self).__init__(button, choice)

        self.initView()

    def initView(self):
        super(VerticalFall, self).initView()
        self.clock.setGeometry(-200, 175, 80, 50)
        self.createObjects()

    def createObjects(self):
        if self.choice == 1:
            self.ball = GraphicsObject(resource_path("./img/ball.png"))
            self.ruler = GraphicsObject(resource_path("./img/ruler.png"))
        else:
            self.ball = MovableImage(40, 40, resource_path("./img/ball.png"))
            self.ruler = MovableImage(50, 505, resource_path("./img/ruler.png"))

    def createScene(self):
        if self.choice == 1:
            self.addItem(self.ball.item)
            self.addItem(self.ruler.item)
        else:
            self.addWidget(self.ruler)
            self.addWidget(self.ball)

    def updateTimer(self):
        self.milli += 1
        if self.milli == 100:
            self.milli = 0
            self.seconds += 1
        if self.milli >= 0 and self.milli <= 9:
            strMilli = "0" + str(self.milli)
        else:
            strMilli = str(self.milli)
        clockString = str(self.seconds) + ":" + strMilli
        self.clock.setText(clockString)

    def resetTimer(self):
        self.milli = 0
        self.seconds = 0
        self.clock.setText("00:00")

    def still(self, state, height, text):
        self.createScene()
        self.resetTimer()
        self.timer.stop()
        self.heightBox = QLineEdit()
        self.heightBox.setReadOnly(True)
        self.heightBox.setAlignment(Qt.AlignCenter)
        self.heightBox.setFont(QFont("Arial", 10))
        self.heightBox.setText(text)
        self.heightBox.setGeometry(-200, 245, 150, 50)

        self.addWidget(self.heightBox)
        self.animState = state

        self.ball.item.setPos(100, height)
        self.ruler.item.setPos(0, 38)

    def drop(self, height, state, base, text):
        self.animState = state
        self.base = base
        self.heightBox.setText(text)

        self.ball.item.setPos(100, height)

        self.ballAnim = QPropertyAnimation(self.ball, b"position")
        self.ballAnim.setStartValue(QPointF(100, height))
        self.ballAnim.setEndValue(QPointF(100, 503))
        self.ballAnim.setEasingCurve(QEasingCurve.InCubic)
        self.animations.append(self.ballAnim)

    def DIYAnim(self):
        self.createScene()
        self.ballAnim = QPropertyAnimation(self.ball, b"position")
        self.ruler.move(-100, 0)
        self.ball.move(0, -38)

        self.ballAnim.setEasingCurve(QEasingCurve.InCubic)
        self.animations.append(self.ballAnim)

    def startAnims(self):
        self.resetTimer()
        if self.choice == 1:
            self.ballAnim.setDuration(self.speed * self.base)
        else:
            self.ballPos = self.ball.pos()
            self.height = (465 - self.ballPos.y()) / 503
            self.base = (((2 * self.height) / 9.81) ** (0.5) * 1000)
            if self.base == 0:
                self.base = 1
            self.ballAnim.setDuration(self.speed * self.base)
            self.rulerPos = self.ruler.pos()

            self.ballAnim.setStartValue(self.ballPos)

            self.endPos = QPoint(self.ballPos.x(), 465)
            self.ballAnim.setEndValue(self.endPos)

            self.ball.setHidden(True)
            self.addItem(self.ball.item)
            self.ball.item.setPos(self.ballPos)

        self.ballAnim.start()
        self.timer.start(10 * self.speed)
        self.ballAnim.finished.connect(self.animFinished)

    def animFinished(self):
        super(VerticalFall, self).animFinished()
        if self.choice == 2:
            self.ball.move(self.endPos)
            self.removeItem(self.ball.item)
            self.ball.setHidden(False)


# Graphics Scene subclass which runs the animation for the "Planck's Constant" Practical
class PlanckAnim(AnimScene):
    def __init__(self, button, choice):
        super(PlanckAnim, self).__init__(button, choice)

        self.base = 5000
        self.unit = 0
        self.choice = choice
        self.begin = None
        self.end = None
        self.circuitConnected = False
        self.wires = []
        self.initView()

    # Creates the objects and sets the colour of the LED as white, which then changes as the animation is run
    def initView(self):
        super(PlanckAnim, self).initView()
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateTimer)

        self.createObjects()
        self.clock.deleteLater()
        self.voltage = QLabel()
        self.voltage.setFont(QFont("Arial", 15))
        self.voltage.setAlignment(Qt.AlignCenter)
        self.voltage.setText("0.00")

        self.bulb = QGraphicsEllipseItem(0, 0, 86, 86)
        self.bulb.setBrush(QColor(255, 255, 255))
        self.red = 255
        self.blue = 255
        self.green = 255
        self.constant = 255
        self.led = 700

        if self.choice == 1:
            self.voltage.setGeometry(348, 470, 64, 40)

    # Once the voltage value crosses the threshold value, the colour of the LED changes
    def updateTimer(self):
        self.milli += 1
        if self.milli == 100:
            self.milli = 0
            self.unit += 1
        if self.milli >= 0 and self.milli <= 9:
            strMilli = "0" + str(self.milli)
        else:
            strMilli = str(self.milli)

        voltString = str(self.unit) + "." + strMilli

        if self.led == 700:
            if float(voltString) >= 1.7 and self.blue != 0:
                self.blue = self.blue - 1
                self.green = self.green - 1
        elif self.led == 450:
            if float(voltString) >= 2.7 and self.red != 0:
                self.red = self.red - 1
                self.green = self.green - 1

        self.bulb.setBrush(QColor(self.red, self.green, self.blue))

        self.voltage.setText(voltString)

    def resetTimer(self):
        self.timer.stop()
        self.milli = 0
        self.unit = 0
        self.red = 255
        self.blue = 255
        self.green = 255
        self.constant = 255
        self.bulb.setBrush(QColor(255, (self.blue), (self.green)))
        self.voltage.setText("0.00")

    def changeLED(self, led):
        self.led = led

    def createObjects(self):
        if self.choice == 1:
            self.circuit = GraphicsObject(resource_path("./img/circuit2.png"))
            self.slider = GraphicsObject(resource_path("./img/slider.png"))
        else:
            self.supply = GraphicsObject(resource_path("./img/supply.png"))
            self.voltmeter = GraphicsObject(resource_path("./img/voltmeter.png"))
            self.vResistor = GraphicsObject(resource_path("./img/resistor.png"))

            self.prevLine = QGraphicsLineItem()

            self.slider = QSlider(minimum=0, maximum=500, orientation=Qt.Horizontal)
            self.slider.setValue(500)
            self.slider.setStyleSheet("background-color: transparent;")
            self.slider.valueChanged.connect(self.updateVoltage)
            self.slider.setFixedSize(180, 15)

            self.node1 = QGraphicsRectItem(0, 0, 10, 10)
            self.node1.setBrush(QColor(0, 0, 0))
            self.node2 = QGraphicsRectItem(0, 0, 10, 10)
            self.node2.setBrush(QColor(0, 0, 0))
            self.node3 = QGraphicsRectItem(0, 0, 10, 10)
            self.node3.setBrush(QColor(0, 0, 0))
            self.node4 = QGraphicsRectItem(0, 0, 10, 10)
            self.node4.setBrush(QColor(0, 0, 0))
            self.node5 = QGraphicsRectItem(0, 0, 10, 10)
            self.node5.setBrush(QColor(0, 0, 0))
            self.node6 = QGraphicsRectItem(0, 0, 10, 10)
            self.node6.setBrush(QColor(0, 0, 0))

    def updateVoltage(self):
        if self.circuitConnected:
            sliderValue = round(((self.slider.value()) / 100), 2)
            voltValue = round((5 - sliderValue), 2)
            self.voltage.setText(str(voltValue))
            if self.led == 700:
                if voltValue >= 1.7 and voltValue > self.oldValue and self.constant != 0:
                    self.constant = self.constant - 5
                    self.blue = self.blue - 5
                    self.green = self.green - 5
                elif voltValue < self.oldValue and voltValue <= 3.23 and self.constant != 255:
                    self.constant = self.constant + 5
                    self.blue = self.blue + 5
                    self.green = self.green + 5
            elif self.led == 630:
                if voltValue >= 1.95 and voltValue > self.oldValue and self.constant != 0:
                    self.constant = self.constant - 5
                    self.green = self.green - 2
                    self.blue = self.blue - 5
                elif voltValue < self.oldValue and voltValue <= 3.48 and self.constant != 255:
                    self.constant = self.constant + 5
                    self.green = self.green + 2
                    self.blue = self.blue + 5
            elif self.led == 580:
                if voltValue >= 2.1 and voltValue > self.oldValue and self.constant != 0:
                    self.constant = self.constant - 5
                    self.blue = self.blue - 5
                elif voltValue < self.oldValue and voltValue <= 3.63 and self.constant != 255:
                    self.constant = self.constant + 5
                    self.blue = self.blue + 5
            elif self.led == 520:
                if voltValue >= 2.35 and voltValue > self.oldValue and self.constant != 0:
                    self.constant = self.constant - 5
                    self.red = self.red - 5
                    self.blue = self.blue - 5
                elif voltValue < self.oldValue and voltValue <= 3.88 and self.constant != 255:
                    self.constant = self.constant + 5
                    self.red = self.red + 5
                    self.blue = self.blue + 5
            elif self.led == 450:
                if voltValue >= 2.75 and voltValue > self.oldValue and self.constant != 0:
                    self.constant = self.constant - 5
                    self.red = self.red - 5
                    self.green = self.green - 5
                elif voltValue < self.oldValue and voltValue <= 4.28 and self.constant != 255:
                    self.constant = self.constant + 5
                    self.red = self.red + 5
                    self.green = self.green + 5
            elif self.led == 420:
                if voltValue >= 2.9 and voltValue > self.oldValue and self.constant != 0:
                    self.constant = self.constant - 5
                    self.red = self.red - 2
                    self.green = self.green - 5
                elif voltValue < self.oldValue and voltValue <= 4.43 and self.constant != 255:
                    self.constant = self.constant + 5
                    self.red = self.red + 2
                    self.green = self.green + 5
            elif self.led == 380:
                if voltValue >= 3.2 and voltValue > self.oldValue and self.constant != 0:
                    self.constant = self.constant - 5
                    self.red = self.red - 4.5
                    self.green = self.green - 5
                    self.blue = self.blue - 4
                elif voltValue < self.oldValue and voltValue <= 4.73 and self.constant != 255:
                    self.constant = self.constant + 5
                    self.red = self.red + 4.5
                    self.green = self.green + 5
                    self.blue = self.blue + 4

            self.bulb.setBrush(QColor(self.red, self.green, self.blue))
            self.oldValue = voltValue

    def createScene(self):
        if self.choice == 1:
            self.addItem(self.bulb)
            self.addItem(self.circuit.item)
            self.addItem(self.slider.item)
            self.addWidget(self.voltage)
        else:
            self.addItem(self.supply.item)
            self.addItem(self.voltmeter.item)
            self.addItem(self.vResistor.item)
            self.addItem(self.bulb)
            self.addWidget(self.voltage)
            self.addWidget(self.slider)
            self.addItem(self.node1)
            self.addItem(self.node2)
            self.addItem(self.node3)
            self.addItem(self.node4)
            self.addItem(self.node5)
            self.addItem(self.node6)
            self.addItem(self.prevLine)

    def changeConnected(self, boolean):
        self.circuitConnected = boolean

    def createLabel(self, text):
        label = QLineEdit()
        label.setReadOnly(True)
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont("Arial", 10))
        label.setText(text)
        self.addWidget(label)
        return label

    def still(self, state, led):
        self.createScene()
        self.resetTimer()
        self.button.setText("Start Animation")
        self.compBox1 = self.createLabel("Variable Resistor")
        self.compBox1.setGeometry(35, 150, 150, 50)

        self.compBox2 = self.createLabel("Bulb")
        self.compBox2.setGeometry(350, 290, 75, 50)

        self.compBox3 = self.createLabel("Voltmeter")
        self.compBox3.setGeometry(450, 500, 100, 50)

        for anim in self.animations:
            anim.stop()

        self.led = led
        self.animState = state
        self.bulb.setPos(348, 343)
        self.circuit.item.setPos(0, 0)
        self.slider.item.setPos(180, 255)

    def slide(self, state):
        self.animState = state
        self.sliderAnim = QPropertyAnimation(self.slider, b"position")
        self.sliderAnim.setStartValue(QPointF(180, 255))
        self.sliderAnim.setEndValue(QPointF(25, 255))

        self.animations.append(self.sliderAnim)

    # For the DIY view, a 2D list is created which stores each component in the circuit, the start and end position of the component, and the index of the components which it connects with
    def DIYAnim(self):
        self.oldValue = 0
        self.createScene()
        self.components = []
        self.supply.item.setPos(0, -300)
        self.vResistor.item.setPos(-200, -170)
        self.slider.move(-190, -135)
        self.bulb.setPos(50, -40)
        self.voltage.setGeometry(60, 115, 64, 40)
        self.voltmeter.item.setPos(50, 100)

        self.node1.setPos(-130, -250)
        self.node2.setPos(300, -250)
        self.node3.setPos(-130, 0)
        self.node4.setPos(300, 0)
        self.node5.setPos(-130, 150)
        self.node6.setPos(300, 150)

        self.components.append([self.supply.item, QPointF(-1, -301), QPointF(184, -197), 4, 5, 0, 2])
        self.components.append([self.bulb, QPointF(49, -41), QPointF(137, 47), 6, 7, 0, 2])
        self.components.append([self.voltmeter.item, QPointF(50, 100), QPointF(137, 201), 8, 9, 0, 2])
        self.components.append([self.vResistor.item, QPointF(-200, -170), QPointF(-1, -84), 4, 6, 0, 2])
        self.components.append([self.node1, QPointF(-131, -251), QPointF(-119, -239), 0, 3, 0, 2])
        self.components.append([self.node2, QPointF(299, -251), QPointF(311, -239), 0, 7, 0, 2])
        self.components.append([self.node3, QPointF(-131, -1), QPointF(-119, 11), 3, 1, 8, 0, 3])
        self.components.append([self.node4, QPointF(299, -1), QPointF(311, 11), 5, 1, 9, 0, 3])
        self.components.append([self.node5, QPointF(-131, 149), QPointF(-119, 161), 6, 2, 0, 2])
        self.components.append([self.node6, QPointF(299, 149), QPointF(311, 161), 7, 2, 0, 2])

    def getComponents(self):
        return self.components

    def startAnims(self):
        self.resetTimer()
        self.timer.start(10 * self.speed)
        self.sliderAnim.setDuration(self.speed * self.base)
        self.sliderAnim.finished.connect(self.animFinished)
        for anim in self.animations:
            anim.start()

    # Procedures which define what happens when the user presses and releases the mouse
    # A wire (line object) is drawn when the mouse is pressed and released
    def mousePressEvent(self, event):
        if self.choice == 2 and not self.circuitConnected:
            self.begin = self.end = event.scenePos()
            self.update()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.choice == 2 and not self.circuitConnected:
            if self.begin is not None:
                self.end = event.scenePos()
                self.removeItem(self.prevLine)
                l = QLineF(self.begin, self.end)
                wire = QGraphicsLineItem(l)
                self.addItem(wire)
                self.prevLine = wire
        super().mouseMoveEvent(event)

    # Procedure checks to see if the wire drawn is connecting 2 adjacent components, if yes, a connection value is added in the components list
    def mouseReleaseEvent(self, event):
        if self.choice == 2 and not self.circuitConnected:
            l = QLineF(self.begin, self.end)
            for component in self.components:
                startPos = component[1]
                endPos = component[2]
                length = len(component)
                if (l.x1() >= startPos.x() and l.x1() <= endPos.x()) and (
                        l.y1() >= startPos.y() and l.y1() <= endPos.y()):
                    validEndComponent1 = self.components[component[3]]
                    validEndComponent2 = self.components[component[4]]

                    validStartPos1 = validEndComponent1[1]
                    validEndPos1 = validEndComponent1[2]

                    validStartPos2 = validEndComponent2[1]
                    validEndPos2 = validEndComponent2[2]

                    length2 = len(validEndComponent1)
                    length3 = len(validEndComponent2)

                    validStartPos3 = QPoint()
                    validEndPos3 = QPoint()

                    if length == 8:
                        validEndComponent3 = self.components[component[5]]
                        validStartPos3 = validEndComponent3[1]
                        validEndPos3 = validEndComponent3[2]
                        length4 = len(validEndComponent3)

                    if (l.x2() >= validStartPos1.x() and l.x2() <= validEndPos1.x()) and (
                            l.y2() >= validStartPos1.y() and l.y2() <= validEndPos1.y()):
                        component[length - 2] += 1
                        validEndComponent1[length2 - 2] += 1
                    elif (l.x2() >= validStartPos2.x() and l.x2() <= validEndPos2.x()) and (
                            l.y2() >= validStartPos2.y() and l.y2() <= validEndPos2.y()):
                        component[length - 2] += 1
                        validEndComponent2[length3 - 2] += 1
                    elif (l.x2() >= validStartPos3.x() and l.x2() <= validEndPos3.x()) and (
                            l.y2() >= validStartPos3.y() and l.y2() <= validEndPos3.y()):
                        component[length - 2] += 1
                        validEndComponent3[length4 - 2] += 1

            w = QGraphicsLineItem(l)
            self.wires.append(w)
            self.updateWires()
            self.begin = self.end = None
        super().mouseReleaseEvent(event)

    def updateWires(self):
        for wire in self.wires:
            self.addItem(wire)

    def removeWires(self):
        self.removeItem(self.prevLine)
        for wire in self.wires:
            self.removeItem(wire)
        self.wires = []
        self.circuitConnected = False
        for item in self.components:
            index = len(item) - 2
            item[index] = 0


# Group box class which displays the table used during the practical and defines the default methods
class GraphCalcBox(QGroupBox):
    def __init__(self):
        super(GraphCalcBox, self).__init__()

        self.graphShown = False
        self.workingOutShown = False

    def initView(self):
        self.setStyleSheet("background-color: white;")
        self.layout = QHBoxLayout()
        self.layout2 = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setRowCount(8)
        self.table.setColumnCount(5)

        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.layout2.addWidget(self.table)

        self.layout.addLayout(self.layout2)
        self.setLayout(self.layout)

    def removeGraph(self):
        self.graphShown = False
        self.layout.removeWidget(self.graphWidget)
        self.graphWidget.deleteLater()

    def removeWorking(self):
        self.workingOutShown = False
        self.layout2.removeWidget(self.workBox)
        self.workBox.deleteLater()

    def getGraphShown(self):
        return self.graphShown

    def getWorkingOutShown(self):
        return self.workingOutShown


# Subclass which displays the calculation process for the Vertical Drop practical
class CalculationVertical(GraphCalcBox):
    def __init__(self):
        super(CalculationVertical, self).__init__()

        self.initView()

    def initView(self):
        super(CalculationVertical, self).initView()

        self.data = {"Distance (m)": ["0.25", "0.50", "0.75", "1.00", "1.25", "1.50", "1.75", "2.00"],
                     "1: time\u00b2 (s\u00b2)": ["0.051", "0.102", "0.153", "0.204", "0.255", "0.306", "0.357",
                                                 "0.408"],
                     "2: time\u00b2(s\u00b2)": ["0.050", "0.099", "0.152", "0.210", "0.249", "0.312", "0.350", "0.415"],
                     "3: time\u00b2 (s\u00b2)": ["0.048", "0.103", "0.156", "0.216", "0.258", "0.307", "0.363",
                                                 "0.413"],
                     "Average time\u00b2 (s\u00b2)": ["0.050", "0.101", "0.154", "0.210", "0.254", "0.308", "0.357",
                                                      "0.412"]}

        headers = []
        for n, key in enumerate(self.data.keys()):
            headers.append(key)
            for m, item in enumerate(self.data[key]):
                nItem = QTableWidgetItem(item)
                self.table.setItem(m, n, nItem)

        self.table.setHorizontalHeaderLabels(headers)
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()

    def graph(self):
        mplGraph = MplCanvas(self, width=5, height=4, dpi=100)
        x = np.array([0.050, 0.101, 0.154, 0.210, 0.254, 0.308, 0.357, 0.412])
        y = np.array([0.25, 0.50, 0.75, 1.00, 1.25, 1.50, 1.75, 2.00])
        self.m, c = np.polyfit(x, y, 1)
        mplGraph.axes.plot(x, y, "x")
        mplGraph.axes.plot(x, self.m * x + c)

        mplGraph.axes.set_xlabel('time\u00b2 (s\u00b2)')
        mplGraph.axes.set_ylabel('Distance (m)')
        mplGraph.axes.grid(b=True, which='major', color='#666666', linestyle='-')
        mplGraph.axes.minorticks_on()
        mplGraph.axes.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)

        graphLayout = QVBoxLayout()

        graphLayout.addWidget(mplGraph)

        self.graphWidget = QWidget()
        self.graphWidget.setLayout(graphLayout)

        self.layout.addWidget(self.graphWidget)

        self.graphShown = True

    def workingOut(self):
        self.workingOutShown = True
        self.workBox = QLabel()
        self.workBox.setAlignment(Qt.AlignCenter)
        self.workBox.setFont(QFont("Arial", 14))
        string1 = "Value of Freefall can be calculated by working out the gradient\n"
        string2 = "The Line of Best Fit follows the equation s = 0.5at\u00b2"
        string3 = "\na = g, gradient = 0.5a\n"
        string4 = "Calculated gradient = " + (str(round(self.m, 2)) + " using Δy/Δx")
        string5 = "\nFinal Value of g = gradient × 2 = " + (str(round(self.m, 2) * 2)) + " m/s\u00b2"

        self.workBox.setText(string1 + string2 + string3 + string4 + string5)

        self.layout2.addWidget(self.workBox)


# Class which displays the calculation process for the Planck's Constant practical
class CalculationPlanck(GraphCalcBox):
    def __init__(self):
        super(CalculationPlanck, self).__init__()

        self.initView()

    def initView(self):
        super(CalculationPlanck, self).initView()
        self.table.setRowCount(7)
        self.table.setColumnCount(6)

        self.data = {"Wavelength (nm)": ["700", "630", "580", "520", "450", "420", "380"],
                     "1/λ (x 10^6 m^-1)": ["1.43", "1.59", "1.72", "1.92", "2.22", "2.38", "2.63"],
                     "1: Voltage (V)": ["1.78", "1.97", "2.14", "2.39", "2.76", "2.96", "3.27"],
                     "2: Voltage (V)": ["1.76", "1.98", "2.12", "2.41", "2.75", "2.98", "3.27"],
                     "3: Voltage (V)": ["1.77", "1.96", "2.10", "2.43", "2.74", "2.98", "3.24"],
                     "Average Voltage (V)": ["1.77", "1.97", "2.12", "2.41", "2.75", "2.97", "3.26"]}

        headers = []
        for n, key in enumerate(self.data.keys()):
            headers.append(key)
            for m, item in enumerate(self.data[key]):
                nItem = QTableWidgetItem(item)
                self.table.setItem(m, n, nItem)

        self.table.setHorizontalHeaderLabels(headers)
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()

    def drawGraph(self):
        graph = MplCanvas(self, width=4, height=4, dpi=100)
        x = np.array([1.43, 1.59, 1.72, 1.92, 2.22, 2.38, 2.63])
        y = np.array([1.77, 1.97, 2.12, 2.41, 2.75, 2.97, 3.26])
        self.m, c = np.polyfit(x, y, 1)
        graph.axes.plot(x, y, "x")
        graph.axes.plot(x, self.m * x + c)

        graph.axes.set_xlabel('1/λ (x10^6 m^-1)')
        graph.axes.set_ylabel('Voltage (V)')
        graph.axes.grid(b=True, which='major', color='#666666', linestyle='-')
        graph.axes.minorticks_on()
        graph.axes.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)

        graphLayout = QVBoxLayout()
        graphLayout.addWidget(graph)

        self.graphWidget = QWidget()
        self.graphWidget.setLayout(graphLayout)

        self.layout.addWidget(self.graphWidget)

        self.graphShown = True

    def workingOut(self):
        self.workingOutShown = True
        self.workBox = QLabel()
        self.workBox.setAlignment(Qt.AlignCenter)
        self.workBox.setFont(QFont("Arial", 14))
        planckConstant = ((self.m * 1.6) / 3) * 10
        string1 = "Planck's Constant can be calulcated using the gradient of the graph\n"
        string2 = "The Line of Best Fit follows the equation V = hc/eλ \n"
        string3 = "h = Planck's Constant, Gradient = hc/e \n"
        string4 = "Calculated gradient = " + (str(round(self.m, 2)) + " x 10^-6 using Δy/Δx \n")
        string5 = "Rearrange for h, h = me/c (where m = gradient)\n"
        string6 = "Final Value of h = " + (str(round(planckConstant, 2))) + " x 10^-34"

        self.workBox.setText(string1 + string2 + string3 + string4 + string5 + string6)

        self.layout2.addWidget(self.workBox)


# Class which displays the calculation process for the Ramp fall practical
class CalculationRamp(QGroupBox):
    def __init__(self):
        super(CalculationRamp, self).__init__()

        self.workingOut1 = False
        self.workingOut2 = False

        self.initView()

    def initView(self):
        self.setStyleSheet("background-color: white;")
        self.layout = QHBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter)
        self.layout2 = QVBoxLayout()
        # self.layout2.setAlignment(Qt.AlignCenter)
        diagram = QLabel()
        pix = QPixmap(resource_path("./img/rampDiagram1.png"))
        diagram.setPixmap(pix)

        self.layout.addWidget(diagram)

        self.layout.addLayout(self.layout2)
        self.setLayout(self.layout)

    def showWorking1(self):
        self.workingOut1 = True
        self.workBox1 = QLabel()
        self.workBox1.setAlignment(Qt.AlignCenter)
        self.workBox1.setFont(QFont("Arial", 14))
        string1 = "Since there is no resistance, the ball rolls freely down the ramp\n"
        string2 = "Acceleration downward is equal to Wsin(θ)/m\n"
        string3 = "where W = Weight = mg, and m is mass of the ball\n"

        self.workBox1.setText(string1 + string2 + string3)
        self.layout2.addWidget(self.workBox1)

    def showWorking2(self):
        self.workingOut2 = True
        self.workBox2 = QLabel()
        self.workBox2.setAlignment(Qt.AlignCenter)
        self.workBox2.setFont(QFont("Arial", 14))
        string1 = "Use s = ut + 0.5at\u00b2\n"
        string2 = "s = length down the ramp, u = initial speed = 0 m/s, a = gsin(θ) \n"
        string3 = "Substitute measured values for s and t and rearrange for g \n"
        string4 = "g = s/0.5sin(θ)t\u00b2, s = 0.5m, t = 0.45s, θ = 30°"
        string5 = "\ng = 9.88 m/s\u00b2"

        self.workBox2.setText(string1 + string2 + string3 + string4 + string5)
        self.layout2.addWidget(self.workBox2)

    def removeWorking1(self):
        self.workingOut1 = False
        self.layout2.removeWidget(self.workBox1)
        self.workBox1.deleteLater()

    def removeWorking2(self):
        self.workingOut2 = False
        self.layout2.removeWidget(self.workBox2)
        self.workBox2.deleteLater()

    def getWorkingOut1Shown(self):
        return self.workingOut1

    def getWorkingOut2Shown(self):
        return self.workingOut2


# Class definition for the canvas which draws the graph, utilises the matplotlib module
# Numpy module used alongside to draw the graph
class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi, tight_layout=True)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


# Class definition which creates an graphics object which can be moved around by the user
# Object is used in the DIY window
class MovableImage(QLabel):
    def __init__(self, width, height, imgPath):
        super(MovableImage, self).__init__()

        self.setStyleSheet("background:transparent")

        self.itemPixmap = QPixmap(imgPath)
        self.item = QGraphicsPixmapItem(self.itemPixmap)

        self.setFixedSize(width, height)
        self.setPixmap(QPixmap(imgPath))
        self.drag_start_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setCursor(Qt.ClosedHandCursor)
            self.drag_start_pos = event.pos()
            self.raise_()

    def mouseMoveEvent(self, event):
        if self.drag_start_pos is not None:
            self.move(self.pos() + event.pos() - self.drag_start_pos)
        super(MovableImage, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.drag_start_pos = None
        self.setCursor(Qt.ArrowCursor)
        self.move(self.pos())

    def setPosition(self, position):
        self.item.setPos(position)

    position = pyqtProperty(QPointF, fset=setPosition)


# Merge sort procedure, used when sorting the data in the tables used in the DIY window
def mergeSort(array):
    if len(array) > 1:
        mid = len(array) // 2
        L = array[:mid]
        R = array[mid:]

        mergeSort(L)

        mergeSort(R)

        i = 0
        j = 0
        k = 0

        while i < len(L) and j < len(R):
            if L[i] < R[j]:
                array[k] = L[i]
                i = i + 1
            else:
                array[k] = R[j]
                j = j + 1
            k = k + 1

        while i < len(L):
            array[k] = L[i]
            i = i + 1
            k = k + 1

        while j < len(R):
            array[k] = R[j]
            k = k + 1
            j = j + 1


def main():
    app = QApplication(sys.argv)
    window = MenuWindow()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
