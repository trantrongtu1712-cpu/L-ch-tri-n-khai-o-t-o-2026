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
def load_all_data():
    all_events = []
    # Quét tất cả file .xlsx trong thư mục
    files = [f for f in os.listdir('.') if f.endswith('.xlsx')]
    
    for file in files:
        try:
            df = pd.read_excel(file)
            # Quét từng ô trong file Excel lịch tháng
            for row in range(len(df)):
                for col in range(len(df.columns)):
                    cell_val = str(df.iloc[row, col])
                    if "-" in cell_val and ":" in cell_val:
                        # Tìm ngày (duyệt ngược lên trên)
                        date_found = None
                        for i in range(1, 5):
                            if row-i >= 0:
                                p_date = str(df.iloc[row-i, col])
                                if re.match(r'\d{4}-\d{2}-\d{2}', p_date):
                                    date_found = p_date
                                    break
                        
                        if date_found:
                            lines = cell_val.split('\n')
                            for line in lines:
                                if line.strip().startswith("-"):
                                    # Trích xuất mã lớp (VD: ESG)
                                    code_match = re.search(r'- ([A-Z0-9Đ]+)', line)
                                    code = code_match.group(1) if code_match else "Lớp học"
                                    
                                    all_events.append({
                                        "title": line.strip(),
                                        "start": date_found,
                                        "allDay": True,
                                        "color": "#00A859" if "TT" in line or "Hà Nội" in line else "#ED1C24",
                                        "extendedProps": {
                                            "full_name": CLASS_MAP.get(code, "Chương trình đào tạo nghiệp vụ"),
                                            "detail": line.strip(),
                                            "date": date_found
                                        }
                                    })
        except: continue
    return all_events

# --- PHẦN XỬ LÝ HIỂN THỊ ---
try:
    events = load_all_data()

    st.title("🗓️ KẾ HOẠCH ĐÀO TẠO AGRIBANK 2026")
    st.markdown("---")

    # Cấu hình lịch ẩn giờ
    calendar_options = {
        "initialView": "dayGridMonth",
        "displayEventTime": False,
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,listMonth",
        },
        "locale": "vi",
    }

    # Hiển thị lịch
    state = calendar(events=events, options=calendar_options, key='agri_cal_v5')

    # DÙNG SESSION_STATE ĐỂ GIỮ THÔNG TIN KHÔNG BỊ ĐÓNG
    if state.get("eventClick"):
        # Lưu thông tin vào bộ nhớ tạm của trình duyệt
        st.session_state.selected_event = state["eventClick"]["event"]

    # HIỂN THỊ THÔNG TIN CHI TIẾT Ở SIDEBAR (THANH BÊN) ĐỂ KHÔNG BỊ TRÔI
    if "selected_event" in st.session_state:
        event = st.session_state.selected_event
        with st.sidebar:
            st.header("🔍 Chi tiết lớp học")
            st.success(f"**Tên chương trình:**\n\n{event['extendedProps']['full_name']}")
            st.info(f"**Mã & Địa điểm:**\n\n{event['extendedProps']['detail']}")
            st.warning(f"**Ngày diễn ra:** {event['extendedProps']['date']}")
            if st.button("Đóng chi tiết"):
                del st.session_state.selected_event
                st.rerun()
    else:
        st.sidebar.write("📌 *Nhấn vào một lớp trên lịch để xem chi tiết tại đây.*")

except Exception as e:
    st.error(f"Lỗi: {e}")
