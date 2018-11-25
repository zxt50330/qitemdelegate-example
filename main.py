import copy
import re
from PySide2 import QtWidgets, QtCore, QtGui
from sys import exit
from time import time

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("QListView with QItemDelegate")
        self.setStyleSheet("""QMainWindow {
                                background: #fff;
                              }
                              QMainWindow::separator {
                                height: 0;
                                border: none;
                                width: 0;
                              }""")
        self.setUnifiedTitleAndToolBarOnMac(True)


class ListView(QtWidgets.QListView):
    def __init__(self):
        super(ListView, self).__init__()
        self.selected = 0
        self.setStyleSheet("""QListView {
                                background: #eee;
                                border: none;
                                border-right: 1px solid #eee;
                              }""")
        color = QtGui.QColor()
        color.setNamedColor("#999")
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Highlight, color)
        self.setPalette(palette)
        self.model = ItemModel(0, 1, self)
        self.setModel(self.model)
        self.setItemDelegate(ItemDelegate())
        self.model.rowsAboutToBeRemoved.connect(self.items_deleted)

    def append(self, thing):
        item = self.build_item(thing)
        self.model.addItem(item)

    def build_item(self, thing):
        title = self.get_title(thing)
        line = self.get_second_line(thing)
        item = Item(title, line, thing["pinned"])
        return item

    def clear(self):
        self.model.clear()

    def get_title(self, thing):
        target = 27
        if thing["pinned"]:
            target -= 5
        text = re.compile("\s*(.*)\n?").match(thing["body"]).groups()[0]
        return (
            "".join([text[0 : target - 3].strip(), "…"])
            if len(text) > target
            else text.strip()
        )

    def get_second_line(self, thing):
        text = thing["body"].splitlines()
        for i, line in enumerate(text):
            if not line:
                del text[i]
        if len(text) > 1 and text[1] != self.get_title(thing):
            return (
                "".join([text[1][0:34].strip(), "…"])
                if len(text[1]) > 37
                else text[1].strip()
            )
        return None

    def insert(self, thing, row):
        item = self.build_item(thing)
        self.selected = row
        self.model.insertItem(item, row)
        self.setCurrentIndex(self.model.index(row))

    def items_deleted(self):
        self.setCurrentIndex(self.model.index(self.selected))

    def remove(self, row):
        self.model.removeItem(row)
        count = self.model.rowCount()
        self.selected = row if row < count else row - 1
        self.setCurrentIndex(self.model.index(self.selected))

    def select(self, row):
        if row >= 0 and row < self.model.rowCount():
            self.setCurrentIndex(self.model.index(row))
            self.selected = row

    def update(self, thing):
        item = self.build_item(thing)
        self.model.updateItem(self.currentIndex(), item)


class Item:
    __slots__ = ["title", "line", "pinned"]

    def __init__(self, title, line, pinned):
        self.title = title
        self.line = line
        self.pinned = pinned


class ItemDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self):
        super(ItemDelegate, self).__init__()

    def paint(self, painter, option, index):
        options = QtWidgets.QStyleOptionViewItem(option)
        style = options.widget.style()
        style.drawControl(QtWidgets.QStyle.CE_ItemViewItem, options, painter)
        painter.save()
        color = QtGui.QColor()
        if option.state & QtWidgets.QStyle.State_Selected:
            color.setNamedColor("#fff")
            painter.setPen(color)
            pin = QtGui.QImage("icons/pinned_selected.png")
        else:
            color.setNamedColor("#333")
            painter.setPen(color)
            pin = QtGui.QImage("icons/pinned.png")
        pin.setDevicePixelRatio(2.0)
        title = index.data(ItemModel.TitleRole)
        line = index.data(ItemModel.LineRole)
        pinned = index.data(ItemModel.PinRole)
        font = painter.font()
        font.setPixelSize(16)
        painter.setFont(font)
        rectangle = option.rect
        rectangle.setX(10)
        pin_rect = copy.copy(rectangle)
        pin_rect.setHeight(32)
        pin_rect.setWidth(32)
        if title:
            pin_point = rectangle.topLeft()
            pin_point.setY(pin_point.y() + 32)
            pin_rect.setTopLeft(pin_point)
            if line:
                point = option.rect.topLeft()
                point.setY(point.y() - 20)
                rectangle.setTopLeft(point)
                pin_point.setY(pin_point.y() - 10)
                pin_rect.setTopLeft(pin_point)
            pin_rect.setHeight(16)
            pin_rect.setWidth(16)
            if pinned:
                painter.drawImage(pin_rect, pin)
                title = "     " + title
            painter.drawText(rectangle, QtCore.Qt.AlignVCenter, title)
        if line:
            point = option.rect.topLeft()
            point.setY(point.y() + 40)
            rectangle.setTopLeft(point)
            font.setPixelSize(12)
            painter.setFont(font)
            painter.drawText(rectangle, QtCore.Qt.AlignVCenter, line)
        painter.restore()


class ItemModel(QtCore.QAbstractListModel):
    TitleRole, LineRole, PinRole = range(QtCore.Qt.UserRole, QtCore.Qt.UserRole + 3)

    def __init__(self, *args, **kwargs):
        super(ItemModel, self).__init__()
        self.items = []

    def addItem(self, item):
        self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(), self.rowCount())
        self.items.append(item)
        self.endInsertRows()

    def clear(self):
        self.beginRemoveRows(QtCore.QModelIndex(), 0, self.rowCount() - 1)
        self.items = []
        self.endRemoveRows()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
        if 0 <= index.row() < self.rowCount():
            item = self.items[index.row()]
            if role == QtCore.Qt.SizeHintRole:
                return QtCore.QSize(100, 80)
            elif role == ItemModel.TitleRole:
                return item.title
            elif role == ItemModel.LineRole:
                if item.line:
                    return item.line
                return None
            elif role == ItemModel.PinRole:
                return item.pinned

    def getItem(self, index):
        row = index.row()
        if index.isValid() and 0 <= row < self.rowCount():
            return self.items[row]

    def insertItem(self, item, index):
        self.beginInsertRows(QtCore.QModelIndex(), index, index)
        self.items.insert(index, item)
        self.endInsertRows()

    def removeItem(self, row):
        self.beginRemoveRows(QtCore.QModelIndex(), row, row)
        del self.items[row]
        self.endRemoveRows()

    def rowCount(self, index=QtCore.QModelIndex()):
        return len(self.items)

    def setData(self, index, item, role=QtCore.Qt.EditRole):
        self.items[index.row()] = item
        self.dataChanged.emit(index, index, [ItemModel.TitleRole,
                              ItemModel.LineRole, ItemModel.PinRole])

    def updateItem(self, index, item):
        self.setData(index, item)


class TextEdit(QtWidgets.QTextEdit):
    def __init__(self):
        super(TextEdit, self).__init__()
        self.setViewportMargins(20, 20, 20, 20)
        self.setStyleSheet("""QTextEdit {
                                border: none;
                                border-bottom: 1px solid #eee;
                                background: #fff;
                                color: #333;
                            }""")
        font = QtGui.QFont()
        font.setPixelSize(16)
        document = self.document()
        document.setDefaultFont(font)


class View:
    def __init__(self):
        self.app = QtWidgets.QApplication([])
        self.app.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)
        self.main_window = MainWindow()
        self.text_edit = TextEdit()
        self.dock = QtWidgets.QDockWidget()
        self.list_view = ListView()
        self.dock.setWidget(self.list_view)
        self.dock.setFeatures(self.dock.NoDockWidgetFeatures)
        self.dock.setTitleBarWidget(QtWidgets.QWidget())
        self.main_window.setCentralWidget(self.text_edit)
        self.main_window.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.dock)
        self.list_view.selectionModel().currentChanged.connect(self.list_item_selected)

    def list_item_selected(self, index):
        self.text_edit.setPlainText(self.things[index.row()]["body"])
        self.text_edit.setFocus()

    def main(self):
        self.populate_item_model()
        self.list_view.select(0)
        self.main_window.resize(800, 600)
        self.main_window.show()
        exit(self.app.exec_())

    def populate_item_model(self):
        # Let us pretend we are getting this data from
        # someplace really clever, rather than from a
        # method a few lines down...
        self.things = sorted(self.data(),
                            key=lambda t: (t["pinned"], t["date"]),
                            reverse=True)
        for thing in self.things:
            self.list_view.append(thing)

    @staticmethod
    def data():
        things = [
            {
                "body": "Lorem ipsum dolor sit amet "
                "consectetur adipiscing elit.\n\n"
                "Curabitur fringilla volutpat "
                "purus, a volutpat quam feugiat eget. "
                "Nulla libero orci, rhoncus quis arcu "
                "eget, efficitur scelerisque est.\n\nNam "
                "elementum ante vitae risus auctor mattis. "
                "Maecenas aliquet placerat purus, at "
                "sollicitudin augue gravida at.",
                "date": time() - 10820,
                "pinned": False,
            },
            {
                "body": "Ut iaculis a elit a fringilla. Duis "
                "et tincidunt augue, non porttitor felis.",
                "date": time() - 190600,
                "pinned": False,
            },
            {
                "body": "Orci varius natoque penatibus et magnis "
                "dis parturient montes, nascetur ridiculus "
                "mus.\n\nAliquam sodales risus tortor, et "
                "ultrices lacus consectetur a.\n\n Cras "
                "iaculis odio quis mauris fringilla egestas. "
                "Cras vitae dolor quis turpis congue auctor et "
                "et eros.\n\nNulla ornare, dolor nec consectetur "
                "scelerisque, tellus lorem molestie felis, a "
                "auctor risus lorem vitae velit.",
                "date": time() - 229200,
                "pinned": True,
            },
            {
                "body": "Vestibulum ac mi id neque aliquam "
                "vestibulum.\n\nPhasellus elementum metus "
                "ligula, quis laoreet nisi commodo ac.",
                "date": time() - 343010,
                "pinned": False,
            },
            {
                "body": "Aenean vel neque id nunc tincidunt "
                "efficitur. Mauris dapibus, nulla vitae "
                "accumsan faucibus, nulla lacus facilisis "
                "felis, lobortis molestie tortor nibh eu arcu.",
                "date": time() - 445600,
                "pinned": False,
            },
        ]
        return things


if __name__ == "__main__":
    view = View()
    view.main()
