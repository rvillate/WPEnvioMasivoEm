

import requests
import pandas as pd
import time
import os
import math

# Puebla 19.116114801615065, -97.77518029799691
# PUEBLA CENTRO_CALVARIO - 18.444887226656423, -97.39351647322451
# villa hermosa - 17.981896333759384, -92.94636959846176
API_KEY = "AIzaSyCIhCZo5ixHouH0c7hkLZ8Z6OBgmw8Bj7E"
CENTER_LAT = 17.981896333759384
CENTER_LNG = -92.94636959846176
SEARCH_RADIUS = 30000  # 100 km
STEP_RADIUS = 10000     # 10 km entre centros
OUTPUT_CSV = "restaurantes_google_maps.csv"

FIELDS = [
    'name', 'formatted_phone_number', 'international_phone_number',
    'website', 'url', 'business_status', 'formatted_address',
    'vicinity', 'opening_hours', 'types', 'geometry', 'rating',
    'user_ratings_total'
]

if os.path.exists(OUTPUT_CSV):
    df = pd.read_csv(OUTPUT_CSV)
    processed_ids = set(df['place_id'])
else:
    df = pd.DataFrame()
    processed_ids = set()

def nearby_search(lat, lng, radius, pagetoken=None):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "radius": radius,
        "type": "restaurant",
        "key": API_KEY
    }
    if pagetoken:
        params["pagetoken"] = pagetoken
    response = requests.get(url, params=params)
    return response.json()

def get_place_details(place_id):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": ",".join(FIELDS),
        "key": API_KEY
    }
    response = requests.get(url, params=params)
    return response.json()

def extraer_direccion(lat, lng):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "latlng": f"{lat},{lng}",
        "key": API_KEY
    }
    response = requests.get(url, params=params).json()
    componentes = {
        "ciudad": "",
        "zona": "",
        "pais": "",
        "departamento": ""
    }
    if "results" in response and len(response["results"]) > 0:
        for comp in response["results"][0]["address_components"]:
            if "locality" in comp["types"]:
                componentes["ciudad"] = comp["long_name"]
            elif "sublocality" in comp["types"] or "neighborhood" in comp["types"]:
                componentes["zona"] = comp["long_name"]
            elif "country" in comp["types"]:
                componentes["pais"] = comp["long_name"]
            elif "administrative_area_level_1" in comp["types"]:
                componentes["departamento"] = comp["long_name"]
    return componentes

def procesar_resultado(details, place_id):
    result = details.get("result", {})
    horario = result.get("opening_hours", {}).get("weekday_text", [])
    lat = result.get("geometry", {}).get("location", {}).get("lat")
    lng = result.get("geometry", {}).get("location", {}).get("lng")
    direccion_detallada = extraer_direccion(lat, lng)
    return {
        "place_id": place_id,
        "name": result.get("name"),
        "status": result.get("business_status"),
        "formatted_address": result.get("formatted_address"),
        "vicinity": result.get("vicinity"),
        "ciudad": direccion_detallada["ciudad"],
        "zona": direccion_detallada["zona"],
        "departamento": direccion_detallada["departamento"],
        "pais": direccion_detallada["pais"],
        "phone": result.get("formatted_phone_number"),
        "phone_internacional": result.get("international_phone_number"),
        "website": result.get("website"),
        "google_maps_url": result.get("url"),
        "lat": lat,
        "lng": lng,
        "rating": result.get("rating"),
        "user_ratings_total": result.get("user_ratings_total"),
        "types": ', '.join(result.get("types", [])),
        "horarios": '\n'.join(horario),
        "whatsapp": "",
        "correo": "",
        "menu": "",
        "categorias": "",
        "que_venden": ""
    }

def guardar_csv(dataframe):
    if not os.path.exists(OUTPUT_CSV):
        dataframe.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    else:
        dataframe.to_csv(OUTPUT_CSV, mode='a', header=False, index=False, encoding="utf-8-sig")

def generar_centros_en_cuadricula(lat_centro, lng_centro, radio_max_km, paso_km):
    centros = []
    grados_por_km_lat = 1 / 110.574
    grados_por_km_lng = 1 / (111.320 * math.cos(math.radians(lat_centro)))

    max_pasos = int(radio_max_km / paso_km)
    for i in range(-max_pasos, max_pasos + 1):
        for j in range(-max_pasos, max_pasos + 1):
            nueva_lat = lat_centro + i * paso_km * grados_por_km_lat
            nueva_lng = lng_centro + j * paso_km * grados_por_km_lng
            centros.append((nueva_lat, nueva_lng))
    return centros

def main():
    total_guardados = 0
    centros = generar_centros_en_cuadricula(CENTER_LAT, CENTER_LNG, SEARCH_RADIUS / 1000, STEP_RADIUS / 1000)

    for index, (lat, lng) in enumerate(centros):
        print(f"\n📍 Punto #{index + 1} buscando en lat: {lat:.6f}, lng: {lng:.6f}")
        pagetoken = None
        pagina = 0
        while True:
            data = nearby_search(lat, lng, STEP_RADIUS, pagetoken)
            if data.get("status") != "OK":
                print(f"⚠️  Error: {data.get('status')} - {data.get('error_message', '')}")
                break

            results = data.get("results", [])
            print(f"📦 Página {pagina + 1}: {len(results)} resultados")

            for place in results:
                place_id = place.get("place_id")
                if place_id in processed_ids:
                    continue
                try:
                    details = get_place_details(place_id)
                    registro = procesar_resultado(details, place_id)
                    df_registro = pd.DataFrame([registro])
                    guardar_csv(df_registro)
                    processed_ids.add(place_id)
                    total_guardados += 1
                    print(f"✅ Guardado: {registro['name']} ({registro['ciudad']}, {registro['zona']})")
                except Exception as e:
                    print(f"❌ Error procesando {place_id}: {e}")
                time.sleep(1.5)

            pagetoken = data.get("next_page_token")
            if not pagetoken:
                break
            time.sleep(3)
            pagina += 1

    print(f"\n🏁 Búsqueda terminada. Total guardados: {total_guardados}")

if __name__ == "__main__":
    main()
