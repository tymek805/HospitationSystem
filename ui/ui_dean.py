from PyQt6.QtWidgets import QSpacerItem, QTextEdit

from ui.main_componenets import *

# from ui.reports import reports

class DeanController(UserController):
    def __init__(self, content_layout, db_manager):
        super().__init__(content_layout)
        self.db_manager = db_manager
        self.main_screen()

    def main_screen(self):
        self.clear_content()
        container = self.main_container()
        self.action_button("Raporty hospitacji", self.reports_screen, container.layout())
        self.action_button("Zatwierdzanie ramowego harmonogramu hspitacji", lambda: print("nieobsługiwane"), container.layout())
        container.layout().addItem( QSpacerItem(40, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        self.content_layout.addWidget(container)

    def reports_screen(self):
        self.clear_content()
        container = QWidget()
        container_layout = QHBoxLayout()

        actions_label = QLabel("Dostępne raporty:")
        actions_label.setFont(QFont("Arial", 14))
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        back_button = QPushButton("Powrót")
        back_button.clicked.connect(self.main_screen)
        container_layout.addWidget(actions_label)
        container_layout.addSpacerItem(spacer)
        container_layout.addWidget(back_button)
        container.setLayout(container_layout)

        self.content_layout.addWidget(container)

        reports = self.db_manager.get_reports()
        for report in reports:
            report_title = f"{report[3]} {report[1]}"
            UserController.action_button(report_title, lambda: self.reports_details(report), self.content_layout,
                                         Qt.AlignmentFlag.AlignHCenter)

    def reports_details(self, report):
        self.clear_content()
        container = QWidget()
        container_layout = QHBoxLayout()
        print(report)
        actions_label = QLabel(
            f"Raport hospitacji w semestrze \"{report[3]} {report[1]}\"")
        actions_label.setFont(QFont("Arial", 14))
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        back_button = QPushButton("Powrót")
        back_button.clicked.connect(self.reports_screen)
        container_layout.addWidget(actions_label)
        container_layout.addSpacerItem(spacer)
        container_layout.addWidget(back_button)
        container.setLayout(container_layout)
        self.content_layout.addWidget(container)

        report_container = QWidget()
        report_layout = QVBoxLayout()

        report_text = QTextEdit()
        report_text.setReadOnly(True)
        text = self.load_file_content(report[0])
        report_text.setText(text)
        report_text.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        report_layout.addWidget(report_text)
        # report_layout.addWidget(side_panel_container, 1)

        report_container.setLayout(report_layout)
        self.content_layout.addWidget(report_container)

    def load_file_content(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                return content
        except Exception as e:
            return f"Error loading file: {str(e)}"