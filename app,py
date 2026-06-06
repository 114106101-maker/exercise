import streamlit as st
from modules import exercise, diet, sleep, stress, diary, wearable

st.set_page_config(page_title="全方位健康管理平台", layout="wide")
st.title("🏋️ 全方位健康管理平台")

menu = st.sidebar.selectbox("選擇功能", [
    "運動追蹤 (姿勢偵測)", "AI 飲食建議", "睡眠追蹤", "壓力管理", "健康日記", "穿戴裝置整合"
])

if menu == "運動追蹤 (姿勢偵測)":
    exercise.run()
elif menu == "AI 飲食建議":
    diet.run()
elif menu == "睡眠追蹤":
    sleep.run()
elif menu == "壓力管理":
    stress.run()
elif menu == "健康日記":
    diary.run()
elif menu == "穿戴裝置整合":
    wearable.run()
