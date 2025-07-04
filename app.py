import os
from flask import Flask, request, jsonify
import psycopg2
import requests

app = Flask(__name__)

FMCSA_API_KEY = os.environ.get("FMCSA_API_KEY")
proxies = {
    "http": "http://35.209.187.70:3128",
    "https": "http://35.209.187.70:3128"
}

# Se requerirá un API KEY para acceder a los endpoints que expone flask
def require_api_key(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('x-api-key')
        if api_key != os.environ.get("INTERNAL_API_KEY"):
            return jsonify({'error': 'Unauthorized access'}), 401
        return f(*args, **kwargs)
    return decorated

# Endpoint que valida si el MC number es efectivamente válido y sino devuelve un error
# Se requiere un API KEY para acceder a este endpoint
@app.route('/validate-mc', methods=['POST'])
@require_api_key
def validate_mc():
    data = request.json
    mc_number = data.get('mc_number')
    if not mc_number:
        return jsonify({'error': 'MC number is required'}), 400

    url = f"https://mobile.fmcsa.dot.gov/qc/services/carriers/docket-number/{mc_number}?webKey={FMCSA_API_KEY}"

    try:
        response = requests.get(url, timeout=10,proxies=proxies)
        if response.status_code != 200:
            return jsonify({'error': 'FMCSA API error', 'status': response.status_code}), 502

        result = response.json()
        # Se extraen los campos relevantes y si no se encuentra el carrier se devuelve un error
        content = result.get("content", [])
        if not content:
            return jsonify({'error': 'Carrier not found'}), 404

        carrier = content[0].get("carrier", {})
        allowed_to_operate = carrier.get("allowedToOperate")
        status_code = carrier.get("statusCode")
        legal_name = carrier.get("legalName")
        dot_number = carrier.get("dotNumber")

        # Lógica de validación del carrier
        is_valid = allowed_to_operate == "Y" and status_code == "A"

        return jsonify({
            "mc_number": mc_number,
            "dot_number": dot_number,
            "legal_name": legal_name,
            "allowed_to_operate": allowed_to_operate,
            "status_code": status_code,
            "is_valid": is_valid
        }), 200

    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

# Endpoint que devuelve todas las cargas de la base de datos en formato JSON
@app.route('/loads', methods=['GET'])
@require_api_key
def get_loads():
    try:
        conn = psycopg2.connect(
            dbname=os.environ.get("POSTGRES_DB", "loads"),
            user=os.environ.get("POSTGRES_USER", "postgres"),
            password=os.environ.get("POSTGRES_PASSWORD"),
            host=os.environ.get("POSTGRES_HOST", "localhost"),
            port=os.environ.get("POSTGRES_PORT", 5432)
        )
        cur = conn.cursor()
        cur.execute("""
            SELECT load_id, origin, destination, pickup_datetime, delivery_datetime,
                   equipment_type, loadboard_rate, notes, weight, commodity_type,
                   num_of_pieces, miles, dimensions
            FROM loads
        """)
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        loads = []
        for row in rows:
            data = dict(zip(columns, row))
            # Transformación de los datos siguiendo el ejemplo del API Get Loads V1 eliminando los datos de contacto
            load = {
                "reference_number": f"{data['load_id']}",
                "stops": [
                    {
                        "type": "Pick",
                        "location": {
                            "city": data["origin"].split(",")[0].strip(),
                            "state": data["origin"].split(",")[1].strip() if "," in data["origin"] else "",
                            "country": "USA"
                        },
                        "pickup_datetime": data["pickup_datetime"].isoformat() + "Z",
                    },
                    {
                        "type": "Drop",
                        "location": {
                            "city": data["destination"].split(",")[0].strip(),
                            "state": data["destination"].split(",")[1].strip() if "," in data["destination"] else "",
                            "country": "USA"
                        },
                        "delivery_datetime": data["delivery_datetime"].isoformat() + "Z",

                    }
                ],
                "equipment_type": {
                    "name": data["equipment_type"]
                },
                "max_buy": float(data["loadboard_rate"]) if data["loadboard_rate"] else 0.0,
                "status": "Available",
                "is_partial": False,
                "weight": float(data["weight"]) if data["weight"] else 0.0,
                "number_of_pieces": int(data["num_of_pieces"]) if data["num_of_pieces"] else 0,
                "commodity_type": data["commodity_type"],
                "sale_notes": data["notes"] or "",
                "dimensions": data["dimensions"],
                "miles": int(data["miles"]) if data["miles"] else 0
            }
            loads.append(load)
        cur.close()
        conn.close()
        return jsonify({"status": 200, "loads": loads}), 200
    except Exception as e:
        return jsonify({'status': 500, 'error': 'Database error', 'details': str(e)}), 500

@app.route('/loads/<int:load_id>', methods=['GET'])
@require_api_key
def get_load_by_id(load_id):
    try:
        conn = psycopg2.connect(
            dbname=os.environ.get("POSTGRES_DB", "loads"),
            user=os.environ.get("POSTGRES_USER", "postgres"),
            password=os.environ.get("POSTGRES_PASSWORD"),
            host=os.environ.get("POSTGRES_HOST", "localhost"),
            port=os.environ.get("POSTGRES_PORT", 5432)
        )
        cur = conn.cursor()
        cur.execute("""
            SELECT load_id, origin, destination, pickup_datetime, delivery_datetime,
                   equipment_type, loadboard_rate, notes, weight, commodity_type,
                   num_of_pieces, miles, dimensions
            FROM loads
            WHERE load_id = %s
        """, (load_id,))
        row = cur.fetchone()
        columns = [desc[0] for desc in cur.description]
        if not row:
            cur.close()
            conn.close()
            return jsonify({'status': 404, 'error': 'Load not found'}), 404

        data = dict(zip(columns, row))
        load = {
            "reference_number": f"{data['load_id']}",
            "stops": [
                {
                    "type": "Pick",
                    "location": {
                        "city": data["origin"].split(",")[0].strip(),
                        "state": data["origin"].split(",")[1].strip() if "," in data["origin"] else "",
                        "country": "USA"
                    },
                    "pickup_datetime": data["pickup_datetime"].isoformat() + "Z",
                },
                {
                    "type": "Drop",
                    "location": {
                        "city": data["destination"].split(",")[0].strip(),
                        "state": data["destination"].split(",")[1].strip() if "," in data["destination"] else "",
                        "country": "USA"
                    },
                    "delivery_datetime": data["delivery_datetime"].isoformat() + "Z",
                }
            ],
            "equipment_type": {
                "name": data["equipment_type"]
            },
            "max_buy": float(data["loadboard_rate"]) if data["loadboard_rate"] else 0.0,
            "status": "Available",
            "is_partial": False,
            "weight": float(data["weight"]) if data["weight"] else 0.0,
            "number_of_pieces": int(data["num_of_pieces"]) if data["num_of_pieces"] else 0,
            "commodity_type": data["commodity_type"],
            "sale_notes": data["notes"] or "",
            "dimensions": data["dimensions"],
            "miles": int(data["miles"]) if data["miles"] else 0
        }
        cur.close()
        conn.close()
        return jsonify({"status": 200, "load": load}), 200
    except Exception as e:
        return jsonify({'status': 500, 'error': 'Database error', 'details': str(e)}), 500

@app.route('/call_logs', methods=['POST'])
@require_api_key
def store_call_log():
    try:
        data = request.get_json()
        # Conversión y validación de tipos
        duration = int(data.get("duration", 0))
        agent_name = data.get("agent_name")
        negotiation_rounds = int(data.get("negotiation_rounds", 0))
        carrier_id = int(data.get("carrier_id")) if data.get("carrier_id") else None
        load_id = int(data.get("load_id")) if data.get("load_id") else None
        sale_closed = data.get("sale_closed") == "deal-closed"
        sentiment = data.get("sentiment")
        notes = data.get("notes", "")

        # Conexión a la base de datos
        conn = psycopg2.connect(
            dbname=os.environ.get("POSTGRES_DB", "carrier_sales"),
            user=os.environ.get("POSTGRES_USER", "postgres"),
            password=os.environ.get("POSTGRES_PASSWORD"),
            host=os.environ.get("POSTGRES_HOST", "localhost"),
            port=os.environ.get("POSTGRES_PORT", 5432)
        )
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO call_logs (
                duration, agent_name, negotiation_rounds, carrier_id, load_id,
                sale_closed, sentiment, notes
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING call_id
        """, (
            duration, agent_name, negotiation_rounds, carrier_id, load_id,
            sale_closed, sentiment, notes
        ))
        call_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": 201, "call_id": call_id}), 201
    except Exception as e:
        return jsonify({'status': 500, 'error': 'Database error', 'details': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
