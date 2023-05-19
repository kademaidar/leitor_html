''' descricao '''

import io
import pandas as pd
import streamlit as st
from bs4 import BeautifulSoup

def separa_tabela(arquivo_baixado):

    ''' descricao '''

    soup = BeautifulSoup(arquivo_baixado, 'html.parser')

    table = soup.find('table', id='jqGridTableDIVGrid')
    identificador = soup.find('div', id='jqgh_jqGridTableDIVGrid_danfe')

    if table:
        if identificador:  # Aqui ele entra se for NFe
            
            data = []
            for row in table.find_all('tr'):
                row_data = [cell.get_text(strip=True) for cell in row.find_all('td')]
                if row_data:
                    data.append(row_data)

            df_NFe = pd.DataFrame(data)
            df_NFe.drop(columns=[0, 1, 4, 5, 11, 17], inplace=True)  # Tem umas colunas que podem ser interessantes, perguntar se o usuario tem interesse
            df_NFe.drop(index=0, inplace=True)
            df_NFe.columns = ['Chave de Acesso', 'I.E. Dest.', 'I.E. Emit.', 'Razão Social Emit.',
                                    'CNPJ/CPF Emit.', 'Nº NF', 'Dt. Emissão Fuso MS', 'UF Emit.', 'Total NF',
                                    'Base Cálc. ICMS', 'Valor ICMS', 'Sit.*']  # Sao 12 colunas

            return df_NFe

        else:  # Aqui ele entra se for CTe

            data = []
            for row in table.find_all('tr'):
                row_data = [cell.get_text(strip=True) for cell in row.find_all('td')]
                if row_data:
                    data.append(row_data)

            df_CTe = pd.DataFrame(data)
            df_CTe.drop(columns=[0], inplace=True)  # Tem uma colunas que pode ser interessante, perguntar se o usuario tem interesse
            df_CTe.drop(index=0, inplace=True)
            df_CTe.columns = ['Chave de Acesso', 'Nome Empresa Emitente', 'CNPJ Emitente', 'Ano/Série/Número',
                              'Data de Emissão', 'Data de Autorização', 'Número do Protocolo',
                              'Valor Total da Prestação do Serviço', 'Valor da BC do ICMS',
                              'Valor do ICMS', 'Sit']  # Sao 11 colunas

            return df_CTe



    else:
        return print('Tabela não encontrada no arquivo HTML.')


def converte_formatos(df_entrada):

    ''' descricao '''

    if len(df_entrada.columns) == 12:
        formatos_dados_NFe = {
            'Chave de Acesso': 'string',
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
                            #   'Data de Emissão', 
                            #   'Data de Autorização', 
                              'Número do Protocolo': 'string',
                            #   'Valor Total da Prestação do Serviço', 
                            #   'Valor da BC do ICMS',
                            #   'Valor do ICMS', 
                              'Sit': 'string',
        }

        df_CTe = df_entrada.astype(formatos_dados_CTe)
        df_CTe['Data de Emissão'] = pd.to_datetime(df_CTe['Data de Emissão'], dayfirst=True)
        df_CTe['Data de Autorização'] = pd.to_datetime(df_CTe['Data de Autorização'], dayfirst=True)
        df_CTe['Valor Total da Prestação do Serviço'] = df_CTe['Valor Total da Prestação do Serviço'].str.replace('.', '').str.replace(',', '.').astype(float)
        df_CTe['Valor da BC do ICMS'] = df_CTe['Valor da BC do ICMS'].str.replace('.', '').str.replace(',', '.').astype(float)
        df_CTe['Valor do ICMS'] = df_CTe['Valor do ICMS'].str.replace('.', '').str.replace(',', '.').astype(float)

        return df_CTe
    


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
    st.write("Número total de linhas: " + str(len(df_saida)))

    st.download_button('Baixar Excel',
                       data=excel_saida,
                       file_name='tabela_extraida.xlsx')
    