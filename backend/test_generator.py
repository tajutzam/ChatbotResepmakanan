from rag.retriever import search_relevant_recipes
from rag.generator import generate_menu_recommendation

if __name__ == "__main__":
    # Contoh input bahan makanan dari pengguna
    bahan_user = "ayam, telur, dan wortel"
    periode = 3  # Rencana menu untuk 3 hari
    
    print(f"Mencari resep relevan di MongoDB Atlas untuk bahan: '{bahan_user}'...")
    resep_terpilih = search_relevant_recipes(bahan_user, top_k=5)
    
    print(f"Ditemukan {len(resep_terpilih)} resep relevan. Memproses dengan LLM Gemini...")
    
    # Memanggil generator LLM untuk membuat menu harian
    hasil_menu = generate_menu_recommendation(bahan_user, periode, resep_terpilih)
    
    print("\n" + "="*50)
    print("--- HASIL REKOMENDASI JADWAL MENU DARI RAG & LLM ---")
    print("="*50)
    print(hasil_menu)