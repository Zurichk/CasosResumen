import json
import requests
import configparser

def get_api_key():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config['deepseek']['apikey']

API_KEY = get_api_key()
deepseek_api_url = 'https://api.deepseek.com/v1/completions'  # Ajusta la URL según sea necesario

system_prompt = """
  Instrucciones a seguir para generar la respuesta:
        Contestame siempre en español, con un tono formal y en pasado.
        Omite nombres propios y referencias a personas o empresas, clientes, etc.
        No incluir información personal, ni fechas, solo mencionar el problema y las soluciones realizadas por el tecnico.
        No incluir ninguna frase negativa, como Queda pendiente hablar con David para determinar si el error se debió a un fallo del programa o a una configuración incorrecta.
        Importante: Enfocar el problema, como si fuera culpa del cliente, pero sin culparle directamente, para que el servicio o reparación no entre en garantía y se pueda cobrar el trabajo realizado.
        No mencionar las instrucciones para generar la respuesta.
        Genera la respuesta en formato JSON.
"""

def generar_resumen(titulo, descripcion, comentarios):
    user_prompt = f"{titulo}. {descripcion}. {comentarios}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    payload = {
        "model": "deepseek-coder",  # Ajusta el modelo si es necesario
        "messages": messages
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(deepseek_api_url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Request failed with status code {response.status_code}: {response.text}")

# Ejemplo de uso
titulo = "Problema en el sistema de facturación"
descripcion = "El sistema dejó de generar facturas correctamente."
comentarios = "El cliente notó que las facturas no se generan desde ayer."

try:
    resumen = generar_resumen(titulo, descripcion, comentarios)
    print(json.dumps(resumen, indent=2, ensure_ascii=False))  # Imprime el resumen en un formato legible
except Exception as e:
    print(f"Error: {str(e)}")
