from PyQt5.QtGui import QFont, QIntValidator
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit


class LabelledIntField(QWidget):
    def __init__(self, title, initial_value=None):
        super(LabelledIntField, self).__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.label = QLabel()
        self.label.setText(title)
        self.label.setFixedWidth(140)
        self.label.setFont(QFont("Arial", weight=QFont.Bold))
        layout.addWidget(self.label)

        self.line_edit = QLineEdit(self)
        self.line_edit.setFixedWidth(120)
        self.line_edit.setValidator(QIntValidator())

        if initial_value:
            self.line_edit.setText(str(initial_value))

        layout.addWidget(self.line_edit)
        layout.addStretch()

    def set_label_width(self, width):
        self.label.setFixedWidth(width)

    def set_input_width(self, width):
        self.line_edit.setFixedWidth(width)

    def get_value(self):
        return int(self.line_edit.text())
