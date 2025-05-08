import re
import streamlit as st
import uuid
from backend.langgraph_.graph import make_graph
from backend.langgraph_.generator import generate

def run_generate_only(selected_table: str):
    # generate 함수 단독 실행
    state = {
        "selected_table": selected_table,
        "user_question": "",
        "user_question_eval": "",
    }
    return generate(state)


def main():
    st.header("DAQUV LLM 퓨샷 생성기")
    st.subheader("테이블 선택 후 유사 질문 생성")

    c1, c2 = st.columns(2)
    if c1.button("PRODUCT_WIP_MONTHLY"):
        st.session_state.selected_table = "PRODUCT_WIP_MONTHLY"
        st.session_state.pop("questions", None)
        st.session_state.pop("excluded_ids", None)
    if c2.button("RAW_MATERIAL_MONTHLY"):
        st.session_state.selected_table = "RAW_MATERIAL_MONTHLY"
        st.session_state.pop("questions", None)
        st.session_state.pop("excluded_ids", None)

    if "selected_table" in st.session_state:
        run_generate_ui(st.session_state.selected_table)


def run_generate_ui(selected_table: str):
    # 질문 초기화
    if "questions" not in st.session_state:
        result = run_generate_only(selected_table)
        raw = result.get("user_question_eval", "")
        st.session_state.questions = [
            {"id": str(uuid.uuid4()), "text": q.strip()}
            for q in raw.split("\n") if q.strip()
        ]
        st.session_state.excluded_ids = set()

    st.subheader(f"‘{selected_table}’ 질문 확인 및 선택")

    # 각 질문 렌더링
    for idx, item in enumerate(st.session_state.questions, start=1):
        cols = st.columns([20, 2], gap="small")
        q_id = item["id"]
        is_excl = q_id in st.session_state.excluded_ids

        with cols[0]:
            st.text_input(
                f"질문 {idx}",
                value=item["text"],
                key=f"{selected_table}_q_{q_id}",
                disabled=is_excl,
                label_visibility="collapsed"
            )
        with cols[1]:
            btn_label = "포함" if is_excl else "제외"
            if st.button(btn_label, key=f"{selected_table}_toggle_{q_id}"):
                if is_excl:
                    st.session_state.excluded_ids.remove(q_id)
                else:
                    st.session_state.excluded_ids.add(q_id)
                st.rerun()

    # Fewshot 생성 및 후속 실행
    spacer, btn_col = st.columns([7, 2])
    with btn_col:
        if st.button("퓨샷 생성", key=f"{selected_table}_proceed"):
            st.session_state.run_followup = True  # ✅ 상태 저장

    # ✅ 결과는 별도 전체 영역에서 출력
    if st.session_state.get("run_followup"):
        run_followup_graph(selected_table)


def run_followup_graph(selected_table: str):
    from backend.llm_models.types import GraphState

    final_qs = [
        st.session_state[f"{selected_table}_q_{q['id']}"]
        for q in st.session_state.questions
        if q["id"] not in st.session_state.excluded_ids
    ]

    if not final_qs:
        st.warning("선택된 질문이 없습니다.")
        return

    st.info("퓨샷 생성 진행 중...")

    for idx, question in enumerate(final_qs, start=1):
        # 번호가 앞에 붙은 경우 제거 (예: '1. 질문내용' → '질문내용')
        clean_question = re.sub(r'^\d+\.\s*', '', question)

        st.markdown(f"## 질문 {idx}: {clean_question}")
        graph = make_graph()
        state: GraphState = {
            "selected_table": selected_table,
            "user_question": clean_question,
            "user_question_eval": "",
        }
        result = graph.invoke(state)

        # 🧭 Commander
        st.markdown("### 🧭 Commander")
        st.json({
            "question": clean_question,
            "answer": selected_table
        })

        # 🧮 NL2SQL
        st.markdown("### 🧮 NL2SQL")
        st.json({
            "question": clean_question,
            "answer": result.get("nl2sql_answer", "")
        })

        # 💬 Respondent
        st.markdown("### 💬 Respondent")
        st.json({
            "question": clean_question,
            "answer": result.get("final_answer", "")
        })


if __name__ == "__main__":
    main()