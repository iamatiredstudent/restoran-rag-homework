"""Streamlit UI: вопрос -> фрагменты -> ответ -> источники."""

from pathlib import Path

import streamlit as st

from app.generator import ask
from app.retriever import Retriever


INDEXCHUNKSJSONL = Path("data/index/chunks.jsonl")
MATRIXNPZ = Path("data/index/matrix.npz")
VECTORIZERPKL = Path("data/index/vectorizer.pkl")

TOPK = 3
MINSCORE = 0.05


DEMOQUESTIONS = [
    "Как ресторану снизить списания скоропортящихся продуктов?",
    "Какие метрики нужно использовать для контроля закупок в ресторане?",
    "Зачем ресторану нужен ABC-анализ ингредиентов?",
    "Кто проживает на дне океана?",
]


def indexexists() -> bool:
    """Проверяет, собран ли индекс."""
    return (
        INDEXCHUNKSJSONL.exists()
        and MATRIXNPZ.exists()
        and VECTORIZERPKL.exists()
    )


@st.cache_resource
def loadretriever() -> Retriever:
    """Загружает retriever один раз."""
    return Retriever()


def safedocid(src: dict) -> str:
    """Безопасно достает docid из источника."""
    docid = src.get("docid")

    if docid is None:
        docid = src.get("docid")

    if docid is None:
        docid = src.get("id")

    if docid is None:
        docid = src.get("chunkid")

    if docid is None:
        docid = "unknown"

    return str(docid)


def safescore(src: dict) -> float:
    """Безопасно достает score."""
    try:
        return float(src.get("score", 0))
    except Exception:
        return 0.0


def renderchunk(i: int, src: dict, expanded: bool = True) -> None:
    """Показывает один найденный фрагмент."""
    docid = safedocid(src)
    score = safescore(src)
    name = src.get("name", "Без названия")
    text = src.get("text", "")

    label = f"[{i}] docid={docid} · score={score:.4f}"

    with st.expander(label, expanded=expanded):
        st.markdown(f"{name}")
        st.text(text)


def renderfragments(sources: list[dict]) -> None:
    """Показывает найденные фрагменты."""
    st.subheader("Найденные фрагменты (top-k)")

    if not sources:
        st.info("Фрагменты не найдены.")
        return

    for i, src in enumerate(sources, 1):
        score = safescore(src)
        renderchunk(i, src, expanded=score >= MINSCORE)


def rendersources(sources: list[dict]) -> None:
    """Показывает источники."""
    st.subheader("Источники")

    if not sources:
        st.info("Источники отсутствуют.")
        return

    for i, src in enumerate(sources, 1):
        renderchunk(i, src, expanded=False)


def main() -> None:
    st.set_page_config(page_title="RAG Tutorial", layout="wide")

    st.title("RAG Tutorial")
    st.caption("Учебный RAG: TF-IDF + demo-ответ с источниками")

    if not indexexists():
        st.error(
            "Индекс не собран. Сначала выполните:\n\n"
            "`uv run python scripts/buildindex.py`"
        )
        st.stop()

    st.sidebar.header("Demo-вопросы")

    for questiontext in DEMOQUESTIONS:
        if st.sidebar.button(questiontext, use_container_width=True):
            st.session_state["question"] = questiontext

    question = st.text_input("Ваш вопрос", key="question")

    if st.button("Спросить", type="primary"):
        if not question.strip():
            st.warning("Введите вопрос.")
            st.stop()

        with st.spinner("Поиск..."):
            result = ask(
                question.strip(),
                k=TOPK,
                retriever=loadretriever(),
            )

        sources = result.get("sources", [])
        answer = result.get("answer", "")

        renderfragments(sources)

        st.subheader("Ответ")
        st.text(answer)

        rendersources(sources)

if __name__ == "__main__":
    main()
