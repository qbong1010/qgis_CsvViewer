from qgis.PyQt.QtWidgets import ( 
    QDockWidget, QVBoxLayout, QPushButton, QFileDialog,
    QTableWidget, QTableWidgetItem, QWidget, QLineEdit, QHBoxLayout, QLabel
)
from qgis.PyQt.QtCore import Qt
import csv
import os


class CsvViewerDockWidget(QDockWidget):

    def __init__(self, iface):
        super().__init__("CSV Viewer by Qbong")
        self.iface = iface
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        # 필요한 라이브러리 import
        try:
            import pandas as pd
            self.pd = pd
        except ImportError:
            self.iface.messageBar().pushMessage(
                "Error", "pandas 라이브러리가 필요합니다. pip install pandas를 실행하세요.", level=2
            )
            return

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
        """Opens a CSV, TXT or Excel file and displays its content in the table."""
        if default:
            file_path = os.path.join(os.path.dirname(__file__), 'default_data.csv')
        else:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "파일 열기", "", 
                "모든 지원 파일 (*.csv *.txt *.xlsx *.xls);;CSV 파일 (*.csv);;텍스트 파일 (*.txt);;엑셀 파일 (*.xlsx *.xls)"
            )
        
        if file_path and os.path.exists(file_path):
            try:
                file_ext = os.path.splitext(file_path)[1].lower()
                
                if file_ext == '.csv':
                    # CSV 파일 처리
                    df = self.pd.read_csv(file_path, encoding='utf-8')
                elif file_ext == '.txt':
                    # TXT 파일 처리 (탭, 쉼표, 세미콜론 구분자 자동 감지)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        first_line = f.readline()
                    if '\t' in first_line:
                        delimiter = '\t'
                    elif ',' in first_line:
                        delimiter = ','
                    elif ';' in first_line:
                        delimiter = ';'
                    else:
                        delimiter = None
                    df = self.pd.read_csv(file_path, encoding='utf-8', delimiter=delimiter)
                elif file_ext in ['.xlsx', '.xls']:
                    # 엑셀 파일 처리
                    df = self.pd.read_excel(file_path)
                else:
                    raise ValueError("지원하지 않는 파일 형식입니다.")

                # DataFrame을 테이블에 표시
                headers = df.columns.tolist()
                self.original_data = df.values.tolist()

                # Initialize table
                self.table.setRowCount(0)
                self.table.setColumnCount(len(headers))
                self.table.setHorizontalHeaderLabels(headers)

                # Display all data
                self.display_data(self.original_data)

                # Clear search input
                self.search_input.clear()
                
            except Exception as e:
                self.iface.messageBar().pushMessage(
                    "Error", f"파일을 여는 중 오류가 발생했습니다: {str(e)}", level=2
                )
        else:
            self.iface.messageBar().pushMessage(
                "Warning", "파일을 찾을 수 없거나 경로가 잘못되었습니다!", level=1
            )

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