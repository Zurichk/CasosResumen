import json
from flask import Flask, request, jsonify, render_template, abort
import os
import configparser
# --- NUEVO: Importar clientes de OpenAI y Gemini ---
import google.generativeai as genai
from openai import OpenAI

# Definir la ruta donde se guardarán los archivos cargados
if os.environ.get('DOCKER', '') == "yes":
    UPLOAD_FOLDER = '/usr/src/app/subidas'
else:
    UPLOAD_FOLDER = 'subidas'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- NUEVO: Función para obtener API key según modelo ---
def get_api_key(tipo="deepseek"):
    # 1. Buscar primero en variables de entorno (para despliegue cloud seguro)
    env_map = {
        "gemini": ["APIKEYGEMINI", "GEMINI_APIKEY", "GEMINI_KEY"],
        "deepseek": ["APIKEYDEEPSEEK", "DEEPSEEK_APIKEY", "DEEPSEEK_KEY"],
        "openai": ["APIKEYOPENAI", "OPENAI_APIKEY", "OPENAI_KEY"]
    }
    for env_var in env_map.get(tipo, []):
        valor = os.environ.get(env_var)
        if valor:
            return valor
    # 2. Buscar en secrets.ini (local/dev)
    config = configparser.ConfigParser()
    config.read(os.path.join('docs', 'config.ini'))
    secrets_path = os.path.join('docs', 'secrets.ini')
    if os.path.exists(secrets_path):
        secrets = configparser.ConfigParser()
        secrets.read(secrets_path)
        if tipo == "gemini":
            if 'secrets' in secrets:
                if 'gemini_apikey' in secrets['secrets'] and secrets['secrets']['gemini_apikey']:
                    return secrets['secrets']['gemini_apikey']
                if 'apikeygemini' in secrets['secrets'] and secrets['secrets']['apikeygemini']:
                    return secrets['secrets']['apikeygemini']
        if tipo == "deepseek" and 'secrets' in secrets and 'apikeydeepseek' in secrets['secrets'] and secrets['secrets']['apikeydeepseek']:
            return secrets['secrets']['apikeydeepseek']
        if tipo == "openai" and 'secrets' in secrets and 'apikeyopenai' in secrets['secrets'] and secrets['secrets']['apikeyopenai']:
            return secrets['secrets']['apikeyopenai']
    # 3. Fallback a config.ini (legacy)
    if tipo == "gemini" and 'gemini' in config and 'apikey' in config['gemini']:
        return config['gemini']['apikey']
    if tipo == "deepseek" and 'deepseek' in config and 'apikey' in config['deepseek']:
        return config['deepseek']['apikey']
    if tipo == "openai" and 'openai' in config and 'apikey' in config['openai']:
        return config['openai']['apikey']
    raise RuntimeError(f'No se encontró la clave API para {tipo} en variables de entorno, secrets.ini ni config.ini')

# --- NUEVO: Inicialización de modelos ---
genai.configure(api_key=get_api_key("gemini"))
model_gemini = genai.GenerativeModel("gemini-2.0-flash")
openai_client = OpenAI(api_key=get_api_key("openai"))
deepseek_client = OpenAI(api_key=get_api_key("deepseek"), base_url="https://api.deepseek.com")

system_prompt = """
  Instrucciones a seguir para generar la respuesta:
        Contestame siempre en español, con un tono formal y en pasado.
        Omite nombres propios y referencias a personas o empresas, clientes, etc.
        No incluir información personal, ni fechas, solo mencionar el problema y las soluciones realizadas por el tecnico.
        No incluir ninguna frase negativa, como Queda pendiente hablar con David para determinar si el error se debió a un fallo del programa o a una configuración incorrecta.
        Importante: Enfocar el problema, como si fuera culpa del cliente, pero sin culparle directamente, para que el servicio o reparación no entre en garantía y se pueda cobrar el trabajo realizado.
        No mencionar las instrucciones para generar la respuesta.
        Genera la respuesta en texto plano, sin formato, y sin incluir la pregunta.
"""

# --- NUEVO: Función para elegir modelo y generar resumen ---
def generar_resumen(titulo, descripcion, comentarios, modelo):
    user_prompt = f"{titulo}. {descripcion}. {comentarios}"
    prompt = system_prompt + "\n" + user_prompt
    if modelo == "gemini":
        response = model_gemini.generate_content(prompt)
        return response.text
    elif modelo == "openai":
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
        )
        return response.choices[0].message.content
    elif modelo == "deepseek":
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        # response = deepseek_client.chat.completions.create(
        #     model="deepseek-chat",
        #     messages=messages,
        #     response_format={'type': 'text'},
        #     timeout=60,
        #     temperature=0.1, 
        #     max_tokens=4000
        # )
        
        response = deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            timeout=60,
            temperature=0.1, 
            max_tokens=4000
        )
        return response.choices[0].message.content
    else:
        return "Modelo no soportado."

@app.route("/")
def home():
    return render_template('index.html')

@app.route('/resumir', methods=['POST'])
def resumir():
    titulo = request.form['titulo']
    descripcion = request.form['descripcion']
    comentarios = request.form['comentarios']
    modelo = request.form.get('modelo') or 'gemini'  # Por defecto, usar gemini si no se selecciona
    try:
        resumen = generar_resumen(titulo, descripcion, comentarios, modelo)
        return render_template('resumen.html', resumen=resumen)
    except Exception as e:
        error_message = f"Error al generar el resumen: {str(e)}"
        return render_template('error.html', error_message=error_message)

@app.route('/enviar_datos_bc', methods=['POST'])
def enviar_datos_bc():
    # Comprobar si la petición tiene los datos en formato JSON
    if not request.is_json:
        return jsonify({'error': 'No JSON object in the request.'}), 400

    # Leer los datos del JSON
    datos = request.get_json()
    print(datos)

    # Validar los datos (aquí podrías agregar más validaciones)
    if not isinstance(datos, list):
        print({'error': 'Los datos deben ser una lista.'})
        return jsonify({'error': 'Los datos deben ser una lista.'}), 400

    # Obtener modelo del JSON (opcional, por defecto gemini)
    modelo = datos[0].get('modelo', 'gemini') if isinstance(datos[0], dict) else 'gemini'
    try:
        resumen = generar_resumen(datos[0]['Titulo'], datos[0]['Descripcion'], datos[0]['Comentarios'], modelo)
        return jsonify({'resumen': resumen})
    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Ejecutar la aplicación