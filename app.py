import streamlit as st
from supabase import create_client
from datetime import datetime, timezone
import time

st.set_page_config(page_title="팀 도서 추천 투표", page_icon="📚", layout="centered")

supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

st.markdown("""
<style>
/* 전체 배경 다크 테마 고정 */
.stApp {
    background: radial-gradient(1000px 600px at 10% -10%, rgba(242,184,75,0.15), transparent 60%),
                radial-gradient(1000px 700px at 100% 0%, rgba(90,110,220,0.25), transparent 55%),
                linear-gradient(160deg, #120c26 0%, #1c2a52 100%);
    color: #f5f3ee;
}

h1, h2, h3, .stMarkdown p, label { 
    color: #f5f3ee !important; 
}

/* 카드 컨테이너 스타일 */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.14);
    border-radius: 20px;
    backdrop-filter: blur(18px);
    padding: 12px;
}

/* 모든 텍스트 입력창 글자색 & 배경색 강제 고정 */
input, textarea {
    background-color: #1e1b38 !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    caret-color: #f2b84b !important;
    border: 1px solid rgba(255,255,255,0.25) !important;
    border-radius: 10px !important;
}

/* 입력창 포커스 시 테두리 강조 */
input:focus, textarea:focus {
    border-color: #f2b84b !important;
    box-shadow: 0 0 0 1px #f2b84b !important;
}

/* 플레이스홀더(힌트 텍스트) 색상 */
input::placeholder, textarea::placeholder {
    color: #8b87a6 !important;
    -webkit-text-fill-color: #8b87a6 !important;
}

/* 투표 멀티셀렉트(드롭다운) 박스 스타일 */
div[data-baseweb="select"] {
    background-color: #1e1b38 !important;
    border-radius: 10px !important;
}

div[data-baseweb="select"] * {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

/* 선택된 태그(칩) 스타일 */
div[data-baseweb="tag"] {
    background-color: #383460 !important;
}

/* 버튼 스타일 */
.stButton > button {
    background-color: #f2b84b !important;
    color: #221703 !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    width: 100%;
}

.stButton > button:hover {
    background-color: #ffc966 !important;
    color: #000000 !important;
}

/* 상단 탭 스타일 */
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

st.session_state.user_name = st.text_input("이름", value=st.session_state.user_name, placeholder="예: 지수")
user_name = st.session_state.user_name.strip()

# 탭 3개로 선언 (추천하기, 투표하기, 결과 보기)
tab1, tab2, tab3 = st.tabs(["책 추천하기", "투표하기", "📊 투표 결과 보기"])

with tab1:
    with st.container(border=True):
        st.subheader("추천 도서 등록")
        st.caption("최소 3권, 최대 5권을 입력하세요.")

        titles = [st.text_input(f"책 제목 {i+1}", key=f"book_{i}", placeholder=f"책 제목 {i+1}") for i in range(5)]

        if st.button("등록하기"):
            filled = [t.strip() for t in titles if t.strip()]
            if not user_name:
                st.warning("이름을 입력해주세요.")
            elif len(filled) < 3:
                st.warning("책을 최소 3권 이상 입력해주세요.")
            else:
                with st.spinner("도서를 등록하는 중입니다..."):
                    rows = [
                        {
                            "user_name": user_name,
                            "book_title": t,
                            "created_at": datetime.now(timezone.utc).isoformat(),
                        }
                        for t in filled
                    ]
                    supabase.table("books").insert(rows).execute()
                
                st.balloons()
                st.success("🎉 추천 도서 등록이 성공적으로 완료되었습니다!")
                st.toast("추천 도서가 정상 저장되었습니다.", icon="✅")
                time.sleep(1.5)
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
                st.info("아직 투표할 책이 없습니다. (본인이 등록한 도서는 제외됩니다)")
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
                        with st.spinner("투표를 저장하는 중입니다..."):
                            rows = [
                                {"voter_name": user_name, "book_id": options[label]}
                                for label in selected
                            ]
                            supabase.table("votes").insert(rows).execute()
                        
                        st.balloons()
                        st.success("🎉 투표가 성공적으로 완료되었습니다!")
                        st.toast("투표 결과가 정상 집계되었습니다.", icon="🗳️")
                        time.sleep(1.5)
                        st.rerun()

with tab3:
    with st.container(border=True):
        st.subheader("📊 실시간 투표 집계 현황")
        
        all_books = supabase.table("books").select("id, book_title, user_name").execute().data
        all_votes = supabase.table("votes").select("book_id").execute().data

        if not all_books:
            st.info("등록된 도서가 없습니다.")
        else:
            vote_counts = {}
            for v in all_votes:
                b_id = v["book_id"]
                vote_counts[b_id] = vote_counts.get(b_id, 0) + 1

            results = []
            for b in all_books:
                results.append({
                    "책 제목": b["book_title"],
                    "추천자": b["user_name"],
                    "득표수": vote_counts.get(b["id"], 0)
                })
            
            # 득표수 높은 순 정렬
            results = sorted(results, key=lambda x: x["득표수"], reverse=True)
            st.dataframe(results, use_container_width=True, hide_index=True)
