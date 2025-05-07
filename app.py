import streamlit as st
from PIL import Image as PILImage
import speech_recognition as sr
from deep_translator import GoogleTranslator
from google.generativeai import configure, GenerativeModel

configure(api_key="AIzaSyCT0oQBlUyF7P1S7qd5A4QDl3aAr_YXOHg")

# Função para gerar nome e modo de preparo
def gerar_receita_com_gemini(ingredientes, usar_so_ingredientes=True):
    prompt = f"""
Você é um chef de cozinha renomado. Crie uma receita utilizando exclusivamente os seguintes ingredientes: {ingredientes}.
Não adicione nenhum outro ingrediente que não esteja listado. 
Liste claramente os INGREDIENTES e o MODO DE PREPARO.RECEITAS SIMPLES NÃO MUITO DIFICIL
"""
    if not usar_so_ingredientes:
        prompt = f"""
Você é um chef de cozinha renomado. Crie uma receita deliciosa, usando os seguintes ingredientes como base: {ingredientes}.
Sinta-se à vontade para adicionar outros ingredientes que combinem bem com os fornecidos. 
Liste claramente os INGREDIENTES e o MODO DE PREPARO.RECEITAS SIMPLES NÃO MUITO DIFICIL
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
        source_stream = source.__enter__()
        st.info("🎤 Por favor, fale agora!")
        recognizer.adjust_for_ambient_noise(source_stream)
        audio = recognizer.listen(source_stream)
        st.info("🔍 Processando...")
    except Exception as e:
        st.error(f"Erro ao acessar o microfone: {e}")
        return ""
    finally:
        source.__exit__(None, None, None)

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
            ["Identifique todos os ingredientes visíve nesta imagem de comida.", image]
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
            border-radius: 8px;            color: #222222;
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

if modo == "✏️ Digitar":
    ingredientes_texto = st.text_input("Digite os ingredientes separados por vírgula:")
    if st.button("🍽️ Gerar Receita"):
        st.session_state.ingredientes_texto = ingredientes_texto
        nome_receita, passos_receita = gerar_receita_com_gemini(ingredientes_texto)
        if nome_receita:
            st.session_state.ultima_receita = (nome_receita, passos_receita)

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

        if ingredientes_texto.strip():
            st.session_state.ingredientes_texto = ingredientes_texto
            nome_receita, passos_receita = gerar_receita_com_gemini(ingredientes_texto)
            if nome_receita:
                st.session_state.ultima_receita = (nome_receita, passos_receita)
        else:
            st.warning("⚠️ Nenhum ingrediente foi identificado nas imagens. Por favor, envie uma imagem válida.")

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

if "ultima_receita" not in st.session_state:
    st.session_state.ultima_receita = None
if "ingredientes_texto" not in st.session_state:
    st.session_state.ingredientes_texto = ""

# Adicionando a opção de escolher se usa apenas os ingredientes fornecidos ou não
usar_so_ingredientes = st.checkbox("Usar apenas os ingredientes fornecidos?", value=True)

if ingredientes_texto.strip() and modo != "📸 Enviar imagem":
    st.session_state.ingredientes_texto = ingredientes_texto
    st.info("🧠 Gerando nome da receita...")
    nome_receita, passos_receita = gerar_receita_com_gemini(ingredientes_texto, usar_so_ingredientes)
    if nome_receita:
        st.session_state.ultima_receita = (nome_receita, passos_receita)
else:
    if modo != "📸 Enviar imagem" and ingredientes_texto.strip() == "":
        st.warning("⚠️ Nenhum ingrediente foi identificado. Por favor, forneça ingredientes válidos para gerar a receita.")

if st.session_state.ultima_receita:
    nome, passos = st.session_state.ultima_receita
    st.markdown(f"""
        <div style="background-color: #ffffff; padding: 25px; border-radius: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.15); margin-top: 20px;">
            <h2 style="color: #8e24aa; font-family: 'Segoe UI', sans-serif; text-align: center; font-weight: bold;">{nome}</h2>
            <h3 style="color: #6a1b9a; font-weight: bold;">👨‍🍳 Modo de Preparo:</h3>
            <pre style="color: #3e3e3e; font-size: 17px; font-family: 'Segoe UI', sans-serif; white-space: pre-wrap; word-wrap: break-word;">
{passos.replace('Ingredientes', '<b>Ingredientes</b>').replace('Modo de Preparo', '<b>Modo de Preparo</b>')}</pre>
        </div>
    """, unsafe_allow_html=True)

    if st.button("🎲 Gerar nova sugestão de receita"):
        st.info("🔁 Gerando nova sugestão de receita...")
        novo_nome, novos_passos = gerar_receita_com_gemini(st.session_state.ingredientes_texto, usar_so_ingredientes)
        if novo_nome:
            st.session_state.ultima_receita = (novo_nome, novos_passos)
            st.success(f"Nova sugestão de receita: {novo_nome}")

if "mostrar_ajuda" not in st.session_state:
    st.session_state.mostrar_ajuda = False

if st.button("❓ Como usar", use_container_width=True):
    st.session_state.mostrar_ajuda = not st.session_state.mostrar_ajuda

if st.session_state.mostrar_ajuda:
    with st.container():
        st.markdown("""  
            <div style="background-color: #f0f2f6; border: 1px solid #ccc; border-radius: 12px; padding: 20px; margin-top: 10px;2px 12px rgba(0,0,0,0.1);">
                <h4 style="margin-top: 0;">📘 <b>Como usar o aplicativo:</b></h4>
                <ol>
                    <li><b>Escolha o método</b> para informar os ingredientes:
                        <ul>
                            <li>🎤 <b>Falar</b>: Clique no botão e fale claramente os ingredientes. Ex: "tomate, arroz, carne".</li>
                            <li>✏️ <b>Digitar</b>: Escreva os ingredientes separados por vírgula.</li>
                            <li>📸 <b>Imagem</b>: Envie uma imagem com os ingredientes visíveis.</li>
                            <li>📄 <b>Arquivo</b>: Carregue um arquivo .txt com os ingredientes.</li>
                        </ul>
                    </li>
                    <li>Clique em <b>"Gerar receita"</b> e aguarde a IA criar a sugestão.</li>
                    <li>Veja o <b>nome da receita</b> e leia o <b>modo de preparo</b> com atenção.</li>
                </ol>
                <p style="margin-bottom: 10px;"><b>Dica:</b> fale ou digite os ingredientes com clareza para melhores resultados.</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("❌ Fechar ajuda", key="fechar_ajuda", use_container_width=True):
                st.session_state.mostrar_ajuda = False
