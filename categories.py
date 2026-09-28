"""
categories.py — Categorias padrão para o sistema de controle financeiro.
"""

from typing import List

# Categorias de ENTRADA (receitas)
CATEGORIAS_ENTRADA = [
    "Salário",
    "Freelance",
    "Investimentos",
    "Vendas",
    "Presente",
    "Reembolso",
    "Outros",
]

# Categorias de SAÍDA (despesas)
CATEGORIAS_SAIDA = [
    "Alimentação",
    "Transporte",
    "Moradia",
    "Saúde",
    "Educação",
    "Lazer",
    "Vestuário",
    "Contas (água/luz/internet)",
    "Assinaturas",
    "Pets",
    "Outros",
]

# Formas de pagamento
FORMAS_PAGAMENTO = [
    "Pix",
    "Cartão de Crédito",
    "Cartão de Débito",
    "Dinheiro",
    "Transferência",
    "Boleto",
]

# Tipos de transação
TIPOS = ["Entrada", "Saída"]


def get_categorias(tipo: str) -> List[str]:
    """Retorna as categorias com base no tipo de transação."""
    if tipo == "Entrada":
        return CATEGORIAS_ENTRADA
    return CATEGORIAS_SAIDA
