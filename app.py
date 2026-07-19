from flask import Flask, render_template, jsonify, request
import os
import requests
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# ==========================================
# CONFIGURAÇÃO DO FIREBASE ADMIN
# ==========================================
try:
    # O Render esconde os arquivos secretos nesta pasta do Linux:
    caminho_chave = '/etc/secrets/firebase-key.json'

    # Se você for testar no seu PC (onde essa pasta não existe), ele usa o arquivo local:
    if not os.path.exists(caminho_chave):
        caminho_chave = 'firebase-key.json'

    cred = credentials.Certificate(caminho_chave)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("✅ Firebase conectado com sucesso!")
except Exception as e:
    print(f"❌ Erro crítico ao iniciar Firebase Admin: {e}")


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/entendendo-cancer')
def entendendo_cancer():
    return render_template('entendendo-cancer.html')


@app.route('/cuidado-acolhimento')
def cuidado_acolhimento():
    return render_template('cuidado-acolhimento.html')


@app.route('/direitos-rede')
def direitos_rede():
    return render_template('direitos-rede.html')


@app.route('/vivencias')
def vivencias():
    return render_template('vivencias.html')


@app.route('/sobre')
def sobre():
    return render_template('sobre.html')


@app.route('/api/moderar', methods=['POST'])
def moderar_texto():
    dados = request.json
    nome = dados.get('nome', 'Anônimo')
    texto_original = dados.get('mensagem', '')
    chave_api = os.environ.get("GEMINI_API_KEY")

    if not chave_api:
        return jsonify({'status': 'erro', 'msg': 'API Key do Gemini ausente.'})

    prompt_comando = f"""
    Você é um moderador inteligente e empático de um fórum de pacientes de câncer e cuidados paliativos.
    Sua tarefa é higienizar o relato abaixo aplicando regras estritas de contexto.

    REGRA 1 - DADOS PESSOAIS (APAGAR): Substitua nomes de pacientes, familiares, telefones pessoais e endereços residenciais por [DADO PROTEGIDO].
    REGRA 2 - RECOMENDAÇÕES (MANTER): NÃO apague nomes de hospitais, clínicas, ONGs, médicos sendo elogiados/recomendados.
    REGRA 3 - SPAM (BLOQUEAR): Se o texto contiver links (URLs), spam ou propagandas, retorne EXATAMENTE o código: BLOQUEADO_SPAM
    REGRA 4 - PALAVRÕES (MANTER): Palavrões usados como expressão de dor ou desabafo pessoal DEVEM SER MANTIDOS.
    REGRA 5 - ÓDIO/OFENSAS (BLOQUEAR): Se houver ofensa a outra pessoa ou discurso de ódio, retorne EXATAMENTE o código: BLOQUEADO_ODIO

    Responda APENAS com o texto final higienizado ou os códigos de bloqueio.
    Texto para analisar: "{texto_original}"
    """

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={chave_api}"
        payload = {"contents": [{"parts": [{"text": prompt_comando}]}]}
        headers = {"Content-Type": "application/json"}

        resposta = requests.post(url, json=payload, headers=headers)
        dados_resposta = resposta.json()

        # Se a API do Google der erro (ex: chave inválida), a gente pega aqui:
        if 'error' in dados_resposta:
            print(f"❌ Erro do Google Gemini: {dados_resposta['error']}")
            return jsonify({'status': 'erro', 'msg': 'Erro na comunicação com a IA.'})

        try:
            texto_limpo = dados_resposta['candidates'][0]['content']['parts'][0]['text'].strip()
        except KeyError:
            # Se o próprio filtro do Google bloquear a mensagem antes de analisar
            return jsonify({'status': 'bloqueado_odio'})

        if "BLOQUEADO_SPAM" in texto_limpo:
            return jsonify({'status': 'bloqueado_spam'})
        if "BLOQUEADO_ODIO" in texto_limpo:
            return jsonify({'status': 'bloqueado_odio'})

        # PYTHON É QUEM SALVA NO FIREBASE
        db.collection("relatos").add({
            "nome": nome,
            "mensagem": texto_limpo,
            "data": datetime.now().strftime("%d/%m/%Y"),
            "timestamp": datetime.now().timestamp(),
            "curtidas": 0
        })

        return jsonify({'status': 'sucesso', 'texto_limpo': texto_limpo})
    except Exception as e:
        print(f"❌ Erro no Backend: {e}")
        return jsonify({'status': 'erro', 'msg': str(e)})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)