"""
voice_input.py — Módulo de reconhecimento de voz e interpretação de texto.
"""

import re
import threading
from typing import Optional, Dict, Any, Tuple

try:
    import speech_recognition as sr
    HAS_SR = True
except ImportError:
    HAS_SR = False

from categories import CATEGORIAS_ENTRADA, CATEGORIAS_SAIDA, FORMAS_PAGAMENTO


def escutar_microfone(timeout: int = 6) -> Tuple[bool, str]:
    """
    Escuta o microfone e converte para texto em português com ajuste de ruído rápido.
    Retorna (sucesso: bool, texto_ou_erro: str).
    """
    if not HAS_SR:
        return False, "Biblioteca speech_recognition não instalada."

    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True
    
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=7)
            texto = recognizer.recognize_google(audio, language="pt-BR")
            return True, texto.strip()
    except sr.WaitTimeoutError:
        return False, "Tempo esgotado! Nenhum som detectado."
    except sr.UnknownValueError:
        return False, "Não consegui entender a fala. Tente falar novamente mais perto do microfone."
    except sr.RequestError as e:
        return False, f"Erro de conexão com o serviço de voz: {e}"
    except Exception as e:
        return False, f"Erro no microfone: {e}"


def interpretar_comando_voz(texto: str) -> Dict[str, Any]:
    """
    Interpreta uma frase dita pelo usuário e extrai com alta precisão:
    - tipo ('Entrada' ou 'Saída')
    - valor (float)
    - categoria (str)
    - forma_pagamento (str)
    - descricao (str limpa, ex: 'Supermercado Extra')
    """
    texto_lower = texto.lower().strip()

    # 1. Identificar Tipo
    tipo = "Saída"  # Padrão
    if any(w in texto_lower for w in ["entrada", "receita", "ganhei", "salário", "salario", "recebi", "venda", "depósito", "deposito"]):
        tipo = "Entrada"

    # 2. Identificar Forma de Pagamento
    pagamento = "Pix"  # Padrão
    if any(w in texto_lower for w in ["crédito", "credito"]):
        pagamento = "Cartão de Crédito"
    elif any(w in texto_lower for w in ["débito", "debito"]):
        pagamento = "Cartão de Débito"
    elif any(w in texto_lower for w in ["dinheiro", "espécie", "especie", "nota", "moeda"]):
        pagamento = "Dinheiro"
    elif "boleto" in texto_lower:
        pagamento = "Boleto"
    elif any(w in texto_lower for w in ["transferência", "transferencia", "ted", "doc"]):
        pagamento = "Transferência"
    elif "pix" in texto_lower:
        pagamento = "Pix"

    # 3. Identificar Categoria e Palavras de Sinônimos
    categoria = None
    palavra_cat_encontrada = ""
    
    sinonimos = {
        "supermercado": "Alimentação", "mercado": "Alimentação", "almoço": "Alimentação",
        "janta": "Alimentação", "restaurante": "Alimentação", "comida": "Alimentação",
        "ifood": "Alimentação", "padaria": "Alimentação", "lanche": "Alimentação",
        "gasolina": "Transporte", "uber": "Transporte", "ônibus": "Transporte", "onibus": "Transporte",
        "combustível": "Transporte", "combustivel": "Transporte", "estacionamento": "Transporte", "pedágio": "Transporte",
        "aluguel": "Moradia", "condomínio": "Moradia", "condominio": "Moradia", "luz": "Contas (água/luz/internet)",
        "água": "Contas (água/luz/internet)", "agua": "Contas (água/luz/internet)", "internet": "Contas (água/luz/internet)",
        "remédio": "Saúde", "remedio": "Saúde", "farmácia": "Saúde", "farmacia": "Saúde", "médico": "Saúde", "hospital": "Saúde",
        "cinema": "Lazer", "festa": "Lazer", "viagem": "Lazer", "jogo": "Lazer", "show": "Lazer",
        "curso": "Educação", "escola": "Educação", "faculdade": "Educação", "livro": "Educação",
        "roupa": "Vestuário", "sapato": "Vestuário",
        "ração": "Pets", "racao": "Pets", "veterinário": "Pets", "veterinario": "Pets", "petshop": "Pets",
        "salário": "Salário", "salario": "Salário", "freela": "Freelance", "freelance": "Freelance",
    }

    for palavra, cat_mapeada in sinonimos.items():
        if palavra in texto_lower:
            categoria = cat_mapeada
            palavra_cat_encontrada = palavra
            break

    cats_testar = CATEGORIAS_ENTRADA if tipo == "Entrada" else CATEGORIAS_SAIDA
    if not categoria:
        for c in cats_testar:
            if c.lower() in texto_lower:
                categoria = c
                palavra_cat_encontrada = c.lower()
                break
        if not categoria:
            categoria = "Outros"

    # 4. Extração Inteligente de Valor
    valor = None
    # Procura primeiro por padrão numérico antes/depois da palavra 'reais', 'real' ou 'r$'
    match_moeda = re.search(r'(\d+[\.,]?\d*)\s*(?:reais|real|r\$)', texto_lower)
    if match_moeda:
        try:
            valor = float(match_moeda.group(1).replace(",", "."))
        except ValueError:
            pass

    if valor is None:
        # Padrão numérico genérico, ignorando números de 4 dígitos referentes a ano (ex: 2026)
        matches = re.findall(r'\b(\d+[\.,]?\d*)\b', texto_lower)
        for m in matches:
            val_clean = m.replace(",", ".")
            try:
                v = float(val_clean)
                # Ignora anos como 2024, 2025, 2026 a menos que seja um valor com decimais
                if "." in val_clean or (v > 0 and v not in [2024, 2025, 2026, 2027]):
                    valor = v
                    break
            except ValueError:
                continue

    # 5. Extração da Descrição Limpa
    # Remove palavras de gatilho estruturais da frase para obter a descrição real do gasto
    termos_remover = [
        "saída", "saida", "entrada", "receita", "ganhei", "gastei", "paguei", "pago",
        "reais", "real", "r$", "no cartão de crédito", "no cartão de débito", "no crédito", "no débito",
        "cartão de crédito", "cartão de débito", "no pix", "pix", "dinheiro", "em espécie", "boleto", "transferência",
        "alimentação", "transporte", "moradia", "saúde", "lazer", "educação", "vestuário", "pets", "outros",
    ]

    frase_limpa = texto_lower
    for t in termos_remover:
        frase_limpa = re.sub(rf'\b{re.escape(t)}\b', '', frase_limpa)

    if valor is not None:
        val_str = str(int(valor)) if valor.is_integer() else str(valor)
        frase_limpa = re.sub(rf'\b{re.escape(val_str)}\b', '', frase_limpa)

    frase_limpa = re.sub(r'\s+', ' ', frase_limpa).strip()

    if len(frase_limpa) >= 3:
        descricao = frase_limpa.title()
    elif palavra_cat_encontrada:
        descricao = palavra_cat_encontrada.title()
    else:
        descricao = texto.capitalize()

    return {
        "tipo": tipo,
        "valor": valor,
        "categoria": categoria,
        "forma_pagamento": pagamento,
        "descricao": descricao,
        "texto_original": texto
    }
