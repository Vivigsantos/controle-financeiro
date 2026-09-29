"""
gui_forms.py — Interface PyQt6 no estilo Midnight Ocean Navy.
"""

import threading
from datetime import datetime, timedelta

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QCursor
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox
)

from categories import TIPOS, FORMAS_PAGAMENTO, get_categorias
from data_manager import DataManager
from utils import FONTE_GEO, CORES_PALETA, formatar_moeda, validar_valor, nome_mes
from voice_input import escutar_microfone, interpretar_comando_voz


class ThreadVoz(QThread):
    """Thread dedicada em PyQt6 para escutar microfone sem travar a interface."""
    resultado_signal = pyqtSignal(bool, str)

    def run(self):
        sucesso, resultado = escutar_microfone(timeout=6)
        self.resultado_signal.emit(sucesso, resultado)


class FormularioRegistro(QWidget):
    """Aba de novo registro em PyQt6 com estilo Midnight Ocean Navy."""

    def __init__(self, data_manager: DataManager, on_registro=None):
        super().__init__()
        self.dm = data_manager
        self.on_registro = on_registro

        self._criar_widgets()
        self._atualizar_recentes()

    def _criar_widgets(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # ── Coluna Esquerda: Formulário de Registro (55%) ──
        card_esquerdo = QFrame()
        card_esquerdo.setObjectName("cardForm")
        card_esquerdo.setStyleSheet(f"""
            QFrame#cardForm {{
                background-color: {CORES_PALETA['card_dark']};
                border: 1px solid {CORES_PALETA['borda_suave']};
                border-radius: 18px;
            }}
        """)

        form_layout = QVBoxLayout(card_esquerdo)
        form_layout.setContentsMargins(25, 20, 25, 20)

        # Cabeçalho do Card
        header_layout = QHBoxLayout()
        lbl_titulo = QLabel("📝 Novo Registro")
        lbl_titulo.setFont(QFont(FONTE_GEO, 14, QFont.Weight.Bold))
        lbl_titulo.setStyleSheet(f"color: {CORES_PALETA['ciano_brilhante']};")
        header_layout.addWidget(lbl_titulo)

        lbl_sub = QLabel("Digite ou Use Comando de Voz")
        lbl_sub.setFont(QFont(FONTE_GEO, 10))
        lbl_sub.setStyleSheet(f"color: {CORES_PALETA['texto_mutado']};")
        header_layout.addWidget(lbl_sub, alignment=Qt.AlignmentFlag.AlignRight)

        form_layout.addLayout(header_layout)

        # Container dos Campos
        grid_layout = QVBoxLayout()
        grid_layout.setSpacing(12)

        # Data
        data_layout = QHBoxLayout()
        lbl_data = QLabel("Data:")
        lbl_data.setFont(QFont(FONTE_GEO, 11, QFont.Weight.Bold))
        lbl_data.setFixedWidth(100)
        lbl_data.setStyleSheet(f"color: {CORES_PALETA['texto_principal']};")
        data_layout.addWidget(lbl_data)

        self._data_atual = datetime.now()

        btn_prev = QPushButton("◀")
        btn_prev.setFixedSize(32, 32)
        btn_prev.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_prev.clicked.connect(self._dia_anterior)
        data_layout.addWidget(btn_prev)

        self.txt_data = QLineEdit(self._data_atual.strftime("%d/%m/%Y"))
        self.txt_data.setFixedWidth(120)
        self.txt_data.setFixedHeight(34)
        self.txt_data.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.txt_data.setFont(QFont(FONTE_GEO, 11))
        data_layout.addWidget(self.txt_data)

        btn_next = QPushButton("▶")
        btn_next.setFixedSize(32, 32)
        btn_next.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_next.clicked.connect(self._proximo_dia)
        data_layout.addWidget(btn_next)

        btn_hoje = QPushButton("Hoje")
        btn_hoje.setFixedHeight(32)
        btn_hoje.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_hoje.clicked.connect(self._data_hoje)
        data_layout.addWidget(btn_hoje)

        data_layout.addStretch()
        grid_layout.addLayout(data_layout)

        # Tipo
        tipo_layout = QHBoxLayout()
        lbl_tipo = QLabel("Tipo:")
        lbl_tipo.setFont(QFont(FONTE_GEO, 11, QFont.Weight.Bold))
        lbl_tipo.setFixedWidth(100)
        lbl_tipo.setStyleSheet(f"color: {CORES_PALETA['texto_principal']};")
        tipo_layout.addWidget(lbl_tipo)

        self.cmb_tipo = QComboBox()
        self.cmb_tipo.addItems(TIPOS)
        self.cmb_tipo.setFixedHeight(34)
        self.cmb_tipo.setFont(QFont(FONTE_GEO, 11))
        self.cmb_tipo.currentTextChanged.connect(self._atualizar_categorias)
        tipo_layout.addWidget(self.cmb_tipo)
        grid_layout.addLayout(tipo_layout)

        # Categoria
        cat_layout = QHBoxLayout()
        lbl_cat = QLabel("Categoria:")
        lbl_cat.setFont(QFont(FONTE_GEO, 11, QFont.Weight.Bold))
        lbl_cat.setFixedWidth(100)
        lbl_cat.setStyleSheet(f"color: {CORES_PALETA['texto_principal']};")
        cat_layout.addWidget(lbl_cat)

        self.cmb_cat = QComboBox()
        self.cmb_cat.setFixedHeight(34)
        self.cmb_cat.setFont(QFont(FONTE_GEO, 11))
        cat_layout.addWidget(self.cmb_cat)
        grid_layout.addLayout(cat_layout)
        self._atualizar_categorias()

        # Descrição
        desc_layout = QHBoxLayout()
        lbl_desc = QLabel("Descrição:")
        lbl_desc.setFont(QFont(FONTE_GEO, 11, QFont.Weight.Bold))
        lbl_desc.setFixedWidth(100)
        lbl_desc.setStyleSheet(f"color: {CORES_PALETA['texto_principal']};")
        desc_layout.addWidget(lbl_desc)

        self.txt_desc = QLineEdit()
        self.txt_desc.setFixedHeight(34)
        self.txt_desc.setFont(QFont(FONTE_GEO, 11))
        self.txt_desc.setPlaceholderText("ex: Supermercado Extra")
        desc_layout.addWidget(self.txt_desc)
        grid_layout.addLayout(desc_layout)

        # Valor
        valor_layout = QHBoxLayout()
        lbl_valor = QLabel("Valor (R$):")
        lbl_valor.setFont(QFont(FONTE_GEO, 11, QFont.Weight.Bold))
        lbl_valor.setFixedWidth(100)
        lbl_valor.setStyleSheet(f"color: {CORES_PALETA['texto_principal']};")
        valor_layout.addWidget(lbl_valor)

        self.txt_valor = QLineEdit()
        self.txt_valor.setFixedHeight(34)
        self.txt_valor.setFont(QFont(FONTE_GEO, 11))
        self.txt_valor.setPlaceholderText("0,00")
        valor_layout.addWidget(self.txt_valor)
        grid_layout.addLayout(valor_layout)

        # Pagamento
        pag_layout = QHBoxLayout()
        lbl_pag = QLabel("Pagamento:")
        lbl_pag.setFont(QFont(FONTE_GEO, 11, QFont.Weight.Bold))
        lbl_pag.setFixedWidth(100)
        lbl_pag.setStyleSheet(f"color: {CORES_PALETA['texto_principal']};")
        pag_layout.addWidget(lbl_pag)

        self.cmb_pag = QComboBox()
        self.cmb_pag.addItems(FORMAS_PAGAMENTO)
        self.cmb_pag.setFixedHeight(34)
        self.cmb_pag.setFont(QFont(FONTE_GEO, 11))
        pag_layout.addWidget(self.cmb_pag)
        grid_layout.addLayout(pag_layout)

        form_layout.addLayout(grid_layout)

        # Botões de Ação
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 15, 0, 5)

        self.btn_registrar = QPushButton("  ✅ Registrar Transação  ")
        self.btn_registrar.setFixedHeight(40)
        self.btn_registrar.setFont(QFont(FONTE_GEO, 11, QFont.Weight.Bold))
        self.btn_registrar.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_registrar.setStyleSheet(f"""
            QPushButton {{
                background-color: {CORES_PALETA['verde_esmeralda']};
                color: #ffffff;
                border-radius: 10px;
                padding: 0 15px;
            }}
            QPushButton:hover {{
                background-color: #0d9668;
            }}
        """)
        self.btn_registrar.clicked.connect(self._registrar)
        btn_layout.addWidget(self.btn_registrar)

        self.btn_voz = QPushButton("  🎤 Preencher por Voz  ")
        self.btn_voz.setFixedHeight(40)
        self.btn_voz.setFont(QFont(FONTE_GEO, 11, QFont.Weight.Bold))
        self.btn_voz.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_voz.setStyleSheet(f"""
            QPushButton {{
                background-color: {CORES_PALETA['card_accent']};
                color: {CORES_PALETA['ciano_brilhante']};
                border: 1px solid {CORES_PALETA['ciano_brilhante']};
                border-radius: 10px;
                padding: 0 15px;
            }}
            QPushButton:hover {{
                background-color: #243866;
            }}
        """)
        self.btn_voz.clicked.connect(self._ouvir_voz)
        btn_layout.addWidget(self.btn_voz)

        form_layout.addLayout(btn_layout)

        self.lbl_feedback = QLabel("")
        self.lbl_feedback.setFont(QFont(FONTE_GEO, 10))
        self.lbl_feedback.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(self.lbl_feedback)

        form_layout.addStretch()
        main_layout.addWidget(card_esquerdo, stretch=55)

        # ── Coluna Direita: Lançamentos Recentes & Dica de Voz (45%) ──
        card_direito = QFrame()
        card_direito.setObjectName("cardDireito")
        card_direito.setStyleSheet(f"""
            QFrame#cardDireito {{
                background-color: {CORES_PALETA['card_dark']};
                border: 1px solid {CORES_PALETA['borda_suave']};
                border-radius: 18px;
            }}
        """)

        right_layout = QVBoxLayout(card_direito)
        right_layout.setContentsMargins(20, 20, 20, 20)

        lbl_rec_title = QLabel("⚡ Últimos Lançamentos")
        lbl_rec_title.setFont(QFont(FONTE_GEO, 12, QFont.Weight.Bold))
        lbl_rec_title.setStyleSheet(f"color: {CORES_PALETA['ciano_brilhante']};")
        right_layout.addWidget(lbl_rec_title)

        self.recent_container = QVBoxLayout()
        self.recent_container.setSpacing(8)
        right_layout.addLayout(self.recent_container)

        right_layout.addStretch()

        # Dica de Voz
        dica_box = QFrame()
        dica_box.setStyleSheet(f"""
            background-color: {CORES_PALETA['bg_dark']};
            border-radius: 12px;
            padding: 10px;
        """)
        dica_layout = QVBoxLayout(dica_box)
        lbl_dica_head = QLabel("💡 Comandos de Voz Rápidos")
        lbl_dica_head.setFont(QFont(FONTE_GEO, 11, QFont.Weight.Bold))
        lbl_dica_head.setStyleSheet(f"color: {CORES_PALETA['amarelo_ouro']};")
        dica_layout.addWidget(lbl_dica_head)

        dicas = [
            "• \"Saída alimentação supermercado 150 no cartão\"",
            "• \"Gasolina 200 reais no pix\"",
            "• \"Entrada salário 5000 reais\"",
        ]
        for d in dicas:
            lbl_d = QLabel(d)
            lbl_d.setFont(QFont(FONTE_GEO, 9))
            lbl_d.setStyleSheet(f"color: {CORES_PALETA['texto_mutado']};")
            dica_layout.addWidget(lbl_d)

        right_layout.addWidget(dica_box)
        main_layout.addWidget(card_direito, stretch=45)

    def _atualizar_recentes(self):
        while self.recent_container.count():
            item = self.recent_container.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        df = self.dm.obter_transacoes()
        if df.empty:
            lbl_vazio = QLabel("Nenhuma transação cadastrada.")
            lbl_vazio.setFont(QFont(FONTE_GEO, 10))
            lbl_vazio.setStyleSheet(f"color: {CORES_PALETA['texto_mutado']};")
            self.recent_container.addWidget(lbl_vazio)
            return

        ultimos = df.tail(5).iloc[::-1]

        for _, row in ultimos.iterrows():
            item_frame = QFrame()
            item_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {CORES_PALETA['card_accent']};
                    border-radius: 10px;
                }}
            """)
            item_layout = QHBoxLayout(item_frame)
            item_layout.setContentsMargins(12, 8, 12, 8)

            tipo = str(row["Tipo"])
            emoji = "🟢" if tipo == "Entrada" else "🔴"
            cor_val = CORES_PALETA['verde_esmeralda'] if tipo == "Entrada" else CORES_PALETA['rosa_coral']

            info_box = QVBoxLayout()
            lbl_desc = QLabel(f"{emoji} {row['Descrição']}")
            lbl_desc.setFont(QFont(FONTE_GEO, 10, QFont.Weight.Bold))
            lbl_desc.setStyleSheet(f"color: {CORES_PALETA['texto_principal']};")
            info_box.addWidget(lbl_desc)

            lbl_sub = QLabel(f"{row['Data']} • {row['Categoria']}")
            lbl_sub.setFont(QFont(FONTE_GEO, 9))
            lbl_sub.setStyleSheet(f"color: {CORES_PALETA['texto_mutado']};")
            info_box.addWidget(lbl_sub)

            item_layout.addLayout(info_box)

            lbl_val = QLabel(formatar_moeda(float(row["Valor"])))
            lbl_val.setFont(QFont(FONTE_GEO, 10, QFont.Weight.Bold))
            lbl_val.setStyleSheet(f"color: {cor_val};")
            item_layout.addWidget(lbl_val, alignment=Qt.AlignmentFlag.AlignRight)

            self.recent_container.addWidget(item_frame)

    def _ouvir_voz(self):
        self.btn_voz.setEnabled(False)
        self.btn_voz.setText("🎙️ Ouvindo...")
        self.lbl_feedback.setText("🎙️ Fale sua transação no microfone...")
        self.lbl_feedback.setStyleSheet(f"color: {CORES_PALETA['ciano_brilhante']};")

        self.thread_voz = ThreadVoz()
        self.thread_voz.resultado_signal.connect(self._finalizar_voz)
        self.thread_voz.start()

    def _finalizar_voz(self, sucesso: bool, resultado: str):
        self.btn_voz.setEnabled(True)
        self.btn_voz.setText("  🎤 Preencher por Voz  ")

        if not sucesso:
            self.lbl_feedback.setText(f"⚠️ {resultado}")
            self.lbl_feedback.setStyleSheet(f"color: {CORES_PALETA['rosa_coral']};")
            return

        dados = interpretar_comando_voz(resultado)

        if dados["tipo"]:
            self.cmb_tipo.setCurrentText(dados["tipo"])
            self._atualizar_categorias()

        if dados["categoria"]:
            self.cmb_cat.setCurrentText(dados["categoria"])

        if dados["descricao"]:
            self.txt_desc.setText(dados["descricao"])

        if dados["valor"]:
            self.txt_valor.setText(str(dados["valor"]))

        if dados["forma_pagamento"]:
            self.cmb_pag.setCurrentText(dados["forma_pagamento"])

        val_fmt = formatar_moeda(dados['valor']) if dados['valor'] else ""
        self.lbl_feedback.setText(f"🗣️ Entendido: \"{dados['descricao']}\" {val_fmt}".strip())
        self.lbl_feedback.setStyleSheet(f"color: {CORES_PALETA['verde_esmeralda']};")

    def _dia_anterior(self):
        try:
            dt = datetime.strptime(self.txt_data.text(), "%d/%m/%Y")
            dt -= timedelta(days=1)
        except ValueError:
            dt = datetime.now() - timedelta(days=1)
        self.txt_data.setText(dt.strftime("%d/%m/%Y"))

    def _proximo_dia(self):
        try:
            dt = datetime.strptime(self.txt_data.text(), "%d/%m/%Y")
            dt += timedelta(days=1)
        except ValueError:
            dt = datetime.now() + timedelta(days=1)
        self.txt_data.setText(dt.strftime("%d/%m/%Y"))

    def _data_hoje(self):
        self.txt_data.setText(datetime.now().strftime("%d/%m/%Y"))

    def _atualizar_categorias(self):
        tipo = self.cmb_tipo.currentText()
        cats = get_categorias(tipo)
        self.cmb_cat.clear()
        self.cmb_cat.addItems(cats)

    def _registrar(self):
        valor = validar_valor(self.txt_valor.text())
        if valor is None:
            QMessageBox.warning(self, "Valor Inválido", "Por favor, insira um valor numérico válido maior que zero.")
            self.txt_valor.setFocus()
            return

        desc = self.txt_desc.text().strip()
        if not desc:
            QMessageBox.warning(self, "Descrição Vazia", "Por favor, insira uma descrição para a transação.")
            self.txt_desc.setFocus()
            return

        data = self.txt_data.text()
        tipo = self.cmb_tipo.currentText()
        cat = self.cmb_cat.currentText()
        pag = self.cmb_pag.currentText()

        self.dm.adicionar(data, tipo, cat, desc, valor, pag)

        emoji = "🟢" if tipo == "Entrada" else "🔴"
        cor = CORES_PALETA['verde_esmeralda'] if tipo == "Entrada" else CORES_PALETA['rosa_coral']
        self.lbl_feedback.setText(f"{emoji} {tipo} registrada: {formatar_moeda(valor)} ({cat})")
        self.lbl_feedback.setStyleSheet(f"color: {cor};")

        self.txt_desc.clear()
        self.txt_valor.clear()
        self.txt_desc.setFocus()

        self._atualizar_recentes()

        if self.on_registro:
            self.on_registro()


class TabelaTransacoes(QWidget):
    """Tabela de transações em PyQt6 no estilo Midnight Ocean Navy."""

    def __init__(self, data_manager: DataManager):
        super().__init__()
        self.dm = data_manager
        self._criar_widgets()
        self.atualizar()

    def _criar_widgets(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        card = QFrame()
        card.setObjectName("cardTabela")
        card.setStyleSheet(f"""
            QFrame#cardTabela {{
                background-color: {CORES_PALETA['card_dark']};
                border: 1px solid {CORES_PALETA['borda_suave']};
                border-radius: 18px;
            }}
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)

        # Toolbar superior
        tool_layout = QHBoxLayout()

        lbl_filtros = QLabel("Filtros:")
        lbl_filtros.setFont(QFont(FONTE_GEO, 10, QFont.Weight.Bold))
        lbl_filtros.setStyleSheet(f"color: {CORES_PALETA['ciano_brilhante']};")
        tool_layout.addWidget(lbl_filtros)

        lbl_mes = QLabel("Mês:")
        lbl_mes.setFont(QFont(FONTE_GEO, 9))
        lbl_mes.setStyleSheet(f"color: {CORES_PALETA['texto_mutado']};")
        tool_layout.addWidget(lbl_mes)

        self.cmb_mes = QComboBox()
        self.cmb_mes.addItems(["Todos"] + [str(i) for i in range(1, 13)])
        self.cmb_mes.setCurrentText(str(datetime.now().month))
        self.cmb_mes.setFixedHeight(30)
        self.cmb_mes.setFixedWidth(85)
        tool_layout.addWidget(self.cmb_mes)

        lbl_ano = QLabel("Ano:")
        lbl_ano.setFont(QFont(FONTE_GEO, 9))
        lbl_ano.setStyleSheet(f"color: {CORES_PALETA['texto_mutado']};")
        tool_layout.addWidget(lbl_ano)

        ano_atual = datetime.now().year
        self.cmb_ano = QComboBox()
        self.cmb_ano.addItems([str(a) for a in range(ano_atual - 5, ano_atual + 2)])
        self.cmb_ano.setCurrentText(str(ano_atual))
        self.cmb_ano.setFixedHeight(30)
        self.cmb_ano.setFixedWidth(90)
        tool_layout.addWidget(self.cmb_ano)

        lbl_tipo = QLabel("Tipo:")
        lbl_tipo.setFont(QFont(FONTE_GEO, 9))
        lbl_tipo.setStyleSheet(f"color: {CORES_PALETA['texto_mutado']};")
        tool_layout.addWidget(lbl_tipo)

        self.cmb_tipo_filtro = QComboBox()
        self.cmb_tipo_filtro.addItems(["Todos"] + TIPOS)
        self.cmb_tipo_filtro.setFixedHeight(30)
        self.cmb_tipo_filtro.setFixedWidth(105)
        tool_layout.addWidget(self.cmb_tipo_filtro)

        btn_filtrar = QPushButton("🔍 Filtrar")
        btn_filtrar.setFixedHeight(30)
        btn_filtrar.setFont(QFont(FONTE_GEO, 9))
        btn_filtrar.clicked.connect(self.atualizar)
        tool_layout.addWidget(btn_filtrar)

        tool_layout.addStretch()

        btn_edit = QPushButton("✏️ Editar")
        btn_edit.setFixedHeight(30)
        btn_edit.clicked.connect(self._editar)
        tool_layout.addWidget(btn_edit)

        btn_del = QPushButton("🗑️ Excluir")
        btn_del.setFixedHeight(30)
        btn_del.clicked.connect(self._excluir)
        tool_layout.addWidget(btn_del)

        btn_ref = QPushButton("🔄 Atualizar")
        btn_ref.setFixedHeight(30)
        btn_ref.clicked.connect(self.atualizar)
        tool_layout.addWidget(btn_ref)

        card_layout.addLayout(tool_layout)

        # Tabela QTableWidget
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(6)
        self.tabela.setHorizontalHeaderLabels(["Data", "Tipo", "Categoria", "Descrição", "Valor", "Pagamento"])
        self.tabela.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setAlternatingRowColors(True)
        self.tabela.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabela.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.tabela.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        card_layout.addWidget(self.tabela)

        self.lbl_resumo = QLabel("")
        self.lbl_resumo.setFont(QFont(FONTE_GEO, 11, QFont.Weight.Bold))
        self.lbl_resumo.setAlignment(Qt.AlignmentFlag.AlignRight)
        card_layout.addWidget(self.lbl_resumo)

        layout.addWidget(card)

    def atualizar(self):
        mes_str = self.cmb_mes.currentText()
        ano_str = self.cmb_ano.currentText()
        tipo_str = self.cmb_tipo_filtro.currentText()

        mes = None if mes_str == "Todos" else int(mes_str)
        ano = int(ano_str)
        tipo = None if tipo_str == "Todos" else tipo_str

        df = self.dm.obter_transacoes(mes=mes, ano=ano, tipo=tipo)

        self.tabela.setRowCount(0)
        self.tabela.clearSpans()

        if df.empty:
            self.lbl_resumo.setText("<span style='color: #94a3b8;'>Nenhuma transação encontrada no período.</span>")
            return

        # Converte Data para datetime temporário para ordenação por mês/ano decrescente
        df_sorted = df.copy()
        df_sorted["_dt_temp"] = df_sorted["Data"].apply(
            lambda d: datetime.strptime(str(d), "%d/%m/%Y") if isinstance(d, str) else datetime.now()
        )
        df_sorted = df_sorted.sort_values(by="_dt_temp", ascending=False)

        # Agrupa transações mantendo a ordem decrescente e os índices originais do DataFrame
        grupos_mes = {}
        for original_idx, row in df_sorted.iterrows():
            dt = row["_dt_temp"]
            chave = (dt.year, dt.month)
            if chave not in grupos_mes:
                grupos_mes[chave] = []
            grupos_mes[chave].append((original_idx, row))

        total_entradas_geral = 0.0
        total_saidas_geral = 0.0
        row_counter = 0

        for (ano_grp, mes_grp), items in grupos_mes.items():
            ent_mes = sum(float(r["Valor"]) for _, r in items if str(r["Tipo"]) == "Entrada")
            sai_mes = sum(float(r["Valor"]) for _, r in items if str(r["Tipo"]) != "Entrada")
            total_entradas_geral += ent_mes
            total_saidas_geral += sai_mes

            nome_m = nome_mes(mes_grp)

            # Insere linha divisória do mês
            self.tabela.insertRow(row_counter)
            self.tabela.setSpan(row_counter, 0, 1, 6)

            header_text = (
                f"  🗓️  {nome_m.upper()} {ano_grp}  •  "
                f"{len(items)} transações  |  "
                f"Entradas: {formatar_moeda(ent_mes)}  |  "
                f"Saídas: {formatar_moeda(sai_mes)}  |  "
                f"Saldo do Mês: {formatar_moeda(ent_mes - sai_mes)}"
            )
            item_header = QTableWidgetItem(header_text)
            item_header.setFont(QFont(FONTE_GEO, 10, QFont.Weight.Bold))
            item_header.setData(Qt.ItemDataRole.UserRole, "MONTH_HEADER")
            item_header.setFlags(Qt.ItemFlag.ItemIsEnabled)

            self.tabela.setItem(row_counter, 0, item_header)
            row_counter += 1

            # Insere transações pertencentes a este mês
            for original_idx, row in items:
                self.tabela.insertRow(row_counter)
                valor = float(row["Valor"])
                tipo_row = str(row["Tipo"])

                item_data = QTableWidgetItem(str(row["Data"]))
                item_tipo = QTableWidgetItem(tipo_row)
                item_cat = QTableWidgetItem(str(row["Categoria"]))
                item_desc = QTableWidgetItem(str(row["Descrição"]))
                item_val = QTableWidgetItem(formatar_moeda(valor))
                item_pag = QTableWidgetItem(str(row.get("Forma de Pagamento", row.get("Forma of Pagamento", "Pix"))))

                item_data.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item_tipo.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item_cat.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item_val.setTextAlignment(Qt.AlignmentFlag.AlignRight)
                item_pag.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                # Armazena o índice real do DataFrame no item
                item_data.setData(Qt.ItemDataRole.UserRole + 1, original_idx)

                for item in [item_data, item_tipo, item_cat, item_desc, item_val, item_pag]:
                    item.setFont(QFont(FONTE_GEO, 10))

                self.tabela.setItem(row_counter, 0, item_data)
                self.tabela.setItem(row_counter, 1, item_tipo)
                self.tabela.setItem(row_counter, 2, item_cat)
                self.tabela.setItem(row_counter, 3, item_desc)
                self.tabela.setItem(row_counter, 4, item_val)
                self.tabela.setItem(row_counter, 5, item_pag)
                row_counter += 1

        saldo_geral = total_entradas_geral - total_saidas_geral
        cor_saldo = CORES_PALETA['verde_esmeralda'] if saldo_geral >= 0 else CORES_PALETA['rosa_coral']
        self.lbl_resumo.setText(
            f"<span style='color: {CORES_PALETA['verde_esmeralda']};'>Entradas: <b>{formatar_moeda(total_entradas_geral)}</b></span> &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"<span style='color: {CORES_PALETA['rosa_coral']};'>Saídas: <b>{formatar_moeda(total_saidas_geral)}</b></span> &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"<span style='color: {cor_saldo};'>Saldo Geral: <b>{formatar_moeda(saldo_geral)}</b></span>"
        )

    def _editar(self):
        row = self.tabela.currentRow()
        if row < 0:
            QMessageBox.information(self, "Selecione", "Selecione uma transação para editar.")
            return

        item_zero = self.tabela.item(row, 0)
        if not item_zero or item_zero.data(Qt.ItemDataRole.UserRole) == "MONTH_HEADER":
            QMessageBox.information(self, "Aviso", "Selecione uma linha de transação válida (não o cabeçalho do mês).")
            return

        real_index = item_zero.data(Qt.ItemDataRole.UserRole + 1)
        data_val = self.tabela.item(row, 0).text()
        tipo_val = self.tabela.item(row, 1).text()
        cat_val = self.tabela.item(row, 2).text()
        desc_val = self.tabela.item(row, 3).text()
        val_val = self.tabela.item(row, 4).text()
        pag_val = self.tabela.item(row, 5).text()

        val_clean = val_val.replace("R$ ", "").replace("R$", "").replace(".", "").replace(",", ".").replace("-", "").strip()

        dlg = QWidget(self, Qt.WindowType.Window)
        dlg.setWindowTitle("Editar Transação")
        dlg.setFixedSize(400, 380)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 20, 20, 20)

        txt_d = QLineEdit(data_val)
        cmb_t = QComboBox()
        cmb_t.addItems(TIPOS)
        cmb_t.setCurrentText(tipo_val)

        cmb_c = QComboBox()
        cmb_c.addItems(get_categorias(tipo_val))
        cmb_c.setCurrentText(cat_val)

        txt_desc = QLineEdit(desc_val)
        txt_v = QLineEdit(val_clean)
        cmb_p = QComboBox()
        cmb_p.addItems(FORMAS_PAGAMENTO)
        cmb_p.setCurrentText(pag_val)

        layout.addWidget(QLabel("Data:"))
        layout.addWidget(txt_d)
        layout.addWidget(QLabel("Tipo:"))
        layout.addWidget(cmb_t)
        layout.addWidget(QLabel("Categoria:"))
        layout.addWidget(cmb_c)
        layout.addWidget(QLabel("Descrição:"))
        layout.addWidget(txt_desc)
        layout.addWidget(QLabel("Valor:"))
        layout.addWidget(txt_v)
        layout.addWidget(QLabel("Pagamento:"))
        layout.addWidget(cmb_p)

        btn_salvar = QPushButton("💾 Salvar Alterações")
        btn_salvar.setFixedHeight(36)
        btn_salvar.setStyleSheet(f"background-color: {CORES_PALETA['verde_esmeralda']}; color: white; border-radius: 8px;")

        def _on_save():
            v = validar_valor(txt_v.text())
            if v is None:
                QMessageBox.warning(dlg, "Erro", "Valor inválido.")
                return
            self.dm.editar(real_index, txt_d.text(), cmb_t.currentText(), cmb_c.currentText(), txt_desc.text(), v, cmb_p.currentText())
            dlg.close()
            self.atualizar()

        btn_salvar.clicked.connect(_on_save)
        layout.addWidget(btn_salvar)

        dlg.show()

    def _excluir(self):
        row = self.tabela.currentRow()
        if row < 0:
            QMessageBox.information(self, "Selecione", "Selecione uma transação para excluir.")
            return

        item_zero = self.tabela.item(row, 0)
        if not item_zero or item_zero.data(Qt.ItemDataRole.UserRole) == "MONTH_HEADER":
            QMessageBox.information(self, "Aviso", "Selecione uma linha de transação válida (não o cabeçalho do mês).")
            return

        real_index = item_zero.data(Qt.ItemDataRole.UserRole + 1)
        desc = self.tabela.item(row, 3).text()
        val = self.tabela.item(row, 4).text()

        reply = QMessageBox.question(
            self, "Confirmar Exclusão",
            f"Deseja realmente excluir esta transação?\n\nDescrição: {desc}\nValor: {val}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.dm.excluir(real_index)
            self.atualizar()
