from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
import uuid

app = Flask(__name__)
CORS(app)

# Configuration Qdrant
qdrant_client = QdrantClient(
    url="https://81903564-328b-4c9a-89fd-df5663026ba1.us-west-2-0.aws.cloud.qdrant.io:6333", 
    api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.lzGcVGsASpkVeDsuATefuvsktjEsKSvuUFfc0h4pFe0",
)

def add_movie(qdrant_client, movie_data):
    try:
        vector = [0.1] * 512

        payload = {
            "title": movie_data.get('title'),
            "director": movie_data.get('director', ''),
            "cast": movie_data.get('cast', []),
            "country": movie_data.get('country', ''),
            "date_added": movie_data.get('date_added', ''),
            "release_year": int(movie_data.get('release_year', 0)),
            "rating": movie_data.get('rating', ''),
            "duration": movie_data.get('duration', ''),
            "listed_in": movie_data.get('listed_in', ''),
            "description": movie_data.get('description', '')
        }
        
        # Créer le point
        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload=payload
        )
        
        # Insérer dans Qdrant
        qdrant_client.upsert(
            collection_name="netflix",
            points=[point]
        )
        
        print(f"Film '{movie_data['title']}' ajouté avec succès!")
        return point.id
        
    except Exception as e:
        print(f"Erreur lors de l'ajout: {e}")
        return None
    
def get_movie_by_id(qdrant_client, movie_id):
    try:
        result = qdrant_client.retrieve(
            collection_name="netflix",
            ids=[movie_id],
            with_payload=True
        )
        
        if result:
            movie = result[0]
            print(f"Film trouvé: {movie.payload['title']}")
            return movie.payload
        else:
            print("Film non trouvé")
            return None
            
    except Exception as e:
        print(f"Erreur lors de la récupération: {e}")
        return None

def search_movies_by_title(qdrant_client, title_search):
    from qdrant_client.models import Filter, FieldCondition, MatchText
    
    try:
        result = qdrant_client.scroll(
            collection_name="netflix",
            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key="title",
                        match=MatchText(text=title_search)
                    )
                ]
            ),
            limit=10,
            with_payload=True
        )
        
        movies = [point.payload for point in result[0]]
        print(f"Trouvé {len(movies)} film(s)")
        return movies
        
    except Exception as e:
        print(f"Erreur lors de la recherche: {e}")
        return []

def get_all_movies(qdrant_client, limit=100):
    try:
        result = qdrant_client.scroll(
            collection_name="netflix",
            limit=limit,
            with_payload=True
        )
        
        movies = [{"id": point.id, **point.payload} for point in result[0]]
        print(f"Récupéré {len(movies)} films")
        return movies
        
    except Exception as e:
        print(f"Erreur lors de la récupération: {e}")
        return []

def update_movie(qdrant_client, movie_id, updated_data):
    try:
        #récupérer le film existant
        existing = qdrant_client.retrieve(
            collection_name="netflix",
            ids=[movie_id],
            with_payload=True
        )
        
        if not existing:
            print("Film non trouvé")
            return False
        
        # fusionner les données existantes avec les nouvelles
        current_payload = existing[0].payload
        current_payload.update(updated_data)
        
        #mettre à jour le payload
        qdrant_client.set_payload(
            collection_name="netflix",
            payload=current_payload,
            points=[movie_id]
        )
        
        print(f"Film mis à jour avec succès!")
        return True
        
    except Exception as e:
        print(f"Erreur lors de la mise à jour: {e}")
        return False

def update_movie_field(qdrant_client, movie_id, field_name, field_value):
    try:
        qdrant_client.set_payload(
            collection_name="netflix",
            payload={field_name: field_value},
            points=[movie_id]
        )
        
        print(f"Champ '{field_name}' mis à jour avec succès!")
        return True
        
    except Exception as e:
        print(f"Erreur lors de la mise à jour: {e}")
        return False

def delete_movie(qdrant_client, movie_id):
    try:
        qdrant_client.delete(
            collection_name="netflix",
            points_selector=[movie_id]
        )
        
        print(f"Film supprimé avec succès!")
        return True
        
    except Exception as e:
        print(f"Erreur lors de la suppression: {e}")
        return False
    
@app.route('/movies', methods=['POST'])
def create_movie():
    """Créer un nouveau film"""
    try:
        movie_data = request.get_json()
        movie_id = add_movie(qdrant_client, movie_data)
        
        if movie_id:
            return jsonify({
                "status": "success",
                "message": "Film ajouté avec succès",
                "movie_id": movie_id
            }), 201
        else:
            return jsonify({
                "status": "error",
                "message": "Erreur lors de l'ajout du film"
            }), 400
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/movies', methods=['GET'])
def get_movies():
    """Récupérer tous les films ou rechercher par titre"""
    try:
        title_search = request.args.get('title')
        limit = int(request.args.get('limit', 100))
        
        if title_search:
            movies = search_movies_by_title(qdrant_client, title_search)
        else:
            movies = get_all_movies(qdrant_client, limit)
        
        return jsonify({
            "status": "success",
            "data": movies,
            "count": len(movies)
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/movies/<movie_id>', methods=['GET'])
def get_movie(movie_id):
    """Récupérer un film par ID"""
    try:
        movie = get_movie_by_id(qdrant_client, movie_id)
        
        if movie:
            return jsonify({
                "status": "success",
                "data": movie
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Film non trouvé"
            }), 404
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    
@app.route('/movies/<movie_id>', methods=['PATCH'])
def update_movie_endpoint(movie_id):
    """Mettre à jour un film"""
    try:
        updated_data = request.get_json()
        success = update_movie(qdrant_client, movie_id, updated_data)
        
        if success:
            return jsonify({
                "status": "success",
                "message": "Film mis à jour avec succès"
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Film non trouvé ou erreur de mise à jour"
            }), 404
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    
@app.route('/movies/<movie_id>', methods=['DELETE'])
def delete_movie_endpoint(movie_id):
    """Supprimer un film"""
    try:
        success = delete_movie(qdrant_client, movie_id)
        
        if success:
            return jsonify({
                "status": "success",
                "message": "Film supprimé avec succès"
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Film non trouvé ou erreur de suppression"
            }), 404
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)