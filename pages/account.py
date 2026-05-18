import streamlit as st

st.set_page_config(page_title="내 계좌", layout="centered")

if "login_user" not in st.session_state:
    st.warning("로그인이 필요합니다.")
    st.stop()

st.title("📁 내 계좌")

st.write("유저:", st.session_state["login_user"])
st.write("이름:", st.session_state.get("user_name"))