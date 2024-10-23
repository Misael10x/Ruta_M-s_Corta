from flask import Flask, request, jsonify, render_template
import math
import random

app = Flask(__name__)

# Define la función de distancia Haversine
def haversine(coord1, coord2):
    R = 6371.0  # Radio de la Tierra en kilómetros

    lat1 = math.radians(coord1[0])
    lon1 = math.radians(coord1[1])
    lat2 = math.radians(coord2[0])
    lon2 = math.radians(coord2[1])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance

# Evalúa la ruta utilizando Haversine
def evalua_ruta(ruta, coord):
    total = 0
    for i in range(len(ruta) - 1):
        ciudad1 = ruta[i]
        ciudad2 = ruta[i + 1]
        total += haversine(coord[ciudad1], coord[ciudad2])
    # Cierra el ciclo
    ciudad1 = ruta[-1]
    ciudad2 = ruta[0]
    total += haversine(coord[ciudad1], coord[ciudad2])
    return total

# Algoritmo de Simulated Annealing
def simulated_annealing(ruta, coord):
    T = 20
    T_MIN = 0
    V_enfriamiento = 100

    while T > T_MIN:
        dist_actual = evalua_ruta(ruta, coord)
        for _ in range(V_enfriamiento):
            # Intercambio aleatorio de dos ciudades
            i = random.randint(1, len(ruta) - 2)  # Excluye la primera y última ciudad
            j = random.randint(1, len(ruta) - 2)
            ruta_tmp = ruta[:]
            ciudad_tmp = ruta_tmp[i]
            ruta_tmp[i] = ruta_tmp[j]
            ruta_tmp[j] = ciudad_tmp
            dist = evalua_ruta(ruta_tmp, coord)
            delta = dist_actual - dist
            # Criterio de aceptación
            if dist < dist_actual:
                ruta = ruta_tmp[:]
                break
            elif random.random() < math.exp(delta / T):
                ruta = ruta_tmp[:]
                break
        T -= 0.005

    return ruta

# Define las coordenadas de las ciudades (una por cada estado de México)
coord = {
    'Aguascalientes': [21.87641043660486, -102.26438663286967],
    'BajaCalifornia': [32.5027, -117.00371],
    'BajaCaliforniaSur': [24.14437, -110.3005],
    'Campeche': [19.8301, -90.53491],
    'Chiapas': [16.75, -93.1167],
    'Chihuahua': [28.6353, -106.0889],
    'CDMX': [19.432713075976878, -99.13318344772986],
    'Coahuila': [25.4260, -101.0053],
    'Colima': [19.2452, -103.725],
    'Durango': [24.0277, -104.6532],
    'Guanajuato': [21.0190, -101.2574],
    'Guerrero': [17.5506, -99.5024],
    'Hidalgo': [20.1011, -98.7624],
    'Jalisco': [20.6767, -103.3475],
    'Mexico': [19.285, -99.5496],
    'Michoacan': [19.701400113725654, -101.20829680213464],
    'Morelos': [18.6813, -99.1013],
    'Nayarit': [21.5085, -104.895],
    'NuevoLeon': [25.6714, -100.309],
    'Oaxaca': [17.0732, -96.7266],
    'Puebla': [19.0414, -98.2063],
    'Queretaro': [20.5972, -100.387],
    'QuintanaRoo': [21.1631, -86.8023],
    'SanLuisPotosi': [22.1565, -100.9855],
    'Sinaloa': [24.8091, -107.394],
    'Sonora': [29.0729, -110.9559],
    'Tabasco': [17.9892, -92.9475],
    'Tamaulipas': [25.4348, -99.134],
    'Tlaxcala': [19.3181, -98.2375],
    'Veracruz': [19.1738, -96.1342],
    'Yucatan': [20.967, -89.6237],
    'Zacatecas': [22.7709, -102.5833]
}

@app.route('/')
def index():
    ciudades = list(coord.keys())
    return render_template('index.html', ciudades=ciudades)

@app.route('/get_routes', methods=['POST'])
def obtener_ruta():
    data = request.json
    ciudad_inicio = data['start']
    ciudad_final = data['end']
    
    if ciudad_inicio not in coord or ciudad_final not in coord:
        return jsonify({'error': 'Ciudad no encontrada'}), 404
    
    # Genera una ruta inicial aleatoria que empiece en ciudad_inicio y termine en ciudad_final
    ruta = list(coord.keys())
    ruta.remove(ciudad_inicio)
    ruta.remove(ciudad_final)
    random.shuffle(ruta)
    ruta = [ciudad_inicio] + ruta + [ciudad_final]

    # Ejecuta el algoritmo de Simulated Annealing
    mejor_ruta = simulated_annealing(ruta, coord)

    # Evalúa la distancia total del mejor recorrido
    distancia_total = evalua_ruta(mejor_ruta, coord)

    # Obtener coordenadas de las ciudades a lo largo de la ruta
    coordenadas_ruta = [coord[ciudad] for ciudad in mejor_ruta]

    return jsonify({
        'mejor_ruta': mejor_ruta,
        'distancia_total': distancia_total,
        'coordenadas_ruta': coordenadas_ruta
    })

if __name__ == '__main__':
    app.run(debug=True)
