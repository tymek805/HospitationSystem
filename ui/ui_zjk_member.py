from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QFrame, QSpacerItem, QSizePolicy, QCheckBox, QDialog, QGridLayout
)

from ui.main_componenets import *


# TODO:
#  - good back button for summary
#  - safety measure for none employee selected and none

class ZJKMemberController(UserController):
    def __init__(self, content_layout, db_manager):
        super().__init__(content_layout)
        self.db_manager = db_manager
        self.main_screen()

    def main_screen(self):
        self.clear_content()
        container = self.main_container()
        self.action_button("Zarządzanie wykazem osób proponowanych do hospitacji", self.list_of_employees, container.layout())
        container.layout().addItem( QSpacerItem(40, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        self.content_layout.addWidget(container)

    def list_of_employees(self):
        self.clear_content()
        header = QWidget()
        header_layout = QHBoxLayout()

        actions_label = QLabel("Osoby proponowane do hospitacji:")
        actions_label.setFont(QFont("Arial", 14))
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        buttons = QWidget()
        buttons_layout = QHBoxLayout()

        back_button = QPushButton("Powrót")
        back_button.clicked.connect(self.main_screen)

        continue_button = QPushButton("Podsumowanie")

        buttons_layout.addWidget(back_button)
        buttons_layout.addWidget(continue_button)
        buttons.setLayout(buttons_layout)

        header_layout.addWidget(actions_label)
        header_layout.addSpacerItem(spacer)
        header_layout.addWidget(buttons)
        header.setLayout(header_layout)

        self.content_layout.addWidget(header)

        # Create employee list
        all_list_content = QWidget()
        all_list_layout = QVBoxLayout(all_list_content)
        
        # Create first part
        employees = self.db_manager.get_employees_for_hospitation()
        overdue_employees = [list(employee) for employee in employees if employee[-1] >= 800]
        if overdue_employees:
            all_list_layout.addWidget(self.create_list_header("Pracownicy nie hospitowani w terminach podanych w zarządzeniu wewnętrznym"))
            all_list_layout.addWidget(self.create_employee_list(overdue_employees))

        suggested_employees = [list(employee) for employee in employees if employee[-1] < 800]
        if suggested_employees:
            all_list_layout.addWidget(self.create_list_header("Pracownicy hospitowani w terminach podanych w zarządzeniu wewnętrznym"))
            all_list_layout.addWidget(self.create_employee_list(suggested_employees))

        continue_button.clicked.connect(lambda : self.summary_screen(overdue_employees, suggested_employees))
        self.content_layout.addWidget(all_list_content)

    @staticmethod
    def create_employee_row(employee_id, name, surname, department, time_from_last_hospitalisation, employee_list, clickable=True):
        row_frame = QFrame()
        row_frame.setStyleSheet("border: 1px solid black; padding: 5px;")

        row_layout = QHBoxLayout(row_frame)

        name_label = QLabel(name)
        surname_label = QLabel(surname)
        department_label = QLabel(department)
        last_hospitation_label = QLabel(f"Czas od ostatniej hospitacji: {time_from_last_hospitalisation}")

        row_layout.addWidget(name_label)
        row_layout.addWidget(surname_label)
        row_layout.addWidget(department_label)
        row_layout.addWidget(last_hospitation_label)

        if clickable:
            row_layout.addStretch()

            select_checkbox = QCheckBox()
            select_checkbox.setStyleSheet("border: 1px solid black; padding: 5px;")
            select_checkbox.setText("Wybierz")

            row_layout.addWidget(select_checkbox)

            employee_list.append((select_checkbox, (employee_id, name, surname, department, time_from_last_hospitalisation)))

        # [label.setFixedWidth(width) for width, label in
        #  zip(max_labels_width, [name_label, surname_label, department_label, last_hospitation_label])]

        return row_frame

    @staticmethod
    def create_list_header(text):
        label = QLabel(text)
        label.setStyleSheet("font-style: italic; font-size: 14px;")
        return label

    def create_employee_list(self, employees, summary=False):
        list_container = QWidget()
        list_layout = QGridLayout(list_container)

        headers = ["Imię", "Nazwisko", "Katedra", "Czas od ostatniej hospitacji"]
        for col, header in enumerate(headers):
            label = QLabel(header)
            label.setStyleSheet("font-weight: bold; padding: 5px;")
            list_layout.addWidget(label, 0, col)

        checkboxes = []
        if not summary:
            select_all = QPushButton("Wybierz wszystkich")
            list_layout.addWidget(select_all, 0, len(headers))
            select_all.clicked.connect(lambda: [ch.setChecked(True) for ch in checkboxes])

        for row_idx, employee in enumerate(employees, start=1):
            for col_idx, value in enumerate(employee[1:]):
                label = QLabel(str(value))
                label.setStyleSheet("padding: 5px; border: 1px solid black;")
                list_layout.addWidget(label, row_idx, col_idx)

            if summary:
                delete_button = QPushButton("Usuń")
                delete_button.clicked.connect(lambda _, e=employee: self.delete_row(list_container, employees, e))
                list_layout.addWidget(delete_button, row_idx, len(headers))
            else:
                checkbox = QCheckBox("Wybierz")
                list_layout.addWidget(checkbox, row_idx, len(headers))
                employee.append(checkbox)
                checkboxes.append(checkbox)

        list_layout.setRowStretch(list_layout.rowCount(), 1)

        return list_container

    def delete_row(self, container, employees, row_id):
        container.hide()
        employees.remove(row_id)
        self.content_layout.addWidget(self.create_employee_list(employees, True))

    def summary_screen(self, overdue_list, normal_list):
        selected_employees = self.get_selected_users(overdue_list)

        if len(selected_employees) != len(overdue_list):
            dialog = NotificationDialog()
            if not dialog.exec():
                return

        self.clear_content()
        selected_employees += self.get_selected_users(normal_list)

        header = QWidget()
        header_layout = QHBoxLayout()

        actions_label = QLabel("Podsumowanie")
        actions_label.setFont(QFont("Arial", 14))
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        buttons = QWidget()
        buttons_layout = QHBoxLayout()

        back_button = QPushButton("Powrót")
        back_button.clicked.connect(self.list_of_employees)

        continue_button = QPushButton("Zatwierdź")
        continue_button.clicked.connect(lambda: self.confirm(selected_employees))

        buttons_layout.addWidget(back_button)
        buttons_layout.addWidget(continue_button)
        buttons.setLayout(buttons_layout)

        header_layout.addWidget(actions_label)
        header_layout.addSpacerItem(spacer)
        header_layout.addWidget(buttons)
        header.setLayout(header_layout)

        self.content_layout.addWidget(header)
        self.content_layout.addWidget(self.create_employee_list(selected_employees, True))

    def confirm(self, selected_employees):
        if not selected_employees:
            notification = EmptySelectedUsersDialog()
            if notification.exec():
                return

        self.db_manager.save_hospitation_employees_list(selected_employees)
        self.confirm_notification()

    def confirm_notification(self):
        notification = ConfirmationDialog()
        if notification.exec():
            self.main_screen()

    @staticmethod
    def get_selected_users(employee_list):
        return [employee[:-1] for employee in employee_list if employee[-1].isChecked()]

class NotificationDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Powiadomienie")
        self.setFixedSize(500, 250)

        main_layout = QVBoxLayout()

        message_text = (
            "Nie wszyscy pracownicy nie hospitowani w terminach podanych w zarządzeniu wewnętrznym zostali wybrani"
        )
        message_label = QLabel(message_text)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setFont(QFont("Arial", 12))
        message_label.setWordWrap(True)

        button_layout = QHBoxLayout()

        continue_button = QPushButton("Kontynuuj")
        back_button = QPushButton("Cofnij")

        continue_button.clicked.connect(self.accept)
        back_button.clicked.connect(self.reject)

        button_layout.addWidget(continue_button)
        button_layout.addWidget(back_button)

        main_layout.addWidget(message_label)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

class ConfirmationDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Powiadomienie")
        self.setFixedSize(250, 150)

        main_layout = QVBoxLayout()
        message_label = QLabel("Wykaz został przesłany")
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setFont(QFont("Arial", 12))

        continue_button = QPushButton("Kontynuuj")
        continue_button.clicked.connect(self.accept)

        main_layout.addWidget(message_label)
        main_layout.addWidget(continue_button)

        self.setLayout(main_layout)

class EmptySelectedUsersDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Powiadomienie")
        self.setFixedSize(250, 150)

        main_layout = QVBoxLayout()
        message_label = QLabel("Nie zostali wybrani żadni pracownicy")
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setWordWrap(True)
        message_label.setFont(QFont("Arial", 12))

        continue_button = QPushButton("Kontynuuj")
        continue_button.clicked.connect(self.accept)

        main_layout.addWidget(message_label)
        main_layout.addWidget(continue_button)

        self.setLayout(main_layout)
