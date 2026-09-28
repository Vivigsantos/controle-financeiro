# 💰 Sistema de Controle Financeiro — Entradas & Saídas

Sistema desktop em Python para acompanhamento de finanças pessoais com interface gráfica, planilha Excel e visualização de dados.

## 📋 Funcionalidades

- **📝 Registro de Transações** — Formulário rápido com data automática, categorias, valor e forma de pagamento
- **📋 Tabela de Transações** — Visualize, filtre, edite e exclua transações
- **📊 Dashboard** — Gráficos interativos: pizza (gastos/categoria), barras (entradas vs saídas), linha (saldo acumulado)
- **📥 Importação CSV** — Importe dados de planilhas externas
- **💾 Backup Automático** — Cópia de segurança ao iniciar o sistema
- **📄 Planilha Excel** — Seus dados ficam em `financas.xlsx`, editável no Excel/LibreOffice

## 🚀 Como Usar

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Executar o sistema

```bash
python main.py
```

### 3. Registrar transações

1. Na aba **📝 Novo Registro**, preencha os campos
2. A data de hoje é preenchida automaticamente
3. Escolha o tipo (Entrada/Saída) — as categorias atualizam automaticamente
4. Digite a descrição e o valor
5. Clique em **Registrar Transação**

### 4. Visualizar transações

- Na aba **📋 Transações**, filtre por mês, ano e tipo
- Selecione uma linha para **editar** ou **excluir**

### 5. Analisar no Dashboard

- Na aba **📊 Dashboard**, veja cards de resumo e gráficos
- Mude o mês/ano para análise de períodos diferentes
- Um alerta aparece quando saídas ultrapassam entradas

### 6. Importar dados existentes

- Menu **Arquivo → Importar CSV**
- O CSV deve ter colunas: `Data, Tipo, Categoria, Descrição, Valor, Forma de Pagamento`

## 📁 Estrutura

```
controle-financeiro/
├── main.py              # Janela principal
├── data_manager.py      # Gerenciador de dados Excel
├── gui_forms.py         # Formulários e tabela
├── gui_dashboard.py     # Dashboard com gráficos
├── categories.py        # Categorias padrão
├── utils.py             # Funções auxiliares
├── requirements.txt     # Dependências
├── financas.xlsx        # Planilha de dados (criada automaticamente)
└── backups/             # Backups automáticos
```

## 💡 Dicas

- A planilha `financas.xlsx` pode ser aberta no Excel ou LibreOffice a qualquer momento
- Backups ficam na pasta `backups/` (os 10 mais recentes são mantidos)
- Valores aceitos: `1234.56`, `1234,56`, `1.234,56`
