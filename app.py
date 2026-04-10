import streamlit as st
import pandas as pd
from streamlit_calendar import calendar
import os
import re

st.set_page_config(page_title="Lịch Đào tạo Agribank 2026", layout="wide")

# 1. TỪ ĐIỂN TRA CỨU TÊN CHƯƠNG TRÌNH (Từ file cũ của bạn)
CLASS_MAP = {
    "AGCP": "Tư duy linh hoạt dành cho lãnh đạo cấp phòng",
    "AGNV": "Tư duy linh hoạt dành cho nhân viên",
    "ESG": "Tổng quan ESG",
    "TQAI": "Tổng quan về AI trong ngân hàng",
    "AITD": "AI nâng cao hiệu suất trong công tác tín dụng",
    "AIKT": "AI nâng cao hiệu suất trong công tác kế toán",
    "LĐ3C": "Kỹ năng lãnh đạo hiện đại 3C",
    "PTDL": "Phân tích dữ liệu và lập báo cáo",
    "KNBH": "Kỹ năng bán hàng và chăm sóc khách hàng chuyên nghiệp thời kỳ chuyển đổi số",
    "KNSP": "Kỹ năng sư phạm",
    "TCS": "Tài chính số",
    "LĐM": "Lao động mới tuyển dụng",
    "PTDLHV": "Phân tích dữ liệu hành vi khách hàng",
    "DBKT": "Phân tích, dự báo kinh tế, thị trường, xu hướng phát triển SPDV ngành NH trong và ngoài nước",
    "KHDN": "Nghiệp vụ cấp tín dụng khách hàng doanh nghiệp"
}

@st.cache_data
def load_data_from_folder():
    all_events = []
    # Quét tất cả file Excel trong thư mục có chữ "LỊCH" hoặc "T3"
    files = [f for f in os.listdir('.') if f.endswith('.xlsx') and ('LỊCH' in f.upper() or 'T3' in f.upper())]
    
    for file in files:
        try:
            df = pd.read_excel(file)
            for row in range(len(df)):
                for col in range(len(df.columns)):
                    cell_content = str(df.iloc[row, col])
                    
                    # Tìm các ô có chứa dấu "-" (định dạng lớp học của bạn)
                    if "-" in cell_content:
                        # Tìm ngày ở các dòng lân cận (thường là dòng phía trên nội dung lớp)
                        date_str = None
                        for i in range(1, 4):
                            if row-i >= 0:
                                val = str(df.iloc[row-i, col])
                                # Kiểm tra định dạng ngày YYYY-MM-DD
                                if re.match(r'\d{4}-\d{2}-\d{2}', val):
                                    date_str = val
                                    break
                        
                        if date_str:
                            lines = cell_content.split('\n')
                            for line in lines:
                                if line.strip().startswith("-"):
                                    # Trích xuất mã lớp (VD: ESG)
                                    match = re.search(r'- ([A-Z0-9Đ]+)', line)
                                    code = match.group(1) if match else "Lớp học"
                                    
                                    all_events.append({
                                        "title": line.strip(),
                                        "start": date_str,
                                        "allDay": True, # QUAN TRỌNG: Dòng này giúp bỏ hiển thị 00:00
                                        "color": "#00A859" if "TT" in line or "Hà Nội" in line else "#ED1C24",
                                        "extendedProps": {
                                            "full_name": CLASS_MAP.get(code, "Chương trình đào tạo nghiệp vụ"),
                                            "detail": line.strip()
                                        }
                                    })
        except:
            continue
    return all_events

try:
    events = load_data_from_folder()

    st.title("🗓️ KẾ HOẠCH ĐÀO TẠO AGRIBANK 2026")
    st.markdown("---")

    # 2. CẤU HÌNH LỊCH - LOẠI BỎ GIỜ
    calendar_options = {
        "initialView": "dayGridMonth",
        "displayEventTime": False, # Lệnh này sẽ ẩn hoàn toàn 00:00 trên giao diện
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,listMonth",
        },
        "locale": "vi",
    }

    state = calendar(events=events, options=calendar_options, key='agri_calendar_v4')

    # 3. NHẤN VÀO HIỆN TÊN CHƯƠNG TRÌNH
    if state.get("eventClick"):
        res = state["eventClick"]["event"]
        st.sidebar.markdown("---")
        st.sidebar.subheader("🔍 Chi tiết chương trình")
        st.sidebar.info(f"**Tên đầy đủ:** \n\n {res['extendedProps']['full_name']}")
        st.sidebar.success(f"**Thông tin:** \n\n {res['extendedProps']['detail']}")

except Exception as e:
    st.error(f"Lỗi: {e}")