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

        # 기본 파일 버튼 레이아웃
        self.default_files_layout = QHBoxLayout()
        
        # 행정동코드 버튼
        self.admin_code_button = QPushButton("법정동코드")
        self.admin_code_button.clicked.connect(lambda: self.open_default_csv('sources/법정동코드 전체자료.txt'))
        self.default_files_layout.addWidget(self.admin_code_button)
        
        # 용도지역분류코드 버튼
        self.land_use_button = QPushButton("용도지역분류코드")
        self.land_use_button.clicked.connect(lambda: self.open_default_csv('sources/default_data2.csv'))
        self.default_files_layout.addWidget(self.land_use_button)
        
        # 기본 파일 버튼 레이아웃 추가
        self.layout.addLayout(self.default_files_layout)

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
        
        # 초기 기본 파일 불러오기 대신 테이블 초기화만 수행
        self.init_table()

    def init_table(self):
        """테이블 초기화"""
        self.table.setRowCount(0)
        self.table.setColumnCount(0)
        self.original_data = []

    def open_default_csv(self, filename):
        """지정된 기본 CSV 파일을 엽니다."""
        file_path = os.path.join(os.path.dirname(__file__), filename)
        self.load_file(file_path)

    def open_csv(self, default=False):
        """사용자가 선택한 CSV, TXT 또는 Excel 파일을 엽니다."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "파일 열기", "", 
            "모든 지원 파일 (*.csv *.txt *.xlsx *.xls);;CSV 파일 (*.csv);;텍스트 파일 (*.txt);;엑셀 파일 (*.xlsx *.xls)"
        )
        
        if file_path and os.path.exists(file_path):
            self.load_file(file_path)

    def load_file(self, file_path):
        """파일을 로드하고 테이블에 표시합니다."""
        if file_path and os.path.exists(file_path):
            try:
                file_ext = os.path.splitext(file_path)[1].lower()
                df = None
                encodings_to_try = ['utf-8', 'cp949', 'euc-kr'] # 시도할 인코딩 목록

                if file_ext == '.csv':
                    for encoding in encodings_to_try:
                        try:
                            df = self.pd.read_csv(file_path, encoding=encoding)
                            break # 성공하면 루프 종료
                        except UnicodeDecodeError:
                            continue # 다음 인코딩 시도
                    if df is None:
                        raise ValueError(f"파일 인코딩을 감지할 수 없습니다. ({', '.join(encodings_to_try)} 시도됨)")
                elif file_ext == '.txt':
                    delimiter = None
                    first_line_decoded = False
                    for encoding in encodings_to_try:
                        try:
                            with open(file_path, 'r', encoding=encoding) as f:
                                first_line = f.readline()
                            first_line_decoded = True # 첫 줄 읽기 성공
                            if '\t' in first_line:
                                delimiter = '\t'
                            elif ',' in first_line:
                                delimiter = ','
                            elif ';' in first_line:
                                delimiter = ';'
                            else: # 구분자를 찾지 못한 경우, 일단 None으로 진행하거나 다른 로직 추가 가능
                                delimiter = None 
                            df = self.pd.read_csv(file_path, encoding=encoding, delimiter=delimiter)
                            break # 성공하면 루프 종료
                        except UnicodeDecodeError:
                            continue # 다음 인코딩 시도
                    if not first_line_decoded or df is None: # 첫 줄조차 못 읽었거나 df가 여전히 None이면
                        raise ValueError(f"텍스트 파일 인코딩을 감지하거나 구분자를 찾을 수 없습니다. ({', '.join(encodings_to_try)} 시도됨)")
                elif file_ext in ['.xlsx', '.xls']:
                    df = self.pd.read_excel(file_path)
                else:
                    raise ValueError("지원하지 않는 파일 형식입니다.")

                if df is None: # 모든 시도 후에도 df가 None이면 오류
                    raise ValueError("파일을 읽을 수 없습니다. 지원하는 인코딩이 아니거나 파일이 손상되었을 수 있습니다.")

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
                
                # 파일명 표시
                self.setWindowTitle(f"CSV Viewer by Qbong - {os.path.basename(file_path)}")
                
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