import streamlit as st
import sqlite3
import pandas as pd
import qrcode
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

# Função para carregar imagem do banco de dados
def carregar_imagem(imagem_blob):
    return Image.open(BytesIO(imagem_blob))

# Função para obter os dados de um planograma pelo ID
def obter_planograma(planograma_id):
    c.execute('SELECT * FROM planogramas WHERE id = ?', (planograma_id,))
    return c.fetchone()

# Função para atualizar um planograma
def atualizar_planograma(planograma_id, nome, imagem, loja, rua, gondola):
    if imagem is not None:
        img_data = imagem.read()
        c.execute('UPDATE planogramas SET nome = ?, imagem = ?, loja = ?, rua = ?, gondola = ? WHERE id = ?', 
                  (nome, img_data, loja, rua, gondola, planograma_id))
    else:
        c.execute('UPDATE planogramas SET nome = ?, loja = ?, rua = ?, gondola = ? WHERE id = ?', 
                  (nome, loja, rua, gondola, planograma_id))
    conn.commit()

# Função para deletar um planograma
def deletar_planograma(planograma_id):
    c.execute('DELETE FROM planogramas WHERE id = ?', (planograma_id,))
    conn.commit()

# Função para gerar um QR Code para o link da imagem
def gerar_qr_code(imagem_url):
    qr = qrcode.make(imagem_url)
    buf = BytesIO()
    qr.save(buf, format="PNG")
    buf.seek(0)
    return buf

# Menu de navegação com botões
st.sidebar.title("Menu de Navegação")
if st.sidebar.button("Cadastro de Planograma"):
    st.session_state.pagina = "Cadastro de Planograma"
if st.sidebar.button("Visualização de Planogramas"):
    st.session_state.pagina = "Visualização de Planogramas"
if st.sidebar.button("Detalhes do Planograma") and 'planograma_id' in st.session_state:
    st.session_state.pagina = "Detalhes do Planograma"

# Verifica qual página está selecionada
pagina = st.session_state.get('pagina', "Cadastro de Planograma")

# Página de Cadastro
if pagina == "Cadastro de Planograma":
    st.title("Cadastro de Planograma")

    nome = st.text_input('Nome do Planograma')
    imagem = st.file_uploader('Upload da Imagem', type=['jpg', 'jpeg', 'png'])
    loja = st.text_input('Loja')
    rua = st.text_input('Rua')
    gondola = st.text_input('Gôndola')

    if st.button('Salvar'):
        if nome and imagem and loja and rua and gondola:
            salvar_planograma(nome, imagem, loja, rua, gondola)
            st.success('Planograma salvo com sucesso!')
        else:
            st.error('Por favor, preencha todos os campos.')

# Página de Visualização
elif pagina == "Visualização de Planogramas":
    st.title("Planogramas Cadastrados")
    
    # Obter todos os planogramas do banco de dados
    c.execute('SELECT id, nome, loja, rua, gondola FROM planogramas')
    planogramas = c.fetchall()
    
    # Exibir planogramas em uma tabela com botões de edição/exclusão na mesma coluna
    if planogramas:
        # Converte os dados para DataFrame
        df_planogramas = pd.DataFrame(planogramas, columns=["ID", "Nome", "Loja", "Rua", "Gôndola"])

        # Adiciona colunas para os botões de ação
        df_planogramas['Ações'] = df_planogramas['ID'].apply(lambda x: (
            st.button("✏️ Editar", key=f"edit_{x}", on_click=lambda: st.session_state.update(pagina="Detalhes do Planograma", planograma_id=x)),
            st.button("🗑️ Excluir", key=f"delete_{x}", on_click=lambda: deletar_planograma(x))
        ))

        # Exibe a tabela com os dados e botões de ação
        st.write("### Planogramas Cadastrados")
        st.dataframe(df_planogramas[["ID", "Nome", "Loja", "Rua", "Gôndola", "Ações"]], width=800)

# Página de Detalhes
elif pagina == "Detalhes do Planograma" and 'planograma_id' in st.session_state:
    planograma_id = st.session_state.planograma_id
    planograma = obter_planograma(planograma_id)

    if planograma:
        st.title(f"Detalhes do Planograma: {planograma[1]}")
        
        # Exibir imagem atual do planograma
        st.image(carregar_imagem(planograma[2]), caption=f'Loja: {planograma[3]} | Rua: {planograma[4]} | Gôndola: {planograma[5]}')

        # Gera e exibe o QR Code
        imagem_url = f"localhost:8501/{planograma_id}"
        qr_code_img = gerar_qr_code(imagem_url)
        st.image(qr_code_img, caption="QR Code para o link da imagem")

        # Formulário de edição
        nome = st.text_input('Nome do Planograma', value=planograma[1])
        imagem = st.file_uploader('Upload de nova imagem (opcional)', type=['jpg', 'jpeg', 'png'])
        loja = st.text_input('Loja', value=planograma[3])
        rua = st.text_input('Rua', value=planograma[4])
        gondola = st.text_input('Gôndola', value=planograma[5])

        # Botão para atualizar o planograma
        if st.button('Atualizar Planograma'):
            atualizar_planograma(planograma_id, nome, imagem, loja, rua, gondola)
            st.success("Planograma atualizado com sucesso!")
        
    else:
        st.error("Planograma não encontrado.")

# Fechar a conexão com o banco de dados
conn.close()
