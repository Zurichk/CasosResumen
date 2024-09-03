import json
from openai import OpenAI
import configparser

def get_api_key():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config['deepseek']['apikey']

API_KEY = get_api_key()
deepseek_api_url = 'https://api.deepseek.com/'  # Ajusta la URL según sea necesario

# Configura el cliente con la API Key y la URL base
client = OpenAI(api_key=API_KEY, base_url=deepseek_api_url)

def generar_resumen(titulo, descripcion, comentarios):
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
    
    user_prompt = f"{titulo}. {descripcion}. {comentarios}"

    response = client.chat.completions.create(
        model="deepseek-coder",  # Ajusta el modelo si es necesario
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        stream=False
    )

    # Imprimir la respuesta cruda para depuración
    print("Raw response:", response)
    print("Response text:", response.text)

    try:
        # Asume que el contenido JSON es la primera opción de la respuesta
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        raise Exception(f"Error processing response: {str(e)}")


# Ejemplo de uso
titulo = "Problema en el sistema de facturación"
descripcion = "El sistema dejó de generar facturas correctamente."
comentarios = "El cliente notó que las facturas no se generan desde ayer."

try:
    resumen = generar_resumen(titulo, descripcion, comentarios)
    print(json.dumps(json.loads(resumen), indent=2, ensure_ascii=False))  # Imprime el resumen en un formato legible
except Exception as e:
    print(f"Error: {str(e)}")
