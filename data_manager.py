"""
data_manager.py — Gerenciamento de dados com cache em memória + planilha Excel.
Mantém um DataFrame em memória para operações rápidas e salva no Excel em background.
"""

import shutil
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side

from utils import formatar_data, parse_data

# Caminho padrão da planilha
ARQUIVO_PADRAO = Path(__file__).parent / "financas.xlsx"
PASTA_BACKUP = Path(__file__).parent / "backups"

# Colunas da planilha
COLUNAS = ["Data", "Tipo", "Categoria", "Descrição", "Valor", "Forma de Pagamento"]


class DataManager:
    """Gerencia transações em memória (rápido) com persistência em Excel (background)."""

    def __init__(self, caminho: Optional[Union[str, Path]] = None):
        self.caminho = Path(caminho) if caminho else ARQUIVO_PADRAO
        self._lock = threading.Lock()
        self._df = pd.DataFrame(columns=COLUNAS)
        self._carregar()

    # ─── Inicialização ───────────────────────────────────────────────────
    def _carregar(self):
        """Carrega dados do Excel para memória (apenas 1 vez, na inicialização)."""
        if not self.caminho.exists():
            self._criar_planilha_vazia()
            return

        try:
            df = pd.read_excel(self.caminho, sheet_name="Transações", engine="openpyxl")
            df["Data"] = df["Data"].astype(str)
            df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce").fillna(0.0)
            self._df = df
        except Exception:
            self._df = pd.DataFrame(columns=COLUNAS)

    def _criar_planilha_vazia(self):
        """Cria a planilha com cabeçalho formatado."""
        wb = Workbook()
        ws = wb.active
        ws.title = "Transações"

        header_font = Font(name="Calibri", bold=True, size=12, color="FFFFFF")
        header_fill = PatternFill(start_color="2d2d44", end_color="2d2d44", fill_type="solid")
        header_align = Alignment(horizontal="center", vertical="center")
        border = Border(bottom=Side(style="thin", color="45475a"))

        for col_idx, nome in enumerate(COLUNAS, 1):
            cell = ws.cell(row=1, column=col_idx, value=nome)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_align
            cell.border = border

        larguras = {"A": 14, "B": 12, "C": 22, "D": 30, "E": 16, "F": 22}
        for col_letra, largura in larguras.items():
            ws.column_dimensions[col_letra].width = largura

        ws.freeze_panes = "A2"
        wb.save(self.caminho)

    # ─── Salvar em background ────────────────────────────────────────────
    def _salvar_async(self):
        """Salva o DataFrame no Excel em uma thread separada (não trava a UI)."""
        df_copia = self._df.copy()
        t = threading.Thread(target=self._salvar_excel, args=(df_copia,), daemon=True)
        t.start()

    def _salvar_excel(self, df: pd.DataFrame):
        """Escreve o DataFrame no arquivo Excel com formatação."""
        with self._lock:
            try:
                wb = Workbook()
                ws = wb.active
                ws.title = "Transações"

                # Cabeçalho
                header_font = Font(name="Calibri", bold=True, size=12, color="FFFFFF")
                header_fill = PatternFill(start_color="2d2d44", end_color="2d2d44", fill_type="solid")
                header_align = Alignment(horizontal="center", vertical="center")

                for col_idx, nome in enumerate(COLUNAS, 1):
                    cell = ws.cell(row=1, column=col_idx, value=nome)
                    cell.font = header_font
                    cell.fill = header_fill
                    cell.alignment = header_align

                larguras = {"A": 14, "B": 12, "C": 22, "D": 30, "E": 16, "F": 22}
                for col_letra, largura in larguras.items():
                    ws.column_dimensions[col_letra].width = largura
                ws.freeze_panes = "A2"

                # Dados
                for row_idx, (_, row) in enumerate(df.iterrows(), 2):
                    ws.cell(row=row_idx, column=1, value=str(row["Data"]))
                    ws.cell(row=row_idx, column=2, value=str(row["Tipo"]))
                    ws.cell(row=row_idx, column=3, value=str(row["Categoria"]))
                    ws.cell(row=row_idx, column=4, value=str(row["Descrição"]))

                    celula_valor = ws.cell(row=row_idx, column=5, value=float(row["Valor"]))
                    celula_valor.number_format = '#,##0.00'
                    if str(row["Tipo"]) == "Entrada":
                        celula_valor.font = Font(color="2e7d32")
                    else:
                        celula_valor.font = Font(color="c62828")

                    ws.cell(row=row_idx, column=6, value=str(row["Forma de Pagamento"]))

                    for col in [1, 2, 3, 5, 6]:
                        ws.cell(row=row_idx, column=col).alignment = Alignment(horizontal="center")

                wb.save(self.caminho)
            except Exception as e:
                print(f"Erro ao salvar planilha: {e}")

    # ─── CRUD (tudo em memória = instantâneo) ────────────────────────────
    def adicionar(self, data: str, tipo: str, categoria: str,
                  descricao: str, valor: float, forma_pagamento: str) -> int:
        """Adiciona transação na memória e salva Excel em background."""
        nova = pd.DataFrame([{
            "Data": data,
            "Tipo": tipo,
            "Categoria": categoria,
            "Descrição": descricao,
            "Valor": valor,
            "Forma de Pagamento": forma_pagamento,
        }])
        self._df = pd.concat([self._df, nova], ignore_index=True)
        self._salvar_async()
        return len(self._df)

    def obter_transacoes(self, mes: Optional[int] = None, ano: Optional[int] = None,
                         tipo: Optional[str] = None, categoria: Optional[str] = None) -> pd.DataFrame:
        """Filtra transações diretamente da memória (muito rápido)."""
        df = self._df.copy()

        if df.empty:
            return df

        # Filtra por mês/ano
        if mes is not None and ano is not None:
            def _filtrar_data(d):
                try:
                    dt = parse_data(str(d))
                    return dt.month == mes and dt.year == ano
                except (ValueError, TypeError):
                    return False
            df = df[df["Data"].apply(_filtrar_data)]

        # Filtra por tipo
        if tipo and tipo != "Todos":
            df = df[df["Tipo"] == tipo]

        # Filtra por categoria
        if categoria and categoria != "Todas":
            df = df[df["Categoria"] == categoria]

        return df.reset_index(drop=True)

    def editar(self, indice: int, data: str, tipo: str, categoria: str,
               descricao: str, valor: float, forma_pagamento: str):
        """Edita transação na memória pelo índice do DataFrame."""
        if 0 <= indice < len(self._df):
            self._df.loc[indice, "Data"] = data
            self._df.loc[indice, "Tipo"] = tipo
            self._df.loc[indice, "Categoria"] = categoria
            self._df.loc[indice, "Descrição"] = descricao
            self._df.loc[indice, "Valor"] = valor
            self._df.loc[indice, "Forma de Pagamento"] = forma_pagamento
            self._salvar_async()

    def excluir(self, indice: int):
        """Exclui transação da memória pelo índice."""
        if 0 <= indice < len(self._df):
            self._df = self._df.drop(indice).reset_index(drop=True)
            self._salvar_async()

    # ─── Resumos (tudo em memória) ───────────────────────────────────────
    def resumo_mensal(self, mes: int, ano: int) -> dict:
        """Resumo financeiro do mês — calculado em memória."""
        df = self.obter_transacoes(mes=mes, ano=ano)

        if df.empty:
            return {
                "total_entradas": 0.0,
                "total_saidas": 0.0,
                "saldo": 0.0,
                "gastos_por_categoria": {},
                "entradas_por_categoria": {},
            }

        entradas = df[df["Tipo"] == "Entrada"]["Valor"].sum()
        saidas = df[df["Tipo"] == "Saída"]["Valor"].sum()

        gastos_cat = (
            df[df["Tipo"] == "Saída"]
            .groupby("Categoria")["Valor"]
            .sum()
            .to_dict()
        )

        entradas_cat = (
            df[df["Tipo"] == "Entrada"]
            .groupby("Categoria")["Valor"]
            .sum()
            .to_dict()
        )

        return {
            "total_entradas": float(entradas),
            "total_saidas": float(saidas),
            "saldo": float(entradas - saidas),
            "gastos_por_categoria": gastos_cat,
            "entradas_por_categoria": entradas_cat,
        }

    def resumo_anual(self, ano: int) -> list:
        """Lista de resumos mensais para o ano inteiro."""
        resumos = []
        for mes in range(1, 13):
            resumo = self.resumo_mensal(mes, ano)
            resumo["mes"] = mes
            resumos.append(resumo)
        return resumos

    def saldo_acumulado(self, ano: int) -> list:
        """Saldo acumulado mês a mês."""
        resumos = self.resumo_anual(ano)
        acumulado = 0.0
        resultado = []
        for r in resumos:
            acumulado += r["saldo"]
            resultado.append({
                "mes": r["mes"],
                "saldo_mes": r["saldo"],
                "saldo_acumulado": acumulado,
            })
        return resultado

    # ─── Importação / Exportação ─────────────────────────────────────────
    def importar_csv(self, caminho_csv: str) -> int:
        """Importa transações de um arquivo CSV."""
        df = pd.read_csv(caminho_csv)

        # Mapeia colunas
        colunas_map = {}
        for col in df.columns:
            col_lower = col.strip().lower()
            for esperada in COLUNAS:
                if esperada.lower() in col_lower or col_lower in esperada.lower():
                    colunas_map[col] = esperada
                    break

        df = df.rename(columns=colunas_map)

        count = 0
        for _, row in df.iterrows():
            try:
                nova = {
                    "Data": str(row.get("Data", formatar_data(datetime.now()))),
                    "Tipo": str(row.get("Tipo", "Saída")),
                    "Categoria": str(row.get("Categoria", "Outros")),
                    "Descrição": str(row.get("Descrição", "")),
                    "Valor": float(row.get("Valor", 0)),
                    "Forma de Pagamento": str(row.get("Forma de Pagamento", "Pix")),
                }
                self._df = pd.concat([self._df, pd.DataFrame([nova])], ignore_index=True)
                count += 1
            except (ValueError, TypeError):
                continue

        if count > 0:
            self._salvar_async()
        return count

    def backup(self) -> str:
        """Cria cópia de segurança da planilha."""
        if not self.caminho.exists():
            return ""

        PASTA_BACKUP.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_backup = "financas_backup_{}.xlsx".format(timestamp)
        destino = PASTA_BACKUP / nome_backup
        shutil.copy2(self.caminho, destino)

        # Mantém apenas os últimos 10 backups
        backups = sorted(PASTA_BACKUP.glob("financas_backup_*.xlsx"))
        if len(backups) > 10:
            for antigo in backups[:-10]:
                antigo.unlink()

        return str(destino)

    def total_registros(self) -> int:
        """Total de transações (direto da memória)."""
        return len(self._df)
