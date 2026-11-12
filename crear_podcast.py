"""
Convierte un guion de dos voces en un podcast MP3 con voces neuronales en español colombiano.

Uso:
    pip install edge-tts
    python crear_podcast.py guion_podcast_field_service.txt podcast_field_service.mp3

Formato del guion: cada línea empieza con el nombre del locutor y dos puntos.
    SALOME: Hola, bienvenidos...
    GONZALO: Hola, Salomé...

Necesita conexión a internet (usa las voces gratuitas de Microsoft Edge).
"""
import asyncio
import sys
from pathlib import Path

import edge_tts

# Voces por locutor. Puedes cambiarlas; ver todas con:  edge-tts --list-voices | findstr es-
VOCES = {
    "SALOME": "es-CO-SalomeNeural",   # mujer, Colombia
    "GONZALO": "es-CO-GonzaloNeural",  # hombre, Colombia
}
VOZ_POR_DEFECTO = "es-CO-SalomeNeural"
VELOCIDAD = "+0%"   # por ejemplo "+10%" para más rápido o "-10%" para más lento


def leer_guion(ruta):
    lineas = []
    for linea in Path(ruta).read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea:
            continue
        if ":" in linea:
            locutor, texto = linea.split(":", 1)
            locutor = locutor.strip().upper()
            if locutor in VOCES:
                lineas.append((VOCES[locutor], texto.strip()))
                continue
        lineas.append((VOZ_POR_DEFECTO, linea))
    return lineas


async def sintetizar(voz, texto):
    audio = bytearray()
    comunicador = edge_tts.Communicate(texto, voz, rate=VELOCIDAD)
    async for parte in comunicador.stream():
        if parte["type"] == "audio":
            audio.extend(parte["data"])
    return bytes(audio)


async def main(entrada, salida):
    lineas = leer_guion(entrada)
    with open(salida, "wb") as archivo:
        for i, (voz, texto) in enumerate(lineas, 1):
            print(f"[{i}/{len(lineas)}] {voz}: {texto[:60]}...")
            archivo.write(await sintetizar(voz, texto))
    print(f"\nListo: {salida}")


if __name__ == "__main__":
    entrada = sys.argv[1] if len(sys.argv) > 1 else "guion_podcast_field_service.txt"
    salida = sys.argv[2] if len(sys.argv) > 2 else "podcast_field_service.mp3"
    asyncio.run(main(entrada, salida))
