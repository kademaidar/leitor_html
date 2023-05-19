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
        df_temporario.drop(index=0, inplace=True)


        if len(df_temporario.columns) == 18:  # Aqui ele entra se for NFe

            df_temporario.drop(columns=[0, 1, 4, 5, 11, 17], inplace=True)  # Tem umas colunas que podem ser interessantes, perguntar se o usuario tem interesse
            df_temporario.columns = ['Chave de Acesso.', 'I.E. Dest.', 'I.E. Emit.', 'Razão Social Emit.',
                                    'CNPJ/CPF Emit.', 'Nº NF', 'Dt. Emissão Fuso MS', 'UF Emit.', 'Total NF',
                                    'Base Cálc. ICMS', 'Valor ICMS', 'Sit.*']  # Sao 12 colunas

            return df_temporario

        elif len(df_temporario.columns) == 12:  # Aqui ele entra se for CTe

            df_temporario.drop(columns=[0], inplace=True)  # Tem uma coluna que pode ser interessante, perguntar se o usuario tem interesse
            df_temporario.columns = ['Chave de Acesso', 'Nome Empresa Emitente', 'CNPJ Emitente', 'Ano/Série/Número',
                                'Data de Emissão', 'Data de Autorização', 'Número do Protocolo',
                                'Valor Total da Prestação do Serviço', 'Valor da BC do ICMS',
                                'Valor do ICMS', 'Sit']  # Sao 11 colunas

            return df_temporario



def converte_formatos(df_entrada):

    ''' descricao '''

    if len(df_entrada.columns) == 12:
        formatos_dados_NFe = {
            'Chave de Acesso.': 'string',
            'I.E. Dest.': 'string',
            'I.E. Emit.': 'string',
            'Razão Social Emit.': 'string',
            'CNPJ/CPF Emit.': 'string',
            'Nº NF': 'string',
            'UF Emit.': 'string',
            'Sit.*': 'string',
        }

        df_NFe = df_entrada.astype(formatos_dados_NFe)
        df_NFe['Dt. Emissão Fuso MS'] = pd.to_datetime(df_NFe['Dt. Emissão Fuso MS'], dayfirst=True).dt.date
        df_NFe['Total NF'] = df_NFe['Total NF'].str.replace('.', '').str.replace(',', '.').astype(float)
        df_NFe['Base Cálc. ICMS'] = df_NFe['Base Cálc. ICMS'].str.replace('.', '').str.replace(',', '.').astype(float)
        df_NFe['Valor ICMS'] = df_NFe['Valor ICMS'].str.replace('.', '').str.replace(',', '.').astype(float)

        return df_NFe
    
    else:
        formatos_dados_CTe = {'Chave de Acesso': 'string', 
                              'Nome Empresa Emitente': 'string', 
                              'CNPJ Emitente': 'string', 
                              'Ano/Série/Número': 'string',
                              'Número do Protocolo': 'string',
                              'Sit': 'string',
        }

        df_CTe = df_entrada.astype(formatos_dados_CTe)
        df_CTe['Data de Emissão'] = pd.to_datetime(df_CTe['Data de Emissão'], dayfirst=True).dt.date
        df_CTe['Data de Autorização'] = pd.to_datetime(df_CTe['Data de Autorização'], dayfirst=True).dt.date
        df_CTe['Valor Total da Prestação do Serviço'] = df_CTe['Valor Total da Prestação do Serviço'].str.replace('.', '').str.replace(',', '.').astype(float)
        df_CTe['Valor da BC do ICMS'] = df_CTe['Valor da BC do ICMS'].str.replace('.', '').str.replace(',', '.').astype(float)
        df_CTe['Valor do ICMS'] = df_CTe['Valor do ICMS'].str.replace('.', '').str.replace(',', '.').astype(float)

        return df_CTe
    


#### Codigo comeca a rodar aqui


uploaded_htmls = st.file_uploader('Selecione os arquivos HTML',
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


    if len(df_saida.columns) == 12:
        tipo_tabela = 'CTe'
    elif len(df_saida.columns) == 13:
        tipo_tabela = 'NFe'
    elif len(df_saida.columns) > 13:
        st.warning('Cuidado: Há mais de um tipo de arquivo!')
        tipo_tabela = 'CTe_e_NFe'
    

    excel_saida = io.BytesIO()
    df_saida.to_excel(excel_saida, index=False, sheet_name='Tabela')
    excel_saida.seek(0)

    
    st.write('Você colocou ' + str(len(uploaded_htmls)) + ' arquivos do tipo ' + tipo_tabela)
    st.write("Nome dos arquivos: " + str(nome_arquivos))
    st.write("Número total de linhas: " + str(len(df_saida)))


    nome_excel = 'tabela_' + tipo_tabela + '.xlsx'

    st.download_button('Baixar Excel',
                    data=excel_saida,
                    file_name=nome_excel)
    