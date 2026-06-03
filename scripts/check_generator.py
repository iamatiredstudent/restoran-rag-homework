"""Проверка demo-ответа (итерация 6)."""

from app.generator import ask


def show(label: str, question: str) -> None:
    print(f"\n--- {label}: «{question}» ---")
    result = ask(question)
    print(f"Ответ:\n{result['answer']}\n")
    print(f"Источников: {len(result['sources'])}")
    for i, src in enumerate(result["sources"], 1):
        print(f"  [{i}] doc_id={src['doc_id']}, score={src['score']:.4f}, name={src['name'][:50]}...")


if __name__ == "__main__":
    show("Есть контекст", "ипотека ставка Citibank")
    show("Нет контекста", "безработица переменные")
    show("Negative", "Как приготовить борщ?")
