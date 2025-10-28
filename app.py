import streamlit as st
import time
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT 
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from io import BytesIO
import re

from docx.shared import Inches
# -----------------------------------------------------------------
# CÁC DÒNG IMPORT ỔN ĐỊNH NHẤT
# -----------------------------------------------------------------
import google.generativeai as genai
from google.generativeai import types

# 🚨 SỬA LỖI QUAN TRỌNG: ĐĂNG KÝ NAMESPACE 'w' TRƯỚC KHI SỬ DỤNG qn('w:...')
from docx.oxml.ns import _register_for_tag
_register_for_tag('w:topBdr') 
# -----------------------------------------------------------------

# -----------------------------------------------------------------
# 1. CẤU HÌNH "BỘ NÃO" AI VÀ PROMPT (GIỮ NGUYÊN)
# -----------------------------------------------------------------

# LẤY API KEY TỪ STREAMLIT SECRETS
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    st.error("LỖI CẤU HÌNH: Ứng dụng chưa được cung cấp 'GEMINI_API_KEY' trong Streamlit Secrets.")
    st.stop() 

# Cấu hình API key cho thư viện Gemini
genai.configure(api_key=API_KEY)

# Khởi tạo mô hình AI 
model = genai.GenerativeModel(model_name="gemini-2.5-flash")

# Đây là "Prompt Gốc" (GIỮ NGUYÊN)
PROMPT_GOC = """
CẢNH BÁO QUAN TRỌNG: TUYỆT ĐỐI KHÔNG SỬ DỤNG BẤT KỲ THẺ HTML NÀO (ví dụ: <br/>, <strong>). Hãy dùng định dạng MARKDOWN thuần túy (dấu * hoặc - cho gạch đầu dòng và xuống dòng tự động).

Bạn là một chuyên gia giáo dục Tiểu học hàng đầu Việt Nam, am hiểu sâu sắc Chương trình GDPT 2018 và kỹ thuật thiết kế Kế hoạch Bài Dạy (giáo án) theo Công văn 2345.

Nhiệm vụ của bạn là soạn một Kế hoạch bài dạy chi tiết, sáng tạo, tập trung vào phát triển năng lực và phẩm chất.

DỮ LIỆU ĐẦU VÀO:
1.  **Môn học:** {mon_hoc}
2.  **Lớp:** {lop}
3.  **Bộ sách:** {bo_sach}
4.  **Tên bài học/Chủ đề:** {ten_bai}
5.  **Yêu cầu cần đạt (Lấy từ Chương trình môn học):** {yeu_cau}
7.  **Yêu cầu tạo phiếu bài tập:** {yeu_cau_phieu} (Dựa vào đây để quyết định có tạo phiếu bài tập hay không)

YÊU CẦU VỀ ĐỊNH DẠNG:
Bạn PHẢI tuân thủ tuyệt đối cấu trúc và các yêu cầu sau:

**I. Yêu cầu cần đạt**
(Phát biểu cụ thể học sinh thực hiện được việc gì; vận dụng được những gì, phẩm chất, năng lực gì.)
1.  **Về kiến thức:** (Bám sát {yeu_cau})
2.  **Về năng lực:** (Năng lực chung: Tự chủ và tự học, Giao tiếp và hợp tác, Giải quyết vấn đề và sáng tạo; Năng lực đặc thù của môn {mon_hoc})
3.  **Về phẩm chất:** (Chọn 1-2 trong 5 phẩm chất: Yêu nước, Nhân ái, Chăm chỉ, Trung thực, Trách nhiệm)

**II. Đồ dùng dạy học**
(Nêu các thiết bị, học liệu được sử dụng trong bài dạy. Nếu Yêu cầu tạo phiếu bài tập là CÓ, phải nhắc đến Phiếu bài tập trong mục này.)
1.  **Chuẩn bị của giáo viên (GV)::** (Tranh ảnh, video, phiếu học tập, link game...)
2.  **Chuẩn bị của học sinh (HS):** (SGK, Vở bài tập, bút màu...)

**III. Các hoạt động dạy học chủ yếu**
**QUY TẮC CỰC KỲ QUAN TRỌNG:** Toàn bộ nội dung của mục 3 này PHẢI được trình bày trong **MỘT BẢNG MARKDOWN DUY NHẤT** có 2 cột.
**QUY TẮC BẮT BUỘC SỐ 2 (NỘI DUNG):** Nội dung trong từng ô phải được trình bày dưới dạng gạch đầu dòng MARKDOWN (dấu * hoặc -) để xuống dòng.

| Hoạt động của giáo viên | Hoạt động của học sinh |
| :--- | :--- |
| **1. Hoạt động Mở đầu (Khởi động, Kết nối)** | **1. Hoạt động Mở đầu (Khởi động, Kết nối)** |
| *Mục tiêu: Tạo tâm thế vui vẻ, hứng thú.* | *Mục tiêu: Đạt được mục tiêu GV đề ra.* |
| **Cách tiến hành:** (Viết chi tiết, dùng dấu gạch đầu dòng `*` cho mỗi bước) | **Cách tiến hành:** (Viết chi tiết các hoạt động tương tác của HS) |
| **2. Hoạt động Hình thành kiến thức mới (Trải nghiệm, Khám phá)** | **2. Hoạt động Hình thành kiến thức mới (Trải nghiệm, Khám phá)** |
| *Mục tiêu: (Bám sát {yeu_cau} để hình thành kiến thức mới)* | *Mục tiêu: Đạt được mục tiêu GV đề ra.* |
| **Cách tiến hành:** (Viết chi tiết, dùng dấu gạch đầu dòng `*` cho mỗi bước) | **Cách tiến hành:** (Viết chi tiết các bước HS quan sát, thảo luận) |
| **3. Hoạt động Luyện tập, Thực hành** | **3. Hoạt động Luyện tập, Thực hành** |
| *Mục tiêu: Áp dụng kiến thức, rèn kỹ năng. Nếu yeu_cau_phieu là CÓ, GV phải giao Phiếu bài tập trong hoạt động này.* | *Mục tiêu: Đạt được mục tiêu GV đề ra.* |
| **Cách tiến hành:** (Viết chi tiết, dùng dấu gạch đầu dòng `*` cho mỗi bước) | **Cách tiến hành:** (Viết chi tiết các bước HS thực hành cá nhân/nhóm) |
| **4. Hoạt động Vận dụng, Trải nghiệm (Củng cố)** | **4. Hoạt động Vận dụng, Trải nghiệm (Củng cố)** |
| *Mục tiêu: Liên hệ thực tế, củng cố bài.* | *Mục tiêu: Đạt được mục tiêu GV đề ra.* |
| **Cách tiến hành:** (Viết chi tiết, dùng dấu gạch đầu dòng `*` cho mỗi bước) | **Cách tiến hành:** (Viết chi tiết các bước HS trả lời, cam kết hành động) |

---

**PHẦN IV. ĐIỀU CHỈNH SAU BÀI DẠY (NẾU CÓ)**
*(Đây là phần để trống để giáo viên ghi chú lại sau khi thực tế giảng dạy)*
1.  **Về nội dung, kiến thức:**
    * ......................................................................
    * ......................................................................
2.  **Về phương pháp, kỹ thuật tổ chức:**
    * ......................................................................
    * ......................................................................
3.  **Về học sinh (những khó khăn, điểm cần lưu ý):**
    * ......................................................................
    * ......................................................................

---

**PHẦN V. PHIẾU BÀI TẬP (NẾU CÓ)**
(QUAN TRỌNG: Bạn CHỈ tạo phần này nếu DỮ LIỆU ĐẦU VÀO số 6 `{yeu_cau_phieu}` là 'CÓ'. Nếu là 'KHÔNG', hãy bỏ qua hoàn toàn phần này và không đề cập gì đến nó.)

- Nếu `{yeu_cau_phieu}` là 'CÓ':
- Hãy thiết kế một Phiếu bài tập (Worksheet) ngắn gọn, bám sát nội dung của **Hoạt động 3: Luyện tập / Thực hành**.
- Phiếu phải được trình bày sinh động, vui nhộn, phù hợp với học sinh tiểu học (ví dụ: dùng emojis 🌟, 🦋, 🖍️, 🐝, lời dẫn thân thiện, có khung viền đơn giản).
- Đặt tên phiếu rõ ràng (ví dụ: PHIẾU BÀI TẬP - BÀI: {ten_bai}).
- Bao gồm 2-3 bài tập nhỏ (ví dụ: nối, điền từ, khoanh tròn).

---
Hãy bắt đầu tạo giáo án.
"""

# -----------------------------------------------------------------
# 2. KHỐI HÀM XỬ LÝ WORD (ĐÃ FIX LỖI NAMESPACE 'w')
# -----------------------------------------------------------------

# Các mẫu regex để nhận diện các loại tiêu đề
ACTIVITY_HEADERS_PATTERN = re.compile(r'^\s*(\*\*|)(\d+\.\sHoạt động.*?)(\*\*|)\s*', re.IGNORECASE)
SUB_ACTIVITY_HEADERS_PATTERN = re.compile(r'^\s*(\*\*|)([a-z]\)\s.*?)(\*\*|)\s*', re.IGNORECASE)

# Loại bỏ mọi trường hợp "Cách tiến hành" và dấu ** thừa
def clean_content(text):
    text = re.sub(r'Cách tiến hành[:]*\s*', '', text, flags=re.IGNORECASE).strip()
    # Loại bỏ triệt để dấu ** thừa
    return text.replace('**', '')

# --- HÀM HỖ TRỢ TẮT/BẬT VIỀN (ĐÃ FIX LỖI set_cell_border NOT DEFINED) ---
def set_cell_border(cell, **kwargs):
    """
    Tùy chỉnh viền của một ô (cell) trong Word.
    """
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()

    borders = {
        'top': 'w:topBdr', 'left': 'w:leftBdr', 'bottom': 'w:bottomBdr', 'right': 'w:rightBdr',
        'insideH': 'w:insideH', 'insideV': 'w:insideV'
    }

    for border_name, border_tag in borders.items():
        if border_name in kwargs:
            bdr = OxmlElement(border_tag)
            
            for key, value in kwargs[border_name].items():
                bdr.set(qn('w:' + key), str(value))
                
            # Xóa viền cũ và thêm viền mới
            for element in tcPr.findall(border_tag):
                tcPr.remove(element)

            tcPr.append(bdr)

# --- HÀM TẠO FILE WORD CHÍNH ---
def create_word_document(markdown_text, lesson_title):
    document = Document()
    
    # Thiết lập font size mặc định cho Normal style
    document.styles['Normal'].font.size = Pt(12) 
    
    # 1. THÊM TIÊU ĐỀ CHÍNH (Yêu cầu: Căn giữa)
    if lesson_title:
        p_heading = document.add_heading(f"KẾ HOẠCH BÀI DẠY: {lesson_title.upper()}", level=1)
        p_heading.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        document.add_paragraph() 
    
    lines = markdown_text.split('\n')
    is_in_table_section = False
    table = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # 1. PHÁT HIỆN BẢNG (III. Các hoạt động dạy học chủ yếu)
        if re.match(r'\|.*Hoạt động của giáo viên.*\|.*Hoạt động của học sinh.*\|', line, re.IGNORECASE):
            is_in_table_section = True
            document.add_heading("III. Các hoạt động dạy học chủ yếu", level=2)
            
            # Tạo bảng 2 cột
            table = document.add_table(rows=1, cols=2)
            table.autofit = False
            table.columns[0].width = Inches(3.5) 
            table.columns[1].width = Inches(3.5)
            
            # Thiết lập headers (Hàng đầu tiên)
            hdr_cells = table.rows[0].cells
            hdr_cells[0].text = "Hoạt động của giáo viên"
            hdr_cells[1].text = "Hoạt động của học sinh"
            
            # Tùy chỉnh viền cho Header (Viền trên ngoài cùng và viền dưới phân cách)
            for cell in hdr_cells:
                set_cell_border(cell, 
                    top={"val": "single", "sz": 12, "color": "auto"},
                    bottom={"val": "single", "sz": 12, "color": "auto"},
                    left={"val": "single", "sz": 12, "color": "auto"},
                    right={"val": "single", "sz": 12, "color": "auto"}
                )
            
            continue
            
        # 2. XỬ LÝ NỘI DUNG BÊN TRONG BẢNG
        if is_in_table_section and table is not None:
            if line.startswith('| :---'):
                continue
            
            # Thoát khỏi bảng khi gặp tiêu đề lớn (PHẦN IV)
            if re.match(r'^[IVX]+\.\s|PHẦN\s[IVX]+\.', line) or line.startswith('---'):
                is_in_table_section = False
                if re.match(r'^[IVX]+\.\s|PHẦN\s[IVX]+\.', line):
                    document.add_heading(line.strip().strip('**'), level=2)
                continue
            
            if line.startswith('|') and len(line.split('|')) >= 3:
                cells_content = [c.strip() for c in line.split('|')[1:-1]]
                
                if len(cells_content) == 2:
                    
                    gv_content = clean_content(cells_content[0])
                    hs_content = clean_content(cells_content[1])
                    
                    # --- KIỂM TRA TIÊU ĐỀ HOẠT ĐỘNG HOẶC TIÊU ĐỀ PHỤ ---
                    is_main_header = ACTIVITY_HEADERS_PATTERN.match(gv_content)
                    is_sub_header = SUB_ACTIVITY_HEADERS_PATTERN.match(gv_content)
                    
                    if is_main_header or is_sub_header:
                        title = gv_content.strip()

                        row_cells = table.add_row().cells 
                        row_cells[0].merge(row_cells[1]) # GỘP CỘT

                        p = row_cells[0].add_paragraph(title)
                        p.runs[0].bold = True 
                        
                        # --- XỬ LÝ VIỀN CHO HÀNG TIÊU ĐỀ HOẠT ĐỘNG (Kẻ ngang phân cách) ---
                        set_cell_border(row_cells[0], 
                            top={"val": "single", "sz": 12, "color": "auto"}, # Viền trên
                            bottom={"val": "single", "sz": 12, "color": "auto"}, # Viền dưới
                            left={"val": "single", "sz": 12, "color": "auto"},
                            right={"val": "single", "sz": 12, "color": "auto"}
                        )
                        
                        continue
                        
                    # --- XỬ LÝ NỘI DUNG THƯỜNG ---
                    else:
                        # TẠO HÀNG MỚI CHO NỘI DUNG GV-HS ĐỒNG BỘ
                        row_cells = table.add_row().cells 
                        
                        # --- TẮT VIỀN NGANG GIỮA CÁC HÀNG NỘI DUNG (ĐÃ SỬA LỖI KẺ NGANG THỪA) ---
                        for cell in row_cells:
                            set_cell_border(cell, 
                                top={"val": "none"}, 
                                bottom={"val": "none"},
                                left={"val": "single", "sz": 12, "color": "auto"},
                                right={"val": "single", "sz": 12, "color": "auto"}
                            )
                        
                        # Xử lý nội dung (GV và HS) từng dòng một để đảm bảo đồng bộ
                        gv_lines_raw = [l.strip() for l in gv_content.split('\n') if l.strip()]
                        hs_lines_raw = [l.strip() for l in hs_content.split('\n') if l.strip()]
                        max_lines = max(len(gv_lines_raw), len(hs_lines_raw))
                        
                        for i in range(max_lines):
                            gv_line = gv_lines_raw[i] if i < len(gv_lines_raw) else ""
                            hs_line = hs_lines_raw[i] if i < len(hs_lines_raw) else ""

                            for cell_index, line_text in enumerate([gv_line, hs_line]):
                                p = row_cells[cell_index].add_paragraph()
                                if not line_text:
                                    continue
                                
                                # Xử lý gạch đầu dòng (buộc dùng List Bullet cho các mục list)
                                if line_text.startswith('*') or line_text.startswith('-') or re.match(r'^\d+\.\s', line_text):
                                    clean_text = re.sub(r'^[*-]\s*|^\d+\.\s*', '', line_text).strip()
                                    p.text = clean_text
                                    p.style = 'List Bullet' 
                                else:
                                    p.text = line_text
                        
                        continue
            
        # 3. XỬ LÝ NỘI DUNG BÊN NGOÀI BẢNG
        
        # Xử lý tiêu đề chính 
        if re.match(r'^[IVX]+\.\s|PHẦN\s[IVX]+\.', line):
            clean_line = line.strip().strip('**')
            document.add_heading(clean_line, level=2)
            
        # Xử lý tiêu đề con
        elif line.startswith('**') and line.endswith('**'):
            clean_line = line.strip('**').strip()
            # Căn giữa Phiếu bài tập
            if 'PHIẾU BÀI TẬP' in clean_line.upper() or 'ĐIỀU CHỈNH' in clean_line.upper():
                p = document.add_heading(clean_line, level=3)
                p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
            else:
                document.add_heading(clean_line, level=3)
            
        # Xử lý gạch đầu dòng Markdown 
        elif line.startswith('*') or line.startswith('-') or re.match(r'^\d+\.\s', line):
            clean_text = re.sub(r'^[*-]\s*|^\d+\.\s*', '', line).strip()
            document.add_paragraph(clean_text, style='List Bullet')
            
        # Xử lý văn bản thuần túy
        else:
            document.add_paragraph(line)
            
    # --- XỬ LÝ VIỀN DƯỚI CỦA HÀNG CUỐI CÙNG TRONG BẢNG ---
    if table and len(table.rows) > 1:
        last_row_cells = table.rows[-1].cells
        for cell in last_row_cells:
            # Chỉ thêm viền dưới để đóng bảng
            set_cell_border(cell, 
                bottom={"val": "single", "sz": 12, "color": "auto"},
                # Đảm bảo viền trên vẫn bị tắt
                top={"val": "none"}, 
                left={"val": "single", "sz": 12, "color": "auto"},
                right={"val": "single", "sz": 12, "color": "auto"}
            )
            
    # Lưu tài liệu vào bộ nhớ (BytesIO)
    bio = BytesIO()
    document.save(bio)
    bio.seek(0)
    return bio

# -----------------------------------------------------------------
# 3. KHỐI LOGIC CHẠY STREAMLIT (UI) - GIỮ NGUYÊN
# -----------------------------------------------------------------

st.title("🤖 Giáo án thông minh - 🚀 [App Tên Bạn]")

# Tạo các trường nhập liệu
with st.form(key='giáo_án_form'):
    st.subheader("📝 Thông tin cơ bản:")
    col1, col2 = st.columns(2)
    with col1:
        mon_hoc = st.selectbox("Môn học:", ["Tiếng Việt", "Toán", "Đạo đức", "Khoa học"])
    with col2:
        lop = st.selectbox("Lớp:", ["1", "2", "3", "4", "5"])
        
    bo_sach = st.text_input("Bộ sách (ví dụ: Chân trời sáng tạo):", "Kết nối tri thức với cuộc sống")
    ten_bai = st.text_input("Tên bài giảng:", "Bài 2: Ngày hôm qua đâu rồi?")

    st.subheader("💡 Yêu cầu chi tiết:")
    yeu_cau = st.text_area(
        "Yêu cầu về kiến thức/nội dung bài giảng (Dán nội dung từ PPCT hoặc sách giáo khoa vào đây):",
        "Đọc đúng, trôi chảy toàn bài thơ. Hiểu được nội dung bài thơ: Ngày hôm qua không mất đi mà hóa thành những điều có ích."
    )
    
    yeu_cau_phieu_value = st.text_area(
        "Nội dung cho Phiếu bài tập (Nếu không cần, để trống):",
        "Bài 1: Nối đúng ý. Bài 2: Khoanh tròn đáp án đúng. Bài 3: Điền từ còn thiếu vào khổ thơ."
    )

    uploaded_files = st.file_uploader("🖼️ Tải lên hình ảnh/tài liệu tham khảo (Tùy chọn):", type=["png", "jpg", "jpeg", "pdf", "docx"], accept_multiple_files=True)

    submit_button = st.form_submit_button(label='✨ Tạo Giáo án')

if submit_button:
    # 1. Chuẩn bị danh sách Content cho AI
    content = []
    
    # Xử lý các file được tải lên
    if uploaded_files:
        st.info(f"Đang xử lý {len(uploaded_files)} file. Quá trình có thể mất vài giây...")
        for uploaded_file in uploaded_files:
            try:
                # Đọc file nhị phân
                file_bytes = uploaded_file.read()
                
                # Tạo đối tượng Part cho file
                file_part = types.Part.from_bytes(
                    data=file_bytes,
                    mime_type=uploaded_file.type
                )
                content.append(file_part)
            except Exception as e:
                st.warning(f"Không thể đọc file {uploaded_file.name}. Bỏ qua file này. Lỗi: {e}")

    if mon_hoc and lop and ten_bai and yeu_cau:
        with st.spinner('⏳ AI đang biên soạn Giáo án, xin chờ một chút...'):
            try:
                # 2. Điền Prompt (6 biến số text)
                final_prompt = PROMPT_GOC.format(
                    mon_hoc=mon_hoc,
                    lop=lop,
                    bo_sach=bo_sach,
                    ten_bai=ten_bai,
                    yeu_cau=yeu_cau,
                    yeu_cau_phieu=yeu_cau_phieu_value
                )
                # Thêm Prompt vào danh sách Content (luôn luôn có)
                content.append(final_prompt)

                # 3. Gọi AI với danh sách nội dung (content)
                response = model.generate_content(content)
                full_text = response.text
                
                # 4. Hiển thị kết quả
                st.balloons() 
                st.subheader("🎉 Giáo án của bạn đã sẵn sàng:")
                
                # --- SỬA LỖI: Lọc bỏ phần giải thích thừa của AI (nếu có) ---
                start_marker = "KẾ HOẠCH BÀI DẠY:"
                start_index = full_text.find(start_marker)

                if start_index != -1:
                    cleaned_text = full_text[start_index:]
                else:
                    cleaned_text = full_text

                st.markdown(cleaned_text) 
                
                # BẮT ĐẦU KHỐI CODE TẢI XUỐNG WORD
                word_bytes = create_word_document(cleaned_text, ten_bai) 
                
                st.download_button(
                    label="⬇️ Tải về Giáo án (Word)",
                    data=word_bytes,
                    file_name=f"GA_{ten_bai.replace(' ', '_')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            except Exception as e:
                st.error(f"Đã có lỗi xảy ra: {e}")
                st.error("Lỗi này có thể do API Key sai, hoặc do chính sách an toàn của Google. Vui lòng kiểm tra lại.")

# BẮT ĐẦU PHẦN SIDEBAR
st.sidebar.title("Giới thiệu")
st.sidebar.info(
"""
Sản phẩm của Hoàng Tọng Nghĩa, Trường Tiểu học Hồng Gai. tham gia ngày hội "Nhà giáo sáng tạo với công nghệ số và trí tuệ nhân tạo".

Sản phẩm ứng dụng AI để tự động biên soạn giáo án Tiểu học theo các tiêu chí sư phạm.
"""
)
st.sidebar.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRz-5c742Z_R6zB4u-7S5Q6w0x-X5uW1k6Fsg&s")
