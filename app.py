import streamlit as st
import json
import os

# 1. ตั้งค่าหน้าเว็บสไตล์คราฟต์เบียร์ระดับพรีเมียม
st.set_page_config(
    page_title="Udomkati Brewing Academy - BJCP Style Guide", 
    page_icon="🍺", 
    layout="wide"
)

# 2. ฟังก์ชันโหลดข้อมูลจากฐานข้อมูล JSON
@st.cache_data
def load_beer_data():
    file_path = "beer_data.json"
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

beer_styles = load_beer_data()

# 3. ส่วนหัวและแบรนด์หน้าเว็บ
st.title("🏆 Udomkati Brewing Academy")
st.subheader("BJCP Beer Style Guidelines (ฉบับภาษาไทย ค้นหาข้อมูลได้ทันที)")
st.write("เครื่องมือช่วยสืบค้นสไตล์เบียร์ คัดกรองค่ากำหนดเชิงเทคนิค และประเมินคาแรคเตอร์เซนเซอร์รี่ (Sensory)")
st.write("---")

# 4. ออกแบบตัวค้นหา (Sidebar)
st.sidebar.image("https://img.icons8.com/color/96/beer.png", width=90)
st.sidebar.header("🔍 ระบบค้นหา & คัดกรอง")

# ช่องพิมพ์ค้นหาด่วน
search_query = st.sidebar.text_input("พิมพ์ชื่อสไตล์ / รหัสสไตล์ (เช่น 1A, IPA, Lager):", "")

# ตัวเลือกหมวดหมู่หลัก (ดึงอัตโนมัติจากไฟล์ JSON)
if beer_styles:
    categories = ["ทั้งหมด"] + sorted(list(set([beer["Category"] for beer in beer_styles])))
    selected_category = st.sidebar.selectbox("เลือกกลุ่มหมวดหมู่เบียร์:", categories)
else:
    selected_category = "ทั้งหมด"

# 5. ฟังก์ชันกรองข้อมูลตามเงื่อนไขใช้งานจริง
filtered_beers = []
for beer in beer_styles:
    match_query = (search_query.lower() in beer["Style"].lower() or 
                   search_query.lower() in beer["ID"].lower() or 
                   search_query.lower() in beer["Category"].lower())
    
    match_category = (selected_category == "ทั้งหมด" or beer["Category"] == selected_category)
    
    if match_query and match_category:
        filtered_beers.append(beer)

# 6. แสดงผลลัพธ์การค้นหาบนหน้าบ้าน (Main Display)
if filtered_beers:
    st.success(f"📋 พบสไตล์เบียร์ที่ตรงกับเงื่อนไขของคุณทั้งหมด {len(filtered_beers)} สไตล์")
    
    # วนลูปสร้างการ์ดข้อมูลเบียร์ที่กรองแล้ว
    for beer in filtered_beers:
        with st.container():
            # ใช้ Expander ซ่อน/กางข้อมูล เพื่อความสวยงามไม่รกหน้าจอ
            with st.expander(f"🍻 [{beer['ID']}] {beer['Style']} — หมวดหมู่หลัก: {beer['Category']}", expanded=True):
                
                # แสดงสถิติเชิงเทคนิค (Technical Parameters) สไตล์แอปพลิเคชันตารางวิเคราะห์
                st.markdown("##### 📊 ข้อมูลเชิงเทคนิค (Technical Specifications)")
                col1, col2, col3, col4, col5 = st.columns(5)
                col1.metric("ABV (แอลกอฮอล์)", beer["ABV"])
                col2.metric("IBU (ระดับความขม)", beer["IBU"])
                col3.metric("SRM (ค่าสีของเบียร์)", beer["SRM"])
                col4.metric("OG (ความถ่วงจำเพาะเริ่ม)", beer["OG"])
                col5.metric("FG (ความถ่วงจำเพาะจบ)", beer["FG"])
                
                st.write("")
                
                # แสดงคาแรคเตอร์การดมและการชิม (Sensory Evaluation Profiles)
                st.markdown("##### 👅 โปรไฟล์การประเมินเนื้อเบียร์และรสชาติ (Sensory Profiles)")
                
                # ทำกล่องตารางข้อความให้อ่านง่าย
                st.markdown(f"**🌟 ภาพรวม (Overall Impression):** {beer['Overall Impression']}")
                st.markdown(f"**👃 อโรม่า/กลิ่น (Aroma):** {beer['Aroma']}")
                st.markdown(f"**👀 รูปลักษณ์/สี/ฟอง (Appearance):** {beer['Appearance']}")
                st.markdown(f"**รสชาติ (Flavor):** {beer['Flavor']}")
                st.markdown(f"**สัมผัสในปาก (Mouthfeel):** {beer['Mouthfeel']}")
                
                if beer.get("Comments"):
                    st.caption(f"💡 *หมายเหตุเพิ่มเติม:* {beer['Comments']}")
                    
        st.write("---") # เส้นคั่นระหว่างเบียร์แต่ละสไตล์
else:
    st.warning("⚠️ ไม่พบข้อมูลสไตล์เบียร์ที่ตรงกับคำค้นหาของคุณ กรุณาลองตรวจสอบใหม่อีกครั้ง")
