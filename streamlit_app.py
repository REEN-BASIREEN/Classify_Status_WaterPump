import streamlit as st
import requests
from joblib import load
from datetime import datetime

# โหลดโมเดลที่อัปโหลดมา
model = load('best_model_IoT.pkl')  # ชื่อไฟล์โมเดล

# URL สำหรับดึงข้อมูลจาก ThingSpeak
THINGSPEAK_CHANNEL_ID = '******************'  # Channel ID ของคุณ
THINGSPEAK_API_KEY = '******************'  # API Key ของคุณ
THINGSPEAK_URL = f"https://api.thingspeak.com/channels/{THINGSPEAK_CHANNEL_ID}/feeds.json?api_key={THINGSPEAK_API_KEY}"


# ฟังก์ชันสำหรับการทำนาย Status
def make_prediction(air_temperature, air_humidity, soil_humidity):
    conditions = [air_temperature, air_humidity, soil_humidity]
    prediction = model.predict([conditions])
    status = "On" if prediction[0] == 1 else "Off"  # สมมติว่าค่า 1 คือ "On" และ 0 คือ "Off"
    return status


# Streamlit UI
st.set_page_config(page_title='Environmental Status Prediction', layout='wide')
st.title('🌱 Status Prediction Based on Environmental Conditions')

# สไตล์ CSS สำหรับตกแต่ง
st.markdown("""
    <style>
        .main {
            text-align: center;
            color: #4CAF50;
            font-size: 40px;
            font-family: 'Arial', sans-serif;
        }
        .feed-info {
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            margin: 20px 0;
                        
        }
        .footer {
            text-align: center;
            margin-top: 20px;
            font-size: 14px;
            color: #888;
        }
        .data-label {
            color: #0000FF;  /* เปลี่ยนสีถ้าต้องการ */
        }
        .status {
            font-size: 48px;  /* ขนาดตัวอักษรสำหรับสถานะ */
            font-weight: bold;
            color: #4CAF50;  /* เปลี่ยนสีถ้าต้องการ */
        }
    </style>
""", unsafe_allow_html=True)

# ดึงข้อมูลจาก ThingSpeak
response = requests.get(THINGSPEAK_URL)

# ตรวจสอบข้อมูลจาก ThingSpeak
if response.status_code == 200:
    data = response.json()
    feeds = data['feeds']
    if feeds:
        latest_feed = feeds[-1]  # ดึงข้อมูลล่าสุด
        timestamp = latest_feed['created_at']
        formatted_time = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ").strftime("%d %B %Y, %H:%M:%S")

        # ดึงค่าจากข้อมูลล่าสุด
        soil_humidity = float(latest_feed['field1'])  # Air Temperature
        air_temperature = float(latest_feed['field2'])  # Air Humidity
        air_humidity = float(latest_feed['field3'])  # Soil Humidity

        # ทำการทำนายโดยใช้ค่าที่ดึงมา
        status = make_prediction(air_temperature, air_humidity, soil_humidity)

        # แสดงผลลัพธ์การทำนาย
        st.markdown(f"<div class='feed-info' ><span style='font-weight: bold; color: black;'>📊 Latest Data </span> <br>"
                     f"<span class='data-label'>Date:Time:</span> {formatted_time} <br>"
                     f"<span class='data-label'>Temperature:</span> {air_temperature} °C <br>"
                     f"<span class='data-label'>Air Humidity:</span> {air_humidity} % <br>"
                     f"<span class='data-label'>Soil Humidity:</span> {soil_humidity} % <br></div>",
                     unsafe_allow_html=True)

        # แสดงผลลัพธ์สถานะ
        st.markdown(
            f'<span style="color: black; font-size: 48px;">🔍 Status: </span><span style="color: red; font-size: 48px;">{status}</span>',
            unsafe_allow_html=True)

    else:
        st.write("🚫 ไม่มีข้อมูลในฟีด")
else:
    st.write("❌ ไม่สามารถดึงข้อมูลจาก ThingSpeak ได้")



