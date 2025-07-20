# Analise Histócia de Ativos
## Simulação de Aportes e Crescimento de Ativos
Este script em Python permite simular o crescimento de investimentos em diferentes ativos (ações, moedas ou BTC), considerando aportes mensais, taxas de operação e, opcionalmente, o reinvestimento de dividendos ("bola de neve"). Ele baixa dados históricos, calcula a quantidade acumulada de ativos e apresenta os resultados em formato de tabela, gráfico ou arquivo Excel.

# 📌 Funcionalidades
- Consulta automática de preços históricos via Yahoo Finance
- Suporte a ativos como ações brasileiras (ex: PETR4.SA), moedas ou BTC
- Consideração de taxas por operação
- Cálculo automático de dividendos simulados com base no Dividend Yield (DY) fornecido
- Simulação de "bola de neve" (reinvestimento de dividendos)
- Exportação para Excel ou visualização em gráfico
- Cálculo da mediana dos fechamentos mensais e DY estimado

# 📥 Requisitos
## Instale as bibliotecas com *bash*:
 * *pip install yfinance*
 * *pip install pandas*
 * *pip install matplotlib*
 * *pip install openpyxl*

# ▶️ Como usar
## Execute o script com:
  *python simulador_aportes.py*

### Durante a execução, o usuário deverá informar:
1. Tipo de ativo (BTC ou outro)
2. Ticker do ativo (caso não seja BTC)
3. Valor do aporte mensal
4. Taxa percentual por operação
5. Se o ativo paga dividendos
6. Se sim, qual o DY anual estimado
7. Forma de saída dos dados: print, gráfico ou salvar Excel

## 📂 Estrutura de Saída

| Data       | Fechamento | Qtd_Comprada_Bruta | Qtd_Acumulada_Bruta | Qtd_Acumulada_Liquida |
|------------|------------|--------------------|----------------------|------------------------|
| 2023-01-05 | 23.45      | 8                  | 8                    | 8                      |
| ...        | ...        | ...                | ...                  | ...                    |

