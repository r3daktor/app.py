import sys
import random
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QPushButton,
    QVBoxLayout, QHBoxLayout, QWidget, QMenu, QAction, QDialog, QLabel, QLineEdit,
    QComboBox, QDateEdit, QTimeEdit, QMessageBox
)
from PyQt5.QtCore import Qt, QDateTime

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Редактор кассовых чеков")
        self.setGeometry(100, 100, 800, 600)

        # Главная таблица "Список чеков"
        self.table = QTableWidget(self)
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Категория", "Наименование", "Организация (ККМ)", "Кассир",
            "Смена", "Чек", "Признак", "Дата/Время", "Способ оплаты"
        ])
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Настройка ширины столбцов
        self.adjust_column_widths()

        # Кнопки "Создать чек" и "Удалить чек"
        self.create_button = QPushButton("Создать чек")
        self.create_button.clicked.connect(self.edit_receipt)

        self.delete_button = QPushButton("Удалить чек")
        self.delete_button.clicked.connect(self.delete_receipt)

        # Горизонтальный макет для кнопок
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.create_button)
        button_layout.addStretch()
        button_layout.addWidget(self.delete_button)

        # Основной макет
        layout = QVBoxLayout()
        layout.addLayout(button_layout)
        layout.addWidget(self.table)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Данные для хранения организаций
        self.organizations = []

    def adjust_column_widths(self):
        """Настройка ширины столбцов по ширине заголовков."""
        header = self.table.horizontalHeader()
        for column in range(self.table.columnCount()):
            header.setSectionResizeMode(column, header.ResizeToContents)
            header.resizeSection(column, header.sectionSize(column) + 20)

    def show_context_menu(self, position):
        menu = QMenu(self)
        delete_action = QAction("Удалить чек", self)
        edit_action = QAction("Редактировать", self)
        delete_action.triggered.connect(self.delete_receipt)
        edit_action.triggered.connect(self.edit_receipt)
        menu.addAction(delete_action)
        menu.addAction(edit_action)
        menu.exec_(self.table.viewport().mapToGlobal(position))

    def delete_receipt(self):
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            self.table.removeRow(selected_row)

    def edit_receipt(self):
        dialog = EditReceiptDialog(self.organizations, self)
        if dialog.exec_():
            category, organization_name, cashier, receipt_number, date_time, calculation_type, items = dialog.get_data()

            # Добавляем новый чек в таблицу
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            self.table.setItem(row_position, 0, QTableWidgetItem(category))
            self.table.setItem(row_position, 1, QTableWidgetItem(""))
            self.table.setItem(row_position, 2, QTableWidgetItem(organization_name))
            self.table.setItem(row_position, 3, QTableWidgetItem(cashier))
            self.table.setItem(row_position, 4, QTableWidgetItem(""))
            self.table.setItem(row_position, 5, QTableWidgetItem(receipt_number))
            self.table.setItem(row_position, 6, QTableWidgetItem(calculation_type))
            self.table.setItem(row_position, 7, QTableWidgetItem(date_time.toString("yyyy-MM-dd HH:mm:ss")))
            self.table.setItem(row_position, 8, QTableWidgetItem(""))


class EditReceiptDialog(QDialog):
    def __init__(self, organizations, parent=None):
        super().__init__(parent)
        self.organizations = organizations
        self._selected_organization = None
        self.setWindowTitle("Чек")
        self.setGeometry(200, 200, 800, 600)

        # Левая часть: ввод данных
        left_layout = QVBoxLayout()

        # Организация
        self.organization_label = QLabel("Выбрать организацию (ККМ):")
        self.organization_button = QPushButton("Выбрать")
        self.organization_button.clicked.connect(self.select_organization)

        # Кассир (с выпадающим списком)
        self.cashier_label = QLabel("Кассир:")
        self.cashier_input = QComboBox()
        self.cashier_input.addItems([
            "Васильев Григорий Павлович",
            "Николаев Евгений Алексеевич"
        ])
        self.cashier_input.setEditable(True)

        # Смена
        self.shift_label = QLabel("Смена:")
        self.shift_input = QLineEdit()

        # Номер чека
        self.receipt_number_label = QLabel("Номер чека:")
        self.receipt_number_input = QLineEdit()

        # Дата и Время
        self.date_label = QLabel("Дата:")
        self.date_edit = QDateEdit(QDateTime.currentDateTime().date())

        self.time_label = QLabel("Время:")
        self.time_edit = QTimeEdit(QDateTime.currentDateTime().time())

        # Признак расчета
        self.calculation_type_label = QLabel("Признак расчета:")
        self.calculation_type_combo = QComboBox()
        self.calculation_type_combo.addItems(["Приход", "Расход", "Возврат прихода", "Возврат расхода"])

        # Таблица товаров/услуг
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(6)
        self.items_table.setHorizontalHeaderLabels(["Наименование", "Кол-во", "Цена", "Скидка (%)", "НДС (%)", "Стоимость"])

        # Кнопка "Добавить товар/услугу"
        self.add_item_button = QPushButton("Добавить товар/услугу")
        self.add_item_button.clicked.connect(self.add_item)

        # Кнопки
        self.print_button = QPushButton("Печать чека")
        self.ok_button = QPushButton("OK")

        self.print_button.clicked.connect(self.print_receipt)
        self.ok_button.clicked.connect(self.accept)

        # Левый макет
        left_layout.addWidget(self.organization_label)
        left_layout.addWidget(self.organization_button)
        left_layout.addWidget(self.cashier_label)
        left_layout.addWidget(self.cashier_input)
        left_layout.addWidget(self.shift_label)
        left_layout.addWidget(self.shift_input)
        left_layout.addWidget(self.receipt_number_label)
        left_layout.addWidget(self.receipt_number_input)
        left_layout.addWidget(self.date_label)
        left_layout.addWidget(self.date_edit)
        left_layout.addWidget(self.time_label)
        left_layout.addWidget(self.time_edit)
        left_layout.addWidget(self.calculation_type_label)
        left_layout.addWidget(self.calculation_type_combo)
        left_layout.addWidget(self.items_table)
        left_layout.addWidget(self.add_item_button)
        left_layout.addWidget(self.print_button)
        left_layout.addWidget(self.ok_button)

        # Правая часть: предварительный просмотр чека
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setStyleSheet("background-color: #f0f0f0;")

        # Основной макет
        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout)
        main_layout.addWidget(self.preview_text)

        self.setLayout(main_layout)

    def select_organization(self):
        """Открытие диалога выбора организации."""
        dialog = OrganizationDialog(self.organizations, self)
        if dialog.exec_():
            self._selected_organization = dialog.get_selected_organization()
            if self._selected_organization:
                self.organization_button.setText(self._selected_organization["name"])
                self.update_previews()
            else:
                QMessageBox.warning(self, "Предупреждение", "Пожалуйста, выберите организацию")

    def update_previews(self):
        """Обновление предварительного просмотра чека."""
        organization = self.organization_button.text() or "Не выбрано"
        cashier = self.cashier_input.currentText() or "Не указан"
        shift = self.shift_input.text() or "Не указана"
        receipt_number = self.receipt_number_input.text() or self.generate_random_receipt_number()
        date = self.date_edit.date().toString("yyyy-MM-dd")
        time = self.time_edit.time().toString("HH:mm:ss")
        calculation_type = self.calculation_type_combo.currentText()

        # Форматирование чека
        preview = f"{organization.center(50)}\n"
        preview += f"Адрес расчета: {organization}\n"
        preview += f"Контактные данные: +7 (XXX) XXX-XX-XX\n"
        preview += "\n" + "Кассовый чек".center(50) + "\n"
        preview += f"Номер чека: {receipt_number}\n"
        preview += f"Смена: {shift}\n"
        preview += f"Кассир: {cashier}\n"
        preview += "=" * 50 + "\n"

        total_cost = 0
        for row in range(self.items_table.rowCount()):
            name = self.items_table.item(row, 0).text() if self.items_table.item(row, 0) else ""
            quantity = float(self.items_table.item(row, 1).text()) if self.items_table.item(row, 1) else 0
            price = float(self.items_table.item(row, 2).text()) if self.items_table.item(row, 2) else 0
            cost = quantity * price
            total_cost += cost

            preview += f"{name}: {quantity} x {price:.2f} = {cost:.2f}\n"

        preview += "=" * 50 + "\n"
        preview += f"{'ИТОГО':<40}{total_cost:>10.2f}\n"

        self.preview_text.setText(preview)

    def generate_random_receipt_number(self):
        """Генерация случайного номера чека из 6 цифр."""
        return f"{random.randint(100000, 999999)}"

    def add_item(self):
        dialog = AddItemDialog(self)
        if dialog.exec_():
            data = dialog.get_data()
            row = self.items_table.rowCount()
            self.items_table.insertRow(row)
            for col, value in enumerate(data):
                self.items_table.setItem(row, col, QTableWidgetItem(value))
            self.update_previews()

    def print_receipt(self):
        QMessageBox.information(self, "Печать", "Функция печати пока не реализована")

    def get_data(self):
        date_time = QDateTime(self.date_edit.date(), self.time_edit.time())
        return [
            self._selected_organization["category"] if self._selected_organization else "",
            "",  # Наименование
            self._selected_organization["name"] if self._selected_organization else "",
            self.cashier_input.currentText(),
            self.shift_input.text(),
            self.receipt_number_input.text(),
            self.calculation_type_combo.currentText(),
            date_time.toString("yyyy-MM-dd HH:mm:ss"),
            ""  # Способ оплаты
        ]


class AddItemDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить товар/услугу")
        self.setGeometry(300, 300, 400, 300)

        # Поля для ввода данных
        self.name_label = QLabel("Наименование:")
        self.name_input = QLineEdit()
        self.generate_random_name()

        self.quantity_label = QLabel("Количество:")
        self.quantity_input = QLineEdit()

        self.price_label = QLabel("Цена:")
        self.price_input = QLineEdit()

        self.discount_label = QLabel("Скидка (%):")
        self.discount_input = QLineEdit()

        self.vat_label = QLabel("НДС (%):")
        self.vat_input = QLineEdit()

        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Отмена")

        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        # Макет
        layout = QVBoxLayout()
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)
        layout.addWidget(self.quantity_label)
        layout.addWidget(self.quantity_input)
        layout.addWidget(self.price_label)
        layout.addWidget(self.price_input)
        layout.addWidget(self.discount_label)
        layout.addWidget(self.discount_input)
        layout.addWidget(self.vat_label)
        layout.addWidget(self.vat_input)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def generate_random_name(self):
        """Генерация случайного числа в формате 0*******."""
        random_number = random.randint(1000000, 9999999)
        self.name_input.setText(f"0{random_number}")

    def get_data(self):
        """Получение данных из диалогового окна."""
        name = self.name_input.text()
        quantity = self.quantity_input.text() or "0"
        price = self.price_input.text() or "0"
        discount = self.discount_input.text() or "0"
        vat = self.vat_input.text() or "0"

        try:
            quantity = float(quantity)
            price = float(price)
            discount = float(discount)
            vat = float(vat)
        except ValueError:
            quantity, price, discount, vat = 0, 0, 0, 0

        cost = quantity * price * (1 - discount / 100)
        return name, str(quantity), str(price), str(discount), str(vat), f"{cost:.2f}"


class OrganizationDialog(QDialog):
    def __init__(self, organizations, parent=None):
        super().__init__(parent)
        self.organizations = organizations
        self.setWindowTitle("Список организаций")
        self.setGeometry(300, 300, 600, 400)

        # Таблица организаций
        self.table = QTableWidget(self)
        self.table.setColumnCount(9)  # Исправлено количество столбцов
        self.table.setHorizontalHeaderLabels([
            "Категория", "Наименование", "Торговый объект", "Адрес расчета", "Контактные данные",
            "Система налогообложения", "ИНН", "ЗН КХТ", "РН КХТ"
        ])

        self.load_data()

        # Кнопки
        self.create_button = QPushButton("Создать")
        self.select_button = QPushButton("Выбрать")
        self.cancel_button = QPushButton("Отмена")

        self.create_button.clicked.connect(self.create_organization)
        self.select_button.clicked.connect(self.handle_select_button)  # Изменено на проверку
        self.cancel_button.clicked.connect(self.close)

        # Макет
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.create_button)
        button_layout.addWidget(self.select_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def load_data(self):
        """Загрузка данных об организациях в таблицу."""
        self.table.setRowCount(len(self.organizations))
        for row, org in enumerate(self.organizations):
            self.table.setItem(row, 0, QTableWidgetItem(org.get("category", "")))
            self.table.setItem(row, 1, QTableWidgetItem(org.get("name", "")))
            self.table.setItem(row, 2, QTableWidgetItem(org.get("trade_object", "")))
            self.table.setItem(row, 3, QTableWidgetItem(org.get("address", "")))
            self.table.setItem(row, 4, QTableWidgetItem(org.get("contact", "")))
            self.table.setItem(row, 5, QTableWidgetItem(org.get("tax_system", "")))
            self.table.setItem(row, 6, QTableWidgetItem(org.get("inn", "")))
            self.table.setItem(row, 7, QTableWidgetItem(org.get("zn_kht", "")))
            self.table.setItem(row, 8, QTableWidgetItem(org.get("rn_kht", "")))

    def handle_select_button(self):
        """Обработка нажатия кнопки 'Выбрать' с проверкой выбора строки."""
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            self.accept()
        else:
            QMessageBox.warning(self, "Предупреждение", "Пожалуйста, выберите организацию")

    def create_organization(self):
        dialog = OrganizationPropertiesDialog(self)
        if dialog.exec_():
            new_org = dialog.get_data()
            self.organizations.append(new_org)
            self.load_data()

    def get_selected_organization(self):
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            return {
                "category": self.table.item(selected_row, 0).text(),
                "name": self.table.item(selected_row, 1).text(),
                "trade_object": self.table.item(selected_row, 2).text(),
                "address": self.table.item(selected_row, 3).text(),
                "contact": self.table.item(selected_row, 4).text(),
                "tax_system": self.table.item(selected_row, 5).text(),
                "inn": self.table.item(selected_row, 6).text(),
                "zn_kht": self.table.item(selected_row, 7).text(),
                "rn_kht": self.table.item(selected_row, 8).text()
            }
        return None


class OrganizationPropertiesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Свойства организации")
        self.setGeometry(400, 400, 400, 300)

        # Поля для ввода данных
        self.category_label = QLabel("Категория:")
        self.category_combo = QComboBox()
        self.category_combo.addItems(["Запчасти", "Работы"])

        self.name_label = QLabel("Наименование:")
        self.name_input = QLineEdit()

        self.trade_object_label = QLabel("Торговый объект:")
        self.trade_object_input = QLineEdit()

        self.address_label = QLabel("Адрес расчета:")
        self.address_input = QLineEdit()

        self.contact_label = QLabel("Контактные данные:")
        self.contact_input = QLineEdit()

        self.tax_system_label = QLabel("Система налогообложения:")
        self.tax_system_input = QLineEdit()

        self.inn_label = QLabel("ИНН:")
        self.inn_input = QLineEdit()

        self.zn_kht_label = QLabel("ЗН КХТ:")
        self.zn_kht_input = QLineEdit()

        self.rn_kht_label = QLabel("РН КХТ:")
        self.rn_kht_input = QLineEdit()

        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Отмена")

        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        # Макет
        layout = QVBoxLayout()
        layout.addWidget(self.category_label)
        layout.addWidget(self.category_combo)
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)
        layout.addWidget(self.trade_object_label)
        layout.addWidget(self.trade_object_input)
        layout.addWidget(self.address_label)
        layout.addWidget(self.address_input)
        layout.addWidget(self.contact_label)
        layout.addWidget(self.contact_input)
        layout.addWidget(self.tax_system_label)
        layout.addWidget(self.tax_system_input)
        layout.addWidget(self.inn_label)
        layout.addWidget(self.inn_input)
        layout.addWidget(self.zn_kht_label)
        layout.addWidget(self.zn_kht_input)
        layout.addWidget(self.rn_kht_label)
        layout.addWidget(self.rn_kht_input)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def get_data(self):
        """Получение данных о новой организации."""
        return {
            "category": self.category_combo.currentText(),
            "name": self.name_input.text(),
            "trade_object": self.trade_object_input.text(),
            "address": self.address_input.text(),
            "contact": self.contact_input.text(),
            "tax_system": self.tax_system_input.text(),
            "inn": self.inn_input.text(),
            "zn_kht": self.zn_kht_input.text(),
            "rn_kht": self.rn_kht_input.text()
        }


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())