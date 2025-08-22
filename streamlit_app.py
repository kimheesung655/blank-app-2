import streamlit as st
import random
from streamlit_drawable_canvas import st_canvas
from PIL import Image, ImageDraw

# -------------------------------
# 세션 상태 안전 초기화 (맨 위)
# -------------------------------
if "apples" not in st.session_state:
    st.session_state["apples"] = [random.randint(1, 9) for _ in range(170)]
if "score" not in st.session_state:
    st.session_state["score"] = 0
if "drag_done" not in st.session_state:
    st.session_state["drag_done"] = False

# -------------------------------
# 앱 제목 및 안내
# -------------------------------
st.set_page_config(page_title="사과 게임", layout="wide")
st.title("사과 게임")
st.caption("마우스로 드래그하여 사과를 선택하세요. 합이 10이면 사라지고 점수가 올라갑니다!")

# -------------------------------
# 점수판 오른쪽 위
# -------------------------------
st.markdown(
    """
    <style>
    .score-div {
        position: fixed;
        top: 20px;
        right: 20px;
        background-color: #fff;
        padding: 10px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
        z-index: 1000;
    }
    </style>
    <div class="score-div">
    """, unsafe_allow_html=True
)
st.metric("현재 점수", st.session_state["score"])
st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------
# 보드 설정
# -------------------------------
cell_size = 40
cols_per_row = 17
rows = len(st.session_state["apples"]) // cols_per_row
width = cols_per_row * cell_size
height = rows * cell_size

# -------------------------------
# 사과 이미지 생성
# -------------------------------
board = Image.new("RGB", (width, height), (255, 255, 255))
draw = ImageDraw.Draw(board)

for i, apple in enumerate(st.session_state["apples"]):
    if apple is None:
        continue
    r = i // cols_per_row
    c = i % cols_per_row
    x, y = c * cell_size, r * cell_size

    # 빨간 동그라미
    draw.ellipse([x+2, y+10, x+cell_size-2, y+cell_size-2], fill="red")
    # 초록색 잎사귀
    draw.polygon(
        [(x+cell_size//2, y), (x+cell_size//2 -5, y+10), (x+cell_size//2 +5, y+10)],
        fill="green"
    )
    # 숫자 표시
    draw.text((x + cell_size//3, y + cell_size//2), str(apple), fill="white")

# -------------------------------
# 드래그 캔버스 생성
# -------------------------------
canvas_result = st_canvas(
    fill_color="rgba(0,0,255,0.15)",
    stroke_color="blue",
    stroke_width=2,
    background_image=board,
    update_streamlit=True,
    width=width,
    height=height,
    drawing_mode="rect",
    key="canvas",
)

# -------------------------------
# 드래그 영역 판정
# -------------------------------
if canvas_result.json_data is not None:
    objects = canvas_result.json_data["objects"]
    if objects:
        last_rect = objects[-1]
        left = last_rect["left"]
        top = last_rect["top"]
        w = last_rect["width"]
        h = last_rect["height"]

        selected = []
        for i, apple in enumerate(st.session_state["apples"]):
            if apple is None:
                continue
            r = i // cols_per_row
            c = i % cols_per_row
            x, y = c * cell_size, r * cell_size
            cx, cy = x + cell_size//2, y + cell_size//2
            if left <= cx <= left + w and top <= cy <= top + h:
                selected.append(i)

        if selected:
            values = [st.session_state["apples"][i] for i in selected]
            if sum(values) == 10 and len(values) >= 2:
                st.session_state["score"] += 10
                for idx in selected:
                    st.session_state["apples"][idx] = None
                st.session_state["drag_done"] = True

# -------------------------------
# 드래그 박스 자동 제거
# -------------------------------
if st.session_state["drag_done"]:
    canvas_result = st_canvas(
        fill_color="rgba(0,0,255,0.15)",
        stroke_color="blue",
        stroke_width=2,
        background_image=board,
        update_streamlit=True,
        width=width,
        height=height,
        drawing_mode="rect",
        key="canvas2",
    )
    st.session_state["drag_done"] = False
