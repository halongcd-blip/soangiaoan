import streamlit as st
import time
from docx import Document
from io import BytesIO
import re # Cần để làm sạch Markdown
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
# Đây là "Prompt Gốc"...

# Đây là "Prompt Gốc" phiên bản Tiểu học chúng ta đã tạo
# Toàn bộ "bộ não" sư phạm nằm ở đây
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
1.  **Chuẩn bị của giáo viên (GV):** (Tranh ảnh, video, phiếu học tập, link game...)
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

# <-- MỚI: ĐÃ ĐỔI THỨ TỰ THÀNH PHẦN IV
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

# <-- MỚI: ĐÃ ĐỔI THỨ TỰ THÀNH PHẦN V
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
# ==================================================================
# KẾT THÚC PHẦN PROMPT MỚI
# ==================================================================
from docx import Document
from docx.shared import Inches
from io import BytesIO
import re

def create_word_document(markdown_text, lesson_title):
    """
    Tạo đối tượng Word (docx) từ nội dung Markdown, xử lý tiêu đề và bảng.
    """
    document = Document()
    
    # 1. THÊM TIÊU ĐỀ CHÍNH (Heading 1)
    if lesson_title:
        document.add_heading(f"KẾ HOẠCH BÀI DẠY: {lesson_title.upper()}", level=1)
        document.add_paragraph() # Xuống dòng
    
    lines = markdown_text.split('\n')
    is_in_table_section = False
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        # 1. PHÁT HIỆN BẢNG (III. Các hoạt động dạy học chủ yếu)
        if line.startswith("| Hoạt động của giáo viên"):
            # Bắt đầu cấu trúc bảng
            is_in_table_section = True
            
            # Thêm tiêu đề mục chính trước khi tạo bảng
            document.add_heading("III. Các hoạt động dạy học chủ yếu", level=2)
            
            # Tạo bảng 2 cột
            table = document.add_table(rows=1, cols=2)
            table.style = 'Table Grid'
            table.autofit = False
            table.columns[0].width = Inches(3) # Căn chỉnh độ rộng cột
            table.columns[1].width = Inches(3)
            
            # Thiết lập headers
            hdr_cells = table.rows[0].cells
            hdr_cells[0].text = "Hoạt động của giáo viên"
            hdr_cells[1].text = "Hoạt động của học sinh"
            
            continue

        # 2. XỬ LÝ NỘI DUNG BÊN TRONG BẢNG
        if is_in_table_section:
            # Bỏ qua dòng phân cách bảng (| :--- | :--- |)
            if line.startswith('| :---'):
                continue
            
            # Xử lý các dòng dữ liệu
            if line.startswith('|') and len(line.split('|')) >= 3:
                # Tách nội dung hai cột (bỏ qua dấu | đầu và cuối)
                cells_content = [c.strip() for c in line.split('|')[1:-1]]
                
                if len(cells_content) == 2:
                    row_cells = table.add_row().cells
                    
                    # Xử lý nội dung từng cell
                    for cell_index, cell_content in enumerate(cells_content):
                        # Tách nội dung bên trong cell theo các dòng Markdown (* hoặc -)
                        content_lines = cell_content.split('\n')
                        for content_line in content_lines:
                            content_line = content_line.strip()
                            if not content_line: continue
                            
                            # Loại bỏ định dạng ** (tiêu đề con như **1. Hoạt động Mở đầu**)
                            if content_line.startswith('**') and content_line.endswith('**'):
                                p = row_cells[cell_index].add_paragraph(content_line.strip('**'))
                                p.runs[0].bold = True
                            
                            # Xử lý gạch đầu dòng
                            elif content_line.startswith('*') or content_line.startswith('-'):
                                p = row_cells[cell_index].add_paragraph(content_line.lstrip('*- ').strip(), style='List Bullet')
                            
                            # Văn bản thường
                            else:
                                row_cells[cell_index].add_paragraph(content_line)
                                
                    continue
            
            # Kiểm tra xem bảng đã kết thúc chưa (khi gặp tiêu đề mục lớn khác)
            if re.match(r'^[IVX]+\.\s|PHẦN\s[IVX]+\.', line) or line.startswith('---'):
                is_in_table_section = False # Thoát khỏi chế độ xử lý bảng

        # 3. XỬ LÝ NỘI DUNG BÊN NGOÀI BẢNG (Logic xử lý tiêu đề gốc)
        
        # Xử lý tiêu đề chính (I. Yêu cầu cần đạt, IV. ĐIỀU CHỈNH SAU BÀI DẠY)
        if re.match(r'^[IVX]+\.\s|PHẦN\s[IVX]+\.', line):
            # Loại bỏ ** nếu có và thêm Heading 2
            clean_line = line.strip().strip('**')
            document.add_heading(clean_line, level=2)
            
        # Xử lý tiêu đề con (Về kiến thức, Chuẩn bị của GV)
        elif line.startswith('**') and line.endswith('**'):
            document.add_heading(line.strip('**'), level=3)
            
        # Xử lý gạch đầu dòng Markdown
        elif line.startswith('*') or line.startswith('-'):
            document.add_paragraph(line.lstrip('*- ').strip(), style='List Bullet')
            
        # Xử lý văn bản thuần túy
        else:
            document.add_paragraph(line)


    # Lưu tài liệu vào bộ nhớ (BytesIO)
    bio = BytesIO()
    document.save(bio)
    bio.seek(0)
    return bio

# -----------------------------------------------------------------
# 2. XÂY DỰNG GIAO DIỆN "CHAT BOX" (Web App)
# -----------------------------------------------------------------

st.set_page_config(page_title="Trợ lý Soạn giáo án AI", page_icon="🤖")
st.title("🤖 Trợ lý Soạn giáo án Tiểu học")
st.write("Sản phẩm của thầy giáo Hoàng Trọng Nghĩa.")
st.markdown("*(Kế hoạch bài dạy được biên soạn theo chuẩn Chương trình GDPT 2018)*")


# Tạo 5 ô nhập liệu cho 5 biến số
mon_hoc = st.text_input("1. Môn học:", placeholder="Ví dụ: Tiếng Việt")
lop = st.text_input("2. Lớp:", placeholder="Ví dụ: 2")
bo_sach = st.text_input("3. Bộ sách:", placeholder="Ví dụ: Cánh Diều")
ten_bai = st.text_input("4. Tên bài học / Chủ đề:", placeholder="Ví dụ: Bài 2: Thời gian của em")
yeu_cau = st.text_area("5. Yêu cầu cần đạt:", placeholder="Điền Yêu cầu cần đạt ...", height=150)
# ... (Phần nhập liệu của mon_hoc, lop, bo_sach, ten_bai, yeu_cau)

# 6. KHAI BÁO BIẾN CHO FILE UPLOADER (Cần nằm ở đây)
uploaded_file = st.file_uploader(
    "6. [Tải Lên] Ảnh/PDF trang Bài tập SGK (Tùy chọn)", 
    type=["pdf", "png", "jpg", "jpeg"]
)

# 7. KHAI BÁO BIẾN CHO CHECKBOX
tao_phieu = st.checkbox("7. Yêu cầu tạo kèm Phiếu Bài Tập", value=False)

# Nút bấm để tạo giáo án
if st.button("🚀 Tạo Giáo án ngay!"):
    # Lưu ý: Giả định bạn đã sửa logic kiểm tra API Key để dùng st.secrets
    if not mon_hoc or not lop or not bo_sach or not ten_bai or not yeu_cau:
        st.error("Vui lòng nhập đầy đủ cả 5 thông tin!")
    # [BỎ: elif API_KEY == "PASTE_KEY_CUA_BAN_VAO_DAY":]

    else:
        with st.spinner("Trợ lý AI đang soạn giáo án, vui lòng chờ trong giây lát..."):
            try:
                # Logic cho Biến số Tùy chọn 1 (Tạo Phiếu Bài Tập)
                yeu_cau_phieu_value = "CÓ" if tao_phieu else "KHÔNG"

                # 1. Chuẩn bị Nội dung (Content List) cho AI (Tích hợp File và Text)
                content = []

               # Logic cho Biến số Tùy chọn 2 (Tải File Bài Tập)
                if uploaded_file is not None: # <--- 8 spaces
                    # Đọc bytes từ đối tượng file của Streamlit
                    file_bytes = uploaded_file.read() # <--- 12 spaces
                    
                    file_part = types.Part.from_bytes( # Giữ nguyên cú pháp này
                    data=file_bytes,
                    mime_type=uploaded_file.type
                    )
                    content.append(file_part) # <--- DÒNG 162: PHẢI CÓ 12 DẤU CÁCH
                
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
                
                # 4. Hiển thị kết quả (Dùng cùng thụt lề với các lệnh trên)
                st.balloons() 
                st.subheader("🎉 Giáo án của bạn đã sẵn sàng:")
# LÀM SẠCH KẾT QUẢ ĐỂ CHỈ HIỂN THỊ GIÁO ÁN
                # Tìm vị trí bắt đầu của giáo án (thường là "I. Yêu cầu cần đạt")
                # Sau đó, cắt bỏ phần thừa ở đầu.
                full_text = response.text
                start_index = full_text.find("I. Yêu cầu cần đạt") # Tìm điểm bắt đầu
                
                if start_index != -1:
                    # Nếu tìm thấy, cắt từ đó trở đi
                    cleaned_text = full_text[start_index:]
                else:
                    # Nếu không tìm thấy, hiển thị toàn bộ nội dung (bao gồm cả lỗi)
                    cleaned_text = full_text

                st.markdown(cleaned_text) 
                
                # BẮT ĐẦU KHỐI CODE TẢI XUỐNG WORD
                word_bytes = create_word_document(cleaned_text, ten_bai) # <--- ĐÃ THÊM ten_bai
                
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

Sản phẩm ứng dụng AI để tự động soạn Kế hoạch bài dạy cho giáo viên Tiểu học theo đúng chuẩn Chương trình GDPT 2018.
"""
)
























































