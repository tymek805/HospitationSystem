from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QFrame, QSpacerItem, QSizePolicy, QTextEdit
)
import functools
from ui.main_componenets import UserController


class Protocols:
    def __init__(self, user_controller: UserController, protocols):
        self.user_controller = user_controller
        self.protocols = protocols

    def protocols_screen_1(self):
        self.user_controller.clear_content()
        container = QWidget()
        container_layout = QHBoxLayout()

        actions_label = QLabel("Dostępne protokoły:")
        actions_label.setFont(QFont("Arial", 14))
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        back_button = QPushButton("Powrót")
        back_button.clicked.connect(self.user_controller.main_screen)
        container_layout.addWidget(actions_label)
        container_layout.addSpacerItem(spacer)
        container_layout.addWidget(back_button)
        container.setLayout(container_layout)
        self.user_controller.content_layout.addWidget(container)

        for protocol in self.protocols:
            protocol_title = f"{self.user_controller.db_manager.get_employee_full_name(protocol[0])} - {protocol[4]}"
            UserController.action_button(protocol_title, functools.partial(self.protocols_screen_2, protocol), self.user_controller.content_layout,
                               Qt.AlignmentFlag.AlignHCenter)
        self.user_controller.content_layout.addStretch()

    def protocols_screen_2(self, protocol):
        self.user_controller.clear_content()

        container = QWidget()
        container_layout = QHBoxLayout()

        actions_label = QLabel(
            f"Protokół hospitacji w semestrze \"{self.user_controller.db_manager.get_semester_name(protocol[-1])}\"")
        actions_label.setFont(QFont("Arial", 14))
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        back_button = QPushButton("Powrót")
        back_button.clicked.connect(lambda: self.protocols_screen_1())
        container_layout.addWidget(actions_label)
        container_layout.addSpacerItem(spacer)
        container_layout.addWidget(back_button)
        container.setLayout(container_layout)
        self.user_controller.content_layout.addWidget(container)
        protocol_container = QWidget()
        protocol_layout = QHBoxLayout()

        protocol_text = QTextEdit()
        protocol_text.setReadOnly(True)
        text = self.user_controller.db_manager.load_protocol_content(protocol[5])
        protocol_text.setText(text)
        protocol_text.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        side_panel_container = QFrame()
        side_panel_container.setFrameShape(QFrame.Shape.Box)
        side_panel_container.setFrameShadow(QFrame.Shadow.Raised)
        side_panel_container.setStyleSheet("border: 2px solid black; border-radius: 5px; padding: 10px;")
        side_panel_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        side_panel = QVBoxLayout()
        side_panel.addWidget(QLabel(f"Ocena końcowa: {protocol[3]}"))
        side_panel.addWidget(QLabel(f"Data utworzenia: {protocol[4]}"))
        side_panel.addWidget(QLabel(f"Hospitowany: {self.user_controller.db_manager.get_fullname(self.user_controller.db_manager.get_employee_id_from_hospitalization(protocol[1]))}"))

        side_panel_container.setLayout(side_panel)
        protocol_layout.addWidget(protocol_text, 3)
        protocol_layout.addWidget(side_panel_container, 1)

        protocol_container.setLayout(protocol_layout)
        self.user_controller.content_layout.addWidget(protocol_container)

