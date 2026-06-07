from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# ============================================
# ROTAS PRINCIPAIS
# ============================================

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

# ============================================
# API - DADOS DINÂMICOS
# ============================================

@app.route('/api/mitos-verdades')
def get_mitos_verdades():
    """Retorna dados para o jogo de mitos e verdades - Flip Cards"""
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
    """Retorna dados de redes de apoio no DF"""
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

# ============================================
# TRATAMENTO DE ERROS
# ============================================

@app.errorhandler(404)
def page_not_found(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('index.html'), 500

# ============================================
# RODANDO A APLICAÇÃO
# ============================================

if __name__ == '__main__':
    # Para desenvolvimento local
    app.run(
        debug=True,
        host='localhost',
        port=5000,
        threaded=True
    )
    
    # Para produção, use um servidor WSGI como gunicorn:
    # gunicorn -w 4 -b 0.0.0.0:5000 app:app
