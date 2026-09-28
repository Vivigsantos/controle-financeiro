"""
gui_components.py — Componentes visuais ultra-modernos usando CustomTkinter (cantos arredondados nativos).
"""

import customtkinter as ctk
from utils import FONTE_GEO, CORES_PALETA


class CardFrame(ctk.CTkFrame):
    """
    Card com cantos arredondados nativos (CustomTkinter) e fundo fosco.
    """

    def __init__(self, parent, fg_color=CORES_PALETA["card_dark"], border_color=CORES_PALETA["borda_suave"],
                 border_width=1, corner_radius=18, padding=20, **kwargs):
        super().__init__(
            parent,
            fg_color=fg_color,
            border_color=border_color,
            border_width=border_width,
            corner_radius=corner_radius,
            **kwargs
        )
        self.pack_propagate(True)


class KPICard(ctk.CTkFrame):
    """Card KPI arredondado com cores foscas e tipografia Avenir Next."""

    def __init__(self, parent, titulo: str, valor: str, cor_destaque: str = "#64b5f6", **kwargs):
        super().__init__(
            parent,
            fg_color=CORES_PALETA["card_dark"],
            border_color=cor_destaque,
            border_width=1.5,
            corner_radius=16,
            **kwargs
        )

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=18, pady=14)

        self.label_titulo = ctk.CTkLabel(
            container,
            text=titulo.lower(),
            font=ctk.CTkFont(family=FONTE_GEO, size=11, weight="bold"),
            text_color=cor_destaque,
            anchor="w"
        )
        self.label_titulo.pack(anchor="w", pady=(0, 2))

        self.label_valor = ctk.CTkLabel(
            container,
            text=valor,
            font=ctk.CTkFont(family=FONTE_GEO, size=20, weight="bold"),
            text_color=CORES_PALETA["texto_principal"],
            anchor="w"
        )
        self.label_valor.pack(anchor="w")

    def atualizar_valor(self, novo_valor: str, nova_cor: str = None):
        self.label_valor.configure(text=novo_valor)
        if nova_cor:
            self.configure(border_color=nova_cor)
            self.label_titulo.configure(text_color=nova_cor)
