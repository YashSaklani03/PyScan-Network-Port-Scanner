from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit
from main import start_scan

def run_pyqt():
    app = QApplication([])
    w = QWidget()
    layout = QVBoxLayout()

    host_input = QLineEdit()
    host_input.setPlaceholderText("Enter host")
    layout.addWidget(host_input)

    btn = QPushButton("Scan")
    layout.addWidget(btn)

    def clicked():
        start_scan(host_input.text())

    btn.clicked.connect(clicked)

    w.setLayout(layout)
    w.show()
    app.exec_()
