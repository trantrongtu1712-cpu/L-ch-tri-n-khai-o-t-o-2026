import streamlit as st
import pandas as pd
from streamlit_calendar import calendar
import os
import re
from datetime import datetime

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
def load_and_group_data():
    all_raw_data = []
    files = [f for f in os.listdir('.') if f.endswith('.xlsx')]
    
    for file in files:
        try:
            df = pd.read_excel(file)
            for row in range(len(df)):
                for col in range(len(df.columns)):
                    cell_val = str(df.iloc[row, col])
                    if "-" in cell_val and ":" in cell_val:
                        # Tìm ngày tương ứng
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
                                    all_raw_data.append({
                                        "date": date_found,
                                        "detail": line.strip()
                                    })
        except: continue

    # XỬ LÝ TÌM NGÀY BẮT ĐẦU VÀ KẾ THÚC
    df_raw = pd.DataFrame(all_raw_data)
    if df_raw.empty: return []
    
    events = []
    # Gom nhóm theo nội dung lớp học để tìm ngày đầu và ngày cuối
    for detail, group in df_raw.groupby('detail'):
        sorted_dates = sorted(group['date'].tolist())
        start_date = sorted_dates[0]
        end_date = sorted_dates[-1]
        
        # Trích xuất mã lớp để tra cứu tên
        code_match = re.search(r'- ([A-Z0-9Đ]+)', detail)
        code = code_match.group(1) if code_match else "Lớp học"
        
        # Định dạng lại ngày để hiển thị thanh bên (DD/MM/YYYY)
        d_start = datetime.strptime(start_date, '%Y-%m-%d').strftime('%d/%m/%Y')
        d_end = datetime.strptime(end_date, '%Y-%m-%d').strftime('%d/%m/%Y')

        events.append({
            "title": detail,
            "start": start_date, # Dùng cho lịch (ISO)
            "end": end_date,      # Dùng cho lịch (ISO)
            "allDay": True,
            "color": "#00A859" if "TT" in detail or "Hà Nội" in detail else "#ED1C24",
            "extendedProps": {
                "full_name": CLASS_MAP.get(code, "Chương trình đào tạo nghiệp vụ"),
                "detail": detail,
                "display_start": f"08:00:00 {d_start}",
                "display_end": f"17:00:00 {d_end}"
            }
        })
    return events

try:
    events = load_and_group_data()
    st.title("🗓️ HỆ THỐNG LỊCH ĐÀO TẠO AGRIBANK 2026")
    st.markdown("---")

    calendar_options = {
        "initialView": "dayGridMonth",
        "displayEventTime": False,
        "headerToolbar": {
            "left": "prev,next today", "center": "title", "right": "dayGridMonth,listMonth",
        },
        "locale": "vi",
    }

    state = calendar(events=events, options=calendar_options, key='agri_cal_v6')

    if state.get("eventClick"):
        st.session_state.selected_event = state["eventClick"]["event"]

    # HIỂN THỊ TẠI THANH BÊN THEO FORMAT YÊU CẦU
    if "selected_event" in st.session_state:
        event = st.session_state.selected_event
        props = event['extendedProps']
        with st.sidebar:
            st.header("🔍 Chi tiết chương trình")
            st.success(f"**Tên chương trình:**\n\n{props['full_name']}")
            st.info(f"**Mã lớp & Địa điểm:**\n\n{props['detail']}")
            
            # Hiển thị ngày giờ theo định dạng ngày-tháng-năm và mốc 08:00 - 17:00
            st.warning(f"🕒 **Bắt đầu:** {props['display_start']}")
            st.error(f"⌛ **Kết thúc:** {props['display_end']}")
            
            if st.button("Đóng chi tiết"):
                del st.session_state.selected_event
                st.rerun()
    else:
        st.sidebar.write("📌 *Nhấn vào một lớp trên lịch để xem chi tiết.*")

except Exception as e:
    st.error(f"Lỗi: {e}")
