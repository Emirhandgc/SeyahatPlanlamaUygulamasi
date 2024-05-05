import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QComboBox, QListWidget, QListWidgetItem, QMessageBox, QSpinBox
import sqlite3
import random
import string

class Konaklama:
    def __init__(self, name, price):
        self.name = name
        self.price = price

class Rota:
    def __init__(self, details, seyahat_suresi):
        self.details = details
        self.seyahat_suresi = seyahat_suresi
        self.konaklama_secenekleri = []

    def konaklama_ekle(self, konaklama):
        self.konaklama_secenekleri.append(konaklama)

    def detay_ekle(self, detay):
        self.details += f"\nDetay: {detay}"

class Seyahat:
    def __init__(self):
        self.connection = sqlite3.connect("seyahat_planlama.db")
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS rotalar (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                details TEXT,
                                seyahat_suresi INTEGER
                            )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS konaklamalar (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT,
                                price INTEGER
                            )''')
        self.connection.commit()

    def rota_ekle(self, rota):
        self.cursor.execute("INSERT INTO rotalar (details, seyahat_suresi) VALUES (?, ?)", (rota.details, rota.seyahat_suresi))
        self.connection.commit()

    def konaklama_ekle(self, konaklama):
        self.cursor.execute("INSERT INTO konaklamalar (name, price) VALUES (?, ?)", (konaklama.name, konaklama.price))
        self.connection.commit()

    def rotalari_getir(self):
        self.cursor.execute("SELECT details FROM rotalar")
        return self.cursor.fetchall()

    def konaklamalari_getir(self):
        self.cursor.execute("SELECT name, price FROM konaklamalar")
        return self.cursor.fetchall()

    def seyahat_sil(self, rota):
        self.cursor.execute("DELETE FROM rotalar WHERE details = (?)", (rota,))
        self.connection.commit()

    def konaklama_sil(self, konaklama):
        self.cursor.execute("DELETE FROM konaklamalar WHERE name = (?)", (konaklama,))
        self.connection.commit()

class SeyahatPlanlamaApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Seyahat Planlama Uygulaması")
        self.setGeometry(100, 100, 400, 300)

        self.seyahat = Seyahat()

        self.init_ui()

    def init_ui(self):
        # Widgets
        self.rota_label = QLabel("Rota Detayları:")
        self.rota_input = QLineEdit()

        self.seyahat_suresi_label = QLabel("Seyahat Süresi (Gün):")
        self.seyahat_suresi_input = QSpinBox()
        self.seyahat_suresi_input.setMinimum(1)
        self.seyahat_suresi_input.setMaximum(365)  # Bir yıldan fazla seyahat süresi olamaz

        self.detay_label = QLabel("Detay:")
        self.detay_input = QLineEdit()

        self.detay_ekle_button = QPushButton("Detay Ekle")
        self.detay_ekle_button.clicked.connect(self.detay_ekle)

        self.rota_ekle_button = QPushButton("Rota Ekle")
        self.rota_ekle_button.clicked.connect(self.rota_ekle)

        self.konaklama_label = QLabel("Konaklama Tesisi Adı:")
        self.konaklama_input = QLineEdit()
        self.konaklama_fiyat_label = QLabel("Fiyat:")
        self.konaklama_fiyat_input = QLineEdit()

        self.konaklama_ekle_button = QPushButton("Konaklama Ekle")
        self.konaklama_ekle_button.clicked.connect(self.konaklama_ekle)

        self.rota_list_label = QLabel("Rotalar:")
        self.rota_list = QListWidget()
        self.rota_list.itemClicked.connect(self.rota_item_clicked)

        self.konaklama_list_label = QLabel("Konaklama Seçenekleri:")
        self.konaklama_list = QListWidget()
        self.konaklama_list.itemClicked.connect(self.konaklama_item_clicked)

        self.seyahat_sil_button = QPushButton("Seyahati Sil")
        self.seyahat_sil_button.clicked.connect(self.seyahat_sil)

        self.konaklama_sil_button = QPushButton("Konaklama Sil")
        self.konaklama_sil_button.clicked.connect(self.konaklama_sil)

        # Layout
        self.layout = QVBoxLayout()

        self.layout.addWidget(self.rota_label)
        self.layout.addWidget(self.rota_input)

        self.layout.addWidget(self.seyahat_suresi_label)
        self.layout.addWidget(self.seyahat_suresi_input)

        self.layout.addWidget(self.detay_label)
        self.layout.addWidget(self.detay_input)
        self.layout.addWidget(self.detay_ekle_button)

        self.layout.addWidget(self.rota_ekle_button)

        self.layout.addWidget(self.konaklama_label)
        self.layout.addWidget(self.konaklama_input)
        self.layout.addWidget(self.konaklama_fiyat_label)
        self.layout.addWidget(self.konaklama_fiyat_input)
        self.layout.addWidget(self.konaklama_ekle_button)

        self.layout.addWidget(self.rota_list_label)
        self.layout.addWidget(self.rota_list)

        self.layout.addWidget(self.konaklama_list_label)
        self.layout.addWidget(self.konaklama_list)

        self.layout.addWidget(self.seyahat_sil_button)
        self.layout.addWidget(self.konaklama_sil_button)

        self.setLayout(self.layout)

        self.update_rota_list()
        self.update_konaklama_list()

    def rota_ekle(self):
        details = self.rota_input.text()
        seyahat_suresi = self.seyahat_suresi_input.value()
        if details:
            rota = Rota(details, seyahat_suresi)
            self.seyahat.rota_ekle(rota)
            self.rota_input.clear()
            self.update_rota_list()
        else:
            QMessageBox.warning(self, "Hata", "Rota detayları boş olamaz.")

    def detay_ekle(self):
        detay = self.detay_input.text()
        if detay:
            current_rota = self.rota_input.text()
            if current_rota:
                rota = Rota(current_rota, 0)
                rota.detay_ekle(detay)
                self.seyahat.rota_ekle(rota)
                self.update_rota_list()
                self.detay_input.clear()
            else:
                QMessageBox.warning(self, "Hata", "Önce bir rota ekleyin.")
        else:
            QMessageBox.warning(self, "Hata", "Detay boş olamaz.")

    def konaklama_ekle(self):
        name = self.konaklama_input.text()
        price = self.konaklama_fiyat_input.text()

        try:
            price = int(price)
        except ValueError:
            QMessageBox.warning(self, "Hata", "Fiyat sayı olmalıdır.")
            return

        if name and price:
            konaklama = Konaklama(name, price)
            self.seyahat.konaklama_ekle(konaklama)
            self.konaklama_input.clear()
            self.konaklama_fiyat_input.clear()
            self.update_konaklama_list()
        else:
            QMessageBox.warning(self, "Hata", "Konaklama tesisi adı ve fiyatı boş olamaz.")

    def update_rota_list(self):
        self.rota_list.clear()
        rotalar = self.seyahat.rotalari_getir()
        for details, duration in rotalar:
            self.rota_list.addItem(QListWidgetItem(f"{details} - Süre: {duration} gün"))

    def update_konaklama_list(self):
        self.konaklama_list.clear()
        konaklamalar = self.seyahat.konaklamalari_getir()
        for name, _ in konaklamalar:
            self.konaklama_list.addItem(QListWidgetItem(name))

    def rota_item_clicked(self, item):
        selected_rota = item.text().split(" - ")[0]
        self.rota_input.setText(selected_rota)

    def konaklama_item_clicked(self, item):
        selected_konaklama = item.text()
        self.konaklama_input.setText(selected_konaklama)

    def seyahat_sil(self):
        selected_item = self.rota_list.currentItem()
        if selected_item:
            rota = selected_item.text().split(" - ")[0]
            self.seyahat.seyahat_sil(rota)
            self.update_rota_list()
        else:
            QMessageBox.warning(self, "Hata", "Önce bir rota seçin.")

    def konaklama_sil(self):
        selected_item = self.konaklama_list.currentItem()
        if selected_item:
            konaklama = selected_item.text()
            self.seyahat.konaklama_sil(konaklama)
            self.update_konaklama_list()
        else:
            QMessageBox.warning(self, "Hata", "Önce bir konaklama seçin.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SeyahatPlanlamaApp()
    window.show()
    sys.exit(app.exec_())
