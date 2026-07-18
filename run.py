
from PyQt5.QtGui import QFont
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QListWidgetItem, QMessageBox, QDialog
from PyQt5 import uic
from PyQt5.QtCore import Qt, QThread, QObject, pyqtSignal

from database.repository import insert_job, get_all_category_titles
from database.catconverter import category_converter
from database.filters import (
    count_backend_frontend_jobs,
    average_salary_by_categories,
    remote_salary_by_categories,
    gender_distribution_by_categories,
    work_type_by_categories,
    experience_years_by_categories,
)
from tools.report import generate_report

from services.jobvision import run
from services.getallcat import fetch_and_save_job_categories

from ui.ui_main import Ui_Dialog

class ReportWorker(QObject):

    finished = pyqtSignal()
    error = pyqtSignal(str)


    def __init__(self, categories):
        super().__init__()
        self.categories = categories


    def run(self):

        try:

            CATEGORIES = self.categories


            data = {
                "backend_frontend": count_backend_frontend_jobs(),

                "salary": average_salary_by_categories(
                    CATEGORIES
                ),

                "remote": remote_salary_by_categories(
                    CATEGORIES
                ),

                "gender": gender_distribution_by_categories(
                    CATEGORIES
                ),

                "work_type": work_type_by_categories(
                    CATEGORIES
                ),

                "experience": experience_years_by_categories(
                    CATEGORIES
                )
            }


            generate_report(data)


            self.finished.emit()


        except Exception as e:

            self.error.emit(str(e))

class ExtractWorker(QObject):

    finished = pyqtSignal()
    progress = pyqtSignal(int)
    error = pyqtSignal(str)


    def __init__(self, categories):
        super().__init__()
        self.categories = categories


    def run(self):

        try:

            ca = category_converter(self.categories)

            total = len(ca)

            all_jobs = []

            for index, category in enumerate(ca):

                jobs = run([category])

                all_jobs.extend(jobs)


                percent = int(
                    ((index + 1) / total) * 100
                )

                self.progress.emit(percent)


            insert_job(
                jobs=all_jobs,
                source="jobvision"
            )


            self.finished.emit()


        except Exception as e:
            self.error.emit(str(e))

class Ui(QDialog, Ui_Dialog):

    def __init__(self):
        super(Ui, self).__init__()
        # uic.loadUi('C:/data/main_ui2.ui', self)

        # uic.loadUi('./ui/main.ui', self)
        self.setupUi(self)
        self.initUI()
        self.show()
        self.extract_thread = None
        self.report_thread = None
        self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint |
                            Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        
        

        self.load_categories()
        self.updatecat.clicked.connect(self.update_categories)
        self.extractdata.clicked.connect(self.extract_data)
        self.deleteselectedcat.clicked.connect(self.delete_selected_category)
        self.report.clicked.connect(self.generate_report)
        self.catcombo.currentTextChanged.connect(self.add_category_to_list)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        main_size = self.size()

        width_ratio = main_size.width() / self.initial_main_size.width()
        height_ratio = main_size.height() / self.initial_main_size.height()

        widgets = self.findChildren(QWidget)
        for widget in widgets:
            if widget.objectName() and "centralwidget" != widget.objectName():
                initial_size = self.initial_sizes[widget.objectName()]
                initial_position = self.initial_positions[widget.objectName()]

                new_width = int(initial_size.width() * width_ratio)
                new_height = int(initial_size.height() * height_ratio)
                new_x = int(initial_position.x() * width_ratio)
                new_y = int(initial_position.y() * height_ratio)

                widget.setGeometry(new_x, new_y, new_width, new_height)

    def initUI(self):
        self.initial_main_size = self.size()
        self.initial_positions = {}
        self.initial_sizes = {}

        widgets = self.findChildren(QWidget)
        for widget in widgets:
            if widget.objectName() and "centralwidget" != widget.objectName():
                self.initial_positions[widget.objectName()] = widget.pos()
                self.initial_sizes[widget.objectName()] = widget.size()

    def load_categories(self):
        categories = get_all_category_titles()

        for category in categories:
            self.catcombo.addItem(category)

    def add_category_to_list(self, category):
        if not category:
            return

        if self.catcombo.currentIndex() == 0:
            return
        
        items = [
            self.listView.item(i).text()
            for i in range(self.listView.count())
        ]

        if category not in items:
            self.listView.addItem(QListWidgetItem(category))

    def update_categories(self):

        try:
            self.setEnabled(False)

            fetch_and_save_job_categories()

            self.setEnabled(True)

            self.catcombo.clear()
            self.load_categories()

            self.show_message(
                "دسته‌بندی‌ها با موفقیت بروزرسانی شدند.",
                QMessageBox.Information,
                "موفقیت"
            )

        except Exception as e:

            self.setEnabled(True)

            self.show_message(
                f"خطا در بروزرسانی دسته‌بندی‌ها:\n{e}",
                QMessageBox.Critical,
                "خطا"
            )

    def extract_data(self):

        if self.extract_thread and self.extract_thread.isRunning():

            self.show_message(
                "استخراج اطلاعات در حال انجام است.\nلطفاً تا پایان صبر کنید.",
                QMessageBox.Warning,
                "هشدار"
            )

            return


        CATEGORIES = [
            self.listView.item(i).text()
            for i in range(self.listView.count())
        ]


        if not CATEGORIES:

            self.show_message(
                "هیچ دسته‌بندی انتخاب نشده است.",
                QMessageBox.Warning,
                "هشدار"
            )

            return


        self.extract_thread = QThread()

        self.worker = ExtractWorker(CATEGORIES)

        self.worker.moveToThread(
            self.extract_thread
        )


        self.extract_thread.started.connect(
            self.worker.run
        )


        self.worker.progress.connect(
            self.update_progress
        )


        self.worker.finished.connect(
            self.extract_finished
        )


        self.worker.error.connect(
            self.extract_error
        )


        self.worker.finished.connect(
            self.extract_thread.quit
        )


        self.worker.finished.connect(
            self.worker.deleteLater
        )


        self.extract_thread.finished.connect(
            self.extract_thread.deleteLater
        )


        self.label_4.setText("0%")


        self.extract_thread.start()

    def delete_selected_category(self):
        selected_items = self.listView.selectedItems()

        if not selected_items:
            self.show_message(
                "لطفاً یک دسته‌بندی را انتخاب کنید.",
                QMessageBox.Warning,
                "هشدار"
            )
            return

        for item in selected_items:
            self.listView.takeItem(
                self.listView.row(item)
            )

    def generate_report(self):


        if self.report_thread and self.report_thread.isRunning():

            self.show_message(
                "گزارش در حال ساخته شدن است.\nلطفاً صبر کنید.",
                QMessageBox.Warning,
                "هشدار"
            )

            return


        CATEGORIES = [
            self.listView.item(i).text()
            for i in range(self.listView.count())
        ]


        if not CATEGORIES:

            self.show_message(
                "هیچ دسته‌بندی انتخاب نشده است.",
                QMessageBox.Warning,
                "هشدار"
            )

            return



        self.report_thread = QThread()


        self.report_worker = ReportWorker(
            CATEGORIES
        )


        self.report_worker.moveToThread(
            self.report_thread
        )


        self.report_thread.started.connect(
            self.report_worker.run
        )


        self.report_worker.finished.connect(
            self.report_finished
        )


        self.report_worker.error.connect(
            self.report_error
        )


        self.report_worker.finished.connect(
            self.report_thread.quit
        )


        self.report_worker.finished.connect(
            self.report_worker.deleteLater
        )


        self.report_thread.finished.connect(
            self.report_thread.deleteLater
        )


        self.report_thread.start()

    def show_message(self, text, msg_type=QMessageBox.Information, title="پیام"):
        
        msg = QMessageBox(self)

        msg.setIcon(msg_type)
        msg.setWindowTitle(title)
        msg.setText(text)

        msg.setStyleSheet("""
            QMessageBox {
                background:#111827;
            }

            QMessageBox QLabel {
                color:white;
                font-size:14px;
            }

            QMessageBox QPushButton {
                background:#5B5EF5;
                color:white;
                border:none;
                border-radius:8px;
                padding:8px 20px;
                min-width:80px;
            }

            QMessageBox QPushButton:hover {
                background:#7074FF;
            }
        """)

        return msg.exec_()   

    def update_progress(self, value):

        self.label_4.setText(
            f"{value}%"
        )


    def extract_finished(self):

        self.label_4.setText(
            "100%"
        )

        self.show_message(
            "استخراج اطلاعات با موفقیت انجام شد.",
            QMessageBox.Information,
            "موفقیت"
        )


    def extract_error(self, error):

        self.show_message(
            f"خطا در استخراج:\n{error}",
            QMessageBox.Critical,
            "خطا"
        )

    def report_finished(self):

        self.show_message(
            "گزارش با موفقیت ساخته شد.",
            QMessageBox.Information,
            "موفقیت"
        )


    def report_error(self, error):

        self.show_message(
            f"خطا در ساخت گزارش:\n{error}",
            QMessageBox.Critical,
            "خطا"
        )


if __name__ == '__main__':
    app = QApplication(sys.argv)
    font = QFont("Vazirmatn", 10)
    app.setFont(font)
    dialog = Ui()
    dialog.exec_()
