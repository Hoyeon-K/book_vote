import streamlit as st
from supabase import create_client
from datetime import datetime, timezone

st.set_page_config(page_title="팀 도서 추천 투표", page_icon="📚", layout="centered")

supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

st.markdown("""
<style>
.stApp {
    background: radial-gradient(1000px 600px at 10% -10%, rgba(242,184,75,0.15), transparent 60%),
                radial-gradient(1000px 700px at 100% 0%, rgba(90,110,220,0.25), transparent 55%),
                linear-gradient(160deg, #120c26 0%, #1c2a52 100%);
    color: #f5f3ee;
}
h1, h2, h3, .stMarkdown p { color: #f5f3ee !important; }
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.14);
    border-radius: 20px;
    backdrop-filter: blur(18px);
    padding: 8px;
}
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.18) !important;
    color: #f5f3ee !important;
    -webkit-text-fill-color: #f5f3ee !important;
    caret-color: #f5f3ee !important;
    border-radius: 12px !important;
}
div[data-testid="stTextInput"] input::placeholder {
    color: #8b87a6 !important;
    -webkit-text-fill-color: #8b87a6 !important;
}
div[data-baseweb="select"] > div {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.18) !important;
    border-radius: 12px !important;
}
div[data-baseweb="select"] * ,
div[data-baseweb="tag"] span {
    color: #f5f3ee !important;
    -webkit-text-fill-color: #f5f3ee !important;
}
.stButton > button {
    background: #f2b84b;
    color: #221703;
    border: none;
    border-radius: 12px;
    font-weight: 600;
}
.stTabs [data-baseweb="tab-list"] { gap: 8px; }
.stTabs [data-baseweb="tab"] {
    background: rgba(255,255,255,0.06);
    border-radius: 10px 10px 0 0;
    color: #c7c4de;
}
</style>
""", unsafe_allow_html=True)

st.title("📚 팀 도서 추천 투표")

if "user_name" not in st.session_state:
    st.session_state.user_name = ""

st.session_state.user_name = st.text_input("이름", value=st.session_state.user_name)
user_name = st.session_state.user_name.strip()

tab1, tab2 = st.tabs(["책 추천하기", "투표하기"])

with tab1:
    with st.container(border=True):
        st.subheader("추천 도서 등록")
        st.caption("최소 3권, 최대 5권을 입력하세요.")

        titles = [st.text_input(f"책 제목 {i+1}", key=f"book_{i}") for i in range(5)]

        if st.button("등록하기"):
            filled = [t.strip() for t in titles if t.strip()]
            if not user_name:
                st.warning("이름을 입력해주세요.")
            elif len(filled) < 3:
                st.warning("책을 최소 3권 이상 입력해주세요.")
            else:
                rows = [
                    {
                        "user_name": user_name,
                        "book_title": t,
                        "created_at": datetime.now(timezone.utc).isoformat(),
                    }
                    for t in filled
                ]
                supabase.table("books").insert(rows).execute()
                st.success("등록되었습니다!")
                st.rerun()

with tab2:
    with st.container(border=True):
        st.subheader("투표하기")

        if not user_name:
            st.warning("이름을 먼저 입력해주세요.")
        else:
            books = (
                supabase.table("books")
                .select("*")
                .neq("user_name", user_name)
                .execute()
                .data
            )

            if not books:
                st.info("아직 투표할 책이 없습니다.")
            else:
                options = {f'{b["book_title"]} — {b["user_name"]}': b["id"] for b in books}
                selected = st.multiselect(
                    "최대 3권까지 선택하세요.",
                    list(options.keys()),
                    max_selections=3,
                )

                if st.button("투표 제출"):
                    if not selected:
                        st.warning("최소 1권을 선택해주세요.")
                    else:
                        rows = [
                            {"voter_name": user_name, "book_id": options[label]}
                            for label in selected
                        ]
                        supabase.table("votes").insert(rows).execute()
                        st.success("투표가 완료되었습니다!")
