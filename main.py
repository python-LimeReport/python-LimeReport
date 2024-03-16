import sys
from PySide6.QtWidgets import QApplication
import LimeReport


if __name__ == "__main__":
    app = QApplication([])
    report = LimeReport.ReportEngine()
    sys.exit(report.designReport())