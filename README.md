# 🍳 **Receitas Inteligentes com IA**

Uma Chefe de cozinha inteligente que cria receitas com base em ingredientes fornecidos via texto, voz, imagem ou arquivo de texto.

## 🔧 **Funcionalidades**

- 🎤 **Entrada por áudio**.
- 📸 **Reconhecimento de ingredientes a partir de imagens**.
- ✍️ **Entrada manual ou via arquivo `.txt`**.
- 👨‍🍳 **Geração de receitas exclusivas com IA (Google Gemini)**.
- 🔄 **Geração de múltiplas sugestões com base nos mesmos ingredientes**.

---

## 📦 **Dependências**

Instalar:

```bash
pip install -r requirements.txt```

## Rodar arquivo: streamlit run app.py 
______________________________________________________
⚠️⚠️  Atenção: É necessário possuir chaves de API válidas para os serviços do Google Gemini e Google Cloud Vision.

    🔑 Como obter as chaves de API
        Google Gemini API:

        Acesse: https://aistudio.google.com/app/apikey

        Crie sua conta (caso ainda não tenha) e gere uma chave de API.

        Google Cloud Vision API:

        Acesse: https://console.cloud.google.com/

        Crie um projeto, ative a API Vision AI e gere uma chave de API na aba "Credenciais".

______________________________________________________

## 📖 Sobre

📚 Detalhes da Implementação
    🧠 Back-End
        O back-end cuida da comunicação com a IA do Google chamada Gemini. É lá que está a função que envia os ingredientes para a IA e recebe de volta uma receita completa com nome e modo de preparo.

        A função principal é a gerar_receita_com_gemini, que usa os ingredientes e cria um texto com a receita usando a inteligência artificial.

    💻 Front-End 
        O Front-End foi feito com Streamlit, que é uma ferramenta bem simples para criar sites e interfaces.
______________________________________________________

🚀 Como Usar
    📥 Escolha como informar os ingredientes:
    🎤 Falar: Clique no botão e diga os ingredientes com clareza. A IA vai entender o que foi falado e usar isso.

    ✏️ Digitar: Escreva os ingredientes separados por vírgula no campo.

    📸 Imagem: Envie uma foto dos ingredientes e a IA vai tentar reconhecer o que tem na imagem.

    📄 Arquivo de Texto: Se você tiver um arquivo .txt com os ingredientes, é só enviar.
______________________________________________________

🍽️ Depois disso:
    Clique no botão para gerar a receita. A IA vai criar um nome e mostrar como preparar.

    Você também pode clicar para gerar outra sugestão de receita com os mesmos ingredientes.
______________________________________________________

⚙️ Pontos Fortes (Coisas boas do projeto)
    Várias formas de entrada: Pode usar voz, imagem, texto ou arquivo.

    Receitas criativas: A IA inventa receitas novas com os ingredientes que você tem.

    Fácil de usar: O visual é simples e qualquer pessoa pode mexer.

    IA potente: Usa o modelo Google Gemini, que é bem rápido e inteligente.
______________________________________________________

⚠️ Pontos Fracos (Coisas que podem melhorar)
    Precisa de internet: Como usa IA da Google, é necessário estar conectado.

    Imagens às vezes não funcionam bem: Se a foto estiver escura ou desfocada, a IA pode não reconhecer os ingredientes direito.

    Depende de chave da API: Para funcionar, precisa de uma chave especial da Google. Se essa chave for desativada ou se acabar a cota gratuita, o sistema para de funcionar.

