from rag.generator import generate_recipe_reply
from rag.retriever import search_relevant_recipes


if __name__ == "__main__":
    message = "Aku punya ayam, telur, dan wortel. Buatkan rencana menu 3 hari."
    recipes = search_relevant_recipes(message, top_k=3)
    reply = generate_recipe_reply(message, [], recipes, is_weekly_plan=True)
    print(reply)
