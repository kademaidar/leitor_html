''' descricao '''

import io
import pandas as pd
import streamlit as st
from bs4 import BeautifulSoup

def separa_tabela(arquivo_baixado):

    ''' descricao '''

    soup = BeautifulSoup(arquivo_baixado, 'html.parser')

    table = soup.find('table', id='jqGridTableDIVGrid')

    if table:
        data = []
        for row in table.find_all('tr'):
            row_data = [cell.get_text(strip=True) for cell in row.find_all('td')]
            if row_data:
                data.append(row_data)

        df_temporario = pd.DataFrame(data)
        df_temporario.drop(columns=[0, 1, 4, 5, 11, 16, 17], inplace=True)  # Tem umas colunas que podem ser interessantes, perguntar se o usuario tem interesse
        df_temporario.drop(index=0, inplace=True)
        df_temporario.columns = ['Chave de Acesso.', 'I.E. Dest.', 'I.E. Emit.', 'Razão Social Emit.',
                                'CNPJ/CPF Emit.', 'Nº NF', 'Dt. Emissão Fuso MS', 'UF Emit.', 'Total NF',
                                'Base Cálc. ICMS', 'Valor ICMS']

        return df_temporario

    else:
        return print('Tabela não encontrada no arquivo HTML.')


def converte_formatos(df_entrada):

    ''' descicao '''

    formatos_dados = {
        'Chave de Acesso.': 'string',
        'I.E. Dest.': 'string',
        'I.E. Emit.': 'string',
        'Razão Social Emit.': 'string',
        'CNPJ/CPF Emit.': 'string',
        'Nº NF': 'string',
        'UF Emit.': 'string',
    }

    df_temporario = df_entrada.astype(formatos_dados)
    df_temporario['Dt. Emissão Fuso MS'] = pd.to_datetime(df_temporario['Dt. Emissão Fuso MS'], dayfirst=True).dt.date
    df_temporario['Total NF'] = df_temporario['Total NF'].str.replace('.', '').str.replace(',', '.').astype(float)
    df_temporario['Base Cálc. ICMS'] = df_temporario['Base Cálc. ICMS'].str.replace('.', '').str.replace(',', '.').astype(float)
    df_temporario['Valor ICMS'] = df_temporario['Valor ICMS'].str.replace('.', '').str.replace(',', '.').astype(float)

    return df_temporario


#### Codigo comeca a rodar aqui

uploaded_htmls = st.file_uploader("Escolha arquivos HTML",
                                  type=['html'],
                                  accept_multiple_files=True)


if len(uploaded_htmls) == 0:
    st.write("Nenhum arquivo selecionado")
else:

    nome_arquivos = []
    lista_dfs = []

    for index, uploaded_html in enumerate(uploaded_htmls):

        conteudo_html = uploaded_html.read().decode('utf-8')
        df_html = separa_tabela(conteudo_html)
        df_formatado = converte_formatos(df_html)
        df_formatado['Pagina'] = index + 1

        lista_dfs.append(df_formatado)
        nome_arquivos.append(uploaded_html.name)


    df_saida = pd.concat(lista_dfs)

    excel_saida = io.BytesIO()
    df_saida.to_excel(excel_saida, index=False, sheet_name='Tabela')
    excel_saida.seek(0)

    st.write('Você colocou ' + str(len(uploaded_htmls)) + ' arquivos.')
    st.write("Nome dos arquivos: " + str(nome_arquivos))

    st.download_button('Baixar Excel',
                       data=excel_saida,
                       file_name='tabela_extraida.xlsx')
    