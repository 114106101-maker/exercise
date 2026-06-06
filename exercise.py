import streamlit as st
import cv2
import mediapipe as mp
import datetime
import pandas as pd
from fpdf import FPDF

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# 動作教學提示與 GIF 示範
exercise_tips = {
    "深蹲": {
        "tip": "保持背部挺直，膝蓋不要超過腳尖，下蹲到大腿與地面平行。",
        "gif": "https://media.tenor.com/2nKX2zQFJxIAAAAC/squat-exercise.gif"
    },
    "伏地挺身": {
        "tip": "雙手與肩同寬，身體保持一直線，下壓到手肘約 90 度再推起。",
        "gif": "https://media.tenor.com/3bQkX9mYQJkAAAAC/pushup.gif"
    },
    "仰臥起坐": {
        "tip": "雙手放在胸前或耳邊，腹部收緊，慢慢抬起上半身。",
        "gif": "https://media.tenor.com/6YxZfQ6l7zIAAAAC/situp.gif"
    },
    "弓箭步": {
        "tip": "一腳向前跨步，後腳膝蓋接近地面，保持上半身直立。",
        "gif": "https://media.tenor.com/5ZkX9mYQJkIAAAAC/lunge.gif"
    }
}

def generate_pdf_report(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="📊 運動報告", ln=True, align="C")
    pdf.ln(10)

    for index, row in df.iterrows():
        pdf.cell(200, 10, txt=f"{row['date']} - {row['action']}：{row['count']} 次 (目標 {row['goal']})", ln=True)

    return pdf

def run():
    st.subheader("🏋️ 運動追蹤 (姿勢偵測)")
    st.write("使用攝影機進行運動次數偵測")

    # 使用者選擇要偵測的動作
    action = st.selectbox("選擇運動動作", list(exercise_tips.keys()))

    # 顯示教學提示與 GIF
    st.info(f"📌 {action} 教學：{exercise_tips[action]['tip']}")
    st.image(exercise_tips[action]["gif"], caption=f"{action} 示範")

    # 目標設定
    goal = st.number_input(f"設定今日 {action} 目標次數", min_value=1, step=1)

    run_camera = st.checkbox("開啟攝影機")
    if run_camera:
        cap = cv2.VideoCapture(0)
        count = 0
        stage = None
        stframe = st.empty()

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image)

            if results.pose_landmarks:
                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                landmarks = results.pose_landmarks.landmark

                # 根據選擇的動作判斷次數
                if action == "深蹲":
                    hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
                    knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
                    if knee.y > hip.y:
                        stage = "down"
                    if knee.y < hip.y and stage == "down":
                        stage = "up"
                        count += 1

                elif action == "伏地挺身":
                    shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
                    elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value]
                    if elbow.y > shoulder.y:
                        stage = "down"
                    if elbow.y < shoulder.y and stage == "down":
                        stage = "up"
                        count += 1

                elif action == "仰臥起坐":
                    nose = landmarks[mp_pose.PoseLandmark.NOSE.value]
                    hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
                    if nose.y > hip.y:
                        stage = "down"
                    if nose.y < hip.y and stage == "down":
                        stage = "up"
                        count += 1

                elif action == "弓箭步":
                    hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
                    knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
                    if knee.y > hip.y:
                        stage = "down"
                    if knee.y < hip.y and stage == "down":
                        stage = "up"
                        count += 1

            stframe.image(image)
            st.write(f"{action} 次數：{count}")

            # 完成率顯示
            if goal > 0:
                progress = min(count / goal, 1.0)
                st.progress(progress)
                st.write(f"完成率：{progress*100:.1f}%")

                if count >= goal:
                    st.success(f"🎉 恭喜達成 {goal} 次 {action} 目標！")

        cap.release()

        # 保存紀錄到 session
        if "exercise_log" not in st.session_state:
            st.session_state["exercise_log"] = []

        st.session_state["exercise_log"].append({
            "date": datetime.date.today(),
            "action": action,
            "count": count,
            "goal": goal
        })
        st.success(f"📊 已保存 {action} 紀錄：{count} 次")

    # 每週報告
    st.subheader("📊 每週運動報告")
    if "exercise_log" in st.session_state and st.session_state["exercise_log"]:
        df = pd.DataFrame(st.session_state["exercise_log"])
        st.write(df)

        df["date"] = pd.to_datetime(df["date"])
        this_week = df[df["date"] >= (datetime.date.today() - datetime.timedelta(days=7))]

        summary = this_week.groupby("action")["count"].sum().reset_index()
        st.bar_chart(summary.set_index("action"))

        for _, row in summary.iterrows():
            st.write(f"{row['action']} 本週總次數：{row['count']}")

    # 月報告
    st.subheader("📈 月報表與趨勢分析")
    if "exercise_log" in st.session_state and st.session_state["exercise_log"]:
        df = pd.DataFrame(st.session_state["exercise_log"])
        df["date"] = pd.to_datetime(df["date"])
        this_month = df[df["date"] >= (datetime.date.today() - datetime.timedelta(days=30))]

        monthly_summary = this_month.groupby("date")["count"].sum().reset_index()
        st.line_chart(monthly_summary.set_index("date"))

        st.write("📌 趨勢分析：顯示過去 30 天的運動次數變化")

        # PDF 報告生成
        if st.button("📄 生成 PDF 報告"):
            pdf = generate_pdf_report(this_month)
            pdf_output = "exercise_report.pdf"
            pdf.output(pdf_output)
            with open(pdf_output, "rb") as f:
                st.download_button("⬇️ 下載 PDF 報告", f, file_name="exercise_report.pdf")
