from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout


class AutoLayoutQFrame(QFrame):
    """
    Фрейм с уже созданным заранее layout\n
    И интерфйесом addWidget для быстрого добавления виджетов прямо на фрейм
    """
    def __init__(self, layout: QVBoxLayout | QHBoxLayout | type = QVBoxLayout, parent=None):
        super().__init__(parent)
        self._layout = layout()
        self.setLayout(self._layout)

    def addWidget(self, widget):
        self._layout.addWidget(widget)

    def layout(self) -> QHBoxLayout | QVBoxLayout:
        return self._layout

    def clear(self):
        """Удалить все виджеты из layout"""
        layout = self.layout()
        if layout is None:
            return
        
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                # Если есть вложенный layout
                sublayout = item.layout()
                if sublayout is not None:
                    self.clear_layout(sublayout)
