import json
from flask import Flask, request, jsonify, render_template, abort
import os
from openai import OpenAI
import configparser

# Definir la ruta donde se guardarán los archivos cargados
if os.environ.get('DOCKER', '') == "yes":
    UPLOAD_FOLDER = '/usr/src/app/subidas'
else:
    UPLOAD_FOLDER = 'subidas'

app = Flask(__name__, static_url_path='/static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_api_key():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config['deepseek']['apikey']

API_KEY = get_api_key()

# Usar DeepSeek
deepseek_api_url = 'https://api.deepseek.com/'
client = OpenAI(api_key=API_KEY, base_url=deepseek_api_url)

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

def generar_resumen(titulo, descripcion, comentarios):
    user_prompt = f"{titulo}. {descripcion}. {comentarios}"

    messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}]

    response = client.chat.completions.create(
        model="deepseek-coder",
        messages=messages,
        response_format={
            'type': 'json_object'
        }
    )

    print(json.loads(response.choices[0].message.content))
    return json.loads(response.choices[0].message.content)

@app.route("/")
def home():
    return render_template('index.html')

@app.route('/resumir', methods=['POST'])
def resumir():
    titulo = request.form['titulo']
    descripcion = request.form['descripcion']
    comentarios = request.form['comentarios']

    try:
        resumen = generar_resumen(titulo, descripcion, comentarios)
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

    # Realizar el resumen
    try:
        resumen = generar_resumen(datos[0]['Titulo'], datos[0]['Descripcion'], datos[0]['Comentarios'])
        return jsonify({'resumen': resumen})
    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Ejecutar la aplicación