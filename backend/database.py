from rag.vectorstore import get_mongo_collection
import numpy as np

# Menghubungkan ke collection MongoDB Atlas
collection = get_mongo_collection()

# Mengambil maksimal 5 resep yang memiliki embedding_vector
docs = list(
    collection.find(
        {"embedding_vector": {"$exists": True}},
        {
            "_id": 0,
            "nama_resep": 1,
            "dokumen_teks": 1,
            "embedding_vector": 1,
        },
    ).limit(5)
)

print("Jumlah resep yang diperiksa:", len(docs))

if len(docs) < 2:
    print("Data resep dengan embedding kurang dari 2.")

else:
    # 1. Memeriksa informasi setiap vektor
    for i, doc in enumerate(docs):
        vector = np.asarray(
            doc["embedding_vector"], dtype=np.float32
        )

        print(f"\nResep {i + 1}: {doc.get('nama_resep')}")
        print("Teks:", doc.get("dokumen_teks", "")[:120])
        print("Dimensi:", vector.shape)
        print("Norm:", np.linalg.norm(vector))
        print("5 nilai pertama:", vector[:5])

    # 2. Membandingkan vektor antar-resep
    print("\nPerbandingan antarvektor:")

    for i in range(len(docs)):
        for j in range(i + 1, len(docs)):
            a = np.asarray(
                docs[i]["embedding_vector"], dtype=np.float32
            )
            b = np.asarray(
                docs[j]["embedding_vector"], dtype=np.float32
            )

            # Memeriksa apakah kedua vektor identik
            identical = np.allclose(a, b)

            # Menghitung cosine similarity
            cosine = np.dot(a, b) / (
                np.linalg.norm(a) * np.linalg.norm(b) + 1e-12
            )

            print(
                f"{docs[i].get('nama_resep')} vs "
                f"{docs[j].get('nama_resep')}: "
                f"identik={identical}, cosine={cosine:.6f}"
            )
