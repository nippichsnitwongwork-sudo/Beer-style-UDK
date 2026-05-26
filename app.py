import streamlit as st
import requests
import json

# 1. ตั้งค่าหน้าเว็บให้เป็นธีม Dark Mode ระดับพรีเมียมสำหรับคราฟต์เบียร์
st.set_page_config(
    page_title="BJCP Thai Beer Style Companion",
    page_icon="🍺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# การปรับแต่ง UI/CSS เสริมให้หน้าตาสวยงาม ทันสมัย ใช้งานง่าย
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stApp { color: #f0f2f6; }
    .beer-card {
        background-color: #1e293b;
        padding: 20px;
        border-radius: 10px;
        border-left: 6px solid #f59e0b;
        margin-bottom: 20px;
    }
    .metric-container {
        background-color: #0f172a;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        border: 1px solid #334155;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. ฟังก์ชันแปลงค่า SRM (สีเบียร์) เป็นรหัสสี Hex เพื่อแสดงผลเป็นวงกลมสีเนื้อเบียร์จริง
def srm_to_hex(srm_range):
    try:
        # ดึงตัวเลขแรกจากช่วงสี เช่น "2 - 3" -> 2
        srm = float(str(srm_range).split('-')[0].strip())
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

# 3. ฟังก์ชันดึงข้อมูลจากฐานข้อมูล BJCP Cloud Database แบบเรียลไทม์
@st.cache_data(ttl=3600) # ทำการ Cache ข้อมูลไว้ 1 ชั่วโมงเพื่อไม่ให้เว็บโหลดช้า
def fetch_bjcp_cloud_data():
    # ลิงก์ฐานข้อมูลออนไลน์โครงสร้าง BJCP 2021 TH Complete Database
    url = "https://raw.githubusercontent.com/nippichsnitwongwork-sudo/Beer-style-UDK/main/beer_db.json"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        pass
    
    # Backup สำรองกรณีเน็ตเวิร์กของ Server มีปัญหา
    return [
        {
            "ID": "1A", "Style": "American Light Lager", "Category": "Standard American Beer",
            "IBU": "8 - 12", "SRM": "2 - 3", "OG": "1.028 - 1.040", "FG": "0.998 - 1.008", "ABV": "2.8 - 4.2%",
            "Overall Impression": "เบียร์ลาเกอร์ที่มีคาร์โบเนชั่นสูง เนื้อเบียร์บางที่สุด แทบไม่มีรสชาติเด่นชัด ออกแบบมาให้ดื่มเย็นจัด",
            "Aroma": "อโรม่าจากมอลต์ระดับต่ำมาก บางครั้งให้ความรู้สึกถึง grain", 
            "Appearance": "สีฟางข้าวอ่อนมากจนถึงสีเหลืองอ่อน น้ำเบียร์ใสเป็นประกาย",
            "Flavor": "รสชาติเป็นกลาง มีความคม จบแบบ dry รสหวานต่ำมาก", 
            "Mouthfeel": "เนื้อเบียร์บางเบามาก คาร์โบเนชั่นสูงมาก", "Comments": ""
        }
    ]

# สั่งโหลดข้อมูลจากคลาวด์มาเก็บในตัวแปรระบบ
beer_db = fetch_bjcp_cloud_data()

# --- ส่วนควบคุมหน้าตาเว็บหน้าบ้าน (UI Layout) ---
st.title("🍺 BJCP Beer Style Companion")
st.markdown("#### **Udomkati Brewing Academy** — ระบบสืบค้นและวิเคราะห์คาแรคเตอร์เบียร์มาตรฐานสากล")
st.write("---")

# ประกาศสร้างหน้าต่างแท็บสำหรับเลือกโหมดการใช้งาน
tab1, tab2, tab3 = st.tabs(["🔍 ค้นหา & เจาะลึกโปรไฟล์เซนเซอร์รี่", "⚖️ เปรียบเทียบสไตล์แบบ Side-by-Side", "📊 สถิติภาพรวมคลังความรู้"])

# ----------------------------------------------------
# TAB 1: ค้นหาและเจาะลึกโปรไฟล์ (Search & Sensory Explore)
# ----------------------------------------------------
with tab1:
    st.markdown("### 🔍 ค้นหาสไตล์และคาแรคเตอร์")
    
    # แผงควบคุมตัวกรองด้านข้าง (Sidebar)
    st.sidebar.image("https://img.icons8.com/color/96/beer.png", width=70)
    st.sidebar.header("🛠️ ตัวกรองขั้นสูง")
    
    search_query = st.sidebar.text_input("พิมพ์รหัสสไตล์ / ชื่อ / คีย์เวิร์ดรสชาติ (เช่น 1A, IPA, คาราเมล):", "")
    
    # คัดแยกหมวดหมู่หลักที่มีทั้งหมดออกมาทำ Dropdown แบบไดนามิก
    all_categories = ["ทั้งหมด"] + sorted(list(set([b["Category"] for b in beer_db])))
    selected_category = st.sidebar.selectbox("เลือกกลุ่มหมวดหมู่หลัก (Category):", all_categories)
    
    # อัลกอริทึมการกรองข้อมูลอัจฉริยะ (Smart Filter)
    filtered_beers = []
    for b in beer_db:
        match_query = (search_query.lower() in b["Style"].lower() or 
                       search_query.lower() in b["ID"].lower() or 
                       search_query.lower() in b["Overall Impression"].lower() or
                       search_query.lower() in b["Flavor"].lower())
        
        match_cat = (selected_category == "ทั้งหมด" or b["Category"] == selected_category)
        
        if match_query and match_cat:
            filtered_beers.append(b)
            
    # แสดงผลลัพธ์
    if filtered_beers:
        st.success(f"📋 พบข้อมูลเบียร์สไตล์ที่ตรงกับเงื่อนไขทั้งหมด {len(filtered_beers)} รายการ")
        
        for beer in filtered_beers:
            beer_hex = srm_to_hex(beer["SRM"])
            
            # ดีไซน์แถบหัวข้อการ์ดเบียร์พร้อมแสดงวงกลมสีเนื้อเบียร์จริงตามค่า SRM
            st.markdown(f"""
            <div style="display: flex; align-items: center; background-color: #1e293b; padding: 12px; border-radius: 8px; margin-top: 15px; margin-bottom: 5px;">
                <div style="width: 24px; height: 24px; background-color: {beer_hex}; border-radius: 50%; margin-right: 15px; border: 2px solid #ffffff;"></div>
                <span style="font-size: 1.25rem; font-weight: bold; color: #f3f4f6;">[{beer['ID']}] {beer['Style']}</span>
                <span style="margin-left: auto; font-size: 0.85rem; color: #9ca3af; background-color: #334155; padding: 4px 12px; border-radius: 12px;">{beer['Category']}</span>
            </div>
            """, unsafe_allow_html=True)
            
            # การแบ่งคอลัมน์แสดงตัวเลขทางเทคนิค
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("ABV (แอลกอฮอล์)", beer["ABV"])
            c2.metric("IBU (ความขม)", beer["IBU"])
            c3.metric("SRM (ระดับสี)", beer["SRM"])
            c4.metric("OG (ความถ่วงเริ่ม)", beer["OG"])
            c5.metric("FG (ความถ่วงจบ)", beer["FG"])
            
            # แสดงข้อมูล Sensory Profile เชิงรายละเอียด
            st.markdown(f"**🌟 ความเข้าใจโดยรวม (Overall Impression):** {beer['Overall Impression']}")
            
            with st.expander("📝 เปิดดูคู่มือการทดสอบชิมเชิงลึก (Aroma, Appearance, Flavor, Mouthfeel)"):
                st.markdown(f"**👃 กลิ่นอโรม่า (Aroma):** {beer['Aroma']}")
                st.markdown(f"**👀 รูปลักษณ์ภายนอก (Appearance):** {beer['Appearance']}")
                st.markdown(f"**👅 รสชาติและบาลานซ์ (Flavor):** {beer['Flavor']}")
                st.markdown(f"**🍺 สัมผัสในปากและเนื้อสัมผัส (Mouthfeel):** {beer['Mouthfeel']}")
                if beer.get("Comments"):
                    st.caption(f"💡 *หมายเหตุจากกรรมการสากล:* {beer['Comments']}")
            st.write("")
    else:
        st.warning("⚠️ ไม่พบข้อมูลที่ตรงกับคำค้นหาของคุณ ลองเปลี่ยนคีย์เวิร์ดใหม่อีกครั้ง")

# ----------------------------------------------------
# TAB 2: เปรียบเทียบสไตล์เบียร์ (Side-by-Side Comparison)
# ----------------------------------------------------
with tab2:
    st.markdown("### ⚖️ ระบบเปรียบเทียบสไตล์เบียร์เชิงวิทยาศาสตร์")
    st.write("เลือกสไตล์เบียร์ 2 ชนิดเพื่อวิเคราะห์ความแตกต่างของค่าสถิติเทคนิคและโปรไฟล์รสชาติเคียงข้างกัน")
    
    if len(beer_db) >= 2:
        # ดึงรายชื่อเบียร์ทั้งหมดมาทำ Dropdown ตัวเลือกเปรียบเทียบ
        beer_options = [f"[{b['ID']}] {b['Style']}" for b in beer_db]
        
        col_select1, col_select2 = st.columns(2)
        with col_select1:
            beer_choice_1 = st.selectbox("เลือกสไตล์เบียร์ที่ 1:", beer_options, index=0)
            b1_data = next(b for b in beer_db if f"[{b['ID']}] {b['Style']}" == beer_choice_1)
        with col_select2:
            beer_choice_2 = st.selectbox("เลือกสไตล์เบียร์ที่ 2:", beer_options, index=min(1, len(beer_options)-1))
            b2_data = next(b for b in beer_db if f"[{b['ID']}] {b['Style']}" == beer_choice_2)
            
        st.write("---")
        
        # ตารางเปรียบเทียบเชิงโครงสร้างสากล
        comparison_matrix = {
            "เกณฑ์การเปรียบเทียบ": ["รหัสหมวดหมู่ (Category)", "ความแรงแอลกอฮอล์ (ABV)", "ระดับความขม (IBU)", "ค่าสีเนื้อเบียร์ (SRM)", "ความถ่วงจำเพาะเริ่ม (OG)", "ความถ่วงจำเพาะจบ (FG)"],
            b1_data["Style"]: [b1_data["Category"], b1_data["ABV"], b1_data["IBU"], b1_data["SRM"], b1_data["OG"], b1_data["FG"]],
            b2_data["Style"]: [b2_data["Category"], b2_data["ABV"], b2_data["IBU"], b2_data["SRM"], b2_data["OG"], b2_data["FG"]]
        }
        st.table(comparison_matrix)
        
        # คอลัมน์เปรียบเทียบข้อมูลเซนเซอร์รี่ (Sensory Grid)
        grid1, grid2 = st.columns(2)
        with grid1:
            st.markdown(f"#### 🍺 โปรไฟล์ของ {b1_data['Style']}")
            st.info(f"**ภาพรวม:** {b1_data['Overall Impression']}")
            st.write(f"**👃 กลิ่นอโรม่า:** {b1_data['Aroma']}")
            st.write(f"**รสชาติ:** {b1_data['Flavor']}")
            st.write(f"**สัมผัสในปาก:** {b1_data['Mouthfeel']}")
        with grid2:
            st.markdown(f"#### 🍺 โปรไฟล์ของ {b2_data['Style']}")
            st.info(f"**ภาพรวม:** {b2_data['Overall Impression']}")
            st.write(f"**👃 กลิ่นอโรม่า:** {b2_data['Aroma']}")
            st.write(f"**รสชาติ:** {b2_data['Flavor']}")
            st.write(f"**สัมผัสในปาก:** {b2_data['Mouthfeel']}")
    else:
        st.info("กำลังโหลดฐานข้อมูลจากระบบคลาวด์...")

# ----------------------------------------------------
# TAB 3: สถิติภาพรวมคลังความรู้ (Dashboard Analytics)
# ----------------------------------------------------
with tab3:
    st.markdown("### 📊 ข้อมูลสถิติโครงสร้างแอปพลิเคชัน")
    if beer_db:
        total_styles = len(beer_db)
        total_cats = len(list(set([b["Category"] for b in beer_db])))
        
        stat1, stat2 = st.columns(2)
        stat1.metric("จำนวนสไตล์เบียร์ในคลังออนไลน์ปัจจุบัน", f"{total_styles} สไตล์")
        stat2.metric("จำนวนหมวดหมู่เบียร์หลัก (Categories)", f"{total_cats} หมวดหมู่")
        
        st.write("---")
        st.success("✅ โครงสร้างระบบเสร็จสมบูรณ์! หน้าเว็บนี้เชื่อมต่อกับเซิร์ฟเวอร์ฐานข้อมูลโดยตรง ทำให้ข้อมูลเป็นระเบียบ แม่นยำ และพร้อมแชร์ลิงก์ให้กลุ่มคนรักคราฟต์เบียร์เข้ามาใช้งานได้ทันที 24 ชั่วโมงครับ")
