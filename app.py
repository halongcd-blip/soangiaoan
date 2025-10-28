import streamlit as st
import time
import re 
from io import BytesIO

# -----------------------------------------------------------------
# CÁC DÒNG IMPORT AN TOÀN VÀ CƠ BẢN NHẤT
# -----------------------------------------------------------------
import google.generativeai as genai
# 🚨 QUAN TRỌNG: SỬ DỤNG CÚ PHÁP CŨ HƠN, ĐƯỢC HỖ TRỢ RỘNG RÃI HƠN
from google.generativeai import types 
# -----------------------------------------------------------------

# -----------------------------------------------------------------
# 1. CẤU HÌNH "BỘ NÃO" AI VÀ PROMPT 
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

# Đây là "Prompt Gốc" (Giữ nguyên yêu cầu OCR mạnh mẽ)
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
8.  **TÀI LIỆU ĐÍNH KÈM (BÀI TẬP SGK):** Nếu có hình ảnh (ảnh chụp sách giáo khoa) hoặc tài liệu đính kèm, bạn **TUYỆT ĐỐI PHẢI THỰC HIỆN NHẬN DIỆN VĂN BẢN (OCR)** để trích xuất **chính xác nội dung các bài tập** từ những tài liệu đó. Sau đó, sử dụng nội dung đã trích xuất để thiết kế **Hoạt động 3: Luyện tập, Thực hành** và **PHẦN V. PHIẾU BÀI TẬP**. **Không được sáng tạo thêm bài tập** khi đã có ảnh SGK.

YÊU CẦU VỀ ĐỊNH DẠNG:
Bạn PHẢI tuân thủ tuyệt đối cấu trúc và các yêu cầu sau:

**I. Yêu cầu cần đạt**
(Phát biểu cụ thể học sinh thực hiện được việc gì; vận dụng được những gì; phẩm chất, năng lực gì.)
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
| *Mục tiêu: Áp dụng kiến thức, rèn kỹ năng. Nếu yeu_cau_phieu là CÓ, GV phải giao Phiếu bài tập trong hoạt động này, **sử dụng nội dung từ ảnh đã tải lên**.* | *Mục tiêu: Đạt được mục tiêu GV đề ra.* |
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
(QUAN TRỌNG: Bạn CHỈ tạo phần này nếu DỮ LIỆU ĐẦU VÀO số 7 `{yeu_cau_phieu}` là 'CÓ'. **Bạn phải sử dụng nội dung bài tập đã được trích xuất từ hình ảnh/tài liệu đính kèm**.)

- Nếu `{yeu_cau_phieu}` là 'CÓ':
- Hãy thiết kế một Phiếu bài tập (Worksheet) ngắn gọn, **bám sát và sử dụng các bài tập đã được trích xuất từ ảnh SGK**.
- Phiếu phải được trình bày sinh động, vui nhộn, phù hợp với học sinh tiểu học (ví dụ: dùng emojis 🌟, 🦋, 🖍️, 🐝, lời dẫn thân thiện, có khung viền đơn giản).
- Đặt tên phiếu rõ ràng (ví dụ: PHIẾU BÀI TẬP - BÀI: {ten_bai}).
- Bao gồm 2-3 bài tập nhỏ (đã lấy từ ảnh).

---
Hãy bắt đầu tạo giáo án.
"""

# -----------------------------------------------------------------
# 2. KHỐI LOGIC CHẠY STREAMLIT (UI)
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
    
    # Kích hoạt lại Tải file/ảnh
    uploaded_files = st.file_uploader(
        "🖼️ Tải lên hình ảnh/tài liệu SGK (Ảnh chụp bài tập là tốt nhất):", 
        type=["png", "jpg", "jpeg", "pdf"], # Giới hạn loại file để tập trung vào nội dung SGK
        accept_multiple_files=True
    )

    yeu_cau_phieu_value = st.selectbox(
        "Bạn có muốn tạo Phiếu bài tập dựa trên nội dung đã tải lên không?",
        ["CÓ", "KHÔNG"]
    )

    submit_button = st.form_submit_button(label='✨ Tạo Giáo án')

if submit_button:
    # 1. Chuẩn bị danh sách Content cho AI
    content = []
    
    # Xử lý các file được tải lên (Multimodal)
    if uploaded_files:
        st.info(f"Đang xử lý {len(uploaded_files)} file. AI sẽ trích xuất bài tập từ đây...")
        for uploaded_file in uploaded_files:
            try:
                # Đọc file nhị phân
                file_bytes = uploaded_file.read()
                
                # Tạo đối tượng Part cho file 
                # 🚨 SỬ DỤNG CÚ PHÁP types.Part.from_bytes, KHẮC PHỤC LỖI TỪ CÁC PHIÊN BẢN TRƯỚC
                file_part = types.Part.from_bytes( 
                    data=file_bytes,
                    mime_type=uploaded_file.type
                )
                content.append(file_part)
            except Exception as e:
                # Xử lý lỗi nếu việc đọc file thất bại
                st.error(f"❌ KHÔNG THỂ XỬ LÝ ẢNH/FILE: {uploaded_file.name}. Lỗi: {e}")
                st.error("Vui lòng kiểm tra lại tên thư viện đã cài đặt trong Streamlit Requirements hoặc thử dùng file khác.")


    if mon_hoc and lop and ten_bai and yeu_cau:
        with st.spinner('⏳ AI đang biên soạn Giáo án và đọc bài tập trong ảnh, xin chờ một chút...'):
            try:
                # 2. Điền Prompt 
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

                # 3. Gọi AI với danh sách nội dung (content bao gồm Prompt và Ảnh/File)
                response = model.generate_content(content)
                full_text = response.text
                
                # 4. Hiển thị kết quả
                st.balloons() 
                st.subheader("🎉 Giáo án của bạn đã sẵn sàng:")
                
                # --- Lọc bỏ phần giải thích thừa của AI (nếu có) ---
                start_marker = "KẾ HOẠCH BÀI DẠY:"
                start_index = full_text.find(start_marker)

                if start_index != -1:
                    cleaned_text = full_text[start_index:]
                else:
                    cleaned_text = full_text

                st.markdown(cleaned_text) 
                
                st.warning("⚠️ **LƯU Ý QUAN TRỌNG:** Chức năng Tải về Word đã bị vô hiệu hóa vì lỗi kỹ thuật nghiêm trọng. Bạn vui lòng **Copy** toàn bộ nội dung Giáo án trên và **Dán** vào file Word. Sau đó, bạn có thể định dạng bảng lại theo ý muốn.")

            except Exception as e:
                st.error(f"Đã có lỗi xảy ra trong quá trình gọi AI: {e}")
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
