import os
import sys

import requests
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QLineEdit, QPushButton, QCheckBox

SCREEN_SIZE = [600, 450]
STATIC_API = "http://static-maps.yandex.ru/1.x/"
GEOCODER_API = "http://geocode-maps.yandex.ru/1.x/"
API_KEY = "40d1649f-0493-4b70-98ba-98533de7710b"


class MapWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.doindex = False
        self.resetSR = False
        self.z = 17
        self.sl = ["map", "sat", "sat,skl"]
        self.curr_s = 0
        self.s = self.sl[self.curr_s]
        self.coords = []
        self.coords2 = []
        self.initUI()
        self.search("Курган")

    def search(self, request_text=None):
        if request_text == None:
            request_text = self.search_text_area.text()
        if self.search_text_area.text() or request_text:
            self.resetSR = False
            params = {
                "apikey": API_KEY,
                "geocode": request_text,
                "format": "json"
            }
            response = requests.get(GEOCODER_API, params=params).json()
            obj = response["response"]["GeoObjectCollection"]["featureMember"][0]
            self.index = ""
            self.addres_line_text = obj["GeoObject"]["metaDataProperty"]["GeocoderMetaData"]["Address"]["formatted"]
            if "postal_code" in (obj["GeoObject"]["metaDataProperty"]["GeocoderMetaData"]["Address"]).keys():
                self.index = obj["GeoObject"]["metaDataProperty"]["GeocoderMetaData"]["Address"]["postal_code"]
            if self.doindex:
                if self.index != "":
                    self.addres_line.setText(f"{self.addres_line_text}, {self.index}")
                else:
                    self.addres_line.setText(self.addres_line_text)
            else:
                self.addres_line.setText(self.addres_line_text)
            coords = list(map(float, obj["GeoObject"]["Point"]["pos"].split()))
            self.coords = coords
            self.coords2 = self.coords[:]
            self.getImage()
            self.update_image()

    def getImage(self):
        if self.resetSR:
            params = {
                "ll": "{},{}".format(*self.coords),
                "z": self.z,
                "l": self.s
            }
            response = requests.get(STATIC_API, params=params)
        else:
            params = {
                "ll": "{},{}".format(*self.coords),
                "z": self.z,
                "l": self.s,
                "pt": f"{self.coords2[0]},{self.coords2[1]},pm2dol"
            }
            response = requests.get(STATIC_API, params=params)

        if not response:
            print("Ошибка выполнения запроса:")
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        # Запишем полученное изображение в файл.
        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

    def update_image(self):
        self.pixmap = QPixmap(self.map_file)  # Изображение
        self.image.resize(600, 450)
        self.image.setPixmap(self.pixmap)

    def initUI(self):
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.setWindowTitle('Free Open source map for SKOLKOVO')

        self.grid = QGridLayout(self)

        self.search_text_area = QLineEdit("Курган")

        self.addres_line = QLineEdit()
        self.addres_line.setReadOnly(True)

        self.search_button = QPushButton("Искать")
        self.search_button.pressed.connect(self.search)

        self.layer_button = QPushButton("Переключить слой")
        self.layer_button.clicked.connect(self.layer)

        self.reset_button = QPushButton("Сброс поискового результата")
        self.reset_button.clicked.connect(self.resetS)

        self.box = QCheckBox("Индекс", self)
        self.box.stateChanged.connect(self.check)

        self.image = QLabel()
        self.image.move(0, 0)

        self.grid.addWidget(self.image, 1, 0, 1, 2)
        self.grid.addWidget(self.search_text_area, 0, 0)
        self.grid.addWidget(self.search_button, 0, 1)
        self.grid.addWidget(self.layer_button, 2, 0)
        self.grid.addWidget(self.reset_button, 2, 1)
        self.grid.addWidget(self.addres_line, 3, 0)
        self.grid.addWidget(self.box, 3, 1)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp:
            if self.z < 17:
                self.z += 1
                self.getImage()
                self.update_image()
        elif event.key() == Qt.Key_PageDown:
            if self.z > 0:
                self.z -= 1
                self.getImage()
                self.update_image()
        if event.key() == Qt.Key_D:
            self.coords[0] = self.coords[0] + 0.001
            self.getImage()
            self.update_image()
        elif event.key() == Qt.Key_A:
            self.coords[0] = self.coords[0] - 0.001
            self.getImage()
            self.update_image()
        elif event.key() == Qt.Key_W:
            self.coords[1] = self.coords[1] + 0.001
            self.getImage()
            self.update_image()
        elif event.key() == Qt.Key_S:
            self.coords[1] = self.coords[1] - 0.001
            self.getImage()
            self.update_image()

    def layer(self):
        if self.curr_s == 2:
            self.curr_s = -1
        self.curr_s += 1
        self.s = self.sl[self.curr_s]
        self.getImage()
        self.update_image()

    def resetS(self):
        self.resetSR = True
        self.getImage()
        self.update_image()
        self.addres_line.setText("")
        self.search_text_area.setText("")

    def check(self, state):
        if state == Qt.Checked:
            self.doindex = True
            if not self.resetSR:
                if self.index != "":
                    self.addres_line.setText(f"{self.addres_line_text}, {self.index}")
        else:
            self.doindex = False
            if not self.resetSR:
                self.addres_line.setText(self.addres_line_text)

    def closeEvent(self, event):
        os.remove(self.map_file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MapWindow()
    ex.show()
    sys.exit(app.exec())