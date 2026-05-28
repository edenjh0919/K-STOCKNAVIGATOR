import streamlit as st
from core.database import supabase

# ---------------------------------------------------
# 페이지 설정
# ---------------------------------------------------
st.set_page_config(
    page_title="K-STOCKNAVIGATOR",
    layout="wide"
)

# ---------------------------------------------------
# 로그인 사용자
# ---------------------------------------------------
login_user = st.session_state.get("login_user")

# ---------------------------------------------------
# CSS
# ---------------------------------------------------
st.markdown("""
<style>

.stock-card {
    background-color:#ffffff;
    border:1px solid #eef2f6;
    border-radius:20px;
    padding:24px;
    margin-bottom:20px;
    box-shadow:0 4px 12px rgba(0,0,0,0.04);
}

.stock-name {
    font-size:24px;
    font-weight:bold;
    color:#191f28;
}

.stock-code {
    font-size:13px;
    color:#8b95a1;
}

.price {
    font-size:28px;
    font-weight:bold;
    margin-top:10px;
}

.red {
    color:#f44336;
}

.blue {
    color:#1e88e5;
}

.gray {
    color:#999;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# 제목
# ---------------------------------------------------
st.title("📈 실시간 주식 거래")

st.markdown("---")

# ---------------------------------------------------
# 사용자 잔액 표시
# ---------------------------------------------------
if login_user:

    user_response = (
        supabase
        .table("users")
        .select("balance")
        .eq("id", login_user)
        .single()
        .execute()
    )

    user_data = user_response.data

    balance = user_data.get("balance") or 0

    st.metric(
        "💰 현재 잔액",
        f"{balance:,}원"
    )

    st.markdown("---")

# ---------------------------------------------------
# 주식 데이터 조회
# ---------------------------------------------------
response = (
    supabase
    .table("stocks")
    .select("*")
    .order("trade_value", desc=True)
    .limit(30)
    .execute()
)

stocks = response.data

# ---------------------------------------------------
# 주식 카드 출력
# ---------------------------------------------------
for row in stocks:

    stock_id = row.get("id")

    stock_name = row.get("stock_name")

    current_price = row.get("current_price") or 0

    change_rate = row.get("change_rate") or 0

    trade_value = row.get("trade_value") or 0

    # 등락률 색상
    if change_rate > 0:
        color_class = "red"
        sign = "+"
    elif change_rate < 0:
        color_class = "blue"
        sign = ""
    else:
        color_class = "gray"
        sign = ""

    # ---------------------------------------------------
    # 카드
    # ---------------------------------------------------
    with st.container(border=True):

        col1, col2 = st.columns([7, 3])

        # ---------------------------------------------------
        # 왼쪽 정보
        # ---------------------------------------------------
        with col1:

            st.markdown(f"""
            <div class="stock-name">
                {stock_name}
            </div>

            <div class="stock-code">
                {stock_id}
            </div>

            <div class="price">
                {current_price:,}원
            </div>

            <div class="{color_class}">
                {sign}{change_rate:.2f}%
            </div>
            """, unsafe_allow_html=True)

            st.caption(f"거래대금: {trade_value:,}원")

        # ---------------------------------------------------
        # 오른쪽 매수
        # ---------------------------------------------------
        with col2:

            if login_user is None:

                st.warning("로그인 필요")

                if st.button(
                    "로그인",
                    key=f"login_{stock_id}"
                ):
                    st.switch_page("pages/login.py")

            else:

                buy_qty = st.number_input(
                    "수량",
                    min_value=1,
                    step=1,
                    key=f"qty_{stock_id}"
                )

                total_price = current_price * buy_qty

                st.write(f"총 금액: {total_price:,}원")

                # 추천 포트폴리오에서 넘어온 값 자동 적용
                recommend_data = st.session_state.get("recommend_buy")

                if recommend_data:

                    for item in recommend_data:

                        if item["stock_id"] == stock_id:

                            buy_qty = item["qty"]

                            total_price = buy_qty * current_price

                            st.success(
                                f"추천 포트폴리오 적용됨: {buy_qty}주"
                            )

                # ---------------------------------------------------
                # 매수 버튼
                # ---------------------------------------------------
                if st.button(
                    "🛒 매수하기",
                    
                    key=f"buy_{stock_id}",
                    use_container_width=True
                ):
                    

                    # 사용자 잔액 조회
                    user_response = (
                        supabase
                        .table("users")
                        .select("balance")
                        .eq("id", login_user)
                        .single()
                        .execute()
                    )

                    user_data = user_response.data

                    current_balance = user_data.get("balance") or 0

                    # 잔액 부족
                    if current_balance < total_price:

                        st.error("잔액이 부족합니다.")

                    else:

                        # ---------------------------------------------------
                        # balance 차감
                        # ---------------------------------------------------
                        new_balance = current_balance - total_price

                        (
                            supabase
                            .table("users")
                            .update({
                                "balance": new_balance
                            })
                            .eq("id", login_user)
                            .execute()
                        )

                        # ---------------------------------------------------
                        # positions 확인
                        # ---------------------------------------------------
                        pos_response = (
                            supabase
                            .table("positions")
                            .select("*")
                            .eq("user_id", login_user)
                            .eq("stock_id", stock_id)
                            .execute()
                        )

                        existing = pos_response.data

                        # 기존 보유
                        if existing:

                            old_qty = existing[0]["quantity"]

                            old_avg = existing[0]["avg_price"]

                            new_qty = old_qty + buy_qty

                            new_avg = int(
                                (
                                    (old_qty * old_avg)
                                    + total_price
                                )
                                / new_qty
                            )

                            (
                                supabase
                                .table("positions")
                                .update({
                                    "quantity": new_qty,
                                    "avg_price": new_avg
                                })
                                .eq("id", existing[0]["id"])
                                .execute()
                            )

                        # 신규 보유
                        else:

                            (
                                supabase
                                .table("positions")
                                .insert({
                                    "user_id": login_user,
                                    "stock_id": stock_id,
                                    "stock_name": stock_name,
                                    "quantity": buy_qty,
                                    "avg_price": current_price
                                })
                                .execute()
                            )

                        # ---------------------------------------------------
                        # 거래 기록 저장
                        # ---------------------------------------------------
                        (
                            supabase
                            .table("trades")
                            .insert({
                                "user_id": login_user,
                                "stock_id": stock_id,
                                "stock_name": stock_name,
                                "quantity": buy_qty,
                                "price": current_price,
                                "trade_type": "BUY"
                            })
                            .execute()
                        )

                        st.success(
                            f"{stock_name} {buy_qty}주 매수 완료!"
                        )

                        # 추천 포트폴리오 초기화
                        if "recommend_buy" in st.session_state:
                            del st.session_state["recommend_buy"]

                        st.rerun()