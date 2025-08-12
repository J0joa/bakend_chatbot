from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fuzzywuzzy import process, fuzz

import re

app = FastAPI()

# Permitir comunicación con el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Local
        "https://frontend-chat-bot-six.vercel.app",  # Producción en Vercel
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Datos globales simulados
datos_usuario = {
    "nombre": "",
    "edad": 0,
    "ingresos": 0,
    "ocupacion": "",
    "tiempo_laborado": 0,
    "carros_seleccionados": [],
}

historial_aprobaciones = []

# Intenciones del chatbot
intenciones = {
    "hola": "¡Hola!, Binvenido a nuestra empresa, aqui podras finaciar tu carro. ¿Qué linea de carros quieres, sport, pickups o camioneta?, ¿De qué color lo quieres, rojo, negro o plateado?.",
    "quiero una camioneta roja": "Hemos cuargado tu carro para que lo visualices en la seccion carrito ChatBot, para mas detalle ve al menu y seleciona catálogo, ¿cuál es tu nombre?",
    "quiero una camioneta negra": "Hemos cuargado tu carro para que lo visualices en la seccion carrito ChatBot, para mas detalle ve al menu y seleciona catálogo, ¿cuál es tu nombre?",
    "quiero una camioneta plateada": "Hemos cuargado tu carro para que lo visualices en la seccion carrito ChatBot, para mas detalle ve al menu y seleciona catálogoAgregado: ca, ¿cuál es tu nombre?",
    "quiero una pickup roja": "Hemos cuargado tu carro para que lo visualices en la seccion carrito ChatBot, para mas detalle ve al menu y seleciona catálogo, ¿cuál es tu nombre?",
    "quiero una pickup negra": "Hemos cuargado tu carro para que lo visualices en la seccion carrito ChatBot, para mas detalle ve al menu y seleciona catálogo, ¿cuál es tu nombre?",
    "quiero una pickup plateada": "Hemos cuargado tu carro para que lo visualices en la seccion carrito ChatBot, para mas detalle ve al menu y seleciona catálogo, ¿cuál es tu nombre?",
    "quiero un sport rojo": "Hemos cuargado tu carro para que lo visualices en la seccion carrito ChatBot, para mas detalle ve al menu y seleciona catálogo, ¿cuál es tu nombre?",
    "quiero un sport negro": "Hemos cuargado tu carro para que lo visualices en la seccion carrito ChatBot, para mas detalle ve al menu y seleciona catálogo, ¿cuál es tu nombre?",
    "quiero un sport plateado": "Hemos cuargado tu carro para que lo visualices en la seccion carrito ChatBot, para mas detalle ve al menu y seleciona catálogo, ¿cuál es tu nombre?",
    "camioneta roja": "Hemos cuargado tu carro para que lo visualices en la seccion carrito ChatBot, para mas detalle ve al menu y seleciona catálogo, ¿cuál es tu nombre?",
    "pickup negra": "Hemos cuargado tu carro para que lo visualices en la seccion carrito ChatBot, para mas detalle ve al menu y seleciona catálogo, ¿cuál es tu nombre?",
    "sport plateado": "Hemos cuargado tu carro para que lo visualices en la seccion carrito ChatBot, para mas detalle ve al menu y seleciona catálogo, ¿cuál es tu nombre?",
    "una sport negra": "Hemos cuargado tu carro para que lo visualices en la seccion carrito ChatBot, para mas detalle ve al menu y seleciona catálogo, ¿cuál es tu nombre?",
    "deseo una camioneta plateada": "Hemos cuargado tu carro para que lo visualices en la seccion carrito ChatBot, para mas detalle ve al menu y seleciona catálogo, ¿cuál es tu nombre?",
    "Mi nombre es": "¿Cuántos años tienes?",
    "Me llamo ": "¿Cuántos años tienes?",
    "tengo  años": "¿Cuál es tu estado civil?",
    "Mi edad es de años": "¿Estado civi?",
    "Soy independiente": "¿Cuánto ganas es tu ingreso mensual?",
    "estoy independiente": "¿Cuánto ganas es tu ingreso mensual?",
    "independiente": "¿Cuánto ganas es tu ingreso mensual?",
    "Estoy soltero": "¿Cuánto ganas es tu ingreso mensual?",
    "soy soltero": "¿Cuánto ganas es tu ingreso mensual?",
    "soltero": "¿Cuánto ganas es tu ingreso mensual?",
    "Estoy casado": "¿Cuánto ganas es tu ingreso mensual?",
    "soy casado": "¿Cuánto ganas es tu ingreso mensual?",
    "casado": "¿Cuánto ganas es tu ingreso mensual?",
    "Estoy pensionado": "¿Cuánto ganas es tu ingreso mensual?",
    "soy pensionado": "¿Cuánto ganas es tu ingreso mensual?",
    "pensionado": "¿Cuánto ganas es tu ingreso mensual?",
    "gano ": "¿Cuánto tiempo lleva laborando en meses?",
    "yo gano": "¿Cuánto tiempo lleva laborando en meses?",
    "es de ": "¿Cuánto tiempo lleva laborando en meses?",
    "meses": "Gracias por la información, estamos procesando tu solicitud de crédito.",
}


# 🔍 Fuzzy Matching
def encontrar_intencion(texto_usuario: str, umbral=75):
    frases = list(intenciones.keys())
    resultado, puntuacion = process.extractOne(texto_usuario.lower(), frases)
    if puntuacion >= umbral:
        return resultado, intenciones[resultado]
    return None, None


def encontrar_similar(texto, opciones, umbral=75):
    for opcion in opciones:
        if fuzz.partial_ratio(opcion, texto) >= umbral:
            return opcion
    return None


# 👤 Modelos
class Mensaje(BaseModel):
    texto: str


class UsuarioRegistro(BaseModel):
    nombre: str
    edad: int
    ocupacion: str
    tiempo_laborado: int


def verificar_credito():
    """Verifica si todos los datos están completos y devuelve dict con aprobación o rechazo."""
    if (
        datos_usuario["edad"] > 0
        and datos_usuario["ingresos"] > 0
        and datos_usuario["tiempo_laborado"] > 0
        and datos_usuario["ocupacion"] != ""
    ):
        aprobado = (
            datos_usuario["edad"] >= 18
            and datos_usuario["ingresos"] >= 1000000
            and datos_usuario["tiempo_laborado"] >= 12
            and datos_usuario["ocupacion"] in ["independiente", "pensionado"]
        )
        respuesta_final = (
            "✅ Tu crédito ha sido aprobado."
            if aprobado
            else "❌ Tu crédito ha sido rechazado."
        )
        accion_final = "CREDITO_APROBADO" if aprobado else "CREDITO_RECHAZADO"

        historial_aprobaciones.append(
            {
                "nombre": datos_usuario["nombre"],
                "edad": datos_usuario["edad"],
                "ingresos": datos_usuario["ingresos"],
                "ocupacion": datos_usuario["ocupacion"],
                "tiempo_laborado": datos_usuario["tiempo_laborado"],
                "resultado": respuesta_final,
            }
        )

        # Reiniciar datos para nuevo usuario
        datos_usuario.clear()
        datos_usuario.update(
            {
                "nombre": "",
                "edad": 0,
                "ingresos": 0,
                "ocupacion": "",
                "tiempo_laborado": 0,
                "carros_seleccionados": [],
            }
        )
        return {"respuesta": respuesta_final, "accion": accion_final}
    return None


@app.post("/chatbot")
async def responder(mensaje: Mensaje):
    texto = mensaje.texto.lower()

    # Registro de carro
    colores = ["rojo", "negro", "plateado"]
    tipos = ["camioneta", "pickup", "sport"]
    color_encontrado = encontrar_similar(texto, colores)
    tipo_encontrado = encontrar_similar(texto, tipos)

    if color_encontrado and tipo_encontrado:
        datos_usuario["carros_seleccionados"].append(
            {"color": color_encontrado, "tipo": tipo_encontrado}
        )
        return {
            "respuesta": f"Tu {tipo_encontrado} {color_encontrado} ha sido agregada al carrito, puedes verla en la seccion carrito ChatBot.  para mas detalle ve al menu y seleciona catálogo, ¿cuál es tu nombre?",
            "accion": "AGREGAR_CARRO",
        }

    clave, respuesta = encontrar_intencion(texto)

    frase_name = ["{nombre}", "soy", "mi nombre es", "me llamo"]

    # Registro de nombre

    if "me llamo" in texto or "mi nombre es" in texto or "soy julanito" in texto:
        nombre = (
            texto.replace("me llamo", "")
            .replace("mi nombre es", "")
            .replace("soy", "")
            .strip()
        )
        datos_usuario["nombre"] = nombre
        return {
            "respuesta": f"Un gusto {nombre}, encantado de tenerte en nuestro ECOMERSE de autos CHEBROLET, ¿cuántos años tienes?",
            "accion": "REGISTRAR_NOMBRE",
        }

    # Edad
    import re
    if "años" in texto:
        # Buscar número que preceda o siga la palabra "años"
        numeros = re.findall(r"\d+", texto)
        if numeros:
            edad = int(numeros[0])
            datos_usuario["edad"] = edad
            res = verificar_credito()
            if res:
                return res
        return {
            "respuesta": f"Tu edad de {edad} años es estupenda, ¿cuánto ganas mensualmente?",
            "accion": "REGISTRAR_EDAD",
        }

    # Ingresos
    

    if any(
        palabra in texto
        for palabra in [
            "gano",
            "ingreso",
            "salario",
            "me pagan",
            "mi pago",
            "mi salario",
            "mi ingreso",
            "es de",
            "ingresos",
            "dolares",
            "pesos",
            "euros",
            "salario de"
        ]
    ):
        numeros = re.findall(r"\d+", texto)
        if numeros:
            ingresos = int(numeros[0])
            datos_usuario["ingresos"] = ingresos
            res = verificar_credito()
            if res:
                return res
            return {
                "respuesta": f"Tus ingresos son de {ingresos}, ¿que eres, independiente, pensionado, soltero o casado?",
                "accion": "REGISTRAR_INGRESOS",
            }

    # Ocupación
    ocupaciones_claves = {
        "independiente": ["independiente", "soy independiente", "estoy independiente"],
        "pensionado": ["pensionado", "soy pensionado", "estoy pensionado"],
        "soltero": ["soltero", "soy soltero", "estoy soltero"],
        "casado": ["casado", "soy casado", "estoy casado", "casada"],
    }

    ocupacion_encontrada = None
    for ocupacion, claves in ocupaciones_claves.items():
        if any(clave in texto for clave in claves):
            ocupacion_encontrada = ocupacion
            break

    if ocupacion_encontrada:
        datos_usuario["ocupacion"] = ocupacion_encontrada
        res = verificar_credito()
        if res:
            return res
        return {
            "respuesta": "¿cuanto tiempo llevas laborando en meses?",
            "accion": "REGISTRAR_OCUPACION",
        }

    # Tiempo laborado
    if "meses" in texto:
        tiempo = int("".join([c for c in texto if c.isdigit()]))
        datos_usuario["tiempo_laborado"] = tiempo
        res = verificar_credito()
        if res:
            return res
        return {
            "respuesta": f"llevas en tu labor {tiempo} meses. Gracias por la información, estamos procesando tu solicitud de crédito.",
            "accion": "REGISTRAR_TIEMPO",
        }

    # Respuesta por defecto
    return {
        "respuesta": respuesta or "No entendí eso, ¿puedes repetirlo?",
        "accion": None,
    }


# ---- NUEVO ENDPOINT que usa tu componente UserDat ----
@app.post("/guardar_usuario")
async def guardar_usuario(usuario: UsuarioRegistro):
    """
    Endpoint usado por UserDat.jsx.
    Actualiza datos_usuario con lo enviado desde el formulario y
    dispara verificación si los datos ya están completos.
    """
    # Actualizar estado global (sin tocar carros_seleccionados ni ingresos si no vienen)
    datos_usuario["nombre"] = usuario.nombre
    datos_usuario["edad"] = usuario.edad
    datos_usuario["ocupacion"] = usuario.ocupacion
    datos_usuario["tiempo_laborado"] = usuario.tiempo_laborado

    # Debug en consola del servidor para ver los datos que llegan
    print("POST /guardar_usuario -> datos_usuario:", datos_usuario)

    # Intentar verificar crédito (si faltan ingresos, no se aprobará todavía)
    res = verificar_credito()
    if res:
        return res

    return {
        "respuesta": "Usuario guardado correctamente",
        "accion": "REGISTRAR_USUARIO",
    }


@app.get("/usuario")
def obtener_usuario():
    print("GET /usuario ->", datos_usuario)
    return datos_usuario


@app.get("/historial")
def ver_historial():
    return historial_aprobaciones
