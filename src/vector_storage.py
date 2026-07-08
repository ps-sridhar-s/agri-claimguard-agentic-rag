from tqdm import tqdm

from pymilvus import MilvusClient

from models.embeddings_models import embedding_client


VECTOR_DIMENSION = 1024
DEFAULT_COLLECTION_NAME = "crop_insurance"


def create_vector_store(
    chunks,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    db_path: str = "./milvus.db",
    batch_size: int = 25,
    drop_old: bool = False,
):
    """
    Create Milvus Lite Vector Store
    """

    print("\nInitializing Milvus Lite...")

    client = MilvusClient(db_path)

    collections = client.list_collections()

    if drop_old and collection_name in collections:
        print("Dropping Existing Collection...")
        client.drop_collection(collection_name)

    collections = client.list_collections()

    if collection_name not in collections:

        print("Creating Collection...")

        client.create_collection(
            collection_name=collection_name,
            dimension=VECTOR_DIMENSION,
            auto_id=True,
        )

    print(f"\nCollection : {collection_name}")
    print(f"Documents  : {len(chunks)}")
    print(f"Batch Size : {batch_size}")

    total = len(chunks)

    for i in tqdm(
        range(0, total, batch_size),
        desc="Embedding Chunks",
        unit="batch",
    ):

        batch = chunks[i : i + batch_size]

        texts = [doc.page_content for doc in batch]
        metadatas = [doc.metadata for doc in batch]

        embeddings = embedding_client.embed_documents(texts)

        data = []

        for text, metadata, embedding in zip(
            texts,
            metadatas,
            embeddings,
        ):

            data.append(
                {
                    "text": text,
                    "metadata": metadata,
                    "vector": embedding,
                }
            )

        client.insert(
            collection_name=collection_name,
            data=data,
        )

    print("\n✅ Milvus Vector Store Created Successfully!")

    ensure_collection_loaded(client, collection_name)

    return client


def chunk_vector_store(chunks):
    return create_vector_store(chunks)


def get_vectorstore(
    db_path: str = "./milvus.db",
    collection_name: str = DEFAULT_COLLECTION_NAME,
):
    client = MilvusClient(db_path)
    ensure_collection_loaded(client, collection_name)
    return client


def ensure_collection_loaded(
    client,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    timeout: float = 30.0,
):
    if collection_name not in client.list_collections():
        raise ValueError(f"Milvus collection '{collection_name}' does not exist.")

    client.load_collection(collection_name, timeout=timeout)

    state = client.get_load_state(collection_name, timeout=timeout)
    state_value = state.get("state") if isinstance(state, dict) else state
    state_name = getattr(state_value, "name", str(state_value))

    if state_name.lower() != "loaded" and str(state_value) != "3":
        raise RuntimeError(
            f"Milvus collection '{collection_name}' did not load. Current state: {state}"
        )

    return client
