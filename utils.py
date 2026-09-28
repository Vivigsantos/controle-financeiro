"""
utils.py — Funções auxiliares: formatação, validação e paleta inspirada na UI Midnight Ocean Navy.
"""

import locale
from datetime import datetime
from typing import Optional

# Tenta configurar locale para pt_BR (formatação de moeda)
try:
    locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, "")
    except locale.Error:
        pass

# ─── Fonte Geométrica Minimalista ─────────────────────────────────────────────
FONTE_GEO = "Avenir Next"

# ─── Paleta de Cores Foscas Elegantes (Midnight Slate & Soft Matte) ──────────
CORES_PALETA = {
    "bg_dark": "#0f172a",          # Fundo Slate Navy Escuro Fosco
    "card_dark": "#1e293b",        # Card Azul Escuro Nobre (Slate 800)
    "card_accent": "#334155",      # Card Secundário / Destaque Soft
    "borda_suave": "#334155",      # Borda Discreta
    "texto_principal": "#f8fafc",  # Texto Branco Suave
    "texto_mutado": "#94a3b8",     # Texto Slate Mutado
    "ciano_brilhante": "#38bdf8",  # Azul Ciano Fosco / Sky Blue (Destaque)
    "azul_oceano": "#60a5fa",      # Azul Oceano Suave
    "verde_esmeralda": "#34d399",  # Verde Menta Esmeralda Fosco (Entradas)
    "rosa_coral": "#fb7185",       # Rosa Coral Suave Fosco (Saídas)
    "amarelo_ouro": "#fbbf24",     # Amarelo Âmbar Fosco
}

# Cores foscas e elegantes para gráficos
CORES_GRAFICOS = [
    "#38bdf8",  # Ciano Oceano Soft
    "#34d399",  # Verde Menta Soft
    "#fb7185",  # Rosa Coral Soft
    "#60a5fa",  # Azul Oceano
    "#fbbf24",  # Âmbar Ouro
    "#a78bfa",  # Lavanda Soft
    "#f472b6",  # Rose Soft
    "#818cf8",  # Índigo Soft
]


# ─── Formatação ──────────────────────────────────────────────────────────────
def formatar_moeda(valor: float) -> str:
    """Formata um valor numérico como moeda brasileira (R$)."""
    if valor < 0:
        return f"-R$ {abs(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_data(data: datetime) -> str:
    """Formata uma data no padrão brasileiro DD/MM/AAAA."""
    if isinstance(data, str):
        return data
    return data.strftime("%d/%m/%Y")


def parse_data(texto: str) -> datetime:
    """Converte texto DD/MM/AAAA para datetime."""
    return datetime.strptime(texto, "%d/%m/%Y")


# ─── Validação ───────────────────────────────────────────────────────────────
def validar_valor(texto: str) -> Optional[float]:
    """
    Valida e converte texto para float.
    Aceita formatos: 1234.56, 1234,56, 1.234,56
    Retorna None se inválido.
    """
    texto = texto.strip()
    if not texto:
        return None

    # Remove R$ e espaços
    texto = texto.replace("R$", "").replace(" ", "")

    # Trata formato brasileiro: 1.234,56 → 1234.56
    if "," in texto and "." in texto:
        texto = texto.replace(".", "").replace(",", ".")
    elif "," in texto:
        texto = texto.replace(",", ".")

    try:
        valor = float(texto)
        if valor <= 0:
            return None
        return round(valor, 2)
    except ValueError:
        return None


def mes_ano_atual() -> tuple[int, int]:
    """Retorna (mês, ano) atual."""
    hoje = datetime.now()
    return hoje.month, hoje.year


MESES_PT = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro",
}


def nome_mes(num: int) -> str:
    """Retorna o nome do mês em português."""
    return MESES_PT.get(num, "")
