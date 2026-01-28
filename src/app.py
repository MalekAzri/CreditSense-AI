from flask import Flask, render_template, request, jsonify
from credit_scoring_qdrant import CreditScoringWithQdrant
import json
import os

# Obtenir le chemin vers la racine du projet
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

app = Flask(__name__,
            template_folder=os.path.join(base_dir, 'templates'),
            static_folder=os.path.join(base_dir, 'static'))

# Initialiser le système
system = CreditScoringWithQdrant(qdrant_url="http://localhost:6333")

@app.route('/')
def index():
    """Page d'accueil"""
    return render_template('index.html')

@app.route('/api/score', methods=['POST'])
def calculate_score():
    """Calcule le score d'un nouveau client"""
    try:
        raw_data = request.json['client_data']
        client_id = request.json.get('client_id', 9999)
        
        # Mappage des noms du formulaire vers les noms attendus par le modèle
        mapping = {
            'amount': 'credit_amount',
            'present_emp_since': 'employment',
            'guarantors': 'other_debtors',
            'other_plans': 'other_installments',
            'num_credits': 'existing_credits',
            'num_dependents': 'people_liable'
        }
        
        # Liste des colonnes numériques
        numeric_cols = [
            'duration', 'credit_amount', 'installment_rate', 
            'residence_since', 'age', 'existing_credits', 'people_liable'
        ]
        
        client_data = {}
        for key, value in raw_data.items():
            mapped_key = mapping.get(key, key)
            
            # Conversion forcée en numérique si nécessaire
            if mapped_key in numeric_cols:
                try:
                    client_data[mapped_key] = int(value)
                except (ValueError, TypeError):
                    client_data[mapped_key] = value
            else:
                client_data[mapped_key] = value
            
        result = system.process_new_client(client_id, client_data)
        
        return jsonify({
            'success': True,
            'score': result['score'],
            'decision': result['decision'],
            'proba_risque': result['proba_risque'],
            'similar_clients': [
                {
                    'id': r.id,
                    'similarity': r.score,
                    'score': r.payload['score'],
                    'decision': r.payload['decision']
                }
                for r in result['similar_clients']
            ]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/clients', methods=['GET'])
def list_clients():
    """Liste tous les clients"""
    try:
        points = system.client.scroll(
            collection_name=system.collection_name,
            limit=100
        )[0]
        
        clients = []
        for point in points:
            clients.append({
                'id': point.id,
                'score': point.payload['score'],
                'decision': point.payload['decision'],
                'proba_risque': point.payload['proba_risque']
            })
        
        return jsonify({'success': True, 'clients': clients})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Statistiques de la base"""
    try:
        info = system.client.get_collection(system.collection_name)
        
        return jsonify({
            'success': True,
            'total_clients': info.points_count,
            'vector_dimensions': info.config.params.vectors.size,
            'distance_metric': str(info.config.params.vectors.distance)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)