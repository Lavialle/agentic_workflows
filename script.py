import os

import truststore

# Utilise le magasin de certificats Windows (proxy / antivirus qui inspecte le HTTPS)
truststore.inject_into_ssl()

from google.cloud import aiplatform, storage

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
GCP_REGION = os.getenv("GCP_REGION")
GCP_BUCKET_NAME = os.getenv("GCP_BUCKET_NAME")

missing = [
    name
    for name, value in {
        "GCP_PROJECT_ID": GCP_PROJECT_ID,
        "GCP_REGION": GCP_REGION,
        "GCP_BUCKET_NAME": GCP_BUCKET_NAME,
    }.items()
    if not value
]
if missing:
    raise SystemExit(f"Variables manquantes (lancer avec --env-file .env) : {', '.join(missing)}")


def test_vertex():
    print("=== Vertex AI ===")
    # aiplatform.init() configure le SDK globalement et renvoie None
    # Transport REST (et non gRPC) pour profiter des certificats système
    aiplatform.init(project=GCP_PROJECT_ID, location=GCP_REGION, api_transport="rest")
    try:
        # Appel réel à l'API pour vérifier les droits et l'activation de Vertex AI
        models = aiplatform.Model.list()
        print(f"OK - projet={GCP_PROJECT_ID}, région={GCP_REGION}, {len(models)} modèle(s) trouvé(s)")
    except Exception as e:
        print(f"ÉCHEC - {type(e).__name__}: {e}")


def test_storage():
    print("=== Cloud Storage ===")
    try:
        storage_client = storage.Client(project=GCP_PROJECT_ID)
        # get_bucket() interroge l'API, contrairement à bucket() qui ne fait aucun appel
        bucket = storage_client.get_bucket(GCP_BUCKET_NAME)
        print(f"OK - nom={bucket.name}")
        print(f"     location={bucket.location}")
        print(f"     créé le={bucket.time_created}")
    except Exception as e:
        print(f"ÉCHEC - {type(e).__name__}: {e}")


if __name__ == "__main__":
    test_vertex()
    test_storage()
