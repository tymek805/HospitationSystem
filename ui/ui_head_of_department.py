from PyQt6.QtWidgets import QSpacerItem, QTableWidget, QTableWidgetItem, QHeaderView, QGridLayout, QComboBox, \
    QStyledItemDelegate

from db.database_manager import DatabaseManager
from ui.main_componenets import *
import random

class HeadOfDepartmentController(UserController):
    def __init__(self, content_layout, db_manager):
        super().__init__(content_layout)
        self.db_manager: DatabaseManager = db_manager
        self.main_screen()

    def main_screen(self):
        self.clear_content()
        container = self.main_container()
        self.action_button("Wybieranie członków zespołu hospitacyjnego", self.choose_inspected, container.layout())
        container.layout().addItem( QSpacerItem(40, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        self.content_layout.addWidget(container)

    def head(self, title, auto_button_action, back_button_action) -> QWidget:
        container = QWidget()
        container_layout = QHBoxLayout()

        actions_label = QLabel(title)
        actions_label.setFont(QFont("Arial", 14))
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        container_layout.addWidget(actions_label)
        container_layout.addSpacerItem(spacer)
        if auto_button_action is not None:
            auto_button = QPushButton("Generuj automatycznie")
            auto_button.clicked.connect(auto_button_action)
            container_layout.addWidget(auto_button)
        back_button = QPushButton("Powrót")
        back_button.clicked.connect(back_button_action)
        container_layout.addWidget(back_button)
        container.setLayout(container_layout)
        return container

    def choose_inspected(self):
        # inspected_list = self.db_manager.get_newest_recommended_list()
        inspected_list = self.db_manager.get_employees()
        if not inspected_list:
            show_error_message("Brak osób proponowanych do hospitacji\nWybranie zespołów niemożliwe")
            return self.main_screen()
        self.clear_content()
        self.content_layout.addWidget(self.head("Osoby proponowane do hospitacji", None, self.main_screen))

        self.table = QTableWidget()
        self.table.setRowCount(len(inspected_list))  # Liczba wierszy
        self.table.setColumnCount(6)  # Liczba kolumn
        self.table.setHorizontalHeaderLabels(["Imię", "Nazwisko", "Katedra", "Czas od ostatniej \nhospitacji", "Wybrany zespół", ""])
        self.table.setWordWrap(False)


        # Wypełnianie tabeli danymi
        for row, (employee_id, name, last_name, department, time) in enumerate(inspected_list):
            item_name = QTableWidgetItem(name)
            item_last_name = QTableWidgetItem(last_name)
            item_department = QTableWidgetItem(department)
            team = self.db_manager.get_team_for(employee_id)
            team_string = '\n'.join([f"{mem[1]} {mem[2]} - {mem[3]}" for mem in team]) if team else "-"
            item_team = QTableWidgetItem(team_string)

            # Ustawianie tooltipów dla komórek
            item_name.setToolTip(name)
            item_last_name.setToolTip(last_name)
            item_department.setToolTip(department)
            item_team.setToolTip(team_string)

            self.table.setItem(row, 0, item_name)
            self.table.setItem(row, 1, item_last_name)
            self.table.setItem(row, 2, item_department)

            self.table.setItem(row, 3, QTableWidgetItem(str(time) + " dni"))
            self.table.setItem(row, 4, item_team)
            choose_button = QPushButton("Wybierz członków zespołu")
            choose_button.clicked.connect(lambda _, emp_id=employee_id: self.choose_inspection_team(emp_id))
            self.table.setCellWidget(row, 5, choose_button)

        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setMinimumHeight(40)
        self.table.verticalHeader().setDefaultSectionSize(40)
        self.table.setColumnWidth(2, 110)
        self.table.setColumnWidth(3, 110)
        self.table.setColumnWidth(4, 130)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)

        # Włączenie wyświetlania pełnego tekstu po najechaniu kursorem
        self.table.setToolTipDuration(-1)
        self.table.setMouseTracking(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.content_layout.addWidget(self.table)



    def choose_inspection_team(self, employee_id):
        self.clear_content()
        employees: list[tuple] = self.db_manager.get_employees()
        chosen_employee = employees.pop([emp[0] for emp in employees].index(employee_id))
        self.content_layout.addWidget(self.head("Członkowie zespołu hospitacyjnego dla hospitowanego\n"
                                                f"{chosen_employee[1]} {chosen_employee[2]} - {chosen_employee[3]}",
                                                lambda: self.auto_generated_teams(employee_id), self.choose_inspected))

        grid_layout = QGridLayout()  # For the two comboboxes
        button_layout = QHBoxLayout()  # For the confirmation button

        # Labels
        label1 = QLabel("Wybierz przewodniczącego:")
        label2 = QLabel("Wybierz drugiego członka zespołu:")

        # ComboBoxes for employee selection
        self.employee_box_1 = QComboBox()
        self.employee_box_2 = QComboBox()

        # Populate the ComboBoxes
        employees_sorted = sorted(employees, key=lambda x: (x[2], x[1], x[3]))
        for emp in employees_sorted:
            display_text = f"{emp[1]} {emp[2]} - {emp[3]}"
            self.employee_box_1.addItem(display_text, emp[0])  # ID as data
            self.employee_box_2.addItem(display_text, emp[0])  # ID as data

        self.employee_box_1.setCurrentIndex(-1)
        self.employee_box_2.setCurrentIndex(-1)

        # Confirmation button
        confirm_button = QPushButton("Zatwierdź")
        confirm_button.setFixedSize(100, 30)
        def confirm_selection():
            # Get selected employee IDs from both combo boxes
            emp1_id = self.employee_box_1.currentData()
            emp2_id = self.employee_box_2.currentData()
            if emp1_id is None or emp2_id is None:
                show_error_message("Nie wybrano wszystkich członków")
                return
            if emp1_id == emp2_id:
                show_error_message("Członkowie nie mogą się powtarzać")
                return
            self.select_team(employee_id, emp1_id, emp2_id)
        confirm_button.clicked.connect(confirm_selection)

        # Adding widgets to layouts
        grid_layout.addWidget(label1, 0, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        grid_layout.addWidget(self.employee_box_1, 0, 1)

        grid_layout.addWidget(label2, 1, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        grid_layout.addWidget(self.employee_box_2, 1, 1)

        button_layout.addStretch()  # Push button to the right
        button_layout.addWidget(confirm_button)

        # Adding sub-layouts to main layout
        sum_layout = QVBoxLayout()
        sum_layout.addLayout(grid_layout)
        sum_layout.addStretch()  # Push button layout to the bottom
        sum_layout.addLayout(button_layout)
        container = QWidget()
        container.setLayout(sum_layout)
        self.content_layout.addWidget(container)

    def auto_generated_teams(self, employee_id):
        self.clear_content()
        self.content_layout.addWidget(self.head("Automatycznie wygenerowane zespoły", None, lambda: self.choose_inspection_team(employee_id)))

        employees: list[tuple] = self.db_manager.get_employees()
        chosen_employee = employees.pop([emp[0] for emp in employees].index(employee_id))

        teams: list[tuple] = []
        for idx in range(10):
            diff_department_emps: [] = [emp for emp in employees if emp[3] != chosen_employee[3]]
            if len(diff_department_emps) <= 0:
                teams.append(tuple(random.sample(employees, 2)))
            elif len(diff_department_emps) <= 0:
                teams.append(
                    (random.choice(diff_department_emps),
                    random.choice(employees))
                )
            else:
                teams.append(tuple(random.sample(diff_department_emps, 2)))

        # Scroll area for teams
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QGridLayout(scroll_widget)

        # Dynamically add teams with buttons
        header_label1 = QLabel("Przewodniczący")
        header_label2 = QLabel("Drugi członek")
        header_label1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_label2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_label1.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_label2.setStyleSheet("font-weight: bold; font-size: 14px;")
        scroll_layout.addWidget(header_label1, 0, 0)
        scroll_layout.addWidget(header_label2, 0, 1)
        for row, team in enumerate(teams):
            row+=1
            # Team member 1
            person_1_label = QLabel(f"{team[0][1]} {team[0][2]} - {team[0][3]}")
            scroll_layout.addWidget(person_1_label, row, 0)

            # Team member 2
            person_2_label = QLabel(f"{team[1][1]} {team[1][2]} - {team[1][3]}")
            scroll_layout.addWidget(person_2_label, row, 1)

            # Select button
            select_button = QPushButton("Wybierz")
            select_button.clicked.connect(lambda _, emp1=team[0][0], emp2=team[1][0], c=employee_id: self.select_team(c ,emp1, emp2))
            scroll_layout.addWidget(select_button, row, 2)

        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        self.content_layout.addWidget(scroll_area)

        self.content_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

    def select_team(self, chosen_inspected_id, team_mem1_id, team_mem2_id):
        print(f"{chosen_inspected_id} {team_mem1_id} {team_mem2_id}")
        self.db_manager.insert_team_for(chosen_inspected_id, team_mem1_id, team_mem2_id)

        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle("")
        msg_box.setText("Dodano zespół hospitacyjny")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
        self.main_screen()
