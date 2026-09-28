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


def escutar_microfone(timeout: int = 5) -> Tuple[bool, str]:
    """
    Escuta o microfone e converte para texto em português.
    Retorna (sucesso: bool, texto_ou_erro: str).
    """
    if not HAS_SR:
        return False, "Biblioteca speech_recognition não instalada."

    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.8)
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=8)
            texto = recognizer.recognize_google(audio, language="pt-BR")
            return True, texto
    except sr.WaitTimeoutError:
        return False, "Tempo esgotado! Nenhum som detectado."
    except sr.UnknownValueError:
        return False, "Não consegui entender a fala. Tente novamente."
    except sr.RequestError as e:
        return False, f"Erro de conexão com o serviço de voz: {e}"
    except Exception as e:
        return False, f"Erro no microfone: {e}"


def interpretar_comando_voz(texto: str) -> Dict[str, Any]:
    """
    Interpreta uma frase dita pelo usuário e extrai:
    - tipo ('Entrada' ou 'Saída')
    - valor (float)
    - categoria (str)
    - forma_pagamento (str)
    - descricao (str)
    
    Exemplo: "Saída supermercado 150 reais no cartão de débito"
    """
    texto_lower = texto.lower()

    # 1. Identificar Tipo
    tipo = "Saída"  # Padrão
    if any(w in texto_lower for w in ["entrada", "receita", "ganhei", "salário", "salario", "recebi", "venda"]):
        tipo = "Entrada"

    # 2. Identificar Valor
    valor = None
    # Procura por padrões numéricos: "150", "150,50", "150.50", "cem reais", etc.
    padrao_valor = r'(\d+[\.,]?\d*)'
    matches = re.findall(padrao_valor, texto_lower)
    if matches:
        for m in matches:
            try:
                v = float(m.replace(",", "."))
                if v > 0:
                    valor = v
                    break
            except ValueError:
                continue

    # 3. Identificar Categoria
    categoria = None
    cats_testar = CATEGORIAS_ENTRADA if tipo == "Entrada" else CATEGORIAS_SAIDA
    
    # Mapeamento de sinônimos/palavras-chave comuns
    sinonimos = {
        "supermercado": "Alimentação", "mercado": "Alimentação", "almoço": "Alimentação",
        "janta": "Alimentação", "restaurante": "Alimentação", "comida": "Alimentação",
        "ifood": "Alimentação", "padaria": "Alimentação",
        "gasolina": "Transporte", "uber": "Transporte", "ônibus": "Transporte",
        "combustível": "Transporte", "estacionamento": "Transporte",
        "aluguel": "Moradia", "condomínio": "Moradia", "luz": "Contas (água/luz/internet)",
        "água": "Contas (água/luz/internet)", "internet": "Contas (água/luz/internet)",
        "remédio": "Saúde", "farmácia": "Saúde", "médico": "Saúde", "hospital": "Saúde",
        "cinema": "Lazer", "festa": "Lazer", "viagem": "Lazer", "jogo": "Lazer",
        "curso": "Educação", "escola": "Educação", "faculdade": "Educação", "livro": "Educação",
        "roupa": "Vestuário", "sapato": "Vestuário",
        "ração": "Pets", "veterinário": "Pets", "petshop": "Pets",
        "salário": "Salário", "freela": "Freelance", "freelance": "Freelance",
    }

    for palavra, cat_mapeada in sinonimos.items():
        if palavra in texto_lower:
            categoria = cat_mapeada
            break

    if not categoria:
        for c in cats_testar:
            if c.lower() in texto_lower:
                categoria = c
                break
        if not categoria:
            categoria = "Outros"

    # 4. Identificar Forma de Pagamento
    pagamento = "Pix"  # Padrão
    if "crédito" in texto_lower or "credito" in texto_lower:
        pagamento = "Cartão de Crédito"
    elif "débito" in texto_lower or "debito" in texto_lower:
        pagamento = "Cartão de Débito"
    elif "dinheiro" in texto_lower or "espécie" in texto_lower:
        pagamento = "Dinheiro"
    elif "boleto" in texto_lower:
        pagamento = "Boleto"
    elif "transferência" in texto_lower or "transferencia" in texto_lower or "ted" in texto_lower or "doc" in texto_lower:
        pagamento = "Transferência"
    elif "pix" in texto_lower:
        pagamento = "Pix"

    # 5. Descrição: texto original limpo ou frase dita
    descricao = texto.strip()

    return {
        "tipo": tipo,
        "valor": valor,
        "categoria": categoria,
        "forma_pagamento": pagamento,
        "descricao": descricao,
        "texto_original": texto
    }
