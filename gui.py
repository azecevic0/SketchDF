import sys

import numpy as np

from matplotlib.backend_bases import MouseButton
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.backends.backend_qtagg import \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.figure import Figure

from numerical_methods import IntegralCurve, RungeKutta, Euler
from expression_parser import Parser, evaluate_AST

DEFAULT_XLIM = (-5, 5)
DEFAULT_YLIM = (-5, 5)

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.ast = None
        self.func = None
        self.plots = []

    def setup_ui(self):
        # self.resize(800, 800)
        self.setWindowTitle('SketchDF')
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QtWidgets.QVBoxLayout(self.central_widget)

        self.graph_canvas = FigureCanvas(Figure(layout='tight'))
        self.toolbar = NavigationToolbar(self.graph_canvas, self)
        main_layout.addWidget(self.toolbar)

        control_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(control_layout)
        
        diff_label = QtWidgets.QLabel("x' = ")
        control_layout.addWidget(diff_label)

        self.formula_line_edit = QtWidgets.QLineEdit()
        control_layout.addWidget(self.formula_line_edit)

        combo_box = QtWidgets.QComboBox()
        combo_box.addItems(['Direction field', 'Slope field'])
        control_layout.addWidget(combo_box)
        self.combo_box = combo_box

        submit_button = QtWidgets.QPushButton('Submit')
        control_layout.addWidget(submit_button)
        submit_button.clicked.connect(self.submit)
        
        main_layout.addWidget(self.graph_canvas)

        self._static_ax = self.graph_canvas.figure.subplots()
        self._static_ax.set_xlim(DEFAULT_XLIM)
        self._static_ax.set_ylim(DEFAULT_YLIM)
        
        self.graph_canvas.mpl_connect('button_press_event', self.on_press)
        self.graph_canvas.mpl_connect('button_release_event', self.on_release)
        

        
    def submit(self):
        formula_string = self.formula_line_edit.text()
        try:
            parser = Parser(formula_string)
            self.ast = parser.parse()
            self.func = evaluate_AST(self.ast)
            self.plots = []
            self.plot_field()
        except SyntaxError as e:
            print(self.ast, file=sys.stderr)
            error_message = f'Syntax error: {e}.'
            QtWidgets.QMessageBox.critical(self, 'Parsing failure!', error_message,
                                           QtWidgets.QMessageBox.StandardButton.Ok)
                                        

    def plot_field(self):
        ts = np.linspace(self._static_ax.get_xlim()[0], self._static_ax.get_xlim()[1], 15)
        xs = np.linspace(self._static_ax.get_ylim()[0], self._static_ax.get_ylim()[1], 15) 
        
        ks = self.func(xs)

        boundsX = self._static_ax.get_xlim()
        boundsY = self._static_ax.get_ylim()  
        self._static_ax.clear()
        self._static_ax.set_xlim(boundsX)
        self._static_ax.set_ylim(boundsY)

        drawArrows = True if self.combo_box.currentText() == 'Direction field' else False

        c = np.sqrt(((boundsX[1] - boundsX[0]) ** 2 + (boundsY[1] - boundsY[0]) ** 2)) / 200
        deltas = np.sqrt(c/(1 + ks**2)) / 2
        for x, k, delta in zip(xs, ks, deltas):
            self._static_ax.plot([ts-delta, ts+delta], [x-delta*k, x+delta*k], '-', color='black')

            if drawArrows:
                for t in ts:    
                    self._static_ax.arrow(t-delta, x-delta*k, 2*delta, 2*delta*k,
                        shape='full', lw=0, length_includes_head=False,
                        head_width=c, head_length=2*c, color='black')
        self.graph_canvas.draw()
                
    def on_release(self, event):
        ax = event.canvas.figure.axes[0]
        if event.button in (MouseButton.LEFT, MouseButton.RIGHT) and ax.get_navigate_mode() and self.ast:
            self.plot_field()           
            min_t, max_t = self._static_ax.get_xlim()
            min_x, max_x = self._static_ax.get_ylim()

            for ic in self.plots:
                if min_t <= ic.t_init <= max_t and min_x <= ic.x_init <= max_x:
                    ts, xs = ic(min_t, max_t)
                    self._static_ax.plot(ts, xs, '-', color='red')
    
    def on_press(self, event):
        ax = event.canvas.figure.axes[0]
        x_data, y_data = event.xdata, event.ydata
        if event.button == MouseButton.LEFT and not ax.get_navigate_mode() and self.ast and x_data and y_data:

            minT, maxT = self._static_ax.get_xlim()

            ic = IntegralCurve(self.func, x_data, y_data)
            self.plots.append(ic)

            ts, xs = ic(minT, maxT)
            self._static_ax.plot(ts, xs, '-', color='red')
            self.graph_canvas.draw()
    
            print(f'Initial condition: x({x_data:.2f}) = {y_data:.2f}', file=sys.stderr)


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
