import sys

import numpy as np

from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.backends.backend_qtagg import \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.qt_compat import QtWidgets, QtGui
from matplotlib.figure import Figure
import expression_parser

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

        graph_canvas = FigureCanvas(Figure(layout='tight'))
        toolbar = NavigationToolbar(graph_canvas, self)
        main_layout.addWidget(toolbar)

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
        submit_button.clicked.connect(lambda _: self.submit())
        
        main_layout.addWidget(graph_canvas)

        self._static_ax = graph_canvas.figure.subplots()
        t = np.linspace(0, 10, 1001)
        self._static_ax.set_xlim(DEFAULT_XLIM)
        self._static_ax.set_ylim(DEFAULT_YLIM)
        self._static_ax.plot(t, np.tan(t), '-')
        
    def submit(self):
        formula_string = self.formula_line_edit.text()
        try:
            parser = expression_parser.Parser(formula_string)
            ast = parser.parse()
            print(ast)
        except Exception as e:
 
            error_message = "Greška u parsiranju: " + str(e)
            QtWidgets.QMessageBox.critical(self, "Neuspešno parsiranje!", error_message,
                                           QtWidgets.QMessageBox.StandardButton.Ok)




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


