"""
main.py — Ponto de entrada do Sistema de Controle Financeiro em PyQt6.
Nitidez cristalina Retina HiDPI, fontes geométrica Avenir Next e paleta de cores foscas elegante.
"""

import sys
from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QCursor
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTabWidget, QStatusBar, QMessageBox, QFileDialog, QFrame
)

from data_manager import DataManager
from gui_forms import FormularioRegistro, TabelaTransacoes
from gui_dashboard import Dashboard
from utils import FONTE_GEO, CORES_PALETA, formatar_moeda


class AplicacaoFinanceira(QMainWindow):
    """Aplicação principal desenvolvida em PyQt6 com nitidez Retina HiDPI."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Controle Financeiro")
        self.resize(1140, 770)
        self.setMinimumSize(980, 680)

        # Configurações de estilo QSS global
        self._aplicar_estilo_qss()

        self.dm = DataManager()
        self._fazer_backup_inicial()

        # Widget Central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header Superior
        self._criar_header(main_layout)

        # Container de Abas QTabWidget
        self._criar_abas(main_layout)

        # Barra de Status
        self._criar_barra_status()

        self._atualizar_status()

    def _aplicar_estilo_qss(self, dark_mode=True):
        """Aplica folha de estilo CSS/QSS global com cantos arredondados e cores foscas elegantes."""
        if dark_mode:
            bg = "#0f172a"          # Slate 900
            card_bg = "#1e293b"     # Slate 800
            card_accent = "#334155" # Slate 700
            borda = "#334155"
            texto = "#f8fafc"
            texto_mutado = "#94a3b8"
            accent_color = "#38bdf8"
            hover_color = "#475569"
            table_alt = "#172033"
        else:
            bg = "#f1f5f9"          # Slate 100
            card_bg = "#ffffff"     # White
            card_accent = "#e2e8f0" # Slate 200
            borda = "#cbd5e1"
            texto = "#0f172a"
            texto_mutado = "#64748b"
            accent_color = "#0284c7"
            hover_color = "#f1f5f9"
            table_alt = "#f8fafc"

        qss = f"""
            QMainWindow, QWidget {{
                background-color: {bg};
                color: {texto};
                font-family: "{FONTE_GEO}";
            }}
            QFrame#cardForm, QFrame#cardTabela, QFrame#cardDireito, QFrame#cardGraficos {{
                background-color: {card_bg};
                border: 1px solid {borda};
                border-radius: 16px;
            }}
            QTabWidget::pane {{
                border: none;
                background-color: {bg};
            }}
            QTabBar::tab {{
                background-color: {card_bg};
                color: {texto_mutado};
                padding: 8px 16px;
                margin-right: 4px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                border: 1px solid {borda};
                border-bottom: none;
                font-weight: bold;
                font-size: 12px;
            }}
            QTabBar::tab:selected {{
                background-color: {card_accent};
                color: {accent_color};
                border-bottom: 2px solid {accent_color};
            }}
            QTabBar::tab:hover {{
                background-color: {hover_color};
            }}
            QLineEdit, QComboBox {{
                background-color: {card_bg};
                color: {texto};
                border: 1px solid {borda};
                border-radius: 8px;
                padding: 5px 10px;
                selection-background-color: {card_accent};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QPushButton {{
                background-color: {card_bg};
                color: {texto};
                border: 1px solid {borda};
                border-radius: 8px;
                padding: 5px 12px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QTableWidget {{
                background-color: {card_bg};
                alternate-background-color: {table_alt};
                color: {texto};
                gridline-color: {borda};
                border: 1px solid {borda};
                border-radius: 10px;
            }}
            QHeaderView::section {{
                background-color: {card_accent};
                color: {accent_color};
                font-weight: bold;
                padding: 8px;
                border: none;
            }}
            QTableWidget::item {{
                padding: 6px;
            }}
            QTableWidget::item:selected {{
                background-color: {card_accent};
                color: {texto};
            }}
            QScrollBar:vertical {{
                background-color: {bg};
                width: 10px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {card_accent};
                border-radius: 5px;
            }}
        """
        self.setStyleSheet(qss)

    def _criar_header(self, parent_layout):
        header = QFrame()
        header.setFixedHeight(55)
        header.setStyleSheet(f"border-bottom: 1px solid {CORES_PALETA['borda_suave']};")

        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 5, 20, 5)

        lbl_logo = QLabel("⚡ Controle Financeiro")
        lbl_logo.setFont(QFont(FONTE_GEO, 16, QFont.Weight.Bold))
        lbl_logo.setStyleSheet(f"color: {CORES_PALETA['ciano_brilhante']};")
        layout.addWidget(lbl_logo)

        lbl_sub = QLabel(" |  Gestão Inteligente & Voz")
        lbl_sub.setFont(QFont(FONTE_GEO, 11))
        lbl_sub.setStyleSheet(f"color: {CORES_PALETA['azul_oceano']};")
        layout.addWidget(lbl_sub)

        layout.addStretch()

        self.modo_escuro = True
        self.btn_tema = QPushButton("☀️ Modo Claro")
        self.btn_tema.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_tema.clicked.connect(self._alternar_tema)
        layout.addWidget(self.btn_tema)

        btn_backup = QPushButton("💾 Backup")
        btn_backup.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_backup.clicked.connect(self._fazer_backup)
        layout.addWidget(btn_backup)

        parent_layout.addWidget(header)

    def _alternar_tema(self):
        if self.modo_escuro:
            self._aplicar_estilo_qss(dark_mode=False)
            self.btn_tema.setText("🌙 Modo Escuro")
            self.modo_escuro = False
        else:
            self._aplicar_estilo_qss(dark_mode=True)
            self.btn_tema.setText("☀️ Modo Claro")
            self.modo_escuro = True

        self.aba_dashboard.atualizar_tema(dark_mode=self.modo_escuro)

    def _criar_abas(self, parent_layout):
        self.tabs = QTabWidget()
        self.tabs.setContentsMargins(15, 10, 15, 10)

        self.aba_registro = FormularioRegistro(self.dm, on_registro=self._ao_registrar)
        self.tabs.addTab(self.aba_registro, "📝 Novo Registro")

        self.aba_transacoes = TabelaTransacoes(self.dm)
        self.tabs.addTab(self.aba_transacoes, "📋 Transações")

        self.aba_dashboard = Dashboard(self.dm)
        self.tabs.addTab(self.aba_dashboard, "📊 Dashboard")

        self.tabs.currentChanged.connect(self._ao_trocar_aba)
        parent_layout.addWidget(self.tabs)

    def _criar_barra_status(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.lbl_status = QLabel("Pronto")
        self.lbl_status.setFont(QFont(FONTE_GEO, 10))
        self.lbl_status.setStyleSheet(f"color: {CORES_PALETA['texto_mutado']}; padding-left: 15px;")
        self.status_bar.addWidget(self.lbl_status)

        self.lbl_saldo = QLabel("")
        self.lbl_saldo.setFont(QFont(FONTE_GEO, 11, QFont.Weight.Bold))
        self.lbl_saldo.setStyleSheet("color: #64b687; padding-right: 15px;")
        self.status_bar.addPermanentWidget(self.lbl_saldo)

    def _ao_registrar(self):
        self._atualizar_status()

    def _ao_trocar_aba(self, idx):
        if idx == 1:
            self.aba_transacoes.atualizar()
        elif idx == 2:
            self.aba_dashboard.atualizar()
        self._atualizar_status()

    def _atualizar_status(self):
        hoje = datetime.now()
        resumo = self.dm.resumo_mensal(hoje.month, hoje.year)
        total = self.dm.total_registros()

        self.lbl_status.setText(f"📊 Total: {total} transações  |  Período: {hoje.strftime('%m/%Y')}")

        saldo = resumo["saldo"]
        cor = CORES_PALETA['verde_esmeralda'] if saldo >= 0 else CORES_PALETA['rosa_coral']
        self.lbl_saldo.setText(f"Saldo do Mês: {formatar_moeda(saldo)}")
        self.lbl_saldo.setStyleSheet(f"color: {cor}; padding-right: 15px;")

    def _fazer_backup(self):
        caminho = self.dm.backup()
        if caminho:
            QMessageBox.information(self, "Backup Realizado", f"✅ Cópia de segurança criada com sucesso em:\n{caminho}")
        else:
            messagebox.showinfo("Backup", "Nenhum registro para salvar no momento.")

    def _fazer_backup_inicial(self):
        try:
            self.dm.backup()
        except Exception:
            pass


def main():
    # Habilita suporte nativo a High-DPI no PyQt6
    app = QApplication(sys.argv)

    window = AplicacaoFinanceira()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
