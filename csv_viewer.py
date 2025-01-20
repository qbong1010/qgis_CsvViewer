from qgis.PyQt.QtWidgets import ( 
    QDockWidget, QVBoxLayout, QPushButton, QFileDialog,
    QTableWidget, QTableWidgetItem, QWidget, QLineEdit, QHBoxLayout, QLabel
)
from qgis.PyQt.QtCore import Qt
import csv
import os


class CsvViewerDockWidget(QDockWidget):

    def __init__(self, iface):
        super().__init__("CSV Viewer")
        self.iface = iface
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        # Main widget and layout
        self.widget = QWidget()
        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)

        # Open CSV button
        self.open_button = QPushButton("Open CSV")
        self.open_button.clicked.connect(self.open_csv)
        self.layout.addWidget(self.open_button)

        # Search bar
        self.search_layout = QHBoxLayout()
        self.search_label = QLabel("Search:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter text to search...")
        self.search_input.textChanged.connect(self.search_table)

        self.search_layout.addWidget(self.search_label)
        self.search_layout.addWidget(self.search_input)
        self.layout.addLayout(self.search_layout)

        # Table widget for displaying CSV content
        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        # Set the main widget
        self.setWidget(self.widget)

        # Data storage
        self.original_data = []
        
        # Load default CSV file
        self.open_csv(default=True)

    def open_csv(self, default=False):
        """Opens a CSV or TXT file and displays its content in the table."""
        if default:
            file_path = os.path.join(os.path.dirname(__file__), 'default_data.txt')  # 파일 확장자 변경
            print(f"Default file path: {file_path}")  # 디버그 출력
        else:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Open CSV or TXT File", "C:\\Users\\dohwa\\Documents\\QGIS\\QPython Script\\매칭테이블", "CSV or TXT files (*.csv *.txt)"
            )
        
        if file_path and os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    # 구분자를 지정합니다. 필요에 따라 '\t' 또는 다른 구분자로 변경하세요.
                    reader = csv.reader(file, delimiter=',')  # 기본은 쉼표로 설정
                    headers = next(reader)
                    self.original_data = list(reader)

                # Initialize table
                self.table.setRowCount(0)
                self.table.setColumnCount(len(headers))
                self.table.setHorizontalHeaderLabels(headers)

                # Display all data
                self.display_data(self.original_data)

                # Clear search input
                self.search_input.clear()
            except Exception as e:
                print(f"Error opening file: {e}")
        else:
            print("File not found or path is incorrect!")  # 디버그 출력

    def display_data(self, data):
        """Displays data in the table."""
        self.table.setRowCount(len(data))
        for row_index, row_data in enumerate(data):
            for col_index, cell in enumerate(row_data):
                self.table.setItem(row_index, col_index, QTableWidgetItem(str(cell)))
        self.table.resizeColumnsToContents()

    def search_table(self):
        """Filters table rows based on the search input."""
        search_text = self.search_input.text().lower()
        if not search_text:
            self.display_data(self.original_data)
            return

        filtered_data = [
            row for row in self.original_data if any(search_text in str(cell).lower() for cell in row)
        ]
        self.display_data(filtered_data)