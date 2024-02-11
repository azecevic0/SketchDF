import sys

import numpy as np

from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.backends.backend_qtagg import \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.qt_compat import QtWidgets, QtGui
from matplotlib.figure import Figure
import expression_parser
from numeric_methods import *
from expression_parser import Parser, evaluate_AST

DEFAULT_XLIM = (-5, 5)
DEFAULT_YLIM = (-5, 5)

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        # self.resize(800, 800)
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QtWidgets.QVBoxLayout(self.central_widget)

        self.graph_canvas = FigureCanvas(Figure(layout='tight'))
        self.toolbar = NavigationToolbar(self.graph_canvas, self)
        main_layout.addWidget(self.toolbar)

        control_layout = QtWidgets.QHBoxLayout(self.central_widget)
        main_layout.addLayout(control_layout)
        
        diff_label = QtWidgets.QLabel("x' = ")
        control_layout.addWidget(diff_label)

        self.formula_line_edit = QtWidgets.QLineEdit()
        control_layout.addWidget(self.formula_line_edit)

        combo_box = QtWidgets.QComboBox()
        combo_box.addItems(['Direction field', 'Slope field'])
        control_layout.addWidget(combo_box)

        submit_button = QtWidgets.QPushButton('Submit')
        control_layout.addWidget(submit_button)
        submit_button.clicked.connect(self.submit)
        
        main_layout.addWidget(self.graph_canvas)

        self._static_ax = self.graph_canvas.figure.subplots()
        self._static_ax.set_xlim(DEFAULT_XLIM)
        self._static_ax.set_ylim(DEFAULT_YLIM)
        
        self.graph_canvas.mpl_connect('button_press_event', lambda event: self.onClick(event))

        
    def submit(self):
        formula_string = self.formula_line_edit.text()
        try:
            parser = Parser(formula_string)
            ast = parser.parse()
            self.ast = ast
            #self._static_ax.callbacks.connect("xlim_changed", lambda artist: print("sta"))
        except Exception as e:
 
            print(ast, file=sys.stderr)
            self.plot(ast)
        except SyntaxError as e:
            error_message = "Greška u parsiranju: " + str(e)
            QtWidgets.QMessageBox.critical(self, "Neuspešno parsiranje!", error_message,
                                           QtWidgets.QMessageBox.StandardButton.Ok)

    def plot(self, ast):
        ts = np.linspace(self._static_ax.get_xlim()[0], self._static_ax.get_xlim()[1], 15)
        xs = np.linspace(self._static_ax.get_ylim()[0], self._static_ax.get_ylim()[1], 15) 
        
        ks = evaluate_AST(ast)(xs)

        boundsX = self._static_ax.get_xlim()
        boundsY = self._static_ax.get_ylim()  
        self._static_ax.clear()
        self._static_ax.set_xlim(boundsX)
        self._static_ax.set_ylim(boundsY)

        c = np.sqrt(((boundsX[1] - boundsX[0]) ** 2 + (boundsY[1] - boundsY[0]) ** 2)) / 200
        deltas = np.sqrt(c/(1 + ks**2)) / 2
        for x, k, delta in zip(xs, ks, deltas):
            self._static_ax.plot([ts-delta, ts+delta], [x-delta*k, x+delta*k], '-', color='black')
        self.graph_canvas.draw()
                
        #ts = np.linspace(

    def onZoomChange(self):
        print("sta")
        #self.plot( ast)
    def onClick(self, event):
        try:
            x_data, y_data = event.inaxes.transData.inverted().transform((event.x, event.y))
            if self.ast is None:
                raise Exception("ast not defined")
        except Exception as e:
            return
        
        minT, maxT = self._static_ax.get_xlim()


        ts, xs = RungeKutta(minT, maxT, self.ast, x_data, y_data)
        self._static_ax.plot(ts, xs, '-')
        self.graph_canvas.draw()

        print(x_data, y_data)
        


if __name__ == "__main__":
    # Check whether there is already a running QApplication (e.g., if running
    # from an IDE).
    qapp = QtWidgets.QApplication.instance()
    if not qapp:
        qapp = QtWidgets.QApplication(sys.argv)

    app = ApplicationWindow()
    app.show()
    app.activateWindow()
    app.raise_()
    qapp.exec()
