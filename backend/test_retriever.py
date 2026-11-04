
from rag.retriever import search_relevant_recipes

query = "ayam, telur, dan wortel"

print(f"\nMencari resep untuk: {query}")

results = search_relevant_recipes(query, top_k=5)

print(f"\nJumlah resep ditemukan: {len(results)}")

for i, resep in enumerate(results, start=1):
    print(f"\n{i}. {resep.get('nama_resep')}")
    print(f"Bahan: {resep.get('bahan_lengkap')}")
    print(f"Skor: {resep.get('score')}")

if not results:
    print("\nTidak ada hasil dari Vector Search.")
