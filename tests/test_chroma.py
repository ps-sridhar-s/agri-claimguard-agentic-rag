import traceback
import time

from langchain_chroma import Chroma
from langchain_core.documents import Document

from models.embeddings_models import embedding_client

print("=" * 80)
print("VECTOR STORE DIAGNOSTIC")
print("=" * 80)

###############################################################################
# TEST 1
###############################################################################

print("\n[TEST 1] Embedding Client")

try:
    print("Embedding Client Type :", type(embedding_client))
    print("Embedding Client      :", embedding_client)
    print("PASS")
except Exception:
    traceback.print_exc()

###############################################################################
# TEST 2
###############################################################################

print("\n[TEST 2] Embed Query")

try:

    start = time.time()

    emb = embedding_client.embed_query("Hello World")

    print("Embedding Length :", len(emb))

    print("Time :", round(time.time() - start, 2), "sec")

    print("PASS")

except Exception:
    traceback.print_exc()

###############################################################################
# TEST 3
###############################################################################

print("\n[TEST 3] Embed Documents")

try:

    docs = [
        "Rice crop damaged due to heavy rain.",
        "Crop insurance policy.",
        "Hybrid retrieval.",
    ]

    start = time.time()

    embeddings = embedding_client.embed_documents(docs)

    print("Returned :", len(embeddings))

    print("Time :", round(time.time() - start, 2), "sec")

    print("PASS")

except Exception:
    traceback.print_exc()

###############################################################################
# TEST 4
###############################################################################

print("\n[TEST 4] Create Chroma")

try:

    vectorstore = Chroma(
        collection_name="test_collection",
        persist_directory="./test_db",
        embedding_function=embedding_client,
    )

    print("PASS")

except Exception:
    traceback.print_exc()

###############################################################################
# TEST 5
###############################################################################

print("\n[TEST 5] Add One Text")

try:

    start = time.time()

    vectorstore.add_texts(
        [
            "Hello World"
        ]
    )

    print("Time :", round(time.time() - start, 2), "sec")

    print("PASS")

except Exception:
    traceback.print_exc()

###############################################################################
# TEST 6
###############################################################################

print("\n[TEST 6] Add One Document")

try:

    doc = Document(
        page_content="Rice crop damaged due to heavy rain.",
        metadata={
            "source": "unit-test"
        },
    )

    start = time.time()

    vectorstore.add_documents(
        [
            doc
        ]
    )

    print("Time :", round(time.time() - start, 2), "sec")

    print("PASS")

except Exception:
    traceback.print_exc()

###############################################################################
# TEST 7
###############################################################################

print("\n[TEST 7] Batch Insert")

try:

    documents = []

    for i in range(10):

        documents.append(
            Document(
                page_content=f"This is sample document {i}",
                metadata={
                    "id": i
                },
            )
        )

    start = time.time()

    vectorstore.add_documents(documents)

    print("Inserted :", len(documents))

    print("Time :", round(time.time() - start, 2), "sec")

    print("PASS")

except Exception:
    traceback.print_exc()

###############################################################################
# TEST 8
###############################################################################

print("\n[TEST 8] Similarity Search")

try:

    start = time.time()

    results = vectorstore.similarity_search(
        "Rice insurance",
        k=3,
    )

    print("Returned :", len(results))

    print("Time :", round(time.time() - start, 2), "sec")

    print("PASS")

except Exception:
    traceback.print_exc()

###############################################################################
# TEST 9
###############################################################################

print("\n[TEST 9] Large Batch")

try:

    docs = []

    for i in range(100):

        docs.append(
            Document(
                page_content=f"Insurance document {i}",
                metadata={
                    "doc": i
                },
            )
        )

    start = time.time()

    vectorstore.add_documents(docs)

    print("Inserted :", len(docs))

    print("Time :", round(time.time() - start, 2), "sec")

    print("PASS")

except Exception:
    traceback.print_exc()

print("\n" + "=" * 80)
print("ALL TESTS COMPLETED")
print("=" * 80)