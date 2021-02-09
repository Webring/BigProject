import os
import sys

import requests
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QLabel

SCREEN_SIZE = [600, 450]
api_adress = "http://static-maps.yandex.ru/1.x/"


class MapWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.l1 = "37.620070"
        self.l2 = "55.75363"
        self.z = 0
        self.getImage(self.z)
        self.initUI()

    def getImage(self, z):
        map_request = f"{api_adress}?ll=&spn=&l=map"
        params = {
            "ll": ",".join([self.l1, self.l2]),
            "l": "map",
            "z": z
        }
        response = requests.get(api_adress, params=params)

        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp:
            self.z += 1
            if (self.z <= 17) and (self.z >= 0):
                self.getImage(self.z)
                self.pixmap = QPixmap(self.map_file)
                self.image.setPixmap(self.pixmap)
        elif event.key() == Qt.Key_PageDown:
            self.z -= 1
            if (self.z >= 0) and (self.z <= 17):
                self.getImage(self.z)
                self.pixmap = QPixmap(self.map_file)
                self.image.setPixmap(self.pixmap)

    def initUI(self):
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.setWindowTitle('Отображение карты')
        self.pixmap = QPixmap(self.map_file)
        self.image = QLabel(self)
        self.image.move(0, 0)
        self.image.resize(600, 450)
        self.image.setPixmap(self.pixmap)

    def closeEvent(self, event):
        os.remove(self.map_file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MapWindow()
    ex.show()
    sys.exit(app.exec())
