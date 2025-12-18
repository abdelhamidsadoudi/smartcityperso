"""
Collecteur Complet Smart City
Collecte TOUS les polluants et indicateurs météo
Génération automatique d'alertes
"""

import requests
import json
import time
import sqlite3
from datetime import datetime
import urllib3
import random
import schedule

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ========================================
# CONFIGURATION
# ========================================
AQICN_KEY = "f2ead9da82c3b57265a4da4d6af31d876561e63c"
OPENWEATHER_KEY = "02f6cb60a87c770ec8554c34959b46ff"
CITY = "paris"
LAT = 48.8566
LON = 2.3522
DB_NAME = "smartcity.db"

INTERVAL_SECONDS= 1

# Seuils d'alerte pour TOUS les polluants (µg/m³)
THRESHOLDS = {
    'pm25': 50,    # PM2.5
    'pm10': 80,    # PM10
    'no2': 40,     # Dioxyde d'azote
    'o3': 120,     # Ozone
    'so2': 125,    # Dioxyde de soufre
    'co': 10000,   # Monoxyde de carbone
    'nh3': 200     # Ammoniac
}

print("=" * 70)
print("COLLECTEUR SMART CITY COMPLET")
print("=" * 70)
print(f"Ville : {CITY}")
print(f"Coordonnees : {LAT}, {LON}")
print("=" * 70)

# ========================================
# FONCTIONS DE COLLECTE
# ========================================

def collect_air_quality():
    """Collecte COMPLÈTE de la qualité de l'air avec TOUS les polluants"""
    try:
        url = f"https://api.waqi.info/feed/{CITY}/?token={AQICN_KEY}"
        response = requests.get(url, timeout=10, verify=False)
        
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'ok':
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                
                station = data['data']
                iaqi = station.get('iaqi', {})
                
                # Récupérer TOUS les polluants
                pm25 = iaqi.get('pm25', {}).get('v')
                pm10 = iaqi.get('pm10', {}).get('v')
                no2 = iaqi.get('no2', {}).get('v')
                o3 = iaqi.get('o3', {}).get('v')
                so2 = iaqi.get('so2', {}).get('v')
                co = iaqi.get('co', {}).get('v')
                nh3 = iaqi.get('nh3', {}).get('v')
                aqi = station['aqi']
                
                # Insérer dans la base
                cursor.execute('''
                    INSERT INTO air_quality 
                    (city, aqi, pm25, pm10, no2, o3, so2, co, nh3, station_name, raw_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    station['city']['name'], 
                    aqi,
                    pm25, pm10, no2, o3, so2, co, nh3,
                    station['city']['name'], 
                    json.dumps(data)
                ))
                
                conn.commit()
                
                # Créer des alertes pour chaque polluant
                pollutants_dict = {
                    'pm25': pm25,
                    'pm10': pm10,
                    'no2': no2,
                    'o3': o3,
                    'so2': so2,
                    'co': co,
                    'nh3': nh3
                }
                
                check_and_create_alerts(cursor, pollutants_dict, 'Zone Industrielle')
                
                conn.commit()
                conn.close()
                
                # Afficher les polluants récupérés
                print(f"  Polluants collectes:")
                if pm25: print(f"     - PM2.5: {pm25} ug/m3")
                if pm10: print(f"     - PM10: {pm10} ug/m3")
                if no2: print(f"     - NO2: {no2} ug/m3")
                if o3: print(f"     - O3: {o3} ug/m3")
                if so2: print(f"     - SO2: {so2} ug/m3")
                if co: print(f"     - CO: {co} ug/m3")
                if nh3: print(f"     - NH3: {nh3} ug/m3")
                
                return True, aqi
    except Exception as e:
        print(f"  Erreur air quality: {str(e)}")
    return False, None

def collect_weather():
    """Collecte COMPLÈTE des données météo"""
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            'lat': LAT, 
            'lon': LON,
            'appid': OPENWEATHER_KEY,
            'units': 'metric', 
            'lang': 'fr'
        }
        response = requests.get(url, params=params, timeout=10, verify=False)
        
        if response.status_code == 200:
            data = response.json()
            
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            
            # Récupérer TOUTES les données météo
            temperature = data['main']['temp']
            feels_like = data['main'].get('feels_like')
            temp_min = data['main'].get('temp_min')
            temp_max = data['main'].get('temp_max')
            humidity = data['main']['humidity']
            pressure = data['main']['pressure']
            wind_speed = data['wind']['speed']
            wind_direction = data['wind'].get('deg', 0)
            clouds = data.get('clouds', {}).get('all', 0)
            visibility = data.get('visibility', 0)
            weather_main = data['weather'][0]['main']
            weather_description = data['weather'][0]['description']
            
            cursor.execute('''
                INSERT INTO weather 
                (city, temperature, feels_like, temp_min, temp_max, humidity,
                 pressure, wind_speed, wind_direction, clouds, visibility,
                 weather_main, weather_description, raw_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['name'], 
                temperature, 
                feels_like,
                temp_min, 
                temp_max,
                humidity, 
                pressure,
                wind_speed, 
                wind_direction,
                clouds, 
                visibility,
                weather_main, 
                weather_description,
                json.dumps(data)
            ))
            
            conn.commit()
            conn.close()
            
            # Afficher les données météo
            print(f"  Meteo collectee:")
            print(f"     - Temperature: {temperature}C (ressenti: {feels_like}C)")
            print(f"     - Humidite: {humidity}%")
            print(f"     - Pression: {pressure} hPa")
            print(f"     - Vent: {wind_speed} m/s, direction: {wind_direction}")
            print(f"     - Nuages: {clouds}%")
            print(f"     - Visibilite: {visibility}m")
            print(f"     - Conditions: {weather_description}")
            
            return True, temperature
    except Exception as e:
        print(f"  Erreur meteo: {str(e)}")
    return False, None

def simulate_iot():
    """Simule les capteurs IoT avec TOUS les polluants"""
    sensors = [
        ("SENSOR_01", "Centre-ville", 48.8566, 2.3522),
        ("SENSOR_02", "Nord Paris", 48.8606, 2.3376),
        ("SENSOR_03", "Est Paris", 48.8449, 2.3735)
    ]
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    count = 0
    for sensor_id, location, lat, lon in sensors:
        try:
            # Simuler tous les polluants
            pm25 = round(random.uniform(5, 75), 1)
            pm10 = round(pm25 * random.uniform(1.3, 1.8), 1)
            no2 = round(random.uniform(10, 60), 1)
            o3 = round(random.uniform(20, 150), 1)
            so2 = round(random.uniform(5, 140), 1)
            co = round(random.uniform(100, 15000), 1)
            temp = round(random.uniform(10, 28), 1)
            humidity = round(random.uniform(35, 85), 1)
            
            cursor.execute('''
                INSERT INTO iot_sensors 
                (sensor_id, location_name, location_lat, location_lon,
                 pm25, pm10, no2, o3, so2, co, temperature, humidity)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (sensor_id, location, lat, lon, pm25, pm10, no2, o3, so2, co, temp, humidity))
            count += 1
        except Exception as e:
            print(f"  Erreur capteur {sensor_id}: {str(e)}")
            pass
    
    conn.commit()
    conn.close()
    return count

def check_and_create_alerts(cursor, pollutants, zone):
    """Vérifier TOUS les seuils et créer des alertes"""
    zones_populations = {
        'Zone Industrielle': 15000,
        'Centre-ville': 25000,
        'Résidentiel Nord': 12000
    }
    
    pollutant_names = {
        'pm25': 'PM2.5',
        'pm10': 'PM10',
        'no2': 'NO2 (Dioxyde d\'azote)',
        'o3': 'O3 (Ozone)',
        'so2': 'SO2 (Dioxyde de soufre)',
        'co': 'CO (Monoxyde de carbone)',
        'nh3': 'NH3 (Ammoniac)'
    }
    
    for pollutant, value in pollutants.items():
        if value is None:
            continue
            
        threshold = THRESHOLDS.get(pollutant)
        if threshold is None:
            continue
        
        pollutant_name = pollutant_names.get(pollutant, pollutant.upper())
        
        # Déterminer le niveau d'alerte
        if value >= threshold * 1.5:
            level = 'Alerte'
            message = f"Niveau {pollutant_name} très élevé: {value}µg/m³ (seuil: {threshold}µg/m³). Mesures d'urgence recommandées."
        elif value >= threshold:
            level = 'Important'
            message = f"Niveau {pollutant_name} élevé: {value}µg/m³ (seuil: {threshold}µg/m³). Évitez les activités physiques intenses à l'extérieur."
        elif value >= threshold * 0.8:
            level = 'Modéré'
            message = f"Niveau {pollutant_name} proche du seuil: {value}µg/m³ (seuil: {threshold}µg/m³). Surveillance accrue recommandée."
        else:
            continue
        
        # Créer l'alerte
        cursor.execute('''
            INSERT INTO alerts (type, zone, level, message, value, threshold, population)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            pollutant_name,
            zone,
            level,
            message,
            value,
            threshold,
            zones_populations.get(zone, 10000)
        ))

def create_prediction_alert():
    """Créer une alerte de prédiction météo"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    if random.random() > 0.7:
        cursor.execute('''
            INSERT INTO alerts (type, zone, level, message, value, threshold, population)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            'Prédiction',
            'Pic de pollution probable',
            'Important',
            'Conditions météorologiques défavorables. Pic de pollution attendu dans les 6 prochaines heures.',
            None,
            None,
            None
        ))
        conn.commit()
    
    conn.close()

def collect_once():
    """Lance une collecte COMPLETE"""
    now = datetime.now().strftime('%H:%M:%S')
    print(f"\n[{now}] Collecte en cours...")
    print("=" * 70)
    
    # 1. Qualité de l'air
    air_ok, aqi = collect_air_quality()
    if air_ok:
        print(f"  Air quality - AQI: {aqi}")
    
    time.sleep(2)
    
    # 2. Météo
    weather_ok, temp = collect_weather()
    if weather_ok:
        print(f"  Meteo complete collectee")
    
    time.sleep(2)
    
    # 3. Capteurs IoT
    iot_count = simulate_iot()
    print(f"  IoT - {iot_count} capteurs simules avec tous les polluants")
    
    # 4. Alertes prédiction
    create_prediction_alert()
    
    # Statistiques
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM air_quality')
    total_air = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM weather')
    total_weather = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM alerts WHERE status = "active"')
    total_alerts = cursor.fetchone()[0]
    conn.close()
    
    print("=" * 70)
    print(f"  TOTAL EN BASE:")
    print(f"     - Air quality: {total_air} enregistrements")
    print(f"     - Meteo: {total_weather} enregistrements")
    print(f"     - Alertes actives: {total_alerts}")
    print("=" * 70)

# ========================================
# PROGRAMME PRINCIPAL
# ========================================

def main():
    print("\nCollecteur pret a demarrer")
    print("Collecte complete de :")
    print("   - Qualite de l'air : PM2.5, PM10, NO2, O3, SO2, CO, NH3")
    print("   - Meteo : Temp, Humidite, Vent, Pression, Visibilite, Nuages")
    print("   - Capteurs IoT : 3 zones simulees")
    print("   - Alertes : Generation automatique\n")

    # Premiere collecte
    print("Premiere collecte immediate...")
    collect_once()
    
    # Programmer les collectes
    schedule.every(INTERVAL_SECONDS).seconds.do(collect_once)
    
    print(f"\nCollecte automatique programmee toutes les {INTERVAL_SECONDS} seconde(s)")
    print("Le dashboard se mettra a jour automatiquement")
    print("Appuyez sur Ctrl+C pour arreter\n")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n\n⛔ Collecteur arrêté")
        print("👋 Au revoir !")

if __name__ == "__main__":
    main()