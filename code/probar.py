import requests
import json

# Definir la URL del punto final
url = 'http://localhost:5000/enviar_datos_bc'
# url = 'https://resumen.onrender.com/enviar_datos_bc'

# Definir el JSON de ejemplo
data = [
    {
        "Titulo": "CALIDONA - Ha registrado el IRPF y le ha creado mal el asiento.",
        "Descripcion": "CALIDONA - Ya hemos encontrado la errata. Se había quedado colgado ese grupo de IVA en la cuenta 472 y lo hemos cambiando. No obstante, hay un ERROR en el asiento que hace en la liquidación de IRPF. El asiento tiene que descargar las cuentas de pasivo de IRPF contra el banco, sin embargo, al registrar la liquidación de IRPF nos ha metido movimientos incorrectos en: - Cuenta de Gastos - Cuenta de acreedores En el banco ha realizado un movimiento de 0€. Adjunto asiento. La sociedad es AVS HOMES Hemos desliquidado los importes de la liquidación de septiembre y vamos a revertir el asiento. Por cierto, no podemos revertir el asiento por no haber sido introducido por un diario Acuérdate por favor de borrar el asiento que te pasé ayer y revisar por qué razón no lo hace bien el sistema. Correo: José Luis - 20/02/24.",
        "Comentarios": "21/02/24 - ALP: Borrar los asientos que dice de las tablas relacionadas. Mando correo a José Luis para avisar. Revisar por qué ha hecho mal el registro del IRPF. Duplico entorno de pruebas. 22/02/24 - ALP: Sigo revisando lo que hace el proceso. Recorre todos los mov. irpf de la fecha indicada y buscar los mov. contabilidad. No coinciden los número con los número de facturas. Hablo con David y me dice que lo vemos mañana. 23/02/24 - ALP: Ver con David. Me dice que está mal y que lo cambie. Modifico código para que coja la cuenta de la conf. irpf y el importe del irpf. Consigo pasar las dimensiones, pero el id. grupo dimensión no hay forma. Lo veo con Lorena. Me llama David y se lo comento. Me dice que no hace falta porque al validar la cuenta se debe de hacer solo. Modifico todo y hago pruebas. Ya lo hace bien. Aviso a David para que lo suba a Microsoft. 23/02/524 - LLB Mirar con Antono Dimension Set ID 26/02/24 - ALP: Entro para comprobar si se subió. Está subido. Actualizo al cliente. Mando correo a José Luis para que pruebe de nuevo. Me confirma que funciona. Pregunta si era fallo del programa o de una configuración. Esperar a hablar con David."
    }
]

# Convertir el JSON a string
payload = json.dumps(data)

# Definir las cabeceras
headers = {
    'Content-Type': 'application/json'
}

# Enviar la solicitud POST
response = requests.post(url, headers=headers, data=payload)

# Mostrar la respuesta
print(response.json())