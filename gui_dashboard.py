"""
gui_dashboard.py — Dashboard financeiro em PyQt6 no estilo Midnight Ocean Navy.
"""

from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QFrame
)

import matplotlib
matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from data_manager import DataManager
from utils import FONTE_GEO, CORES_PALETA, CORES_GRAFICOS, formatar_moeda, nome_mes


class Dashboard(QWidget):
    """Aba de Dashboard Analytics em PyQt6 no estilo Midnight Ocean Navy."""

    def __init__(self, data_manager: DataManager):
        super().__init__()
        self.dm = data_manager
        self.dark_mode = True
        self._criar_widgets()
        self.atualizar()

    def _criar_widgets(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # ── Header ──
        header_layout = QHBoxLayout()

        lbl_head = QLabel("Visão Geral & Analytics")
        lbl_head.setFont(QFont(FONTE_GEO, 14, QFont.Weight.Bold))
        lbl_head.setStyleSheet(f"color: {CORES_PALETA['ciano_brilhante']};")
        header_layout.addWidget(lbl_head)

        header_layout.addStretch()

        lbl_mes = QLabel("Mês:")
        lbl_mes.setFont(QFont(FONTE_GEO, 9))
        lbl_mes.setStyleSheet(f"color: {CORES_PALETA['texto_mutado']};")
        header_layout.addWidget(lbl_mes)

        self.cmb_mes = QComboBox()
        self.cmb_mes.addItems([str(i) for i in range(1, 13)])
        self.cmb_mes.setCurrentText(str(datetime.now().month))
        self.cmb_mes.setFixedHeight(30)
        header_layout.addWidget(self.cmb_mes)

        lbl_ano = QLabel("Ano:")
        lbl_ano.setFont(QFont(FONTE_GEO, 9))
        lbl_ano.setStyleSheet(f"color: {CORES_PALETA['texto_mutado']};")
        header_layout.addWidget(lbl_ano)

        ano_atual = datetime.now().year
        self.cmb_ano = QComboBox()
        self.cmb_ano.addItems([str(a) for a in range(ano_atual - 5, ano_atual + 2)])
        self.cmb_ano.setCurrentText(str(ano_atual))
        self.cmb_ano.setFixedHeight(30)
        header_layout.addWidget(self.cmb_ano)

        btn_ref = QPushButton("🔄 Atualizar")
        btn_ref.setFixedHeight(30)
        btn_ref.setFont(QFont(FONTE_GEO, 9))
        btn_ref.clicked.connect(self.atualizar)
        header_layout.addWidget(btn_ref)

        main_layout.addLayout(header_layout)

        # ── Cards KPI ──
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(12)

        self.card_entradas = self._criar_card_kpi("Entradas do Mês", "R$ 0,00", CORES_PALETA['verde_esmeralda'])
        cards_layout.addWidget(self.card_entradas["frame"])

        self.card_saidas = self._criar_card_kpi("Saídas do Mês", "R$ 0,00", CORES_PALETA['rosa_coral'])
        cards_layout.addWidget(self.card_saidas["frame"])

        self.card_saldo = self._criar_card_kpi("Saldo Líquido", "R$ 0,00", CORES_PALETA['ciano_brilhante'])
        cards_layout.addWidget(self.card_saldo["frame"])

        main_layout.addLayout(cards_layout)

        # ── Frame do Gráfico ──
        self.card_graficos = QFrame()
        self.card_graficos.setObjectName("cardGraficos")
        self.card_graficos.setStyleSheet(f"""
            QFrame#cardGraficos {{
                background-color: {CORES_PALETA['card_dark']};
                border: 1px solid {CORES_PALETA['borda_suave']};
                border-radius: 18px;
            }}
        """)
        self.chart_layout = QVBoxLayout(self.card_graficos)
        self.chart_layout.setContentsMargins(10, 10, 10, 10)

        main_layout.addWidget(self.card_graficos, stretch=1)

        self.lbl_alerta = QLabel("")
        self.lbl_alerta.setFont(QFont(FONTE_GEO, 11, QFont.Weight.Bold))
        self.lbl_alerta.setStyleSheet(f"color: {CORES_PALETA['rosa_coral']};")
        self.lbl_alerta.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.lbl_alerta)

    def _criar_card_kpi(self, titulo: str, valor: str, cor_destaque: str) -> dict:
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {CORES_PALETA['card_dark']};
                border: 1.5px solid {cor_destaque};
                border-radius: 16px;
            }}
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(18, 14, 18, 14)

        lbl_t = QLabel(titulo.lower())
        lbl_t.setFont(QFont(FONTE_GEO, 10, QFont.Weight.Bold))
        lbl_t.setStyleSheet(f"color: {cor_destaque}; border: none;")
        layout.addWidget(lbl_t)

        lbl_v = QLabel(valor)
        lbl_v.setFont(QFont(FONTE_GEO, 20, QFont.Weight.Bold))
        lbl_v.setStyleSheet(f"color: {CORES_PALETA['texto_principal']}; border: none;")
        layout.addWidget(lbl_v)

        return {"frame": frame, "val_label": lbl_v, "title_label": lbl_t}

    def atualizar_tema(self, dark_mode: bool):
        self.dark_mode = dark_mode
        self.atualizar()

    def atualizar(self):
        mes = int(self.cmb_mes.currentText())
        ano = int(self.cmb_ano.currentText())

        resumo = self.dm.resumo_mensal(mes, ano)

        self.card_entradas["val_label"].setText(formatar_moeda(resumo["total_entradas"]))
        self.card_saidas["val_label"].setText(formatar_moeda(resumo["total_saidas"]))

        saldo = resumo["saldo"]
        saldo_cor = CORES_PALETA['verde_esmeralda'] if saldo >= 0 else CORES_PALETA['rosa_coral']
        self.card_saldo["val_label"].setText(formatar_moeda(saldo))
        self.card_saldo["frame"].setStyleSheet(f"""
            QFrame {{
                background-color: {CORES_PALETA['card_dark']};
                border: 1.5px solid {saldo_cor};
                border-radius: 16px;
            }}
        """)
        self.card_saldo["title_label"].setStyleSheet(f"color: {saldo_cor}; border: none;")

        if resumo["total_saidas"] > resumo["total_entradas"] and resumo["total_entradas"] > 0:
            self.lbl_alerta.setText("⚠️ atenção: as despesas superaram as receitas neste mês!")
        else:
            self.lbl_alerta.setText("")

        self._desenhar_graficos(resumo, ano)

    def _desenhar_graficos(self, resumo: dict, ano: int):
        while self.chart_layout.count():
            child = self.chart_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if self.dark_mode:
            bg_color = CORES_PALETA['card_dark']
            text_color = CORES_PALETA['texto_principal']
            muted_color = CORES_PALETA['texto_mutado']
            grid_color = CORES_PALETA['borda_suave']
        else:
            bg_color = "#ffffff"
            text_color = "#2c3e50"
            muted_color = "#7f8c8d"
            grid_color = "#e2e8f0"

        fig = Figure(figsize=(13, 4.2), dpi=150)
        fig.patch.set_facecolor(bg_color)

        # ── Gráfico 1: Donut Cyber Midnight ──
        ax1 = fig.add_subplot(131)
        ax1.set_facecolor(bg_color)
        gastos = resumo["gastos_por_categoria"]

        if gastos:
            categorias = list(gastos.keys())
            valores = list(gastos.values())
            total_val = sum(valores)
            cores = CORES_GRAFICOS[: len(categorias)]

            wedges, texts, autotexts = ax1.pie(
                valores, labels=None, autopct="%1.0f%%",
                colors=cores, startangle=90, pctdistance=0.70,
                textprops={"fontsize": 8, "color": "#ffffff", "fontfamily": "sans-serif", "weight": "bold"},
                wedgeprops=dict(width=0.42, edgecolor=bg_color, linewidth=2.5)
            )

            # Oculta porcentagem nas fatias < 4% para evitar texto embolado/sobreposto
            labels_legenda = []
            for i, autotext in enumerate(autotexts):
                pct = (valores[i] / total_val) * 100 if total_val > 0 else 0
                labels_legenda.append(f"{categorias[i]} ({pct:.0f}%)")
                if pct < 4.0:
                    autotext.set_text("")
                else:
                    autotext.set_text(f"{pct:.0f}%")

            total_saidas_fmt = formatar_moeda(resumo["total_saidas"])
            ax1.text(0, 0, f"TOTAL\n{total_saidas_fmt}", ha="center", va="center",
                     fontsize=9, fontweight="bold", color=text_color, fontfamily="sans-serif")

            ax1.legend(
                wedges, labels_legenda, loc="lower center",
                bbox_to_anchor=(0.5, -0.28), fontsize=7, ncol=2, frameon=False,
                labelcolor=muted_color
            )
        else:
            ax1.text(0, 0, "Sem lançamentos\nno período", ha="center", va="center",
                     fontsize=10, color=muted_color, fontfamily="sans-serif")

        ax1.set_title("Categorias de Gastos", fontsize=11, fontweight="bold", pad=12, color=text_color, fontfamily="sans-serif")

        # ── Gráfico 2: Barras Ciano vs Rosa ──
        ax2 = fig.add_subplot(132)
        ax2.set_facecolor(bg_color)
        resumos_ano = self.dm.resumo_anual(ano)

        meses = [nome_mes(r["mes"])[:3] for r in resumos_ano]
        entradas = [r["total_entradas"] for r in resumos_ano]
        saidas = [r["total_saidas"] for r in resumos_ano]

        x = range(len(meses))
        largura = 0.36

        ax2.bar([i - largura / 2 for i in x], entradas, largura,
                label="Entradas", color=CORES_PALETA['verde_esmeralda'], alpha=0.9, edgecolor="none")
        ax2.bar([i + largura / 2 for i in x], saidas, largura,
                label="Saídas", color=CORES_PALETA['rosa_coral'], alpha=0.9, edgecolor="none")

        ax2.set_xticks(list(x))
        ax2.set_xticklabels(meses, fontsize=7, rotation=45, color=muted_color, fontfamily="sans-serif")
        ax2.set_title("Entradas vs Saídas (Ano)", fontsize=11, fontweight="bold", pad=12, color=text_color, fontfamily="sans-serif")
        ax2.legend(fontsize=8, frameon=False, labelcolor=muted_color)
        ax2.tick_params(axis="y", labelsize=8, colors=muted_color)
        ax2.grid(axis="y", linestyle=":", alpha=0.3, color=grid_color)
        for spine in ax2.spines.values():
            spine.set_color(grid_color)

        # ── Gráfico 3: Curva Suave Gradient (Evolução do Saldo) ──
        ax3 = fig.add_subplot(133)
        ax3.set_facecolor(bg_color)
        saldos = self.dm.saldo_acumulado(ano)

        meses_labels = [nome_mes(s["mes"])[:3] for s in saldos]
        saldos_acum = [s["saldo_acumulado"] for s in saldos]

        ax3.plot(meses_labels, saldos_acum, marker="o", color=CORES_PALETA['ciano_brilhante'],
                 linewidth=2.5, markersize=5, markerfacecolor=CORES_PALETA['azul_oceano'],
                 markeredgecolor=CORES_PALETA['ciano_brilhante'])

        ax3.fill_between(
            meses_labels, saldos_acum, alpha=0.22, color=CORES_PALETA['ciano_brilhante']
        )
        ax3.axhline(y=0, color=CORES_PALETA['azul_oceano'], linestyle="--", linewidth=0.8, alpha=0.5)
        ax3.set_title("Evolução do Saldo Acumulado", fontsize=11, fontweight="bold", pad=12, color=text_color, fontfamily="sans-serif")
        ax3.tick_params(axis="x", labelsize=7, rotation=45, colors=muted_color)
        ax3.tick_params(axis="y", labelsize=8, colors=muted_color)
        ax3.grid(axis="y", linestyle=":", alpha=0.3, color=grid_color)
        for spine in ax3.spines.values():
            spine.set_color(grid_color)

        fig.tight_layout(pad=2.0)

        canvas = FigureCanvasQTAgg(fig)
        self.chart_layout.addWidget(canvas)
