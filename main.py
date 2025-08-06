from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fuzzywuzzy import process, fuzz

app = FastAPI()

# Permitir comunicación con el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    "hola": "¡Hola! ¿En qué puedo ayudarte?",
    "Hola, quiero comprar un carro": "¡Con gusto! ¿que color de carros quieres ver?",
    "quiero ver carros rojos": "ok, perfecto, ¿qué linea de carros quieres, sport, pickups o camioneta?, ¿qué color quieres, rojo, negro o plateado?.",
    "gracias": "Con gusto, ¿Qué color y linea  te interesa? Tenemos camionetas, sport y pickups de diferentes colores; rojo, negro y plateado.",
    "camioneta": "¿Qué color deseas para la camioneta?",
    "pickup": "¿Qué color deseas para el pickup?",
    "sport": "¿Qué color deseas para el carro sport?",
    # Variantes con artículos
    "quiero una camioneta roja": "Agregado: camioneta rojo",
    "quiero una camioneta negra": "Agregado: camioneta negro",
    "quiero una camioneta plateada": "Agregado: camioneta plateado",
    "quiero una pickup roja": "Agregado: pickup rojo",
    "quiero una pickup negra": "Agregado: pickup negro",
    "quiero una pickup plateada": "Agregado: pickup plateado",
    "quiero un sport rojo": "Agregado: sport rojo",
    "quiero un sport negro": "Agregado: sport negro",
    "quiero un sport plateado": "Agregado: sport plateado",
    # Variantes sin artículo
    "camioneta roja": "Agregado: camioneta rojo",
    "pickup negra": "Agregado: pickup negro",
    "sport plateado": "Agregado: sport plateado",
    # Nuevas variantes comunes
    "comprar pickup roja": "Agregado: pickup rojo",
    "una sport negra": "Agregado: sport negro",
    "deseo una camioneta plateada": "Agregado: camioneta plateado",
    "Aprubas credito de finaciamiento": "claro que si, ¿Cuál es tu nombre?",
    "tienes credito": "claro que si, ¿Cuál es tu nombre?",
    "Aprubas credito ": "claro que si, ¿Cuál es tu nombre?",
    "tienes finaciamiento": "claro que si, ¿Cuál es tu nombre?",
    "finacias": "claro que si, ¿Cuál es tu nombre?",
    "Mi nombre es": "¿Cuántos años tienes?", 
    "Me llamo luis": "¿Cuántos años tienes?",
    "tengo 30 años" : "¿Estado civi?", 
    "Mi edad es de 90 años" : "¿Estado civi?", 
    "Soy casado":"¿Cuánto es tu ingreso mensual?",
    "Estoy casado":"¿Cuánto es tu ingreso mensual?",
    "casado":"¿Cuánto es tu ingreso mensual?",
    "Soy independiente":"¿Cuánto es tu ingreso mensual?",
    "Estoy independiente":"¿Cuánto es tu ingreso mensual?",
    "independiente":"¿Cuánto es tu ingreso mensual?",
    "Soy pensionado":"¿Cuánto es tu ingreso mensual?",
    "Estoy pensionado":"¿Cuánto es tu ingreso mensual?",
    "pensionado":"¿Cuánto es tu ingreso mensual?",
    "gano 2000000": "¿Cuánto tiempo lleva laborando?",
    "yo gano 2000000": "¿Cuánto tiempo lleva laborando?",
    "es de 2000000": "¿Cuánto tiempo lleva laborando en meses?",
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

# 👤 Modelo de mensaje del usuario
class Mensaje(BaseModel):
    texto: str

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
            "respuesta": f"Agregado: {tipo_encontrado} {color_encontrado}",
            "accion": "AGREGAR_CARRO",
        }

    clave, respuesta = encontrar_intencion(texto)

    # Registro de nombre
    if "me llamo" in texto:
        nombre = texto.split("me llamo")[-1].strip().split(" ")[0]
        datos_usuario["nombre"] = nombre
        return {
            "respuesta": f"Nombre registrado: {nombre}",
            "accion": "REGISTRAR_NOMBRE",
        }

    # Edad
    if "tengo" in texto and "años" in texto:
        edad = int("".join([c for c in texto if c.isdigit()]))
        datos_usuario["edad"] = edad
        return {
            "respuesta": f"Edad registrada: {edad} años",
            "accion": "REGISTRAR_EDAD",
        }

    # Ingresos
    if "gano" in texto or "ingreso" in texto:
        ingresos = int("".join([c for c in texto if c.isdigit()]))
        datos_usuario["ingresos"] = ingresos
        return {
            "respuesta": f"Ingresos registrados: {ingresos}",
            "accion": "REGISTRAR_INGRESOS",
        }

    # Ocupación
    if "independiente" in texto:
        datos_usuario["ocupacion"] = "independiente"
        return {
            "respuesta": "Ocupación registrada: independiente",
            "accion": "REGISTRAR_OCUPACION",
        }

    if "pensionado" in texto:
        datos_usuario["ocupacion"] = "pensionado"
        return {
            "respuesta": "Ocupación registrada: pensionado",
            "accion": "REGISTRAR_OCUPACION",
        }

    # Tiempo laborado
    if "meses" in texto:
        tiempo = int("".join([c for c in texto if c.isdigit()]))
        datos_usuario["tiempo_laborado"] = tiempo

        # ✅ VERIFICACIÓN AUTOMÁTICA DE CRÉDITO
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

            # Guardar en historial (copia del usuario actual)
            historial_aprobaciones.append({
                "nombre": datos_usuario["nombre"],
                "edad": datos_usuario["edad"],
                "ingresos": datos_usuario["ingresos"],
                "ocupacion": datos_usuario["ocupacion"],
                "tiempo_laborado": datos_usuario["tiempo_laborado"],
                "resultado": respuesta_final,
            })

            # Reiniciar datos para nuevo usuario
            datos_usuario.clear()
            datos_usuario.update({
                "nombre": "",
                "edad": 0,
                "ingresos": 0,
                "ocupacion": "",
                "tiempo_laborado": 0,
                "carros_seleccionados": [],
            })

            return {
                "respuesta": respuesta_final,
                "accion": accion_final,
            }

        # Si aún no se puede verificar, solo registrar el tiempo
        return {
            "respuesta": f"Tiempo registrado: {tiempo} meses",
            "accion": "REGISTRAR_TIEMPO",
        }

    # Respuesta por defecto si no se entiende
    return {
        "respuesta": respuesta or "No entendí eso, ¿puedes repetirlo?",
        "accion": None,
    }

@app.get("/usuario")
def obtener_usuario():
    print(datos_usuario)
    return datos_usuario

@app.get("/historial")
def ver_historial():
    return historial_aprobaciones
