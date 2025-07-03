import os
from flask import Flask, request, jsonify
import psycopg2
import requests

app = Flask(__name__)

FMCSA_API_KEY = os.environ.get("FMCSA_API_KEY")

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
        response = requests.get(url, timeout=10)
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
        # Conexión a la base de datos Postgres
        conn = psycopg2.connect(
            dbname=os.environ.get("POSTGRES_DB", "carrier_sales"),
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
        loads = [dict(zip(columns, row)) for row in rows]
        cur.close()
        conn.close()
        return jsonify(loads), 200
    except Exception as e:
        return jsonify({'error': 'Database error', 'details': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5055, ssl_context='adhoc',host='0.0.0.0')
