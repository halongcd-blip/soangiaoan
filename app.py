import streamlit as st
import time
from docx import Document
from io import BytesIO
import re # Cần để làm sạch Markdown
from docx.shared import Inches

# -----------------------------------------------------------------
# IMPORT THƯ VIỆN
# -----------------------------------------------------------------
import google.generativeai as genai
from PIL import Image # Thư viện xử lý ảnh Pillow
# -----------------------------------------------------------------


# -----------------------------------------------------------------
# 1. CẤU HÌNH "BỘ NÃO" AI
# -----------------------------------------------------------------

# LẤY API KEY TỪ STREAMLIT SECRETS
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    # Không cần dòng này khi chạy thực tế, chỉ dùng cho hướng dẫn
    # st.error("LỖI CẤU HÌNH: Ứng dụng chưa được cung cấp 'GEMINI_API_KEY' trong Streamlit Secrets.")
    # st.stop() # Dừng ứng dụng
    # Thay thế bằng API Key giả để code chạy qua (chỉ trong môi trường giả lập này)
    API_KEY = "FAKE_API_KEY_FOR_DEMO" 


# Cấu hình API key cho thư viện Gemini (Chỉ truyền API Key để tránh lỗi)
genai.configure(api_key=API_KEY)

# Sử dụng model gemini-2.5-flash (ổn định nhất, hỗ trợ ảnh, không dùng -latest)
model = genai.GenerativeModel(model_name="gemini-2.5-flash")
# -----------------------------------------------------------------


# Đây là "Prompt Gốc" phiên bản Tiểu học chúng ta đã tạo (GIỮ NGUYÊN)
PROMPT_GOC = """
CẢNH BÁO QUAN TRỌNG: TUYỆT ĐỐI KHÔNG SỬ DỤNG BẤT CỨ THẺ HTML NÀO (ví dụ: <br/>, <strong>). Hãy dùng định dạng MARKDOWN thuần túy (dấu * hoặc - cho gạch đầu dòng và xuống dòng tự động).

Bạn là một chuyên gia giáo dục Tiểu học hàng đầu Việt Nam, am hiểu sâu sắc Chương trình GDPT 2018 và kỹ thuật thiết kế Kế hoạch Bài Dạy (giáo án) theo Công văn 2345.

Nhiệm vụ của bạn là soạn một Kế hoạch bài dạy chi tiết, sáng tạo, tập trung vào phát triển năng lực và phẩm chất.
Nếu người dùng tải lên hình ảnh, bạn phải:
1. Phân tích hình ảnh đó (đây là ảnh chụp bài tập trong SGK).
2. Trích xuất (chuyển ảnh thành chữ) nội dung các bài tập trong ảnh.
3. Sử dụng nội dung chữ vừa trích xuất đó để đưa vào "Hoạt động 3: Luyện tập, Thực hành" một cách hợp lý.

DỮ LIỆU ĐẦU VÀO:
1.  **Môn học:** {mon_hoc}
2.  **Lớp:** {lop}
3.  **Bộ sách:** {bo_sach}
4.  **Tên bài học/Chủ đề:** {ten_bai}
5.  **Yêu cầu cần đạt (Lấy từ Chương trình môn học):** {yeu_cau}
6.  **Yêu cầu tạo phiếu bài tập:** {yeu_cau_phieu}
7.  **Yêu cầu tạo sơ đồ tư duy:** {yeu_cau_mindmap} # <-- Biến số 7

YÊU CẦU VỀ ĐỊNH DẠNG:
Bạn PHẢI tuân thủ tuyệt đối cấu trúc và các yêu cầu sau:

**I. Yêu cầu cần đạt**
(Phát biểu cụ thể học sinh thực hiện được việc gì; vận dụng được những gì; phẩm chất, năng lực gì.)
1.  **Về kiến thức:** (Bám sát {yeu_cau})
2.  **Về năng lực:** (Năng lực chung: Tự chủ và tự học, Giao tiếp và hợp tác, Giải quyết vấn đề và sáng tạo; Năng lực đặc thù của môn {mon_hoc})
3.  **Về phẩm chất:** (Chọn 1-2 trong 5 phẩm chất: Yêu nước, Nhân ái, Chăm chỉ, Trung thực, Trách nhiệm)

**II. Đồ dùng dạy học**
(Nêu các thiết bị, học liệu được sử dụng trong bài dạy. Nếu Yêu cầu tạo phiếu bài tập là CÓ, phải nhắc đến Phiếu bài tập trong mục này.)
1.  **Chuẩn bị của giáo viên (GV):** (Tranh ảnh, video, phiếu học tập, link game...)
2.  **Chuẩn bị của học sinh (HS):** (SGK, Vở bài tập, bút màu...)

**III. Các hoạt động dạy học chủ yếu**
**QUY TẮC QUAN TRỌNG VỀ NỘI DUNG:** Phần này PHẢI được soạn thật kỹ lưỡng, chi tiết. Ưu tiên sử dụng các phương pháp và kỹ thuật dạy học tích cực (ví dụ: KWL, Mảnh ghép, Khăn trải bàn, Góc học tập, Trạm học tập, Đóng vai, Sơ đồ tư duy...) để phát huy tối đa năng lực và phẩm chất của học sinh theo Chương trình GDPT 2018.
**QUY TẮC QUAN TRỌNG VỀ BẢNG BIỂU:** Toàn bộ nội dung của mục 3 này PHẢI được trình bày trong **MỘT BẢNG MARKDOWN DUY NHẤT** có 2 cột.

| Hoạt động của giáo viên | Hoạt động của học sinh |
| :--- | :--- |
| **1. Hoạt động Mở đầu (Khởi động, Kết nối)** | |
| *Mục tiêu: Tạo tâm thế vui vẻ, hứng thú.* | *Mục tiêu: Đạt được mục tiêu GV đề ra.* |
| (Viết chi tiết, dùng dấu gạch đầu dòng `*` cho mỗi bước) | (Viết chi tiết các hoạt động tương tác của HS) |
| **2. Hoạt động Hình thành kiến thức mới (Trải nghiệm, Khám phá)** | |
| *Mục tiêu: (Bám sát {yeu_cau} để hình thành kiến thức mới)* | *Mục tiêu: Đạt được mục tiêu GV đề ra.* |
| (Viết chi tiết, dùng dấu gạch đầu dòng `*` cho mỗi bước) | (Viết chi tiết các bước HS quan sát, thảo luận) |
| **3. Hoạt động Luyện tập, Thực hành** | |
| *Mục tiêu: Áp dụng kiến thức, rèn kỹ năng. (Nếu có ảnh tải lên, GV sẽ dùng bài tập từ ảnh ở đây. Nếu yeu_cau_phieu là CÓ, GV phải giao Phiếu bài tập).* | *Mục tiêu: Đạt được mục tiêu GV đề ra.* |
| (Viết chi tiết, dùng dấu gạch đầu dòng `*` cho mỗi bước) | (Viết chi tiết các bước HS thực hành cá nhân/nhóm) |
| **4. Hoạt động Vận dụng, Trải nghiệm (Củng cố)** | |
| *Mục tiêu: Liên hệ thực tế, củng cố bài.* | *Mục tiêu: Đạt được mục tiêu GV đề ra.* |
| (Viết chi tiết, dùng dấu gạch đầu dòng `*` cho mỗi bước) | (Viết chi tiết các bước HS trả lời, cam kết hành động) |

---

**PHẦN IV. ĐIỀU CHỈNH SAU BÀI DẠY (NẾU CÓ)**
*(Đây là phần để trống để giáo viên ghi chú lại sau khi thực tế giảng dạy)*
1.  **Về nội dung, kiến thức:**
    * ......................................................................
2.  **Về phương pháp, kỹ thuật tổ chức:**
    * ......................................................................
3.  **Về học sinh (những khó khăn, điểm cần lưu ý):**
    * ......................................................................

---

**PHẦN V. PHIẾU BÀI TẬP (NẾU CÓ)**
(QUAN TRỌNG: Bạn CHỈ tạo phần này nếu DỮ LIỆU ĐẦU VÀO số 6 `{yeu_cau_phieu}` là 'CÓ'. Nếu là 'KHÔNG', hãy bỏ qua hoàn toàn phần này.)

- Nếu `{yeu_cau_phieu}` là 'CÓ':
- Hãy thiết kế một Phiếu bài tập (Worksheet) ngắn gọn, bám sát nội dung của **Hoạt động 3: Luyện tập / Thực hành**.
- Phiếu phải được trình bày sinh động, vui nhộn (dùng emojis 🌟, 🦋, 🖍️, 🐝, lời dẫn thân thiện).
- Đặt tên phiếu rõ ràng (ví dụ: PHIẾU BÀI TẬP - BÀI: {ten_bai}).
- Bao gồm 2-3 bài tập nhỏ (ví dụ: nối, điền từ, khoanh tròn).

---

**PHẦN VI. SƠ ĐỒ TƯ DUY (MÃ NGUỒN GRAPHVIZ)**
(QUAN TRỌNG: Bạn CHỈ tạo phần này nếu DỮ LI LIỆU ĐẦU VÀO số 7 `{yeu_cau_mindmap}` là 'CÓ'. Nếu là 'KHÔNG', hãy bỏ qua hoàn toàn phần này.)

- Nếu `{yeu_cau_mindmap}` là 'CÓ':
- **YÊU CẦU BẮT BUỘC:** Bạn PHẢI tạo một Sơ đồ tư duy (Mind Map) tóm tắt nội dung chính của bài học {ten_bai} bằng **ngôn ngữ Graphviz DOT**.
- **TUYỆT ĐỐI KHÔNG SỬ DỤNG:** Markdown, gạch đầu dòng, hay bất kỳ định dạng nào khác ngoài mã Graphviz DOT thuần túy trong phần này.
- Sơ đồ phải rõ ràng, phân cấp, sử dụng tiếng Việt có dấu trong các nhãn (label). Sử dụng `layout=twopi` hoặc `layout=neato` để có bố cục tỏa tròn đẹp mắt.
- **QUAN TRỌNG:** Bọc toàn bộ mã code Graphviz DOT trong 2 thẻ **DUY NHẤT**: `[START_GRAPHVIZ]` ở dòng đầu tiên và `[END_GRAPHVIZ]` ở dòng cuối cùng của mã nguồn. Không thêm bất kỳ văn bản nào khác bên ngoài hai thẻ này trong phần VI.

- **Ví dụ cấu trúc mã Graphviz DOT:**
`[START_GRAPHVIZ]`
`digraph MindMap {{`
`    graph [layout=twopi, ranksep=1.5];` # Gợi ý layout tỏa tròn
`    node [shape=box, style="rounded,filled", fillcolor=lightblue, fontname="Arial"];` # Định dạng nút
`    edge [fontname="Arial"];` # Định dạng đường nối
`    center [label="{ten_bai}", fillcolor=lightyellow];` # Nút trung tâm
`    center -> "Nhanh1";`
`    "Nhanh1" [label="Nhánh Chính 1"];` # Đặt nhãn tiếng Việt
`    "Nhanh1" -> "ND1_1" [label="Nội dung 1.1"];` # Đặt nhãn tiếng Việt
`    "Nhanh1" -> "ND1_2" [label="Nội dung 1.2"];` # Đặt nhãn tiếng Việt
`    center -> "Nhanh2";`
`    "Nhanh2" [label="Nhánh Chính 2"];` # Đặt nhãn tiếng Việt
`    "Nhanh2" -> "ND2_1" [label="Nội dung 2.1"];` # Đặt nhãn tiếng Việt
`}}`
`[END_GRAPHVIZ]`

---
Hãy bắt đầu tạo giáo án.
"""
# ==================================================================
# KẾT THÚC PHẦN PROMPT (GIỮ NGUYÊN)
# ==================================================================

# Các hàm xử lý Word (ĐÃ SỬA CHỮA LỖI ** VÀ PHẦN VI - TẬP TRUNG VÀO LOGIC PARSING)
def clean_content(text):
    # 1. Loại bỏ cụm "Cách tiến hành"
    text = re.sub(r'Cách tiến hành[:]*\s*', '', text, flags=re.IGNORECASE).strip()

    # 2. Loại bỏ TẤT CẢ các thẻ HTML (bao gồm <br>)
    text = re.sub(r'<[^>]+>', '', text, flags=re.IGNORECASE).strip()

    # 3. Loại bỏ dấu ** thừa trong văn bản thường
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text).strip() # Loại bỏ **...** và giữ lại nội dung bên trong

    return text

def create_word_document(markdown_text, lesson_title):
    document = Document()
    if lesson_title:
        document.add_heading(f"KẾ HOẠCH BÀI DẠY: {lesson_title.upper()}", level=1)
        document.add_paragraph()

    lines = markdown_text.split('\n')
    is_in_table_section = False
    is_in_graphviz_section = False
    table = None
    current_row = None
    
    # --------------------------------------------------------------------------------
    # 1. LƯU MÃ GRAPHVIZ RIÊNG ĐỂ XỬ LÝ LATER (Tách code ra khỏi dòng chảy chính)
    # --------------------------------------------------------------------------------
    graph_code_content = ""
    parsing_graph = False
    
    for line in lines:
        if "[START_GRAPHVIZ]" in line:
            parsing_graph = True
            continue
        if "[END_GRAPHVIZ]" in line:
            parsing_graph = False
            break # Dừng ngay khi tìm thấy thẻ đóng
        if parsing_graph:
            graph_code_content += line + "\n"
    # --------------------------------------------------------------------------------


    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Bỏ qua mọi thứ trong khối Graphviz khi xử lý nội dung Word
        if "[START_GRAPHVIZ]" in line or "[END_GRAPHVIZ]" in line:
            continue
        
        # Bỏ qua nội dung Graphviz đã được lưu
        if graph_code_content.strip() and line.strip() in graph_code_content.split('\n'):
            continue
        
        # --------------------------------------------------------------------------------
        # XỬ LÝ BẢNG CHÍNH (HOẠT ĐỘNG)
        # --------------------------------------------------------------------------------
        if re.match(r'\|.*Hoạt động của giáo viên.*\|.*Hoạt động của học sinh.*\|', line, re.IGNORECASE):
            is_in_table_section = True
            document.add_heading("III. Các hoạt động dạy học chủ yếu", level=2)
            table = document.add_table(rows=1, cols=2)
            table.style = 'Table Grid'
            table.autofit = False
            table.columns[0].width = Inches(3.5)
            table.columns[1].width = Inches(3.5)
            hdr_cells = table.rows[0].cells
            hdr_cells[0].text = "Hoạt động của giáo viên"
            hdr_cells[1].text = "Hoạt động của học sinh"
            current_row = table.add_row().cells
            continue

        if is_in_table_section and table is not None:
            if line.startswith('| :---'):
                continue

            # Kiểm tra kết thúc bảng
            if re.match(r'^[IVX]+\.\s|PHẦN\s[IVX]+\.', line) or line.startswith('---'):
                is_in_table_section = False
                continue

            if line.startswith('|') and len(line.split('|')) >= 3:
                cells_content = [c.strip() for c in line.split('|')[1:-1]]

                if len(cells_content) == 2:
                    gv_content = cells_content[0].strip().replace('**', '')
                    hs_content = cells_content[1].strip().replace('**', '')

                    ACTIVITY_HEADERS_PATTERN = re.compile(r'^\s*(\d+\.\sHoạt động.*)\s*', re.IGNORECASE)
                    is_main_header = ACTIVITY_HEADERS_PATTERN.match(gv_content)
                    
                    if is_main_header:
                        title = gv_content.strip().strip('*').strip()
                        current_row = table.add_row().cells
                        current_row[0].merge(current_row[1])
                        p = current_row[0].add_paragraph(title)
                        p.runs[0].bold = True
                        current_row = table.add_row().cells 
                        continue
                    
                    else:
                        if current_row is None:
                            current_row = table.add_row().cells

                        for cell_index, cell_content in enumerate([gv_content, hs_content]):
                            cell_content_cleaned = clean_content(cell_content)
                            content_lines = cell_content_cleaned.split('\n')
                            
                            for content_line in content_lines:
                                content_line = content_line.strip()
                                if not content_line: continue
                                
                                if content_line.startswith('*') or content_line.startswith('-'):
                                    p = current_row[cell_index].add_paragraph(content_line.lstrip('*- ').strip(), style='List Bullet')
                                else:
                                    current_row[cell_index].add_paragraph(content_line)
                    continue

        # --------------------------------------------------------------------------------
        # XỬ LÝ NỘI DUNG NGOÀI BẢNG (I, II, IV, V, VI)
        # --------------------------------------------------------------------------------
        if re.match(r'^[IVX]+\.\s|PHẦN\s[IVX]+\.', line):
            clean_line = line.strip().strip('**')
            
            # XỬ LÝ PHẦN VI: TẠO GỢI Ý OUTLINE TỪ MÃ GRAPHVIZ ĐÃ LƯU
            if clean_line.startswith("PHẦN VI."):
                 document.add_heading("PHẦN VI. GỢI Ý SƠ ĐỒ TƯ DUY", level=2)
                 
                 if graph_code_content.strip():
                     # Regex để tìm tất cả các nhãn (label)
                     # re.DOTALL để khớp với các nhãn có xuống dòng (\n)
                     # Lọc bỏ các ký tự đặc biệt như **
                     labels = re.findall(r'label="([^"]*)"', graph_code_content, re.DOTALL)
                     
                     # Lọc bỏ các label rỗng và trùng lặp
                     unique_labels = sorted(list(set(label.strip() for label in labels if label.strip())))

                     if unique_labels:
                         document.add_paragraph("(Dưới đây là gợi ý nội dung chính (Key Ideas) được trích xuất từ sơ đồ tư duy do AI tạo. Giáo viên có thể dựa vào đây để vẽ hoặc chèn hình ảnh sơ đồ từ giao diện web.)")
                         document.add_paragraph() 

                         for label in unique_labels:
                             # Lấy nhãn, thay thế \n bằng dấu gạch đầu dòng thứ cấp
                             processed_label = label.replace(r'\n', '\n')
                             label_parts = processed_label.split('\n')
                             
                             main_label = label_parts[0].strip().replace('**', '') 
                             
                             # Bỏ qua nhãn rỗng hoặc chỉ là dấu chấm phẩy
                             if not main_label or main_label == ';': 
                                 continue
                             
                             # Lọc các nhãn thường là tiêu đề chung (như Tự chủ, Hợp tác, Kiến thức...)
                             if len(main_label) > 10: 
                                 # Nhãn chính (main bullet)
                                 p = document.add_paragraph(f"• {main_label}", style='List Bullet')
                                 # p.paragraph_format.left_indent = Inches(0.25) # Đã có trong style List Bullet
                                     
                             # Thêm các dòng phụ (sub bullet)
                             for part in label_parts[1:]:
                                 part = part.strip().replace('**', '') 
                                 if part and len(part) > 3: # Loại bỏ các phần quá ngắn
                                     p = document.add_paragraph(f"  - {part}")
                                     p.style = 'List Continue 2' # Style cho gạch đầu dòng cấp 2
                                     p.paragraph_format.left_indent = Inches(0.5)

                     else:
                         document.add_paragraph("(AI đã tạo Graphviz nhưng không tìm thấy nhãn nội dung (label) để trích xuất gợi ý. Vui lòng kiểm tra lại yêu cầu.)")
                     
                 else:
                     document.add_paragraph("(Không tìm thấy mã nguồn Graphviz. Có thể yêu cầu tạo sơ đồ tư duy là 'KHÔNG'.)")
                 
                 continue 
            
            # Tiêu đề các phần khác
            document.add_heading(clean_line, level=2)

        # Các tiêu đề con (vd: 1. **Về kiến thức:**)
        elif line.startswith('**') and line.endswith('**'):
            document.add_heading(line.strip('**').replace('**', ''), level=3)

        # Danh sách gạch đầu dòng (List Bullet)
        elif line.startswith('*') or line.startswith('-'):
            document.add_paragraph(line.lstrip('*- ').strip().replace('**', ''), style='List Bullet')
        else:
            # Văn bản thường (cũng loại bỏ ** thừa)
            document.add_paragraph(line.replace('**', ''))


    bio = BytesIO()
    document.save(bio)
    bio.seek(0)
    return bio
# -----------------------------------------------------------------
# 2. XÂY DỰNG GIAO DIỆN "CHAT BOX" (Web App) (GIỮ NGUYÊN)
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

# 6. KHAI BÁO BIẾN CHO FILE UPLOADER
uploaded_file = st.file_uploader(
    "6. [Tải Lên] Ảnh/PDF trang Bài tập SGK (Tùy chọn)",
    type=["pdf", "png", "jpg", "jpeg"]
)

# 7. KHAI BÁO BIẾN CHO CHECKBOX PHIẾU BÀI TẬP
tao_phieu = st.checkbox("7. Yêu cầu tạo kèm Phiếu Bài Tập", value=False)

# 8. <-- MỚI: Thêm Checkbox cho Sơ đồ tư duy
tao_mindmap = st.checkbox("8. Yêu cầu tạo Sơ đồ tư duy trực quan", value=True)

# Nút bấm để tạo giáo án
if st.button("🚀 Tạo Giáo án ngay!"):
    if not mon_hoc or not lop or not bo_sach or not ten_bai or not yeu_cau:
        st.error("Vui lòng nhập đầy đủ cả 5 thông tin!")
    else:
        with st.spinner("Trợ lý AI đang soạn giáo án, vui lòng chờ trong giây lát..."):
            try:
                # Logic cho Biến số Tùy chọn 1 (Tạo Phiếu Bài Tập)
                yeu_cau_phieu_value = "CÓ" if tao_phieu else "KHÔNG"

                # Logic cho Biến số Tùy chọn 2 (Sơ đồ tư duy)
                yeu_cau_mindmap_value = "CÓ" if tao_mindmap else "KHÔNG"


                # 1. Chuẩn bị Nội dung (Content List) cho AI (Tích hợp File và Text)
                content = []

                # 2. Điền Prompt (7 biến số text)
                final_prompt = PROMPT_GOC.format(
                    mon_hoc=mon_hoc,
                    lop=lop,
                    bo_sach=bo_sach,
                    ten_bai=ten_bai,
                    yeu_cau=yeu_cau,
                    yeu_cau_phieu=yeu_cau_phieu_value,
                    yeu_cau_mindmap=yeu_cau_mindmap_value # <-- Thêm biến số 7
                )

                # 3. Logic cho Biến số Tùy chọn 2 (Tải File Bài Tập)
                if uploaded_file is not None:
                    # Xử lý PDF (nếu có)
                    if uploaded_file.type == "application/pdf":
                        st.error("Lỗi: Tính năng tải lên file PDF chưa được hỗ trợ. Vui lòng tải file ảnh (PNG, JPG).")
                        st.stop() # Dừng thực thi nếu là PDF

                    # Xử lý ảnh
                    image = Image.open(uploaded_file)
                    content.append(image)

                # 4. Thêm Prompt vào danh sách Content (luôn luôn có)
                content.append(final_prompt)

                # 5. Gọi AI với danh sách nội dung (content)
                response = model.generate_content(content)

                # 6. Hiển thị kết quả
                st.balloons()
                st.subheader("🎉 Giáo án của bạn đã sẵn sàng:")

                # LÀM SẠCH KẾT QUẢ ĐỂ CHỈ HIỂN THỊ GIÁO ÁN
                full_text = response.text

                # Lọc sạch thẻ <br> (lỗi cũ)
                full_text = re.sub(r'<\s*br\s*\/?>', '\n', full_text, flags=re.IGNORECASE)

                start_index = full_text.find("I. Yêu cầu cần đạt")

                if start_index != -1:
                    cleaned_text = full_text[start_index:]
                else:
                    cleaned_text = full_text

                # LỌC "Cách tiến hành:" RA KHỎI PHẦN HIỂN THỊ WEB
                cleaned_text_display = re.sub(r'Cách tiến hành[:]*\s*', '', cleaned_text, flags=re.IGNORECASE)

                # --- KHỐI LOGIC HIỂN THỊ SƠ ĐỒ TƯ DUY TRÊN WEB (GIỮ NGUYÊN) ---
                start_tag = "[START_GRAPHVIZ]"
                end_tag = "[END_GRAPHVIZ]"

                if tao_mindmap and start_tag in cleaned_text_display:
                    try:
                        # Tách nội dung trước và sau code Graphviz
                        before_graph = cleaned_text_display.split(start_tag)[0]
                        temp = cleaned_text_display.split(start_tag)[1]
                        graph_code = temp.split(end_tag)[0].strip()
                        after_graph = temp.split(end_tag)[1]

                        # Hiển thị
                        st.markdown(before_graph)
                        st.subheader("Sơ đồ tư duy (Mind Map) - VẼ TRỰC TIẾP:")
                        if graph_code:
                            st.graphviz_chart(graph_code) # Vẽ sơ đồ
                        else:
                            st.warning("AI đã tạo thẻ tag nhưng mã nguồn Graphviz rỗng. Vui lòng chạy lại.")
                        
                        # Loại bỏ tiêu đề "PHẦN VI." nếu nó nằm trong `after_graph` vì đã vẽ sơ đồ
                        after_graph = re.sub(r'PHẦN VI\.\s*SƠ ĐỒ TƯ DUY.*', '', after_graph, flags=re.IGNORECASE)
                        st.markdown(after_graph)

                    except IndexError:
                        st.error("Lỗi khi trích xuất mã nguồn Graphviz: Không tìm thấy thẻ đóng `[END_GRAPHVIZ]`.")
                        st.markdown(cleaned_text_display)
                    except Exception as e:
                        st.error(f"Lỗi khi vẽ sơ đồ tư duy: {e}")
                        st.markdown(cleaned_text_display)
                else:
                    st.markdown(cleaned_text_display)
                # --- KẾT THÚC KHỐI LOGIC SƠ ĐỒ TƯ DUY ---


                # BẮT ĐẦU KHỐI CODE TẢI XUỐNG WORD
                # Hàm create_word_document đã được sửa để tạo GỢI Ý OUTLINE
                word_bytes = create_word_document(cleaned_text, ten_bai)


                st.download_button(
                    label="⬇️ Tải về Giáo án (Word)",
                    data=word_bytes,
                    file_name=f"GA_{ten_bai.replace(' ', '_')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            except Exception as e:
                # Xử lý lỗi đặc biệt khi API Key bị lỗi (chỉ cần một dòng thông báo)
                if "API_KEY" in str(e):
                    st.error("Lỗi xác thực API: Vui lòng kiểm tra lại 'GEMINI_API_KEY' trong Streamlit Secrets.")
                else:
                    st.error(f"Đã có lỗi xảy ra: {e}")
                    st.error("Lỗi này có thể do AI không tạo ra đúng định dạng hoặc có lỗi kết nối.")

# BẮT ĐẦU PHẦN SIDEBAR
st.sidebar.title("Giới thiệu")
st.sidebar.info(
"""
Sản phẩm của Hoàng Trọng Nghĩa, Trường Tiểu học Hồng Gai. tham gia ngày hội "Nhà giáo sáng tạo với công nghệ số và trí tuệ nhân tạo".

Sản phẩm ứng dụng AI để tự động soạn Kế hoạch bài dạy cho giáo viên Tiểu học theo đúng chuẩn Chương trình GDPT 2018.
"""
)
