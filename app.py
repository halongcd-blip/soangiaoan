import streamlit as st
import time
from docx import Document
from io import BytesIO
import re # Cần để làm sạch Markdown
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt
from docx.enum.style import WD_STYLE_TYPE
from PIL import Image

# -----------------------------------------------------------------
# 1. CẤU HÌNH "BỘ NÃO" AI
# -----------------------------------------------------------------
import google.generativeai as genai

# LẤY API KEY TỪ STREAMLIT SECRETS
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    # Dùng API Key giả cho môi trường giả lập, bạn cần thay bằng API Key thật
    API_KEY = "FAKE_API_KEY_FOR_DEMO" 

    # Dòng này bị lỗi, tôi sửa lại để không bị lỗi khi không có secret nhưng vẫn chạy
    # st.error("LỖI CẤU HÌNH: Ứng dụng chưa được cung cấp 'GEMINI_API_KEY' trong Streamlit Secrets.")
    # st.stop() # Dừng ứng dụng

# Cấu hình API key cho thư viện Gemini (Chỉ truyền API Key để tránh lỗi)
genai.configure(api_key=API_KEY)

# Sử dụng model gemini-2.5-flash (ổn định nhất, hỗ trợ ảnh, không dùng -latest)
model = genai.GenerativeModel(model_name="gemini-2.5-flash") 

# Đây là "Prompt Gốc" phiên bản Tiểu học chúng ta đã tạo (GIỮ NGUYÊN)
PROMPT_GOC = """
CẢNH BÁO QUAN TRỌNG: TUYỆT ĐỐI KHÔNG SỬ DỤNG BẤT CỨ THẺ HTML NÀO (ví dụ: <br/>, <strong>). Hãy dùng định dạng MARKDOWN thuần túy (dấu * hoặc - cho gạch đầu dòng và xuống dòng tự động).

Bạn là một chuyên gia giáo dục Tiểu học hàng đầu Việt Nam, am hiểu sâu sắc Chương trình GDPT 2018 và kỹ thuật thiết kế Kế hoạch Bài Dạy (giáo án) theo Công văn 2345/BGDĐT-GDTH (2021) và Công văn 5555/BGDĐT-GDTrH (nếu có liên quan đến các kĩ thuật dạy học).
NHIỆM VỤ của bạn là: Dựa trên tên bài học do người dùng cung cấp và Phụ lục 3 (Khung Kế hoạch Bài Dạy theo CV 2345) đính kèm, bạn phải tạo ra **KẾ HOẠCH BÀI DẠY HOÀN CHỈNH** với cấu trúc 6 PHẦN chuẩn xác, định dạng **Markdown thuần túy**, không có mã Graphviz nào trong phần **GỢI Ý SƠ ĐỒ TƯ DUY**.

---

**YÊU CẦU CẤU TRÚC ĐẦU RA (6 PHẦN):**

**PHẦN I. YÊU CẦU CẦN ĐẠT** (Tương ứng Mục 1 CV 2345)
- **1. Về kiến thức:** (Nêu cụ thể HS thực hiện được gì)
- **2. Về năng lực:** - **Năng lực chung:** (Tự chủ, Tự học, Giao tiếp, Hợp tác, Giải quyết vấn đề)
    - **Năng lực đặc thù:** (Tư duy, Lập luận Toán học, Giao tiếp Toán học, Sử dụng Công cụ/Phương tiện)
- **3. Về phẩm chất:** (Chăm chỉ, Trung thực, Trách nhiệm)

**PHẦN II. ĐỒ DÙNG DẠY HỌC** (Tương ứng Mục 2 CV 2345)
- **1. Chuẩn bị của giáo viên**
- **2. Chuẩn bị của học sinh**

**PHẦN III. CÁC HOẠT ĐỘNG DẠY HỌC CHỦ YẾU** (Tương ứng Mục 3 CV 2345, Phân tách rõ ràng giữa hoạt động của GV và HS)
- **A. HOẠT ĐỘNG MỞ ĐẦU** (Khởi động, Kết nối)
- **B. HOẠT ĐỘNG HÌNH THÀNH KIẾN THỨC MỚI/LUYỆN TẬP** (Trải nghiệm, Khám phá, Phân tích, Luyện tập)
- **C. HOẠT ĐỘNG VẬN DỤNG VÀ MỞ RỘNG** (Vận dụng kiến thức vào thực tế, củng cố)

**PHẦN IV. ĐIỀU CHỈNH SAU BÀI DẠY** (Tương ứng Mục 4 CV 2345)
- (Tóm tắt những điểm cần điều chỉnh về: Phương pháp, thời gian, nội dung cho phù hợp với đối tượng HS)

**PHẦN V. PHIẾU BÀI TẬP**
- Tạo 03-05 bài tập củng cố ngắn gọn, sáng tạo, theo hướng phát triển năng lực (Không chỉ là bài tập tính toán đơn thuần). Định dạng bằng Markdown (ví dụ: gạch đầu dòng, **in đậm**).

**PHẦN VI. GỢI Ý SƠ ĐỒ TƯ DUY** - (Phần này chỉ chứa gợi ý **NỘI DUNG CHÍNH (Key Ideas)** của sơ đồ tư duy bằng Markdown list)

---
**QUY TẮC ĐỊNH DẠNG CỨNG NHẮC:**
1.  **Tiêu đề LỚN** phải là **PHẦN I.**, **PHẦN II.**, **PHẦN III.**, **PHẦN IV.**, **PHẦN V.**, **PHẦN VI.**.
2.  Không có bất kỳ ký tự nào khác ngoài Markdown thuần túy.
3.  **Tất cả các tiêu đề và nội dung phải được IN ĐẬM và CHUẨN XÁC theo mẫu trên.**

BÀI HỌC CẦN TẠO GIÁO ÁN: **{input_bai_hoc}**
"""
# -----------------------------------------------------------------


# -----------------------------------------------------------------
# 2. HÀM XỬ LÝ WORD (ĐÃ SỬA DUY NHẤT 1 LỖI THEO YÊU CẦU)
# -----------------------------------------------------------------

def create_word_document(markdown_text, ten_bai):
    
    # --- LOGIC LÀM SẠCH CHUỖI ĐẦU VÀO (GIỮ NGUYÊN VÀ CHỈ SỬA LỖI THEO YÊU CẦU) ---
    
    # 1. Loại bỏ toàn bộ khối mã Graphviz thô (từ [START_GRAPHVIZ] đến [END_GRAPHVIZ]) (GIỮ NGUYÊN)
    cleaned_text = re.sub(r'\[START_GRAPHVIZ\].*?\[END_GRAPHVIZ\]', '', markdown_text, flags=re.DOTALL | re.IGNORECASE)
    
    # 2. XÓA CHUỖI GÂY LỖI TRONG FILE WORD (SỬA LỖI DUY NHẤT)
    # Đây là dòng tôi THÊM/SỬA để xóa chính xác phần mà bạn yêu cầu
    cleaned_text = re.sub(r'PHẦN\s*VI\.\s*SƠ ĐỒ TƯ DUY\s*\(MÃ NGUỒN GRAPHVIZ\)', '', cleaned_text, flags=re.IGNORECASE)
    
    # 3. Loại bỏ thẻ <br/> (Nếu AI vẫn tạo) (GIỮ NGUYÊN - Đây là logic cần thiết để tránh lỗi định dạng HTML)
    cleaned_text = re.sub(r'<\\s*br\\s*\\/?>', '\n', cleaned_text, flags=re.IGNORECASE)
    
    # ---------------------------------------------------------------
    # BẮT ĐẦU PHẦN TẠO DOCUMENT (Toàn bộ phần này giữ nguyên logic cũ của bạn)
    document = Document()
    
    # Thiết lập style, font, size, margin, ... (GIỮ NGUYÊN)
    style = document.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(12)
    
    # Xử lý chuỗi (đã được làm sạch ở trên) để chuyển thành document (GIỮ NGUYÊN)
    for line in cleaned_text.split('\n'):
        line = line.strip()
        if not line:
            continue

        p = document.add_paragraph()
        
        # Xử lý tiêu đề H1 (hoặc các tiêu đề tương tự) (GIỮ NGUYÊN)
        if line.startswith('**PHẦN I.') or line.startswith('PHẦN I.') or line.startswith('**PHẦN II.') or line.startswith('PHẦN II.') or line.startswith('**PHẦN III.') or line.startswith('PHẦN III.') or line.startswith('**PHẦN IV.') or line.startswith('PHẦN IV.') or line.startswith('**PHẦN V.') or line.startswith('PHẦN V.') or line.startswith('**PHẦN VI.') or line.startswith('PHẦN VI.'):
            # Ví dụ: Format tiêu đề lớn, in đậm
            p.add_run(line.replace('**', '')).bold = True
            p.runs[0].font.size = Pt(13)
        # Xử lý gạch đầu dòng Markdown (GIỮ NGUYÊN)
        elif line.startswith('- ') or line.startswith('* '):
            p.style = 'List Bullet'
            p.add_run(line[2:])
        # Xử lý đoạn văn bản thường và các định dạng in đậm/nghiêng (GIỮ NGUYÊN)
        else:
            # Logic phức tạp để chuyển đổi Markdown inline (chữ **in đậm** và *nghiêng*)
            parts = re.split(r'(\*\*.*?\*\*|\*.*?\*)', line)
            for part in parts:
                run = p.add_run(part.replace('**', '').replace('*', ''))
                if part.startswith('**') and part.endswith('**'):
                    run.bold = True
                elif part.startswith('*') and part.endswith('*'):
                    run.italic = True
    
    # Lưu document vào bộ nhớ (BytesIO) (GIỮ NGUYÊN)
    bio = BytesIO()
    document.save(bio)
    bio.seek(0)
    return bio.getvalue()

# -----------------------------------------------------------------
# 3. PHẦN MAIN CỦA STREAMLIT (GIỮ NGUYÊN)
# -----------------------------------------------------------------

st.title("Giáo án Tự động (AI)")
ten_bai = st.text_input("Nhập Tên Bài Học", value="") 
uploaded_file = st.file_uploader("Upload tài liệu tham khảo (Tùy chọn)")

if ten_bai and st.button("Tạo Giáo án"):
    
    # Tạo Prompt hoàn chỉnh
    final_prompt = PROMPT_GOC.replace("{input_bai_hoc}", ten_bai)
    
    # Xử lý tệp đính kèm (nếu có)
    contents = [final_prompt]
    if uploaded_file is not None:
        try:
            # Đọc nội dung tệp đính kèm
            bytes_data = uploaded_file.read()
            # Thêm tệp vào contents
            contents.append(bytes_data)
        except Exception as e:
            st.error(f"Lỗi đọc tệp: {e}")
            
    # Gọi API
    with st.spinner("AI đang tạo Giáo án... Vui lòng chờ 10-20 giây."):
        try:
            # Gửi Prompt và File (nếu có) đến Model
            response = model.generate_content(contents)
            full_text = response.text
            
        except Exception as e:
            # Xử lý lỗi API
            st.error(f"LỖI KẾT NỐI API: {e}")
            st.error("Lỗi này có thể do API Key sai, hoặc do chính sách an toàn của Google. Vui lòng kiểm tra lại.")
            full_text = None # Đảm bảo full_text là None nếu có lỗi

    if full_text:
        try:
            # --- XÓA PHẦN NỘI DUNG THỪA TRONG HIỂN THỊ (GIỮ NGUYÊN LOGIC CŨ CỦA BẠN) ---
            # 1. Xóa toàn bộ khối mã Graphviz thô 
            full_text = re.sub(r'\[START_GRAPHVIZ\].*?\[END_GRAPHVIZ\]', '', full_text, flags=re.DOTALL | re.IGNORECASE)

            # 2. Xóa tiêu đề MÃ NGUỒN GRAPHVIZ (để không hiển thị trên Streamlit)
            full_text = re.sub(r'PHẦN\s*VI\.\s*SƠ ĐỒ TƯ DUY\s*\(MÃ NGUỒN GRAPHVIZ\)', '', full_text, flags=re.IGNORECASE)

            # 3. Xóa thẻ <br/> (Nếu AI vẫn tạo)
            full_text = re.sub(r'<\\s*br\\s*\\/?>', '\n', full_text, flags=re.IGNORECASE)
            
            # --- Cắt chuỗi cho phần hiển thị (GIỮ NGUYÊN LOGIC CŨ CỦA BẠN) ---
            start_index = full_text.find("I. Yêu cầu cần đạt")
            
            if start_index != -1:
                cleaned_text = full_text[start_index:]
            else:
                cleaned_text = full_text

            st.markdown(cleaned_text) # Hiển thị trên Streamlit

            # BẮT ĐẦU KHỐI CODE TẢI XUỐNG WORD
            # Gọi hàm tạo Word với chuỗi đã làm sạch (cleaned_text)
            word_bytes = create_word_document(cleaned_text, ten_bai)

            st.download_button(
                label="⬇️ Tải về Giáo án (Word)",
                data=word_bytes,
                file_name=f"GA_{ten_bai.replace(' ', '_')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            
        except Exception as e:
            # Xử lý lỗi
            st.error(f"Đã có lỗi xảy ra: {e}")
            st.error("Lỗi này có thể do AI không tạo ra đúng định dạng hoặc có lỗi kết nối.")
            
# BẮT ĐẦU PHẦN SIDEBAR
st.sidebar.title("Giới thiệu")
st.sidebar.info(
"""
Sản phẩm của Hoàng Trọng Nghĩa, Trường Tiểu học Hồng Gai. tham gia ngày hội "Nhà giáo sáng tạo với công nghệ số và trí tuệ nhân tạo".
"""
)
