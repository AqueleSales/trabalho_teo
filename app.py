from flask import Flask, render_template, jsonify, request
import os
import google.generativeai as genai

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# ==========================================
# CONFIGURAÇÃO DA IA (GEMINI)
# ==========================================
chave_api = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=chave_api)
modelo_ia = genai.GenerativeModel('gemini-1.5-flash')

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

@app.route('/api/mitos-verdades')
def get_mitos_verdades():
    dados = [
        {
            "id": 1,
            "pergunta": "Se não tem histórico familiar não há risco",
            "resposta": "❌ MITO. Apenas 5-10% dos casos estão relacionados a histórico familiar. Fatores ambientais e comportamentais são muito relevantes.",
            "tipo": "mito"
        },
        {
            "id": 2,
            "pergunta": "Mamografia substitui o cuidado com as mamas",
            "resposta": "❌ MITO. A mamografia complementa, mas não substitui o auto-exame e a atenção às mudanças nas mamas.",
            "tipo": "mito"
        },
        {
            "id": 3,
            "pergunta": "É possível evitar o câncer através da alimentação",
            "resposta": "✅ VERDADE. Uma dieta rica em alimentos in natura, especialmente de origem vegetal, reduz significativamente o risco.",
            "tipo": "verdade"
        },
        {
            "id": 4,
            "pergunta": "Existem alimentos milagrosos que curam câncer",
            "resposta": "❌ MITO. Não há alimento que cure câncer. A alimentação saudável apenas contribui para a prevenção e melhor resposta ao tratamento.",
            "tipo": "mito"
        },
        {
            "id": 5,
            "pergunta": "Exposição a forno micro-ondas provoca câncer",
            "resposta": "❌ MITO. A radiação do micro-ondas apenas aquece alimentos, não alterando sua estrutura molecular ou criando substâncias cancerígenas.",
            "tipo": "mito"
        },
        {
            "id": 6,
            "pergunta": "Atividade física reduz risco de câncer mesmo sem perder peso",
            "resposta": "✅ VERDADE. O exercício reduz risco independentemente da perda de peso, através do equilíbrio hormonal e fortalecimento imunológico.",
            "tipo": "verdade"
        },
        {
            "id": 7,
            "pergunta": "Excesso de gordura corporal aumenta o risco de câncer",
            "resposta": "✅ VERDADE. O excesso de gordura provoca alterações hormonais e inflamatórias que estimulam proliferação celular anormal.",
            "tipo": "verdade"
        },
        {
            "id": 8,
            "pergunta": "Câncer é sempre uma sentença de morte",
            "resposta": "❌ MITO. Muitos tipos de câncer têm altas taxas de cura quando detectados precocemente. A qualidade de vida é possível em todas as fases.",
            "tipo": "mito"
        }
    ]
    return jsonify(dados)

@app.route('/api/redes-apoio-df')
def get_redes_apoio():
    redes = [
        {
            "nome": "Hospital de Base (HBDF)",
            "endereco": "SGAN 915 Norte, Asa Norte, Brasília - DF",
            "telefone": "(61) 3315-1234",
            "tipo": "sus_oncologia",
            "especialidades": ["Quimioterapia", "Cirurgia Oncológica", "Radioterapia"]
        },
        {
            "nome": "Hospital Regional de Taguatinga (HRT)",
            "endereco": "Taguatinga, Brasília - DF",
            "telefone": "(61) 3305-1000",
            "tipo": "sus_oncologia",
            "especialidades": ["Oncologia", "Radioterapia", "Suporte Psicológico"]
        },
        {
            "nome": "Hospital Universitário de Brasília (HUB)",
            "endereco": "Campus Darcy Ribeiro, Brasília - DF",
            "telefone": "(61) 3307-7000",
            "tipo": "sus_oncologia",
            "especialidades": ["Radioterapia", "Oncologia Clínica"]
        },
        {
            "nome": "Rede Feminina / Casa Rosa",
            "endereco": "HBDF - Asa Norte",
            "telefone": "Contato via HBDF",
            "tipo": "ong",
            "especialidades": ["Hospedagem", "Suporte Emocional", "Assistência Social"]
        },
        {
            "nome": "ABAC-Luz",
            "endereco": "Brasília - DF",
            "telefone": "A confirmar",
            "tipo": "ong",
            "especialidades": ["Educação em Saúde", "Prevenção de Mama", "Grupos de Apoio"]
        },
        {
            "nome": "Canomama",
            "endereco": "Brasília - DF",
            "telefone": "A confirmar",
            "tipo": "ong",
            "especialidades": ["Reabilitação", "Esportes", "Empoderamento Feminino"]
        }
    ]
    return jsonify(redes)

@app.route('/api/moderar', methods=['POST'])
def moderar_texto():
    dados = request.json
    texto_original = dados.get('mensagem', '')

    # O "Super Prompt" com a lógica contextual
    prompt_comando = f"""
    Você é um moderador inteligente e empático de um fórum de pacientes de câncer e cuidados paliativos.
    Sua tarefa é higienizar o relato abaixo aplicando regras estritas de contexto.

    REGRA 1 - DADOS PESSOAIS (APAGAR): 
    Substitua nomes de pacientes, familiares, telefones pessoais e endereços residenciais por [DADO PROTEGIDO].

    REGRA 2 - RECOMENDAÇÕES (MANTER): 
    NÃO apague nomes de hospitais, clínicas, ONGs, médicos sendo elogiados/recomendados, nem telefones públicos de instituições. Isso é rede de apoio útil.

    REGRA 3 - SPAM (BLOQUEAR): 
    Se o texto contiver links (URLs), spam de emojis sem sentido ou "ASCII art", retorne EXATAMENTE o código: BLOQUEADO_SPAM

    REGRA 4 - PALAVRÕES E CONTEXTO EMOCIONAL (MANTER): 
    Palavrões usados como expressão de dor, medo, frustração ou desabafo pessoal (ex: "puta merda, estou com medo") DEVEM SER MANTIDOS. Fazem parte do luto.

    REGRA 5 - ÓDIO E OFENSAS (BLOQUEAR): 
    Se o palavrão ou o texto for um ataque direto, ofensa a outra pessoa, discriminação ou discurso de ódio, retorne EXATAMENTE o código: BLOQUEADO_ODIO

    Responda APENAS com o texto final higienizado ou com um dos códigos de bloqueio. Não adicione mais nenhuma palavra.

    Texto para analisar:
    "{texto_original}"
    """

    try:
        resposta = modelo_ia.generate_content(prompt_comando)
        texto_limpo = resposta.text.strip()
        return jsonify({'status': 'sucesso', 'texto_limpo': texto_limpo})
    except Exception as e:
        print(f"Erro na IA: {e}")
        # Em caso de falha na API do Google, deixa o texto original passar para não quebrar o site
        return jsonify({'status': 'erro', 'texto_limpo': texto_original})

@app.errorhandler(404)
def page_not_found(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('index.html'), 500

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000, threaded=True)