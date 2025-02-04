import sqlite3
from datetime import date, datetime, timedelta
from enum import Enum
import os

class UserType(Enum):
    HEAD_OF_DEPARTMENT = "HEAD_OF_DEPARTMENT"
    DEAN = "DEAN"
    ZJK_MEMBER = "Członek Zespołu Jakości Kształcenia"
    INSPECTION_TEAM_MEMBER = "Członek Zespołu Hospitującego"
    INSPECTED = "Hospitowany"

class DatabaseManager:
    DATABASE_NAME = "pwr.db"
    logged_user = None

    def __init__(self):
        self.initialize_database()

    def initialize_database(self):
        if os.path.exists(self.DATABASE_NAME):
            os.remove(self.DATABASE_NAME)

        connection = sqlite3.connect(self.DATABASE_NAME)
        cursor = connection.cursor()

        cursor.executescript('''
        -- Tabla: Ramowy harmonogram hospitacji
        CREATE TABLE IF NOT EXISTS Ramowy_harmonogram_hospitacji (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            zatwierdzony BOOLEAN
        );

        -- Tabla: Katedra
        CREATE TABLE IF NOT EXISTS Katedra (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numer INTEGER NOT NULL,
            nazwa VARCHAR(255) NOT NULL
        );

        -- Tabla: Pracownik uczelni
        CREATE TABLE IF NOT EXISTS Pracownik_uczelni (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            katedra_id INTEGER,
            termin_ostatniej_hospitacji DATE,
            czas_od_ostatniej_hospitacji INTEGER,
            stanowisko VARCHAR(255),
            imie VARCHAR(255),
            nazwisko VARCHAR(255),
            pesel VARCHAR(255),
            adres_email VARCHAR(255),
            telefon VARCHAR(255),
            plec VARCHAR(1),
            adres_zamieszkania VARCHAR(255),
            FOREIGN KEY (katedra_id) REFERENCES Katedra(id)
        );

        -- Tabla: Hospitacja
        CREATE TABLE IF NOT EXISTS Hospitacja (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            zespol_hospitujacy_id INTEGER,
            pracownik_uczelni_id INTEGER,
            ramowy_harmonogram_hospitacji_id INTEGER,
            termin_hospitacji DATE,
            FOREIGN KEY (zespol_hospitujacy_id) REFERENCES Zespol_hospitujacy(id),
            FOREIGN KEY (pracownik_uczelni_id) REFERENCES Pracownik_uczelni(id),
            FOREIGN KEY (ramowy_harmonogram_hospitacji_id) REFERENCES Ramowy_harmonogram_hospitacji(id)
        );

        -- Tabla: Zespol hospitujacy
        CREATE TABLE IF NOT EXISTS Zespol_hospitujacy (
            id INTEGER PRIMARY KEY AUTOINCREMENT
        );

        -- Tabla: Pracownik uczelni Zespol hospitujacy
        CREATE TABLE IF NOT EXISTS Pracownik_uczelni_Zespol_hospitujacy (
            pracownik_uczelni_id INTEGER,
            zespol_hospitujacy_id INTEGER,
            PRIMARY KEY (pracownik_uczelni_id, zespol_hospitujacy_id),
            FOREIGN KEY (pracownik_uczelni_id) REFERENCES Pracownik_uczelni(id),
            FOREIGN KEY (zespol_hospitujacy_id) REFERENCES Zespol_hospitujacy(id)
        );

        -- Tabla: Protokół hospitacji
        CREATE TABLE IF NOT EXISTS Protokol_hospitacji (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hospitacja_id INTEGER,
            zespol_hospitujacy_id INTEGER,
            ocena_koncowa FLOAT,
            data_utworzenia DATE,
            sciezka_do_pliku VARCHAR(255),
            raport_z_hospitacji_id INTEGER,
            FOREIGN KEY (hospitacja_id) REFERENCES Hospitacja(ID),
            FOREIGN KEY (zespol_hospitujacy_id) REFERENCES Zespol_hospitujacy(id),
            FOREIGN KEY (raport_z_hospitacji_id) REFERENCES Raport_z_hospitacji(id)
        );

        -- Tabla: Raport z hospitacji
        CREATE TABLE IF NOT EXISTS Raport_z_hospitacji (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            semestr_id INTEGER,
            sciezka_do_pliku VARCHAR(255),
            FOREIGN KEY (semestr_id) REFERENCES Semestr(id)
        );

        -- Tabla: Semestr
        CREATE TABLE IF NOT EXISTS Semestr (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Rok INTEGER NOT NULL,
            Ktora_polowa BOOLEAN,
            Nazwa_semestru VARCHAR(255)
        );

        -- Tabla: Zajęcia
        CREATE TABLE IF NOT EXISTS Zajecia (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pracownik_uczelni_id INTEGER,
            dzien_tygodnia INTEGER,
            czas_rozpoczecia TIME,
            FOREIGN KEY (pracownik_uczelni_id) REFERENCES Pracownik_uczelni(id)
        );

        -- Tabla: Wykaz osób proponowanych do hospitacji
        CREATE TABLE IF NOT EXISTS Wykaz_osob_proponowanych_do_hospitacji (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_utworzenia DATE
        );

        -- Tabla: Wykaz osób proponowanych do hospitacji Pracownik uczelni
        CREATE TABLE IF NOT EXISTS Wykaz_osob_proponowanych_do_hospitacji_Pracownik_uczelni (
            wykaz_osob_proponowanych_do_hospitacji_id INTEGER,
            pracownik_uczelni_id INTEGER,
            PRIMARY KEY (wykaz_osob_proponowanych_do_hospitacji_id, pracownik_uczelni_id),
            FOREIGN KEY (wykaz_osob_proponowanych_do_hospitacji_id) REFERENCES Wykaz_osob_proponowanych_do_hospitacji(id),
            FOREIGN KEY (pracownik_uczelni_id) REFERENCES Pracownik_uczelni(id)
        );

        -- Tabela: Użytkownicy
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pracownik_uczelni_id INTEGER NOT NULL,
            username VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            FOREIGN KEY (pracownik_uczelni_id) REFERENCES Pracownik_uczelni(id)
        );
        ''')

        connection.commit()
        connection.close()
        self.populate_database()

    def populate_database(self):
        connection = sqlite3.connect(self.DATABASE_NAME)
        cursor = connection.cursor()

        # Katedra
        cursor.execute("INSERT OR IGNORE INTO Katedra (numer, nazwa) VALUES (?, ?)", (45, 'Katedra Informatyki Stosowanej'))

        cursor.execute("SELECT id FROM Katedra")
        katedra_id = cursor.fetchone()[0]

        # Pracownicy
        dates = ["2024-01-15", "2023-11-20", "2024-05-10", "2024-02-05", "2022-09-15", '2023-06-15', '2022-09-20', '2023-01-10', '2021-11-05', '2023-07-01']
        times = [(datetime.today() - datetime.strptime(d, '%Y-%m-%d')).days for d in dates]
        employees = [
            (katedra_id, "2024-01-15", times[0], UserType.INSPECTED.name, "Jan", "Kowalski", "99012231571", "jan.kowalski@example.com", "348872185", "M", "Żeromskiego 1"),
            (katedra_id, "2023-11-20", times[1], UserType.INSPECTION_TEAM_MEMBER.name, "Anna", "Nowak", "05312543485", "anna.nowak@example.com", "725585457", "K", "1 Maja 10"),
            (katedra_id, "2024-05-10", times[2], UserType.ZJK_MEMBER.name, "Piotr", "Zieliński", "63041773698", "piotr.zielinski@example.com", "555666777", "M", "Czwartaków 3"),
            (katedra_id, "2024-02-05", times[3], UserType.DEAN.name, "Maria", "Wiśniewska", "86100808117", "maria.wisniewska@example.com", "444555666", "K", "Morcinka 4"),
            (katedra_id, "2022-09-15", times[4], UserType.HEAD_OF_DEPARTMENT.name, "Tomasz", "Lewandowski", "77788899900", "tomasz.lewandowski@example.com", "645771393", "M", "Kasprzaka Marcina 5"),
            (katedra_id, '2023-06-15', times[5], UserType.INSPECTED.name, 'Marek', 'Kowalczyk', '66112766582', 'marek.kowalczyk@example.com', '957248128', 'M', 'Wojska Polskiego 1'),
            (katedra_id, '2022-09-20', times[6], UserType.INSPECTED.name, 'Ewa', 'Nowicka', '98765432109', 'ewa.nowicka@example.com', '574029616', 'K', 'Niedziałkowskiego 2'),
            (katedra_id, '2023-01-10', times[7], UserType.INSPECTED.name, 'Tomasz', 'Wiśniewski', '05292919362', 'tomasz.wisniewski@example.com', '880484915', 'M', 'Gajowicka 3'),
            (katedra_id, '2021-11-05', times[8], UserType.INSPECTED.name, 'Karolina', 'Zielińska', '03320649562', 'karolina.zielinska@example.com', '890700359', 'K', 'Hallera 4'),
            (katedra_id, '2023-07-01', times[9], UserType.INSPECTED.name, 'Paweł', 'Lewandowski', '97080351623', 'pawel.lewandowski@example.com', '881630304', 'M', 'Piłsudzkiego 5')
        ]

        cursor.executemany("""
                INSERT OR IGNORE INTO Pracownik_uczelni (katedra_id, termin_ostatniej_hospitacji, czas_od_ostatniej_hospitacji, 
                stanowisko, imie, nazwisko, pesel, adres_email, telefon, plec, adres_zamieszkania) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, employees)

        cursor.execute("SELECT ID FROM Pracownik_uczelni")
        employees_id = cursor.fetchall()

        users = [(employees_id[i][0], f"user{i + 1}", f"pass") for i in range(len(UserType))]

        cursor.executemany("""
            INSERT OR IGNORE INTO Users (pracownik_uczelni_id, username, password) 
            VALUES (?, ?, ?)
        """, users)

        cursor.execute("INSERT OR IGNORE INTO Ramowy_harmonogram_hospitacji (id, zatwierdzony) VALUES (1, 1)")

        cursor.execute("INSERT OR IGNORE INTO Zespol_hospitujacy (id) VALUES (1)")

        team_members = [(2, 1), (3, 1)]
        cursor.executemany("""
            INSERT OR IGNORE INTO Pracownik_uczelni_Zespol_hospitujacy (pracownik_uczelni_id, zespol_hospitujacy_id) 
            VALUES (?, ?)
        """, team_members)

        cursor.execute("""
            INSERT OR IGNORE INTO Hospitacja (zespol_hospitujacy_id, pracownik_uczelni_id, ramowy_harmonogram_hospitacji_id, termin_hospitacji) 
            VALUES (1, 1, 1, ?)
        """, (date.today(),))

        cursor.execute("""
            INSERT OR IGNORE INTO Hospitacja (zespol_hospitujacy_id, pracownik_uczelni_id, ramowy_harmonogram_hospitacji_id, termin_hospitacji) 
            VALUES (1, 2, 1, ?)
        """, ((datetime.now() - timedelta(days=7)).date(),))

        cursor.execute("INSERT OR IGNORE INTO Semestr (rok, ktora_polowa, nazwa_semestru) VALUES (2024, 1, 'Semestr letni')")

        cursor.execute("""
            INSERT OR IGNORE INTO Raport_z_hospitacji (semestr_id, sciezka_do_pliku) 
            VALUES (1, 'reports/raport1.txt')
        """)

        cursor.execute("""
            INSERT OR IGNORE INTO Protokol_hospitacji (hospitacja_id, zespol_hospitujacy_id, ocena_koncowa, data_utworzenia, sciezka_do_pliku, raport_z_hospitacji_id)
            VALUES (1, 1, 4.5, ?, 'protocols/protokol1.txt', 1)
        """, (date.today(),))

        cursor.execute("""
                    INSERT OR IGNORE INTO Protokol_hospitacji (hospitacja_id, zespol_hospitujacy_id, ocena_koncowa, data_utworzenia, sciezka_do_pliku, raport_z_hospitacji_id)
                    VALUES (2, 1, 5.0, ?, 'protocols/protokol2.txt', 1)
                """, ((datetime.now() - timedelta(days=7)).date(),))

        connection.commit()
        connection.close()

    def _ask_database(self, query, parameters = ()):
        connection = sqlite3.connect(self.DATABASE_NAME)
        cursor = connection.cursor()
        cursor.execute(query, parameters)
        results = cursor.fetchall()
        connection.close()

        return results

    def get_employees(self):
        return self._ask_database("""
            SELECT 
                pu.id,
                pu.Imie,
                pu.Nazwisko,
                k.Nazwa,
                pu.Czas_od_ostatniej_hospitacji
            FROM Pracownik_uczelni pu 
            JOIN Katedra k 
                ON pu.katedra_id = k.ID;
        """)

    def get_team_for(self, employee_id):
        return self._ask_database("""
        SELECT 
            pu.id AS pracownik_id,
            pu.imie,
            pu.nazwisko,
            k.nazwa AS katedra
        FROM Pracownik_uczelni pu
        JOIN Pracownik_uczelni_Zespol_hospitujacy pz ON pu.id = pz.pracownik_uczelni_id
        JOIN (
            SELECT h.zespol_hospitujacy_id
            FROM Hospitacja h
            WHERE h.pracownik_uczelni_id = ? AND h.ramowy_harmonogram_hospitacji_id IS NULL
            ORDER BY h.termin_hospitacji DESC
            LIMIT 1
        ) AS nh ON pz.zespol_hospitujacy_id = nh.zespol_hospitujacy_id
        JOIN Katedra k ON pu.katedra_id = k.id;
        """, (employee_id, ))

    def insert_team_for(self, employee_id, team_mem1_id, team_mem2_id):
        connection = sqlite3.connect(self.DATABASE_NAME)
        cursor = connection.cursor()
        cursor.execute("""
        SELECT h.id,
                h.zespol_hospitujacy_id
            FROM Hospitacja h
            WHERE h.pracownik_uczelni_id = ? AND 
            h.ramowy_harmonogram_hospitacji_id IS NULL
            ORDER BY h.termin_hospitacji DESC
            LIMIT 1;""", (employee_id,))
        results = cursor.fetchall()
        if not results:
            cursor.execute("""
                INSERT INTO Hospitacja (zespol_hospitujacy_id, pracownik_uczelni_id, ramowy_harmonogram_hospitacji_id, termin_hospitacji)
                VALUES (NULL, ?, NULL, NULL)
            """, (employee_id,))
            inspection_id = cursor.lastrowid
        else:
            inspection_id = results[0][0]
            cursor.execute("""
                        DELETE FROM Zespol_hospitujacy WHERE id = ?
                    """, (results[0][1],))
        cursor.execute("""
                        INSERT INTO Zespol_hospitujacy DEFAULT VALUES
                    """)
        new_inspection_team_id = cursor.lastrowid
        cursor.execute("""
            UPDATE Hospitacja
            SET zespol_hospitujacy_id = ?
            WHERE id = ?
        """, (new_inspection_team_id, inspection_id))

        team_members = [(team_mem1_id, new_inspection_team_id), (team_mem2_id, new_inspection_team_id)]
        cursor.executemany("""
                    INSERT OR IGNORE INTO Pracownik_uczelni_Zespol_hospitujacy (pracownik_uczelni_id, zespol_hospitujacy_id) 
                    VALUES (?, ?)
                """, team_members)


        connection.commit()
        connection.close()


    def get_employees_for_hospitation(self):
        connection = sqlite3.connect(self.DATABASE_NAME)
        cursor = connection.cursor()

        cursor.execute("""
            SELECT 
                Pracownik_uczelni.ID,
                Pracownik_uczelni.Imie,
                Pracownik_uczelni.Nazwisko,
                Katedra.Nazwa AS Nazwa_Katedry,
                Pracownik_uczelni.czas_od_ostatniej_hospitacji
            FROM 
                Pracownik_uczelni
            JOIN 
                Katedra ON Pracownik_uczelni.katedra_id = Katedra.id
            LEFT JOIN 
                Wykaz_osob_proponowanych_do_hospitacji_Pracownik_uczelni AS Wykaz
                ON Pracownik_uczelni.ID = Wykaz.pracownik_uczelni_id
            LEFT JOIN 
                Wykaz_osob_proponowanych_do_hospitacji AS WykazOsob
                ON Wykaz.wykaz_osob_proponowanych_do_hospitacji_id = WykazOsob.ID
            WHERE 
                (Wykaz.pracownik_uczelni_id IS NULL 
                OR WykazOsob.data_utworzenia < DATE('now', '-2 years')) AND
                Pracownik_uczelni.stanowisko = ?;
        """, (UserType.INSPECTED.name,))

        results = cursor.fetchall()
        connection.close()

        return results

    def get_newest_recommended_list(self):
        connection = sqlite3.connect(self.DATABASE_NAME)
        cursor = connection.cursor()

        query = """
            WITH Najnowszy_wykaz AS (
                SELECT id
                FROM Wykaz_osob_proponowanych_do_hospitacji
                ORDER BY data_utworzenia DESC
                LIMIT 1
            )
            SELECT 
                pu.id,
                pu.Imie,
                pu.Nazwisko,
                k.Nazwa,
                pu.Czas_od_ostatniej_hospitacji
            FROM Najnowszy_wykaz nw 
            LEFT JOIN Wykaz_osob_proponowanych_do_hospitacji_Pracownik_uczelni woppu 
                ON nw.id = woppu.Wykaz_osob_proponowanych_do_hospitacji_id
            LEFT JOIN Pracownik_uczelni pu 
                ON woppu.pracownik_uczelni_id = pu.ID
            LEFT JOIN Katedra k 
                ON pu.katedra_id = k.ID;
            
        """

        cursor.execute(query)
        results = cursor.fetchall()
        connection.close()

        return results

    def save_hospitation_employees_list(self, employees):
        connection = sqlite3.connect(self.DATABASE_NAME)
        cursor = connection.cursor()

        query = """
            INSERT INTO Wykaz_osob_proponowanych_do_hospitacji (data_utworzenia) VALUES (?)
        """
        cursor.execute(query, (datetime.today().strftime('%Y-%m-%d'),))
        connection.commit()

        wykaz_id = cursor.lastrowid

        for employee in employees:
            cursor.execute(
                "INSERT INTO Wykaz_osob_proponowanych_do_hospitacji_Pracownik_uczelni (wykaz_osob_proponowanych_do_hospitacji_id, pracownik_uczelni_id) VALUES (?, ?)",
                (wykaz_id, employee[0])
            )
        connection.commit()
        connection.close()

    def login(self, username, password):
        connection = sqlite3.connect(self.DATABASE_NAME)
        cursor = connection.cursor()

        cursor.execute("SELECT pracownik_uczelni_id FROM Users WHERE username=? AND password=?", (username, password))
        self.logged_user = cursor.fetchone()

        connection.close()

        if self.logged_user is not None:
            self.logged_user = self.logged_user[0]
            return self.get_user_role()
        else: return None

    def get_user_role(self):
        connection = sqlite3.connect(self.DATABASE_NAME)
        cursor = connection.cursor()

        cursor.execute("SELECT stanowisko FROM Pracownik_uczelni WHERE id=?", (self.logged_user,))
        role = cursor.fetchone()[0]

        connection.close()

        return role

    def get_employee_id_from_hospitalization(self, hospitalization_id):
        connection = sqlite3.connect(self.DATABASE_NAME)
        cursor = connection.cursor()

        cursor.execute("SELECT pracownik_uczelni_id FROM Hospitacja WHERE id=?", (hospitalization_id, ))
        employee_id = cursor.fetchone()

        connection.close()
        return employee_id[0]

    def get_fullname(self, employee_id):
        connection = sqlite3.connect(self.DATABASE_NAME)
        cursor = connection.cursor()

        cursor.execute("SELECT imie, nazwisko FROM Pracownik_uczelni WHERE id=?", (employee_id,))
        fullname = cursor.fetchone()

        connection.close()
        return ' '.join(fullname)

    def get_employee_full_name(self, protocol_id):
        connection = sqlite3.connect(self.DATABASE_NAME)
        cursor = connection.cursor()

        query = """
            SELECT pu.Imie || ' ' || pu.Nazwisko AS Full_Name
            FROM Protokol_hospitacji ph
            JOIN Hospitacja h ON ph.hospitacja_id = h.ID
            JOIN Pracownik_uczelni pu ON h.Pracownik_uczelni_id = pu.ID
            WHERE ph.ID = ?;
        """

        cursor.execute(query, (protocol_id,))
        result = cursor.fetchone()
        connection.close()

        return result[0] if result else None

    def get_all_protocols(self, employee_id):
        connection = sqlite3.connect(self.DATABASE_NAME)
        cursor = connection.cursor()

        query = """
            SELECT ph.ID AS Protocol_ID, 
                   ph.hospitacja_id, 
                   ph.zespol_hospitujacy_id, 
                   ph.ocena_koncowa, 
                   ph.data_utworzenia, 
                   ph.sciezka_do_pliku, 
                   ph.raport_z_hospitacji_id
            FROM Protokol_hospitacji ph
            JOIN Hospitacja h ON ph.hospitacja_id = h.ID
            JOIN Zespol_hospitujacy zh ON ph.zespol_hospitujacy_id = zh.ID
            JOIN Pracownik_uczelni_Zespol_hospitujacy puzh 
                ON zh.ID = puzh.zespol_hospitujacy_id
            WHERE puzh.Pracownik_uczelni_ID = ?;
        """

        cursor.execute(query, (employee_id,))
        results = cursor.fetchall()
        connection.close()

        return results

    def get_protocols(self, employee_id):
        connection = sqlite3.connect(self.DATABASE_NAME)
        cursor = connection.cursor()

        cursor.execute("""SELECT 
            Protokol_hospitacji.id,
            Protokol_hospitacji.hospitacja_id,
            Protokol_hospitacji.zespol_hospitujacy_id,
            Protokol_hospitacji.ocena_koncowa,
            Protokol_hospitacji.data_utworzenia,
            Protokol_hospitacji.sciezka_do_pliku,
            Protokol_hospitacji.raport_z_hospitacji_id
            FROM Protokol_hospitacji 
            JOIN Hospitacja ON Protokol_hospitacji.hospitacja_id = Hospitacja.id
            WHERE pracownik_uczelni_id = ?;
        """, (employee_id,))

        protocols = cursor.fetchall()

        connection.close()
        return protocols

    def get_reports(self):
        connection = sqlite3.connect(self.DATABASE_NAME)
        cursor = connection.cursor()

        cursor.execute("""SELECT 
            Raport_z_hospitacji.sciezka_do_pliku,
            Semestr.rok,
            Semestr.ktora_polowa,
            Semestr.nazwa_semestru
            FROM Raport_z_hospitacji 
            JOIN Semestr ON Raport_z_hospitacji.semestr_id = Semestr.id;
        """)

        reports = cursor.fetchall()

        connection.close()
        return reports


    def get_semester_name(self, report_id):
        connection = sqlite3.connect(self.DATABASE_NAME)
        cursor = connection.cursor()

        print(type(report_id), report_id)
        cursor.execute("""
            SELECT Semestr.nazwa_semestru
            FROM Raport_z_hospitacji
            JOIN Semestr ON Raport_z_hospitacji.semestr_id = Semestr.id
            WHERE Raport_z_hospitacji.id = ?;
        """, (report_id, ))

        semester_name = cursor.fetchone()

        connection.close()
        return semester_name[0]

    def load_protocol_content(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                return content
        except Exception as e:
            return f"Error loading file: {str(e)}"