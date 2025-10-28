import streamlit as st
import time
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT 
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from io import BytesIO
import re
from io import BytesIO

from docx.shared import Inches
# -----------------------------------------------------------------
# CÁC DÒNG IMPORT ỔN ĐỊNH NHẤT
# -----------------------------------------------------------------
import google.generativeai as genai
# Lớp Part nằm trực tiếp ở thư viện gốc, không qua module 'types'
from google.generativeai import types
# -----------------------------------------------------------------

# -----------------------------------------------------------------
# 1. CẤU HÌNH "BỘ NÃO" AI
# -----------------------------------------------------------------

# LẤY API KEY TỪ STREAMLIT SECRETS
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    st.error("LỖI CẤU HÌNH: Ứng dụng chưa được cung cấp 'GEMINI_API_KEY' trong Streamlit Secrets.")
    st.stop() # Dừng ứng dụng

# Cấu hình API key cho thư viện Gemini
genai.configure(api_key=API_KEY)

# Khởi tạo mô hình AI (Cú pháp này hoàn toàn đúng với gói google-generativeai)
model = genai.GenerativeModel(model_name="gemini-2.5-flash")

# Đây là "Prompt Gốc" phiên bản Tiểu học chúng ta đã tạo
# Toàn bộ "bộ não" sư phạm nằm ở đây
PROMPT_GOC = """
CẢNH BÁO QUAN TRỌNG: TUYỆT ĐỐI KHÔNG SỬ DỤNG BẤT KỲ THẺ HTML NÀO (ví dụ: <br/>, <strong>). Hãy đảm bảo các phần sau:
1. TIÊU ĐỀ: Các tiêu đề chính (Kế hoạch bài dạy, PHIẾU BÀI TẬP) phải được TÔ ĐEN (sử dụng **...**), và các tiêu đề con (Về kiến thức, Năng lực chung) phải được TÔ ĐEN (sử dụng **...**).
2. BẢNG HOẠT ĐỘNG:
    a) Phải có Bảng Hoạt động (Hoạt động của giáo viên | Hoạt động của học sinh).
    b) Các nội dung (Hoạt động 1, Hoạt động a)...) trong bảng phải được phân tách bằng DÒNG NỘI DUNG MỚI, KHÔNG DÙNG THẺ <br/>.
    c) Phải duy trì sự đối ứng (đồng bộ) giữa cột Giáo viên và Học sinh, mỗi câu/ý của GV phải đối ứng với câu/ý của HS trên cùng một hàng ngang.
    d) KHÔNG SỬ DỤNG DẤU ** trong nội dung thường.
    e) Các mục list (gạch đầu dòng) phải sử dụng ký tự Markdown (-) hoặc (*).

Dựa trên các thông tin sau, hãy tạo KẾ HOẠCH BÀI DẠY (Giáo án) đầy đủ theo cấu trúc chuẩn.
- Môn học: {mon_hoc}
- Lớp: {lop}
- Bộ sách: {bo_sach}
- Tên bài giảng: {ten_bai}
- Yêu cầu kiến thức (dựa trên phân phối chương trình): {yeu_cau}
- Yêu cầu cho Phiếu bài tập: {yeu_cau_phieu}

TUYỆT ĐỐI CHỈ TRẢ VỀ NỘI DUNG GIÁO ÁN, KHÔNG TRẢ VỀ BẤT KỲ LỜI GIỚI THIỆU HAY GIẢI THÍCH NÀO.
"""

# -----------------------------------------------------------------
# 2. KHỐI HÀM XỬ LÝ WORD (ĐÃ SỬA LỖI set_cell_border)
# -----------------------------------------------------------------

# Các mẫu regex để nhận diện các loại tiêu đề
ACTIVITY_HEADERS_PATTERN = re.compile(r'^\s*(\*\*|)(\d+\.\sHoạt động.*?)(\*\*|)\s*', re.IGNORECASE)
SUB_ACTIVITY_HEADERS_PATTERN = re.compile(r'^\s*(\*\*|)([a-z]\)\s.*?)(\*\*|)\s*', re.IGNORECASE)

# Loại bỏ mọi trường hợp "Cách tiến hành" và dấu ** thừa
def clean_content(text):
    text = re.sub(r'Cách tiến hành[:]*\s*', '', text, flags=re.IGNORECASE).strip()
    # Yêu cầu: Loại bỏ triệt để dấu ** thừa
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
            
            # Tùy chỉnh viền cho Header
            for cell in hdr_cells:
                # Viền trên (ngoài cùng) và dưới (phân cách header)
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
                        
                        # --- XỬ LÝ VIỀN CHO HÀNG TIÊU ĐỀ HOẠT ĐỘNG ---
                        set_cell_border(row_cells[0], 
                            top={"val": "single", "sz": 12, "color": "auto"}, # Viền trên
                            bottom={"val": "single", "sz": 12, "color": "auto"}, # Viền dưới
                            left={"val": "single", "sz": 12, "color": "auto"},
                            right={"val": "single", "sz": 12, "color": "auto"}
                        )
                        
                        continue
                        
                    # --- XỬ LÝ NỘI DUNG THƯỜNG ---
                    else:
                        # TẠO HÀNG MỚI ĐỂ ĐẢM BẢO ĐỒNG BỘ NỘI DUNG GV - HS
                        row_cells = table.add_row().cells 
                        
                        # --- TẮT VIỀN NGANG GIỮA CÁC HÀNG NỘI DUNG ---
                        for cell in row_cells:
                            # Chỉ giữ viền đứng giữa và viền ngoài (nếu là viền ngoài cùng)
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
                                
                                # Yêu cầu: Buộc sử dụng gạch đầu dòng (-) và loại bỏ số/ký tự list cũ
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
            # Chỉ thêm viền dưới
            set_cell_border(cell, 
                bottom={"val": "single", "sz": 12, "color": "auto"},
                # Đảm bảo viền trên vẫn bị tắt (để không tạo kẻ ngang giữa hàng nội dung)
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
# 3. KHỐI LOGIC CHẠY STREAMLIT (KHÔNG THAY ĐỔI)
# -----------------------------------------------------------------

# (Phần này giữ nguyên, dùng cho logic gọi AI và giao diện)

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
        "Đọc đúng, trôi chảy toàn bài thơ. Hiểu được nội dung bài thơ: Ngày hôm qua không mất đi mà hóa thành những điều có ích nếu chúng ta biết quý trọng và sử dụng thời gian một cách hiệu quả."
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
                st.balloons() # Hiệu ứng bóng bay khi thành công
                st.subheader("🎉 Giáo án của bạn đã sẵn sàng:")
                
                # --- SỬA LỖI: Lọc bỏ phần giải thích thừa của AI (nếu có) ---
                start_marker = "KẾ HOẠCH BÀI DẠY:"
                start_index = full_text.find(start_marker)

                if start_index != -1:
                    # Nếu tìm thấy, cắt từ đó trở đi
                    cleaned_text = full_text[start_index:]
                else:
                    # Nếu không tìm thấy, hiển thị toàn bộ nội dung (bao gồm cả lỗi)
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

# BẮT ĐẦU PHẦN SIDEBAR (PHẢI THỤT LỀ BẰNG 0)
st.sidebar.title("Giới thiệu")
st.sidebar.info(
"""
Sản phẩm của Hoàng Tọng Nghĩa, Trường Tiểu học Hồng Gai. tham gia ngày hội "Nhà giáo sáng tạo với công nghệ số và trí tuệ nhân tạo".

Sản phẩm ứng dụng AI để tự động biên soạn giáo án Tiểu học theo các tiêu chí sư phạm.
"""
)
st.sidebar.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRz-5c742Z_R6zB4u-7S5Q6w0x-X5uW1k6Fsg&s") # Thay thế bằng ảnh phù hợp
