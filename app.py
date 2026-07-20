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
    caminho_chave = '/etc/secrets/firebase-key.json'
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

@app.route('/papel-enfermagem')
def papel_enfermagem():
    return render_template('papel-enfermagem.html')


@app.route('/api/moderar', methods=['POST'])
def moderar_texto():
    dados = request.json
    nome = dados.get('nome', 'Anônimo')
    texto_original = dados.get('mensagem', '')
    foto_base64 = dados.get('foto', '')  # <--- AGORA O PYTHON RECEBE A FOTO DO SEU FRONTEND
    chave_api = os.environ.get("GEMINI_API_KEY")

    if not chave_api:
        return jsonify({'status': 'erro', 'msg': 'API Key do Gemini ausente no servidor.'})

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
        modelo_ativo = "models/gemini-3.5-flash"

        try:
            get_models_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={chave_api}"
            lista_modelos = requests.get(get_models_url, timeout=3).json()
            if 'models' in lista_modelos:
                for m in lista_modelos['models']:
                    nome_modelo = m.get('name', '')
                    metodos = m.get('supportedGenerationMethods', [])
                    if 'generateContent' in metodos and (
                            'gemini-3.5-flash' in nome_modelo or 'gemini-3.1-flash-lite' in nome_modelo):
                        modelo_ativo = nome_modelo
                        break
        except:
            pass

        url = f"https://generativelanguage.googleapis.com/v1beta/{modelo_ativo}:generateContent?key={chave_api}"
        payload = {"contents": [{"parts": [{"text": prompt_comando}]}]}
        headers = {"Content-Type": "application/json"}

        resposta = requests.post(url, json=payload, headers=headers)
        dados_resposta = resposta.json()

        if 'error' in dados_resposta:
            print(f"❌ Erro do Google Gemini: {dados_resposta['error']}")
            fallback_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent?key={chave_api}"
            resposta_fallback = requests.post(fallback_url, json=payload, headers=headers)
            dados_resposta = resposta_fallback.json()
            if 'error' in dados_resposta:
                return jsonify({'status': 'erro',
                                'msg': f"IA indisponível: {dados_resposta['error'].get('message', 'Erro desconhecido')}"})

        try:
            texto_limpo = dados_resposta['candidates'][0]['content']['parts'][0]['text'].strip()
        except KeyError:
            return jsonify({'status': 'bloqueado_odio'})

        if "BLOQUEADO_SPAM" in texto_limpo:
            return jsonify({'status': 'bloqueado_spam'})
        if "BLOQUEADO_ODIO" in texto_limpo:
            return jsonify({'status': 'bloqueado_odio'})

        db.collection("relatos").add({
            "nome": nome,
            "mensagem": texto_limpo,
            "foto": foto_base64,  # <--- E SALVA A FOTO DIRETAMENTE NO FIREBASE!
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