import streamlit as st
import pandas as pd
from streamlit_calendar import calendar
import os
import re
from datetime import datetime

st.set_page_config(page_title="Lịch Đào tạo Agribank 2026", layout="wide")

# 1. TỪ ĐIỂN TRA CỨU TÊN CHƯƠNG TRÌNH (Bổ sung đầy đủ mã lớp)
CLASS_MAP = {
    "PTDLHV": "Phân tích dữ liệu hành vi khách hàng",
    "KNSPCS": "Kỹ năng sư phạm chuyên sâu",
    "TCBV": "Phát triển tài chính bền vững",
    "TCS": "Tài chính số",
    "ESG": "Phân tích chuyên sâu báo cáo ESG",
    "AGCP": "Chương trình đào tạo cán bộ mới",
    "AGNV": "Nghiệp vụ ngân hàng cơ bản",
    "TQAI": "Tổng quan về AI trong ngân hàng",
    "AITD": "Ứng dụng AI trong công tác tín dụng",
    "AIKT": "Ứng dụng AI trong kế toán",
    "LĐM": "Lao động mới tuyển dụng",
    "PTDL": "Phân tích dữ liệu hành vi khách hàng",
    "KNBH": "Kỹ năng bán hàng và chăm sóc khách hàng chuyên nghiệp",
    "KNSP": "Kỹ năng sư phạm",
    "KHDN": "Nghiệp vụ cấp tín dụng khách hàng doanh nghiệp",
    "DBKT": "Dự báo kinh tế và phân tích thị trường",
    "AILDĐV": "AI nâng cao hiệu suất và tư duy Agile lãnh đạo đơn vị",
    "LĐ3C": "Kỹ năng lãnh đạo hiện đại 3C"
}

@st.cache_data
def load_and_group_data():
    all_raw_data = []
    # Quét tất cả file Excel trong thư mục
    files = [f for f in os.listdir('.') if f.endswith('.xlsx')]
    
    for file in files:
        try:
            df = pd.read_excel(file)
            for row in range(len(df)):
                for col in range(len(df.columns)):
                    cell_val = str(df.iloc[row, col])
                    if "-" in cell_val and ":" in cell_val:
                        # Tìm ngày tương ứng (tìm ngược lên tối đa 5 dòng)
                        date_found = None
                        for i in range(1, 6):
                            if row-i >= 0:
                                p_date = str(df.iloc[row-i, col])
                                # Sử dụng Regex để nhặt ra phần YYYY-MM-DD kể cả khi có giờ phía sau
                                date_match = re.search(r'(\d{4}-\d{2}-\d{2})', p_date)
                                if date_match:
                                    date_found = date_match.group(1)
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

    df_raw = pd.DataFrame(all_raw_data)
    if df_raw.empty: return []
    
    events = []
    # Gom nhóm theo nội dung lớp (detail) để xác định ngày bắt đầu và kết thúc
    for detail, group in df_raw.groupby('detail'):
        sorted_dates = sorted(group['date'].tolist())
        start_str = sorted_dates[0]
        end_str = sorted_dates[-1]
        
        # Chuyển đổi an toàn: chỉ lấy 10 ký tự đầu (YYYY-MM-DD) để tránh lỗi "00:00:00 remains"
        dt_start = datetime.strptime(start_str[:10], '%Y-%m-%d')
        dt_end = datetime.strptime(end_str[:10], '%Y-%m-%d')
        
        # Định dạng hiển thị Thanh bên: Ngày/Tháng/Năm
        display_start = dt_start.strftime('%d/%m/%Y')
        display_end = dt_end.strftime('%d/%m/%Y')

        # Trích xuất mã lớp để tra từ điển
        code_match = re.search(r'- ([A-Z0-9Đ]+)', detail)
        code = code_match.group(1) if code_match else "Lớp học"

        events.append({
            "title": detail,
            "start": start_str,
            "end": end_str,
            "allDay": True,
            "color": "#00A859" if any(x in detail for x in ["TT", "Hà Nội", "HNI"]) else "#ED1C24",
            "extendedProps": {
                "full_name": CLASS_MAP.get(code, "Chương trình đào tạo nghiệp vụ"),
                "detail": detail,
                "display_start": f"08:00:00 {display_start}",
                "display_end": f"17:00:00 {display_end}"
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

    state = calendar(events=events, options=calendar_options, key='agri_cal_final')

    if state.get("eventClick"):
        st.session_state.selected_event = state["eventClick"]["event"]

    # HIỂN THỊ THANH BÊN (SIDEBAR) THEO YÊU CẦU
    if "selected_event" in st.session_state:
        event = st.session_state.selected_event
        props = event['extendedProps']
        with st.sidebar:
            st.header("🔍 Chi tiết chương trình")
            st.success(f"**Tên chương trình:**\n\n{props['full_name']}")
            st.info(f"**Mã lớp & Địa điểm:**\n\n{props['detail']}")
            
            # Hiển thị Ngày-Tháng-Năm và giờ cố định
            st.warning(f"🕒 **Bắt đầu:** {props['display_start']}")
            st.error(f"⌛ **Kết thúc:** {props['display_end']}")
            
            if st.button("Đóng chi tiết"):
                del st.session_state.selected_event
                st.rerun()
    else:
        st.sidebar.write("📌 *Nhấn vào một lớp trên lịch để xem chi tiết.*")

except Exception as e:
    st.error(f"Lỗi: {e}")            "allDay": True,
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
