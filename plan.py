import streamlit as st
import pandas as pd
import sqlite3
from PIL import Image
from io import BytesIO

# Configuração da conexão com o banco de dados
conn = sqlite3.connect('planograma.db')
c = conn.cursor()

# Criar a tabela se não existir
c.execute('''
CREATE TABLE IF NOT EXISTS planogramas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    imagem BLOB,
    loja TEXT,
    rua TEXT,
    gondola TEXT
)
''')
conn.commit()

# Função para salvar imagem no banco de dados
def salvar_planograma(nome, imagem, loja, rua, gondola):
    img_data = imagem.read()  # Lê os dados diretamente do objeto UploadedFile
    c.execute('INSERT INTO planogramas (nome, imagem, loja, rua, gondola) VALUES (?, ?, ?, ?, ?)', (nome, img_data, loja, rua, gondola))
    conn.commit()

# Carregar imagem do banco de dados
def carregar_imagem(imagem_blob):
    return Image.open(BytesIO(imagem_blob))

# Interface do app
st.title('Sistema de Planograma do Supermercado')

# Menu para cadastro de novo planograma
st.sidebar.header('Cadastrar Planograma')
nome = st.sidebar.text_input('Nome do Planograma')
imagem = st.sidebar.file_uploader('Upload da Imagem', type=['jpg', 'jpeg', 'png'])
loja = st.sidebar.text_input('Loja')
rua = st.sidebar.text_input('Rua')
gondola = st.sidebar.text_input('Gôndola')

if st.sidebar.button('Salvar'):
    if nome and imagem and loja and rua and gondola:
        salvar_planograma(nome, imagem, loja, rua, gondola)
        st.sidebar.success('Planograma salvo com sucesso!')
    else:
        st.sidebar.error('Por favor, preencha todos os campos.')

# Visualização de planogramas
st.header('Planogramas Cadastrados')
c.execute('SELECT * FROM planogramas')
planogramas = c.fetchall()

for planograma in planogramas:
    st.subheader(planograma[1])
    st.image(carregar_imagem(planograma[2]), caption=f'Loja: {planograma[3]} | Rua: {planograma[4]} | Gôndola: {planograma[5]}')

# Fechar a conexão com o banco de dados
conn.close()
