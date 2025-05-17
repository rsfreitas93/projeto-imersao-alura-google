import os
import json
from google import genai
from main import app
from flask import jsonify, request
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types  # Para criar conteúdos (Content e Part)

os.environ['GOOGLE_API_KEY'] = 'COLE_SUA_API_KEY_AQUI'
client = genai.Client()

# Função auxiliar que envia uma mensagem para um agente via Runner e retorna a resposta final
def call_agent(agent: Agent, message_text: str, file_data: bytes = None, file_mime_type: str = None) -> str:
    # Cria um serviço de sessão em memória
    session_service = InMemorySessionService()
    # Cria uma nova sessão (você pode personalizar os IDs conforme necessário)
    session = session_service.create_session(app_name=agent.name, user_id="user1", session_id="session1")
    # Cria um Runner para o agente
    runner = Runner(agent=agent, app_name=agent.name, session_service=session_service)
    # Cria a lista de partes para o conteúdo da mensagem de entrada
    parts = [types.Part(text=message_text)] # Começa com a parte de texto

    # Se dados da imagem foram fornecidos, cria uma parte para a imagem e a adiciona à lista
    if file_data and file_mime_type:
        image_part = types.Part(
            inline_data={
                "data": file_data, 
                "mime_type": file_mime_type,
            }
        )
        parts.append(image_part)

    # Cria o conteúdo da mensagem de entrada
    content = types.Content(role="user", parts=parts)

    final_response = ""
    # Itera assincronamente pelos eventos retornados durante a execução do agente
    for event in runner.run(user_id="user1", session_id="session1", new_message=content):
        if event.is_final_response():
          for part in event.content.parts:
            if part.text is not None:
              final_response += part.text
              final_response += "\n"
    return final_response

# Agentes de IA criados
def agente_nutricionista_dicas(dados_entrada):
   dica_nutri = Agent(
        name="agente_dica_nutri",
        model="gemini-2.0-flash",
        instruction="""
        Você é um nutricionista. A sua tarefa é analisar os dados recebidos de uma pessoa para dar dicas simples e rápidas que possam 
        ser úteis para a saúde dessa pessoa e que vá de encontro com o objetivo dela. Seja educado e bem humorado na sua resposta. 
        Você vai receber como informação um breve texto explicando os dados de entrada e o foco da sua resposta. 
        Sua resposta deve ter no máximo 300 caracteres.
        """,
        description="Agente nutricionista que analise dados para dar dica rápida"
    )
   
   dica_final = call_agent(dica_nutri, dados_entrada)
   return dica_final
def agente_nutricionista_tecnico(dados_entrada, limite_caracteres):
   analise_nutri = Agent(
        name="agente_nutri_tecnico",
        model="gemini-2.0-flash",
        instruction=f"""
        Você é um nutricionista. A sua tarefa é analisar criticamente os dados recebidos de uma pessoa para dar orientações que possam 
        ser úteis para a saúde dessa pessoa e que vá de encontro com o objetivo dela. Seja educado, bem humorado e objetivo na sua resposta. 
        Traga elementos técnicos na sua resposta e seja criterioso.
        Você vai receber como informação um breve texto explicando os dados de entrada e o foco da sua resposta. 
        Sua resposta deve ter no máximo {limite_caracteres} caracteres.
        """,
        description="Agente nutricionista que analise dados criticamente"
    )
   
   analise_final = call_agent(analise_nutri, dados_entrada)
   return analise_final
def agente_conversor_medidas(dados_entrada):
   conversor_medidas = Agent(
        name="agente_conversor_medidas",
        model="gemini-2.0-flash",
        instruction="""
        Você é um especialista em conversão de medidas culinárias. 
        Você vai receber como informação um breve texto explicando os dados de entrada e o foco da sua resposta. 
        """,
        description="Agente conversor de unidades de medidas para gramas"
    )
   
   analise_final = call_agent(conversor_medidas, dados_entrada)
   return analise_final
def agente_interprete_fotos(dados_entrada, image_data, image_mime_type):
   interprete_fotos = Agent(
        name="agente_interprete_fotos",
        model="gemini-2.0-flash",
        instruction="""
        Você é um especialista em culinária, medidas culinárias e nutrição. 
        Você vai receber como informação uma breve texto explicando os dados de entrada e o foco da sua resposta. 
        Você também receberá uma imagem para analisar.
        Siga as instruções do texto para analisar a imagem e gerar a resposta no formato solicitado.
        """,
        description="Agente especialista em identificar alimentos e quantidades em imagens"
    )
   
   analise_final = call_agent(interprete_fotos, dados_entrada, file_data=image_data, file_mime_type=image_mime_type)
   return analise_final
def agente_interprete_planos_alimentares(dados_entrada, file_data, file_mime_type):
   interprete_fotos = Agent(
        name="agente_interprete_planos_alimentares",
        model="gemini-2.0-flash",
        instruction="""
        Você é um especialista em culinária e nutrição. 
        Você vai receber como informação uma breve texto explicando os dados de entrada e o foco da sua resposta. 
        Você também receberá um arquivo para analisar.
        Siga as instruções do texto para analisar o arquivo e gerar a resposta no formato solicitado.
        """,
        description="Agente especialista em padronizar informações de planos alimentares"
    )
   
   analise_final = call_agent(interprete_fotos, dados_entrada, file_data=file_data, file_mime_type=file_mime_type)
   return analise_final

# Funções de chamada dos agentes
@app.route('/agentes_ia/nutricao/getDicaRapida')
def getDicaRapida():
    # CONSIDERE RECUPERAR ESSAS INFORMAÇÕES DE UM BANCO DE DADOS
    refeicoes_7dias = [
        {"refeicao":"Café da Manhã","alimentos_consumidos":["Ovos mexidos (2 unidades)","Pão integral (1 fatia)","Abacate (1/4)"],"estimativa_de_calorias":350,"estimativa_de_proteinas":20,"estimativa_de_gorduras":25,"data":"2025-05-13"},
        {"refeicao":"Almoço","alimentos_consumidos":["Filé de frango grelhado (150g)","Arroz integral (100g cozido)","Feijão carioca (100g cozido)","Salada mista (alface, tomate, pepino)"],"estimativa_de_calorias":550,"estimativa_de_proteinas":40,"estimativa_de_gorduras":15,"data":"2025-05-13"},
        {"refeicao":"Café da Tarde","alimentos_consumidos":["Iogurte natural integral (1 pote)","Granola (30g)"],"estimativa_de_calorias":200,"estimativa_de_proteinas":10,"estimativa_de_gorduras":8,"data":"2025-05-13"},
        {"refeicao":"Jantar","alimentos_consumidos":["Sopa de legumes com carne magra","Torrada integral (2 unidades)"],"estimativa_de_calorias":400,"estimativa_de_proteinas":30,"estimativa_de_gorduras":12,"data":"2025-05-13"},
        {"refeicao":"Café da Manhã","alimentos_consumidos":["Mingau de aveia com frutas vermelhas","Amêndoas (10g)"],"estimativa_de_calorias":300,"estimativa_de_proteinas":8,"estimativa_de_gorduras":10,"data":"2025-05-14"},
        {"refeicao":"Almoço","alimentos_consumidos":["Salmão assado (120g)","Batata doce cozida (150g)","Brócolis cozido"],"estimativa_de_calorias":600,"estimativa_de_proteinas":35,"estimativa_de_gorduras":30,"data":"2025-05-14"},
        {"refeicao":"Café da Tarde","alimentos_consumidos":["Ovo cozido (1 unidade)","Palitos de cenoura e pepino"],"estimativa_de_calorias":100,"estimativa_de_proteinas":6,"estimativa_de_gorduras":5,"data":"2025-05-14"},
        {"refeicao":"Jantar","alimentos_consumidos":["Omelete com queijo e espinafre","Salada verde"],"estimativa_de_calorias":350,"estimativa_de_proteinas":25,"estimativa_de_gorduras":20,"data":"2025-05-14"},
        {"refeicao":"Ceia","alimentos_consumidos":["Leite desnatado (200ml)"],"estimativa_de_calorias":80,"estimativa_de_proteinas":7,"estimativa_de_gorduras":1,"data":"2025-05-14"},
        {"refeicao":"Café da Manhã","alimentos_consumidos":["Smoothie de frutas com whey protein"],"estimativa_de_calorias":280,"estimativa_de_proteinas":25,"estimativa_de_gorduras":5,"data":"2025-05-15"},
        {"refeicao":"Almoço","alimentos_consumidos":["Carne moída magra com purê de batata","Couve refogada"],"estimativa_de_calorias":500,"estimativa_de_proteinas":40,"estimativa_de_gorduras":20,"data":"2025-05-15"},
        {"refeicao":"Café da Tarde","alimentos_consumidos":["Frutas (maçã e banana)"],"estimativa_de_calorias":150,"estimativa_de_proteinas":2,"estimativa_de_gorduras":1,"data":"2025-05-15"},
        {"refeicao":"Jantar","alimentos_consumidos":["Wrap integral com atum e vegetais"],"estimativa_de_calorias":400,"estimativa_de_proteinas":30,"estimativa_de_gorduras":15,"data":"2025-05-15"},
        {"refeicao":"Café da Manhã","alimentos_consumidos":["Torradas integrais com azeite e tomate (2 unidades)"],"estimativa_de_calorias":250,"estimativa_de_proteinas":5,"estimativa_de_gorduras":15,"data":"2025-05-16"},
        {"refeicao":"Almoço","alimentos_consumidos":["Lasanha de abobrinha com ricota e espinafre"],"estimativa_de_calorias":450,"estimativa_de_proteinas":25,"estimativa_de_gorduras":25,"data":"2025-05-16"},
        {"refeicao":"Café da Tarde","alimentos_consumidos":["Um punhado de castanhas"],"estimativa_de_calorias":180,"estimativa_de_proteinas":6,"estimativa_de_gorduras":15,"data":"2025-05-16"},
        {"refeicao":"Jantar","alimentos_consumidos":["Salada grande com frango desfiado, folhas, tomate e pepino"],"estimativa_de_calorias":300,"estimativa_de_proteinas":30,"estimativa_de_gorduras":10,"data":"2025-05-16"},
        {"refeicao":"Café da Manhã","alimentos_consumidos":["Panquecas de banana e ovo (2 unidades)","Mel (fio)"],"estimativa_de_calorias":320,"estimativa_de_proteinas":15,"estimativa_de_gorduras":10,"data":"2025-05-17"},
        {"refeicao":"Almoço","alimentos_consumidos":["Arroz com lentilha","Bife grelhado (100g)","Abobrinha refogada"],"estimativa_de_calorias":550,"estimativa_de_proteinas":35,"estimativa_de_gorduras":20,"data":"2025-05-17"},
        {"refeicao":"Café da Tarde","alimentos_consumidos":["Vitamina de abacate com leite"],"estimativa_de_calorias":220,"estimativa_de_proteinas":5,"estimativa_de_gorduras":18,"data":"2025-05-17"},
        {"refeicao":"Jantar","alimentos_consumidos":["Peixe branco cozido com legumes no vapor"],"estimativa_de_calorias":380,"estimativa_de_proteinas":30,"estimativa_de_gorduras":15,"data":"2025-05-17"},
        {"refeicao":"Café da Manhã","alimentos_consumidos":["Pão de queijo (2 unidades)","Café com leite"],"estimativa_de_calorias":400,"estimativa_de_proteinas":10,"estimativa_de_gorduras":25,"data":"2025-05-18"},
        {"refeicao":"Almoço","alimentos_consumidos":["Feijoada (porção pequena)","Arroz branco","Couva refogada","Laranja"],"estimativa_de_calorias":700,"estimativa_de_proteinas":40,"estimativa_de_gorduras":40,"data":"2025-05-18"},
        {"refeicao":"Café da Tarde","alimentos_consumidos":["Bolo simples (1 fatia)"],"estimativa_de_calorias":250,"estimativa_de_proteinas":3,"estimativa_de_gorduras":10,"data":"2025-05-18"},
        {"refeicao":"Jantar","alimentos_consumidos":["Pizza (2 fatias - mussarela)"],"estimativa_de_calorias":600,"estimativa_de_proteinas":20,"estimativa_de_gorduras":30,"data":"2025-05-18"},
        {"refeicao":"Café da Manhã","alimentos_consumidos":["Cereal integral com leite e frutas picadas"],"estimativa_de_calorias":300,"estimativa_de_proteinas":10,"estimativa_de_gorduras":5,"data":"2025-05-19"},
        {"refeicao":"Almoço","alimentos_consumidos":["Macarrão integral com molho bolonhesa","Salada"],"estimativa_de_calorias":500,"estimativa_de_proteinas":30,"estimativa_de_gorduras":20,"data":"2025-05-19"},
        {"refeicao":"Café da Tarde","alimentos_consumidos":["Barra de cereal"],"estimativa_de_calorias":120,"estimativa_de_proteinas":3,"estimativa_de_gorduras":5,"data":"2025-05-19"},
        {"refeicao":"Jantar","alimentos_consumidos":["Sanduíche natural (pão integral, frango desfiado, alface, tomate)"],"estimativa_de_calorias":350,"estimativa_de_proteinas":25,"estimativa_de_gorduras":10,"data":"2025-05-19"}
    ]
    objetivo_usuario = "Ganhar massa muscular"

    string_json = json.dumps(refeicoes_7dias)
    dados_entrada = f"""Estou enviando as refeições dos ultimos 7 dias (Refeições) e os objetivos da pessoa (Objetivos).\n
                        Refeições: {string_json}\n
                        Objetivos: {objetivo_usuario}\n
                        Foque sua resposta em indicações de alimentos para ajustar nas refeições ou refeições a serem incluídas ou extintas."""
    resposta_agente = agente_nutricionista_dicas(dados_entrada)
    
    return jsonify(resposta_agente)

@app.route('/agentes_ia/nutricao/getDicaMetas')
def getDicaMetas():
    # CONSIDERE RECUPERAR ESSAS INFORMAÇÕES DE UM BANCO DE DADOS
    indicacao_diaria = '{"calorias":2000,"carboidratos":250,"proteinas":100,"gorduras":80}'
    progresso_diario = '{"calorias":1500,"carboidratos":200,"proteinas":90,"gorduras":60}'
    progresso_semanal = '{"calorias":0.57,"carboidratos":0.57,"proteinas":0.64,"gorduras":0.63}'
    objetivo_usuario = "Emagrecimento"
    dias_restantes_semana = 4

    dados_entrada = f"""Estou enviando minha indicação diária de consumo (Indicação Diária), meu progresso atual do dia (Progresso Atual), 
                        meu progresso semanal em porcentagem (Progesso Semanal), quantos dias ainda tem na semana (Dias Restantes) e os meus objetivos (Objetivos).\n
                        Indicação Diária: {indicacao_diaria}\n
                        Progresso Atual: {progresso_diario}\n
                        Progesso Semanal: {progresso_semanal}\n
                        Dias Restantes: {dias_restantes_semana}\n
                        Objetivos: {objetivo_usuario}\n
                        Foque sua resposta em me orientar como devo realizar minhas proximas refeições a fim de atingir a meta semanal que mais se adeque ao meu objetivo
                        sem ultrapassar os limites de indicação diaria no contexto semanal. Inclua em sua resposta uma explicação técnica simples para justificar sua análise."""
    resposta_agente = agente_nutricionista_tecnico(dados_entrada, 600)
    
    return jsonify(resposta_agente)

@app.route('/agentes_ia/nutricao/getConversao', methods=['POST'])
def getConversao():
    dados_recebidos = request.get_json()
    alimento = dados_recebidos.get('nome')
    quantidade = dados_recebidos.get('quantidade')
    unidade = dados_recebidos.get('unidade')

    dados_entrada = f"""Estou enviando um alimento (Alimento), uma quantidade (Quantidade) e uma unidade de medida (Unidade).\n
                        Alimento: {alimento}\n
                        Quantidade: {quantidade}\n
                        Unidade: {unidade}\n
                        Converta essa quantidade desse alimento para o peso em gramas. Espero como resposta somente o valor do peso."""
    resposta_agente = agente_conversor_medidas(dados_entrada)
    
    return jsonify(resposta_agente)

@app.route('/agentes_ia/nutricao/getAlimentosImg', methods=['POST'])
def getAlimentosImg():
    # Verifica se o arquivo 'imagem' foi enviado na requisição POST
    if 'imagem' not in request.files:
        return jsonify({"error": "Nenhuma imagem foi enviada na requisição."}), 400

    file = request.files['imagem']

    # Verifica se o nome do arquivo está vazio (caso o usuário não tenha selecionado um arquivo)
    if file.filename == '':
        return jsonify({"error": "Nenhum arquivo selecionado."}), 400

    # Verifica se o arquivo é de fato uma imagem (opcional, mas recomendado)
    if not file.mimetype or not file.mimetype.startswith('image/'):
         return jsonify({"error": "Tipo de arquivo não suportado. Por favor, envie uma imagem."}), 400

    try:
        # Lê o conteúdo binário da imagem
        image_data = file.read()
        image_mime_type = file.mimetype # Obtém o tipo MIME do arquivo (ex: 'image/jpeg', 'image/png')

        # Define as instruções de texto para o agente
        dados_entrada = """Estou enviando um arquivo anexo de imagem.\n
                       Analise essa imagem e identifique quais alimentos estão presentes nela e suas quantidades aproximadas em gramas.
                       Como resposta espero apenas o nome do alimento identificado e o peso como no exemplo abaixo.
                       Arroz: 150 gramas
                       Carne vermelha: 100 gramas
                       Molho: 20 gramas"""

        # Chama a função agente_interprete_fotos, passando o texto E os dados da imagem
        resposta_agente = agente_interprete_fotos(dados_entrada, image_data, image_mime_type)

        return jsonify(resposta_agente)

    except Exception as e:
        # Tratamento de erro básico caso algo dê errado ao ler o arquivo ou chamar o agente
        return jsonify({"error": f"Ocorreu um erro ao processar a imagem: {e}"}), 500

@app.route('/agentes_ia/nutricao/getPlanoAlim', methods=['POST'])
def getPlanoAlim():
    if 'plano' not in request.files:
        return jsonify({"error": "Nenhum plano foi enviada na requisição."}), 400

    file = request.files['plano']

    # Verifica se o nome do arquivo está vazio (caso o usuário não tenha selecionado um arquivo)
    if file.filename == '':
        return jsonify({"error": "Nenhum arquivo selecionado."}), 400

    try:
        # Lê o conteúdo binário do arquivo
        arquivo_data = file.read()
        arquivo_mime_type = file.mimetype 

        # Define as instruções de texto para o agente
        dados_entrada = """Estou enviando um arquivo anexo de um plano alimentar.\n
                       Analise as informações desse arquivo.
                       Como resposta quero um texto semelhante ao exemplo abaixo:

                       Validade do plano: de 01/05/2025 até 18/05/2025
                       Objetivo do plano: Emagrecimento
                       Café da manhã: 3 ovos, 2 fatias de pão e 300ml de leite
                       Almoço: Salada de folhas verdes com frango grelhado
                       Jantar: Sopa de legumes com tofu
                       """

        # Chama a função agente_interprete_planos_alimentares, passando o texto E o arquivo
        resposta_agente = agente_interprete_planos_alimentares(dados_entrada, arquivo_data, arquivo_mime_type)

        return jsonify(resposta_agente)

    except Exception as e:
        # Tratamento de erro básico caso algo dê errado ao ler o arquivo ou chamar o agente
        return jsonify({"error": f"Ocorreu um erro ao processar o plano alimentar: {e}"}), 500

@app.route('/agentes_ia/nutricao/getAnaliseBio')
def getAnaliseBio():
    # CONSIDERE RECUPERAR ESSAS INFORMAÇÕES DE UM BANCO DE DADOS
    dados_bioimpedancia = """[  {"data":2025-01-01,"peso":80,"gordura":0.32,"massa":15,"agua":0.65},
                                {"data":2025-02-01,"peso":82,"gordura":0.34,"massa":20,"agua":0.45},
                                {"data":2025-03-01,"peso":76,"gordura":0.28,"massa":19,"agua":0.70},
                                {"data":2025-04-01,"peso":72,"gordura":0.20,"massa":18,"agua":0.88}
                            ]"""
    objetivo = "Hipertrofia"
    
    dados_entrada = f"""Estou enviando meus dados de bioimpedancia (Bioimpedancia) e os meus objetivos (Objetivos).\n
                        Bioimpedancia: {dados_bioimpedancia}\n
                        Objetivos: {objetivo}\n
                        Foque sua resposta em fazer uma análise critica desses dados, mostrando o quão mais próximo do meu objetivo estou.
                        Fale sobre possíveis proximos passos que posso assumir como objetivo e inclua em sua resposta explicações técnicas,
                        mas de fácil compreensão para justificar sua análise.
                        Faça a resposta como o exemplo abaixo:
                        
                        Análise da evolução desde 01/01/2025 até 01/04/2025:
                        Peso: Redução de 8,0 kg.
                        Gordura Corporal: Aumento de 0,0 %.
                        Massa Muscular: Redução de 2,0 kg.
                        Água Corporal: Redução de 2,0 %.
                        Observação: A evolução é mista. Uma análise mais detalhada com um profissional é recomendada."""
    resposta_agente = agente_nutricionista_tecnico(dados_entrada, 1000)
    
    return jsonify(resposta_agente)

@app.route('/agentes_ia/nutricao/chefbot', methods=['POST'])
def chefbot():
    dados_recebidos = request.get_json()
    msgUser = dados_recebidos.get('msg')

    chat_config = types.GenerateContentConfig(
        system_instruction = "Você é um asistente culinário que sempre responde de maneira clara e bem explicada.",
    )

    chat = client.chats.create(
        model="gemini-2.0-flash",
        config=chat_config,
    )

    resposta = chat.send_message(msgUser)
    
    return jsonify(resposta.text)
