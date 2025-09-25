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