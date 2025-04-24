import streamlit as st
from PIL import Image as PILImage
import speech_recognition as sr
from deep_translator import GoogleTranslator
from google.generativeai import configure, GenerativeModel

configure(api_key="SUA_API_KEY")


# Função para gerar nome e modo de preparo
def gerar_receita_com_gemini(ingredientes, usar_somente=True):
    if usar_somente:
        prompt = f"""
Você é um chef de cozinha renomado. Crie uma receita utilizando exclusivamente os seguintes ingredientes: {ingredientes}.
Não adicione nenhum outro ingrediente que não esteja listado. 
Liste claramente os INGREDIENTES e o MODO DE PREPARO.
"""
    else:
        prompt = f"""
Você é um chef de cozinha experiente e criativo. Com base nos ingredientes fornecidos: {ingredientes}, crie uma receita deliciosa. 
Se necessário, você pode adicionar outros ingredientes que combinem bem. 
Apresente a lista de INGREDIENTES e o MODO DE PREPARO de forma organizada.
"""

    try:
        modelo = GenerativeModel("gemini-1.5-flash")
        response = modelo.generate_content(prompt)
        receita_completa = response.text
        receita_pt = GoogleTranslator(source='auto', target='pt').translate(receita_completa)

        linhas = receita_pt.strip().split("\n")
        nome = linhas[0]
        passos = "\n".join(linhas[1:])

        return nome, passos
    except Exception as e:
        st.error(f"Erro ao gerar a receita: {e}")
        return None, None


# Transcrição do áudio
def transcrever_audio():
    recognizer = sr.Recognizer()
    source = sr.Microphone()
    
    try:
        source_stream = source.__enter__()  # Abre o microfone manualmente
        st.info("🎤 Por favor, fale agora!")
        recognizer.adjust_for_ambient_noise(source_stream)
        audio = recognizer.listen(source_stream)
        st.info("🔍 Processando...")
    except Exception as e:
        st.error(f"Erro ao acessar o microfone: {e}")
        return ""
    finally:
        source.__exit__(None, None, None)  # Fecha o microfone

    try:
        texto = recognizer.recognize_google(audio, language="pt-BR")
        st.success(f"Insumos detectados: {texto}")
        return texto
    except sr.UnknownValueError:
        st.error("Não consegui entender o que você disse.")
        return ""
    except sr.RequestError:
        st.error("Erro ao acessar o serviço de reconhecimento.")
        return ""


# Função para identificar imagem
def identificar_imagem(arquivo_imagem):
    try:
        modelo_vision = GenerativeModel("gemini-1.5-flash")
        image = PILImage.open(arquivo_imagem)
        response = modelo_vision.generate_content(
            ["Identifique todos os ingredientes visíveis nesta imagem de comida.", image]
        )
        return response.text.strip()
    except Exception as e:
        st.error(f"Erro ao identificar ingredientes com Gemini: {e}")
        return None


# Interface
st.title("🍳 Receitas Inteligentes")

st.markdown(""" 
    <style>
        body {
            background: linear-gradient(135deg, #cda5f1, #ffe0b2);
            background-attachment: fixed;
            color: #222222;
        }
        .stApp {
            background: linear-gradient(135deg, #cda5f1, #ffe0b2);
            color: #222222;
        }
        h1, h2, h3, h4 {
            color: #2f2f2f;
        }
        .stTextArea, .stTextInput {
            background-color: rgba(255, 255, 255, 0.3);
            border-radius: 10px;
            color: #222222;
            padding: 10px;
        }
        .stTextInput input {
            background-color: rgba(255, 255, 255, 0.3);
            border-radius: 8px;
            color: #222222;
            padding: 10px;
        }
        button {
            background-color: #ffb74d;
            color: #222222;
            border: none;
            border-radius: 8px;
            padding: 0.5em 1em;
        }
    </style>
""", unsafe_allow_html=True)


modo = st.radio("Como deseja informar os ingredientes?", ["🎤 Falar", "✏️ Digitar", "📸 Enviar imagem", "📄 Carregar arquivo de texto"])
ingredientes_texto = ""


if modo == "🎤 Falar":
    if st.button("Clique para falar"):
        ingredientes_texto = transcrever_audio()

elif modo == "✏️ Digitar":
    ingredientes_texto = st.text_input("Digite os ingredientes separados por vírgula:")

elif modo == "📸 Enviar imagem":
    arquivos_imagem = st.file_uploader("Carregue imagens dos ingredientes", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

    if "ingredientes_imagem" not in st.session_state:
        st.session_state.ingredientes_imagem = []

    if arquivos_imagem:
        st.session_state.ingredientes_imagem = arquivos_imagem

    if st.button("🔍 Identificar ingredientes e gerar receita"):
        ingredientes_identificados = []
        for img in st.session_state.ingredientes_imagem:
            ingrediente = identificar_imagem(img)
            if ingrediente:
                st.success(f"🧾 Ingredientes identificados: {ingrediente}")
                ingredientes_identificados.append(ingrediente)

        ingredientes_texto = ", ".join(ingredientes_identificados)
        st.session_state.ingredientes_texto = ingredientes_texto

        nome_receita, passos_receita = gerar_receita_com_gemini(ingredientes_texto, usar_somente=True)

        if nome_receita:
            st.session_state.ultima_receita = (nome_receita, passos_receita)

elif modo == "📄 Carregar arquivo de texto":
    arquivo_txt = st.file_uploader("Envie um arquivo .txt com os ingredientes que você tem", type=["txt"])
    if arquivo_txt is not None:
        try:
            conteudo = arquivo_txt.read().decode("utf-8")
            st.success("Arquivo lido com sucesso!")
            st.text_area("📋 Ingredientes do arquivo:", value=conteudo, height=150)
            ingredientes_texto = conteudo
        except Exception as e:
            st.error(f"Erro ao ler o arquivo: {e}")


# Checkbox para usar somente os ingredientes fornecidos
usar_somente = st.checkbox("🔒 Usar somente os ingredientes fornecidos", value=True)


# Inicializa sessão
if "ultima_receita" not in st.session_state:
    st.session_state.ultima_receita = None

if "ingredientes_texto" not in st.session_state:
    st.session_state.ingredientes_texto = ""


# Caso de digitação, fala ou arquivo texto
if ingredientes_texto.strip() and modo != "📸 Enviar imagem":
    st.session_state.ingredientes_texto = ingredientes_texto
    st.info("🧠 Gerando nome da receita...")

    nome_receita, passos_receita = gerar_receita_com_gemini(ingredientes_texto, usar_somente)
    if nome_receita:
        st.session_state.ultima_receita = (nome_receita, passos_receita)


# Exibir a receita final
if st.session_state.ultima_receita:
    nome, passos = st.session_state.ultima_receita
    st.subheader(f"📛 Receita: {nome}")

    if st.button("👩‍🍳 Mostrar modo de preparo"):
        st.text_area("Modo de Preparo", value=passos, height=300)

    if st.button("🎲 Gerar nova sugestão de receita"):
        st.info("🔁 Gerando nova sugestão de receita...")
        novo_nome, novos_passos = gerar_receita_com_gemini(st.session_state.ingredientes_texto, usar_somente)
        if novo_nome:
            st.session_state.ultima_receita = (novo_nome, novos_passos)
            st.success(f"Nova sugestão de receita: {novo_nome}")
            st.text_area("Modo de Preparo da nova sugestão", value=novos_passos, height=300)
