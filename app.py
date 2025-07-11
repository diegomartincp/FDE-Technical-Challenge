import os
from flask import Flask, request, jsonify
import psycopg2
import requests
import time

app = Flask(__name__)

# Get the FMCSA API key from the env 
FMCSA_API_KEY = os.environ.get("FMCSA_API_KEY")
# DB connection from env
def get_conn():
    return psycopg2.connect(
        dbname=os.environ.get("POSTGRES_DB"),
        user=os.environ.get("POSTGRES_USER"),
        password=os.environ.get("POSTGRES_PASSWORD"),
        host=os.environ.get("POSTGRES_HOST"),
        port=os.environ.get("POSTGRES_PORT", 5432)
    )

# API key ir required to access all endpoints besides the healthcheck
def require_api_key(f):
    from functools import wraps
    @wraps(f)
    # Token is send as "Authorization: ApiKey xxxxxxxxxx"
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('ApiKey '):
            return jsonify({'error': 'Unauthorized access'}), 401
        api_key = auth_header.split(' ', 1)[1]
        if api_key != os.environ.get("INTERNAL_API_KEY"):
            return jsonify({'error': 'Unauthorized access'}), 401
        return f(*args, **kwargs)
    return decorated



# This endpoints validates the MC number using the FMCSA API and returns the carrier name if found
# This endpoint is protected by an API key, which is required to access it
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
        # Extract relevant data from the response
        content = result.get("content", [])
        # If the content is empty, the carrier was not found
        if not content:
            return jsonify({'error': 'Carrier not found'}), 404

        carrier = content[0].get("carrier", {})
        allowed_to_operate = carrier.get("allowedToOperate")
        status_code = carrier.get("statusCode")
        legal_name = carrier.get("legalName")
        dot_number = carrier.get("dotNumber")

        # Check if the carrier is valid based on the allowedToOperate and statusCode values
        is_valid = allowed_to_operate == "Y" and status_code == "A"

        #Return the result as JSON
        return jsonify({
            "mc_number": mc_number,
            "dot_number": dot_number,
            "legal_name": legal_name,
            "allowed_to_operate": allowed_to_operate,
            "status_code": status_code,
            "is_valid": is_valid
        }), 200

    except Exception as e:
        print("Error in /validate-mc:", e, flush=True)
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

# This endpoint returns all the loads in the database
# This endpoint is protected by an API key, which is required to access it
@app.route('/loads', methods=['GET'])
@require_api_key
def get_loads():
    try:
        conn = get_conn()
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
            # Transform data following the example of Get Loads V1, but removing contact data bacause of lack of data
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
        print("Error in /loads:", e, flush=True)
        return jsonify({'status': 500, 'error': 'Database error', 'details': str(e)}), 500

# This endpoint return a specific load by its ID
# The API key is required to access this endpoint
@app.route('/loads/<int:load_id>', methods=['GET'])
@require_api_key
def get_load_by_id(load_id):
    try:
        conn = get_conn()
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
        print("Error in /loads/id:", e, flush=True)
        return jsonify({'status': 500, 'error': 'Database error', 'details': str(e)}), 500

#This endpoint is used to send the call logs to the server and store them in the database.
# It returns the call log id if the call log is stored successfully.
# The endpoint requires an API key in the Authorization header with the format "ApiKey <api_key>".
# It expects a JSON payload with the following fields:
# - duration (int): The duration of the call in seconds.
# - agent_name (str): The name of the agent who handled the call.
# - negotiation_rounds (int): The number of negotiation rounds in the call.
# - carrier_id (int): The ID of the carrier who handled the call.
# - load_id (int): The ID of the load associated with the call.
# - sale_closed (bool): A flag indicating whether the sale was closed
@app.route('/call_logs', methods=['POST'])
@require_api_key
def store_call_log():
    try:
        data = request.get_json()
        print(data, flush=True)
        # Convert string values to appropriate types
        duration = int(data.get("duration", 0))
        agent_name = data.get("agent_name")
        negotiation_rounds = int(data.get("negotiation_rounds", 0))
        carrier_id = int(data.get("carrier_id")) if data.get("carrier_id") else None
        load_id = int(data.get("load_id")) if data.get("load_id") else None
        sale_closed = data.get("sale_closed") == "deal-closed"
        sentiment = data.get("sentiment")
        notes = data.get("notes", "")

        conn = get_conn()
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
        print("Error in /call_logs:", e, flush=True)
        return jsonify({'status': 500, 'error': 'Database error', 'details': str(e)}), 500

# Healthcheck endpoint to check the server's health.
@app.route("/")
def index():
    return "ok"

"""
# Enable for developement
if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
"""