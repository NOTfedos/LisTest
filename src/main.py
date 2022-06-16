import sys
import os
import PyQt5.QtWidgets as qt
from PyQt5 import uic, QtGui
from PyQt5.QtCore import Qt, QRectF


from lissajousgen import LissajousGenerator, LissajousFigure


# Настройки фигуры по умолчанию
default_settings = {
    "freq_x": 2,
    "freq_y": 3,
    "color": "Синий",
    "width": 1
}

colors = {
    "Красный": Qt.red,
    "Зелёный": Qt.green,
    "Жёлтый": Qt.yellow,
    "Синий": Qt.blue
}


class LissajousWindow(qt.QMainWindow):
    def __init__(self):
        super(LissajousWindow, self).__init__()

        # Загружаем интерфейс из файла
        uic.loadUi(os.path.join("static", "main_window_gr.ui"), self)

        # Ставим версию и иконку
        with open(os.path.join("static", "version.txt"), "r") as f:
            version = f.readline()
        self.setWindowTitle("Генератор фигур Лиссажу. Версия {}. CC BY-SA 4.0 Ivanov".format(
            version
        ))
        script_dir = os.path.dirname(os.path.realpath(__file__))
        print(script_dir)
        self.setWindowIcon(QtGui.QIcon(os.path.join(script_dir, "..", "static", "icon.bmp")))

        # Создаем генератор фигур
        self.generator = LissajousGenerator()

        # Создаем сцену для рисования
        self.scene = qt.QGraphicsScene()
        self.graphicsView.setScene(self.scene)

        self.plot_button.clicked.connect(self.plot_button_click_handler)
        self.save_button.clicked.connect(self.save_button_click_handler)

        # Устанавливаем размер
        self.resize(800, 300)

        # Инициализируем аттрибуты (конкретно для рисования фигур Лиссажу)
        self.lines = []
        self.first = True

        self.settings = default_settings

        self.set_pen()

        # Первичное построение фигуры
        self.plot_lissajous_figure()

    def plot_button_click_handler(self):
        """
        Обработчик нажатия на кнопку применения настроек
        """
        # Получаем данные из текстовых полей
        self.settings = dict()

        self.settings["freq_x"] = float(self.freq_x_lineedit.text())
        self.settings["freq_y"] = float(self.freq_y_lineedit.text())
        self.settings["color"] = self.color_combobox.currentText()
        self.settings["width"] = int(self.width_combobox.currentText())

        # Устанавливаем параметры рисования
        self.set_pen()

        # Перестраиваем график
        self.plot_lissajous_figure()

    def set_pen(self):
        self.pen = QtGui.QPen(colors[self.settings["color"]], self.settings["width"])

    def plot_lissajous_figure(self):
        """
        Обновление фигуры
        """

        # Удаляем устаревшие данные графика
        for line in self.lines:
            self.scene.removeItem(line)

        self.lines = []

        self.scene.setBackgroundBrush(Qt.white)

        # Выбираем масштаб
        h = self.graphicsView.frameGeometry().height()
        w = self.graphicsView.frameGeometry().width()
        if self.first:
            scale = 122.7
            self.first = False
        else:
            scale = min(h / 2.2, w / 2.2)

        # Генерируем новую фигуру
        figure = self.generator.generate_figure(self.settings["freq_x"], self.settings["freq_y"],
                                                scale)

        # Отрисовываем фигуру
        x0, y0 = figure.x_arr[0], figure.y_arr[0]
        for x, y in zip(figure.x_arr[1:], figure.y_arr[1:]):
            self.lines.append(self.scene.addLine(x0, y0, x, y, self.pen))
            x0, y0 = x, y
        self.lines.append(self.scene.addLine(x0, y0, figure.x_arr[0], figure.y_arr[0], self.pen))

        # self.graphicsView.render(painter)
        self.graphicsView.show()

    def save_button_click_handler(self):
        """
        Обработчик нажатия на кнопку сохранения настроек
        """
        file_path, _ = qt.QFileDialog.getSaveFileName(self, "Сохранение изображения", "C:\\",
                                                            "PNG(*.png);;JPEG(*.jpg *.jpeg);;All Files(*.*) ")

        if file_path == "":
            return

        # Сохраняем изображение в файл
        image = QtGui.QImage(self.scene.width(), self.scene.height(), QtGui.QImage.Format_ARGB32_Premultiplied)
        painter = QtGui.QPainter(image)
        self.scene.render(painter, QRectF(image.rect()))
        painter.end()

        image.save(file_path)

        return


if __name__ == "__main__":

    # Инициализируем приложение Qt
    app = qt.QApplication(sys.argv)

    # Создаём и настраиваем главное окно
    main_window = LissajousWindow()

    # Показываем окно
    main_window.show()

    # Запуск приложения
    sys.exit(app.exec_())
