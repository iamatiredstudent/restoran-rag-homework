from app.retriever import Retriever


TOPK = 3
MINSCORE = 0.3

REFUSALEMPTYQUESTION = "Введите вопрос."
REFUSALNOCONTEXT = "В базе не найдено релевантных фрагментов. Ответить по данным невозможно."


def normalizehit(hit: dict) -> dict:
    """
    Приводит любой результат поиска к единому формату.
    Важно: в каждом source обязательно должен быть ключ docid.
    """

    doc_id = hit.get("doc_id")

    if doc_id is None:
        doc_id = hit.get("doc_id")

    if doc_id is None:
        doc_id = hit.get("id")

    if doc_id is None:
        doc_id = hit.get("chunk_id")

    if doc_id is None:
        doc_id = "unknown"

    try:
        score = float(hit.get("score", 0))
    except Exception:
        score = 0.0

    return {
        "doc_id": doc_id,
        "score": score,
        "name": hit.get("name", "Без названия"),
        "text": hit.get("text", ""),
    }


def filterhits(hits: list[dict]) -> list[dict]:
    """
    Оставляет только релевантные фрагменты.
    Для тестов важно не отрезать нормальные результаты mini-index.
    """

    result = []

    for hit in hits:
        item = normalizehit(hit)

        if item["score"] >= MINSCORE:
            result.append(item)

    return result


def buildanswer(hits: list[dict]) -> str:
    """
    Формирует ответ только на основании найденных фрагментов.
    """

    if not hits:
        return REFUSALNOCONTEXT

    parts = ["Ответ сформирован только на основании найденных фрагментов:"]

    for i, hit in enumerate(hits, 1):
        item = normalizehit(hit)

        parts.append("")
        parts.append(f"[{i}] {item['name']}")
        parts.append(f"doc_id={item['doc_id']}, score={item['score']:.2f}")
        parts.append(item["text"])

    return "\n".join(parts)


def formatsources(hits: list[dict]) -> list[dict]:
    """
    Возвращает список sources строго в формате, который ожидают тесты:
    каждый элемент обязан содержать doc_id.
    """

    sources = []

    for hit in hits:
        item = normalizehit(hit)

        sources.append(
            {
                "doc_id": item["doc_id"],
                "score": item["score"],
                "name": item["name"],
                "text": item["text"],
            }
        )

    return sources


def ask(question: str, k: int = TOPK, retriever: Retriever | None = None) -> dict:
    """
    Вопрос -> ответ и список источников.
    """

    question = question.strip()

    if not question:
        return {
            "answer": REFUSALEMPTYQUESTION,
            "sources": [],
        }

    r = retriever or Retriever()
    rawhits = r.search(question, k=k)

    relevanthits = filterhits(rawhits)

    if not relevanthits:
        return {
            "answer": REFUSALNOCONTEXT,
            "sources": [],
        }

    return {
        "answer": buildanswer(relevanthits),
        "sources": formatsources(relevanthits),
    }


# Совместимость со старыми названиями функций
buildanswer = buildanswer
formatsources = formatsources
filterrelevant_hits = filterhits
filterrelevanthits = filterhits