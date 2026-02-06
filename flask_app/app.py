from flask import Flask, render_template, request, jsonify
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Supabase Configuration
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY environment variables")

supabase: Client = create_client(url, key)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/records')
def records_page():
    return render_template('records.html')

@app.route('/kanban')
def kanban():
    return render_template('kanban.html')

@app.route('/team')
def team_page():
    return render_template('team.html')

@app.route('/reports')
def reports_page():
    return render_template('reports.html')

# --- API Endpoints ---

@app.route('/api/records', methods=['GET', 'POST'])
def api_records():
    if request.method == 'GET':
        # Select all records
        response = supabase.table('records').select("*").execute()
        records = response.data
        
        # Process JSON fields if necessary
        # Supabase returns JSON columns as dicts automatically if defined as JSON
        # If text, we might need parsing. Assuming TEXT in DB for 'attendant' based on old schema.
        # But if we create new table, better to use JSONB.
        # Check if 'attendant' needs parsing.
        
        for r in records:
            if isinstance(r.get('attendant'), str):
                try:
                    r['attendant'] = json.loads(r['attendant'])
                except:
                    r['attendant'] = [r['attendant']]
            elif not r.get('attendant'):
                r['attendant'] = []
                
        return jsonify(records)
    
    if request.method == 'POST':
        data = request.json
        # Convert attendant list to JSON string if basic text column, 
        # or keep as list if JSONB. Let's assume input is compatible.
        # The previous app stored it as JSON string.
        record_id = data.get('id')
        
        payload = {
            'attendant': data.get('attendant', []),  # Pass list directly for JSONB
            'secretary': data.get('secretary'),
            'date': data.get('date'),
            'endDate': data.get('endDate', ''),
            'status': data.get('status', 'Novo'),
            'task': data.get('task', '')
        }
        
        if record_id:
            payload['id'] = record_id
        
        # Check if exists (upsert logic)
        # supabase.table('records').upsert(payload).execute() is easiest
        try:
            supabase.table('records').upsert(payload).execute()
        except Exception as e:
            # If fail, returns error. 
            # Note: 'id' must be primary key for upsert to work.
            return jsonify({'status': 'error', 'message': str(e)}), 500
            
        return jsonify({'status': 'success'})

@app.route('/api/records/<int:id>', methods=['DELETE'])
def delete_record(id):
    try:
        supabase.table('records').delete().eq('id', id).execute()
        return jsonify({'status': 'deleted'})
    except Exception as e:
         return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/attendants', methods=['GET', 'POST'])
def api_attendants():
    if request.method == 'GET':
        response = supabase.table('attendants').select("name").order('name').execute()
        # Return list of names
        result = [r['name'] for r in response.data]
        return jsonify(result)
    
    if request.method == 'POST':
        name = request.json.get('name')
        if name:
            try:
                supabase.table('attendants').insert({'name': name}).execute()
            except Exception as e:
                # Ignore duplicate error (like INSERT OR IGNORE)
                print(f"Error adding attendant: {e}")
                pass
        return jsonify({'status': 'success'})

@app.route('/api/attendants/<name>', methods=['DELETE'])
def delete_attendant(name):
    try:
        supabase.table('attendants').delete().eq('name', name).execute()
        return jsonify({'status': 'deleted'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/secretaries', methods=['GET', 'POST'])
def api_secretaries():
    if request.method == 'GET':
        response = supabase.table('secretaries').select("name").order('name').execute()
        result = [r['name'] for r in response.data]
        return jsonify(result)
    
    if request.method == 'POST':
        name = request.json.get('name')
        if name:
            try:
                supabase.table('secretaries').insert({'name': name}).execute()
            except Exception as e:
                pass
        return jsonify({'status': 'success'})

@app.route('/api/secretaries/<name>', methods=['DELETE'])
def delete_secretary(name):
    try:
        supabase.table('secretaries').delete().eq('name', name).execute()
        return jsonify({'status': 'deleted'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

from datetime import datetime
from collections import Counter

@app.route('/api/reports/stats')
def api_reports_stats():
    try:
        # Fetch all records
        response = supabase.table('records').select("*").execute()
        records = response.data
        
        # Initialize aggregators
        daily_counts = Counter()
        status_counts = Counter()
        attendant_counts = Counter()
        
        for r in records:
            # Daily counts
            if r.get('date'):
                # Normalize date format if needed, assuming DD/MM/YYYY or YYYY-MM-DD
                # For simplicity, we just use the string as key for now
                daily_counts[r['date']] += 1
                
            # Status counts
            status = r.get('status', 'Indefinido')
            status_counts[status] += 1
            
            # Attendant counts
            attendant = r.get('attendant')
            if isinstance(attendant, str):
                try:
                    # Try to parse if it's a JSON string
                    attendant_list = json.loads(attendant)
                    if isinstance(attendant_list, list):
                        for a in attendant_list:
                            attendant_counts[a] += 1
                    else:
                        attendant_counts[str(attendant_list)] += 1
                except:
                    # If plain string (not JSON)
                    attendant_counts[attendant] += 1
            elif isinstance(attendant, list):
                for a in attendant:
                    attendant_counts[a] += 1
                    
        return jsonify({
            'daily_counts': dict(daily_counts),
            'status_counts': dict(status_counts),
            'team_performance': dict(attendant_counts.most_common(10)) # Top 10
        })
        
    except Exception as e:
        print(f"Error generating reports: {e}")
        return jsonify({'error': str(e)}), 500

# --- DTI Rooms Module ---

@app.route('/dti/rooms')
def dti_rooms_page():
    return render_template('dti_rooms.html')

@app.route('/api/dti/rooms', methods=['POST'])
def save_dti_rooms_data():
    try:
        data = request.json
        date = data.get('date')
        
        if not date:
            return jsonify({'error': 'Date is required'}), 400

        # Check if record exists for this date
        check = supabase.table('dti_room_status').select('id').eq('date', date).execute()
        
        payload_room = {
            'date': date,
            'updated_at': datetime.now().isoformat(),
            'datacenter_rodizio': data.get('datacenter_rodizio'),
            'datacenter_ar1_temp': data.get('datacenter_ar1_temp'),
            'datacenter_ar1_humidity': data.get('datacenter_ar1_humidity'),
            'datacenter_ar1_status': data.get('datacenter_ar1_status'),
            'datacenter_ar2_temp': data.get('datacenter_ar2_temp'),
            'datacenter_ar2_humidity': data.get('datacenter_ar2_humidity'),
            'datacenter_ar2_status': data.get('datacenter_ar2_status'),
            'datacenter_backup_status': data.get('datacenter_backup_status'),
            'datacenter_obs': data.get('datacenter_obs'),
            'electric_ac_status': data.get('electric_ac_status'),
            'electric_nobreak_shara1_status': data.get('electric_nobreak_shara1_status'),
            'electric_nobreak_shara2_status': data.get('electric_nobreak_shara2_status'),
            'electric_nobreak_shara3_status': data.get('electric_nobreak_shara3_status'),
            'electric_nobreak_apc1_status': data.get('electric_nobreak_apc1_status'),
            'electric_nobreak_apc2_status': data.get('electric_nobreak_apc2_status'),
            'electric_nobreak_apc3_status': data.get('electric_nobreak_apc3_status'),
            'electric_obs': data.get('electric_obs'),
            'telecom_ac1_status': data.get('telecom_ac1_status'),
            'telecom_ac2_status': data.get('telecom_ac2_status'),
            'telecom_obs': data.get('telecom_obs'),
            'general_report': data.get('general_report')
        }

        payload_generator = {
            'date': date,
            'updated_at': datetime.now().isoformat(),
            'generator_gdd': data.get('generator_gdd'),
            'generator_fuel_level': data.get('generator_fuel_level'),
            'generator_fuel_percent': data.get('generator_fuel_percent'),
            'generator_next_review': data.get('generator_next_review'),
            'generator_obs': data.get('generator_obs')
        }

        if check.data:
            # Update existing
            record_id = check.data[0]['id']
            supabase.table('dti_room_status').update(payload_room).eq('id', record_id).execute()
        else:
            # Insert new
            supabase.table('dti_room_status').insert(payload_room).execute()

        # Handle Generator Data
        check_gen = supabase.table('dti_generator_status').select('id').eq('date', date).execute()
        if check_gen.data:
            gen_id = check_gen.data[0]['id']
            supabase.table('dti_generator_status').update(payload_generator).eq('id', gen_id).execute()
        else:
            supabase.table('dti_generator_status').insert(payload_generator).execute()

        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error saving DTI room data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dti/rooms/latest', methods=['GET'])
def get_dti_rooms_data():
    try:
        date = request.args.get('date')
        if not date:
            # Default to today
            date = datetime.now().strftime('%Y-%m-%d')
            
        response = supabase.table('dti_room_status').select("*").eq('date', date).execute()
        
        if response.data:
            data = response.data[0]
            
            # Fetch generator data
            try:
                response_gen = supabase.table('dti_generator_status').select('*').eq('date', date).execute()
                if response_gen.data:
                    data.update(response_gen.data[0])
            except Exception as e:
                print(f"Error fetching generator data: {e}")
                
            return jsonify(data)
        else:
             return jsonify({'status': 'no_data'})
    except Exception as e:
        print(f"Error fetching DTI room data: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
