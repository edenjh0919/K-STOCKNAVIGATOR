import streamlit as st
from core.database import supabase

# ---------------------------------------------------
# 페이지 설정
# ---------------------------------------------------
st.set_page_config(
    page_title="내 계좌",
    layout="wide"
)

# ---------------------------------------------------
# 로그인 체크
# ---------------------------------------------------
if st.session_state.get("login_user") is None:

    st.warning("로그인이 필요한 서비스입니다.")

    if st.button("로그인 하러가기"):
        st.switch_page("pages/login.py")

    st.stop()

# ---------------------------------------------------
# 현재 로그인 사용자
# ---------------------------------------------------
login_id = st.session_state.get("login_user")

# ---------------------------------------------------
# 사용자 정보 조회
# ---------------------------------------------------
response = (
    supabase
    .table("users")
    .select("*")
    .eq("id", login_id)
    .single()
    .execute()
)

user_data = response.data

if not user_data:

    st.error("사용자 정보를 불러올 수 없습니다.")
    st.stop()

# ---------------------------------------------------
# 사용자 정보
# ---------------------------------------------------
user_name = user_data.get("user_name") or "사용자"

seed_money = user_data.get("seed_money") or 0

balance = user_data.get("balance") or 0

# ---------------------------------------------------
# 제목
# ---------------------------------------------------
st.title("📁 내 계좌")

st.markdown("---")

# ---------------------------------------------------
# 계좌 정보
# ---------------------------------------------------
st.subheader(f"👋 {user_name}님의 계좌")

col1, col2 = st.columns(2)

with col1:

    st.metric(
        "💰 현재 잔액",
        f"{balance:,}원"
    )

with col2:

    st.metric(
        "🏦 시드머니",
        f"{seed_money:,}원"
    )

st.markdown("---")

# ---------------------------------------------------
# 시드머니 설정
# ---------------------------------------------------
st.subheader("💵 시드머니 설정")

default_seed = int(seed_money) if seed_money else 5000000

input_seed = st.number_input(
    "시드머니를 입력하세요",
    min_value=0,
    value=0,
    step=100000,
    format="%d"
)

if st.button("저장", use_container_width=True):

    try:

        # 추가할 금액
        add_money = int(input_seed)

        # 최신 사용자 정보 다시 조회
        latest_user = (
            supabase
            .table("users")
            .select("seed_money, balance")
            .eq("id", login_id)
            .single()
            .execute()
        )

        latest_data = latest_user.data

        current_seed = latest_data.get("seed_money") or 0

        current_balance = latest_data.get("balance") or 0

        # 누적 계산
        new_seed = current_seed + add_money

        new_balance = current_balance + add_money

        # DB 업데이트
        (
            supabase
            .table("users")
            .update({
                "seed_money": new_seed,
                "balance": new_balance
            })
            .eq("id", login_id)
            .execute()
        )

        st.success("✅ 시드머니가 추가되었습니다!")

        st.rerun()

    except Exception as e:

        st.error(f"❌ 저장 실패: {e}")

# ---------------------------------------------------
# 추천 포트폴리오
# ---------------------------------------------------
st.markdown("---")

st.header("📈 추천 투자 포트폴리오")

# ---------------------------------------------------
# 주식 데이터 조회
# ---------------------------------------------------
stock_response = (
    supabase
    .table("stocks")
    .select("*")
    .order("trade_value", desc=True)
    .limit(20)
    .execute()
)

stocks = stock_response.data

# ---------------------------------------------------
# 추천용 종목 리스트
# ---------------------------------------------------
valid_stocks = []

for s in stocks:

    price = s.get("current_price") or 0

    if price > 0:

        valid_stocks.append({
            "id": s.get("id"),
            "name": s.get("stock_name"),
            "price": int(price)
        })

# ---------------------------------------------------
# 데이터 부족 방어
# ---------------------------------------------------
if len(valid_stocks) < 5:

    st.warning("추천용 데이터가 부족합니다.")

else:

    budget = int(balance)

    recommend_list = []

    # ---------------------------------------------------
    # 방법 1
    # ---------------------------------------------------
    stock1 = valid_stocks[0]

    qty1 = budget // stock1["price"]

    recommend_list.append({
        "title": "🔥 공격형 몰빵 투자",
        "desc": "거래대금 최상위 종목 중심의 전략",
        "items": [
            {
                "stock_id": stock1["id"],
                "name": stock1["name"],
                "qty": qty1,
                "price": stock1["price"]
            }
        ]
    })

    # ---------------------------------------------------
    # 방법 2
    # ---------------------------------------------------
    stock2 = valid_stocks[1]

    qty_a = (budget // 2) // stock1["price"]

    qty_b = (budget // 2) // stock2["price"]

    recommend_list.append({
        "title": "⚡ 인기 종목 분산 투자",
        "desc": "인기 종목 2개를 균형 있게 분산",
        "items": [
            {
                "stock_id": stock1["id"],
                "name": stock1["name"],
                "qty": qty_a,
                "price": stock1["price"]
            },
            {
                "stock_id": stock2["id"],
                "name": stock2["name"],
                "qty": qty_b,
                "price": stock2["price"]
            }
        ]
    })

    # ---------------------------------------------------
    # 방법 3
    # ---------------------------------------------------
    stock3 = valid_stocks[2]

    stock4 = valid_stocks[3]

    qty_a = (budget * 40 // 100) // stock1["price"]

    qty_b = (budget * 30 // 100) // stock3["price"]

    qty_c = (budget * 30 // 100) // stock4["price"]

    recommend_list.append({
        "title": "🛡️ 안정형 분산 투자",
        "desc": "리스크를 줄이는 분산 투자",
        "items": [
            {
                "stock_id": stock1["id"],
                "name": stock1["name"],
                "qty": qty_a,
                "price": stock1["price"]
            },
            {
                "stock_id": stock3["id"],
                "name": stock3["name"],
                "qty": qty_b,
                "price": stock3["price"]
            },
            {
                "stock_id": stock4["id"],
                "name": stock4["name"],
                "qty": qty_c,
                "price": stock4["price"]
            }
        ]
    })

    # ---------------------------------------------------
    # 방법 4
    # ---------------------------------------------------
    stock5 = valid_stocks[4]

    qty_each = budget // 5

    recommend_list.append({
        "title": "🎯 균등 분할 투자",
        "desc": "여러 종목을 균등하게 투자",
        "items": [
            {
                "stock_id": stock1["id"],
                "name": stock1["name"],
                "qty": qty_each // stock1["price"],
                "price": stock1["price"]
            },
            {
                "stock_id": stock2["id"],
                "name": stock2["name"],
                "qty": qty_each // stock2["price"],
                "price": stock2["price"]
            },
            {
                "stock_id": stock3["id"],
                "name": stock3["name"],
                "qty": qty_each // stock3["price"],
                "price": stock3["price"]
            },
            {
                "stock_id": stock4["id"],
                "name": stock4["name"],
                "qty": qty_each // stock4["price"],
                "price": stock4["price"]
            },
            {
                "stock_id": stock5["id"],
                "name": stock5["name"],
                "qty": qty_each // stock5["price"],
                "price": stock5["price"]
            }
        ]
    })

    # ---------------------------------------------------
    # 추천 카드 출력
    # ---------------------------------------------------
    for idx, rec in enumerate(recommend_list, 1):

        with st.container(border=True):

            st.subheader(f"방법 {idx}. {rec['title']}")

            st.caption(rec["desc"])

            total_cost = 0

            cols = st.columns(len(rec["items"]))

            for col, item in zip(cols, rec["items"]):

                name = item["name"]

                qty = item["qty"]

                price = item["price"]

                cost = qty * price

                total_cost += cost

                with col:

                    st.info(
                        f"""
### {name}

📦 {qty}주

💰 {cost:,}원
"""
                    )

            remain = budget - total_cost

            col1, col2 = st.columns(2)

            with col1:

                st.metric(
                    "💰 총 투자금",
                    f"{total_cost:,}원"
                )

            with col2:

                st.metric(
                    "🪙 남은 금액",
                    f"{remain:,}원"
                )

            # ---------------------------------------------------
            # 추천 포트폴리오 구매
            # ---------------------------------------------------
            if st.button(
                f"🛒 방법 {idx} 그대로 구매하기",
                key=f"recommend_buy_{idx}",
                use_container_width=True
            ):

                st.session_state["recommend_buy"] = rec["items"]

                st.switch_page("pages/dashboard.py")

# ---------------------------------------------------
# 보유 주식
# ---------------------------------------------------
st.markdown("---")

st.header("📦 보유 주식")

st.metric(
    "📈 총 보유 주식 자산",
    f"{total_stock_asset:,}원"
)

position_response = (
    supabase
    .table("positions")
    .select("*")
    .eq("user_id", login_id)
    .execute()
)

positions = position_response.data

total_stock_asset = 0

if not positions:

    st.info("보유 중인 주식이 없습니다.")

else:

    for pos in positions:

        stock_name = pos.get("stock_name")

        quantity = pos.get("quantity")

        avg_price = pos.get("avg_price")

        # 현재가 조회
        stock_response = (
            supabase
            .table("stocks")
            .select("current_price")
            .eq("id", pos.get("stock_id"))
            .single()
            .execute()
        )

        stock_data = stock_response.data

        current_price = stock_data.get("current_price") or 0

        eval_price = current_price * quantity

        total_stock_asset += eval_price

        buy_price = avg_price * quantity

        profit = eval_price - buy_price

        profit_rate = (
            (profit / buy_price) * 100
            if buy_price > 0 else 0
        )

        with st.container(border=True):

            col1, col2, col3, col4 = st.columns(4)

            with col1:

                st.subheader(stock_name)

                st.caption(pos.get("stock_id"))

            with col2:

                st.metric(
                    "보유 수량",
                    f"{quantity}주"
                )

            with col3:

                st.metric(
                    "총 보유금액",
                    f"{eval_price:,}원",
                    f"{current_price:,}원 × {quantity}주"
            )

            with col4:

                st.metric(
                    "평가 손익",
                    f"{profit:,}원",
                    f"{profit_rate:.2f}%"
                )

# ---------------------------------------------------
# 총 보유 주식 자산 표시
# ---------------------------------------------------
st.markdown("---")

st.metric(
    "📈 총 보유 주식 자산",
    f"{total_stock_asset:,}원"
)
