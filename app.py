import streamlit as st
import json
import os

# 1. ตั้งค่าหน้าเว็บให้เป็นแบบธีมมืดและกว้างแบบพรีเมียม (Craft Beer Hub Theme)
st.set_page_config(
    page_title="BJCP Thai Beer Style Companion",
    page_icon="🍺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# การปรับแต่งสไตล์ CSS ตกแต่ง UI เพิ่มเติม
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stApp { color: #f0f2f6; }
    .metric-box {
        background-color: #1f2937;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #f59e0b;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. ฟังก์ชันช่วยแปลงค่า SRM เป็นรหัสสี Hex เพื่อแสดงผลแถบสีเบียร์เสมือนจริง
def srm_to_color(srm_range):
    try:
        # ดึงตัวเลขตัวแรกจากช่วง SRM เช่น "2 - 3" -> 2
        srm = float(srm_range.split('-')[0].strip())
    except:
        srm = 2
    
    if srm <= 2: return "#F3F9CB"
    elif srm <= 4: return "#F5E7A4"
    elif srm <= 6: return "#E7C367"
    elif srm <= 8: return "#D4A343"
    elif srm <= 10: return "#C48633"
    elif srm <= 13: return "#B46C29"
    elif srm <= 17: return "#944F1D"
    elif srm <= 20: return "#783815"
    elif srm <= 25: return "#5B240E"
    elif srm <= 30: return "#401307"
    elif srm <= 35: return "#260B04"
    else: return "#080201"

# 3. โหลดฐานข้อมูล JSON
@st.cache_data
def load_data():
    if os.path.exists("beer_db.json"):
        with open("beer_db.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return []

beer_db = load_data()

# --- ส่วนของการจัดหน้าเว็บ (UI Setup) ---
st.title("🍺 BJCP Beer Style Companion")
st.caption("Udomkati Brewing Academy x คนรักคราฟต์เบียร์ไทย — คู่มือสไตล์เบียร์ฉบับดิจิทัลโต้ตอบได้")

# แบ่งหน้าเว็บออกเป็นสไลด์แท็บหลัก 3 แท็บ
tab1, tab2, tab3 = st.tabs(["🔍 ค้นหาและเจาะลึกสไตล์", "⚖️ เปรียบเทียบสไตล์เบียร์", "📊 สรุปภาพรวมและสถิติ"])

# ----------------------------------------------------
# TAB 1: ค้นหาและเจาะลึกสไตล์ (Search & Sensory Explore)
# ----------------------------------------------------
with tab1:
    st.subheader("ค้นหาโปรไฟล์เซนเซอร์รี่และข้อมูลเชิงเทคนิค")
    
    # ตัวกรองข้อมูลบนเมนูด้านข้าง
    st.sidebar.header("⚙️ ตัวกรองข้อมูลเบียร์")
    search_query = st.sidebar.text_input("พิมพ์ชื่อสไตล์ / รหัสสไตล์ / คีย์เวิร์ดรสชาติ:", "")
    
    categories = ["ทั้งหมด"] + sorted(list(set([b["Category"] for b in beer_db]))) if beer_db else ["ทั้งหมด"]
    selected_cat = st.sidebar.selectbox("เลือกหมวดหมู่กลุ่มเบียร์:", categories)
    
    # กรองข้อมูล
    filtered_beers = []
    for b in beer_db:
        match_q = (search_query.lower() in b["Style"].lower() or 
                   search_query.lower() in b["ID"].lower() or 
                   search_query.lower() in b["Overall Impression"].lower())
        match_c = (selected_cat == "ทั้งหมด" or b["Category"] == selected_cat)
        if match_q and match_c:
            filtered_beers.append(b)
            
    if filtered_beers:
        for beer in filtered_beers:
            with st.container():
                beer_color = srm_to_color(beer["SRM"])
                st.markdown(f"""
                <div style="display: flex; align-items: center; background-color: #1e293b; padding: 12px; border-radius: 8px; margin-top: 15px;">
                    <div style="width: 25px; height: 25px; background-color: {beer_color}; border-radius: 50%; margin-right: 15px; border: 1px solid #fff;"></div>
                    <span style="font-size: 1.2rem; font-weight: bold; color:#f3f4f6;">[{beer['ID']}] {beer['Style']}</span>
                    <span style="margin-left: auto; font-size: 0.85rem; color:#9ca3af; background-color:#334155; padding: 4px 10px; border-radius: 12px;">{beer['Category']}</span>
                </div>
                """, unsafe_allow_html=True)
                
                # รายละเอียดข้างในสไตล์
                col1, col2, col3, col4, col5 = st.columns(5)
                col1.metric("ABV", beer["ABV"])
                col2.metric("IBU (ความขม)", beer["IBU"])
                col3.metric("SRM (สี)", beer["SRM"])
                col4.metric("OG", beer["OG"])
                col5.metric("FG", beer["FG"])
                
                # แสดง Sensory รายละเอียด
                st.markdown(f"**📝 ความรู้สึกโดยรวม (Overall Impression):** {beer['Overall Impression']}")
                
                with st.expander("🔍 กางดูข้อมูลประสาทสัมผัสเชิงลึก (Aroma, Flavor, Mouthfeel, Appearance)"):
                    st.write(f"**👃 กลิ่นอโรม่า (Aroma):** {beer['Aroma']}")
                    st.write(f"**👀 รูปลักษณ์ภายนอก (Appearance):** {beer['Appearance']}")
                    st.write(f"**👅 รสชาติ (Flavor):** {beer['Flavor']}")
                    st.write(f"**🍺 สัมผัสในปาก (Mouthfeel):** {beer['Mouthfeel']}")
                    if beer.get("Comments"):
                        st.info(f"📌 **บันทึกเพิ่มเติม:** {beer['Comments']}")
    else:
        st.warning("ไม่พบสไตล์เบียร์ที่ตรงกับเงื่อนไขการค้นหา")

# ----------------------------------------------------
# TAB 2: ระบบเปรียบเทียบสไตล์เบียร์ (Side-by-Side Comparison)
# ----------------------------------------------------
with tab2:
    st.subheader("⚖️ ระบบเปรียบเทียบสไตล์เบียร์เชิงวิทยาศาสตร์")
    st.write("เลือกสไตล์เบียร์ที่คุณต้องการนำมาวิเคราะห์เปรียบเทียบความแตกต่าง")
    
    if len(beer_db) >= 2:
        beer_names = [f"[{b['ID']}] {b['Style']}" for b in beer_db]
        
        c1, c2 = st.columns(2)
        with c1:
            choice_1 = st.selectbox("เลือกเบียร์สไตล์ที่ 1:", beer_names, index=0)
            beer1 = next(b for b in beer_db if f"[{b['ID']}] {b['Style']}" == choice_1)
        with c2:
            choice_2 = st.selectbox("เลือกเบียร์สไตล์ที่ 2:", beer_names, index=1 if len(beer_names)>1 else 0)
            beer2 = next(b for b in beer_db if f"[{b['ID']}] {b['Style']}" == choice_2)
            
        st.write("---")
        
        # ตารางเปรียบเทียบความแตกต่าง
        comp_data = {
            "คุณลักษณะ": ["หมวดหมู่หลัก (Category)", "ความแรงแอลกอฮอล์ (ABV)", "ระดับความขม (IBU)", "ระดับสี (SRM)", "ค่าความถ่วงจำเพาะเริ่ม (OG)", "ค่าความถ่วงจำเพาะจบ (FG)", "ความประทับใจโดยรวม (Overall)"],
            beer1["Style"]: [beer1["Category"], beer1["ABV"], beer1["IBU"], beer1["SRM"], beer1["OG"], beer1["FG"], beer1["Overall Impression"]],
            beer2["Style"]: [beer2["Category"], beer2["ABV"], beer2["IBU"], beer2["SRM"], beer2["OG"], beer2["FG"], beer2["Overall Impression"]]
        }
        st.table(comp_data)
        
        # เปรียบเทียบโปรไฟล์กลิ่นรสชาติ
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            st.markdown(f"### 👅 โปรไฟล์ของ {beer1['Style']}")
            st.write(f"**👃 กลิ่น:** {beer1['Aroma']}")
            st.write(f"**รสชาติ:** {beer1['Flavor']}")
            st.write(f"**สัมผัสในปาก:** {beer1['Mouthfeel']}")
        with col_b2:
            st.markdown(f"### 👅 โปรไฟล์ของ {beer2['Style']}")
            st.write(f"**👃 กลิ่น:** {beer2['Aroma']}")
            st.write(f"**รสชาติ:** {beer2['Flavor']}")
            st.write(f"**สัมผัสในปาก:** {beer2['Mouthfeel']}")
    else:
        st.info("กรุณาเพิ่มข้อมูลสไตล์เบียร์ในไฟล์ข้อมูลก่อนเพื่อเปิดใช้งานระบบเปรียบเทียบ")

# ----------------------------------------------------
# TAB 3: สรุปภาพรวมและสถิติ (Dashboard Analytics)
# ----------------------------------------------------
with tab3:
    st.subheader("📊 ข้อมูลภาพรวมคลังความรู้ BJCP")
    if beer_db:
        st.metric("จำนวนสไตล์เบียร์ที่พร้อมใช้งานในระบบปัจจุบัน", f"{len(beer_db)} สไตล์")
        st.info("ระบบจัดเก็บและแยกแยะข้อมูลในรูปแบบ JSON เรียบร้อยแล้ว ทำให้สามารถขยายฐานข้อมูลในอนาคตได้อย่างไม่จำกัดโดยไม่กระทบความเร็วของหน้าเว็บแอปพลิเคชัน")
    else:
        st.warning("ยังไม่มีข้อมูลในคลัง")
