import streamlit as st
import google.generativeai as genai
import time

# -----------------------------------------------------------------
# 1. CẤU HÌNH "BỘ NÃO" AI
# -----------------------------------------------------------------

# LẤY API KEY TỪ STREAMLIT SECRETS VÌ LÝ DO BẢO MẬT
try:
    # Tên biến bí mật trong Streamlit Cloud là "GEMINI_API_KEY"
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    st.error("LỖI CẤU HÌNH: Ứng dụng chưa được cung cấp 'GEMINI_API_KEY' trong Streamlit Secrets.")
    st.stop() # Dừng ứng dụng nếu không tìm thấy key

# Cấu hình API key cho thư viện Gemini
genai.configure(api_key=API_KEY)

# Khởi tạo mô hình AI (chúng ta dùng gemini-2.5-flash)
model = genai.GenerativeModel(model_name="gemini-2.5-flash")

# Đây là "Prompt Gốc" phiên bản Tiểu học chúng ta đã tạo
# Toàn bộ "bộ não" sư phạm nằm ở đây
PROMPT_GOC = """
Bạn là một chuyên gia giáo dục Tiểu học hàng đầu Việt Nam, am hiểu sâu sắc Chương trình GDPT 2018 và kỹ thuật thiết kế kế hoạch bài dạy (giáo án) theo Công văn 2345.

Nhiệm vụ của bạn là soạn một Kế hoạch bài dạy hoàn chỉnh, bám sát các file giáo án mẫu đã được cung cấp.

DỮ LIỆU ĐẦU VÀO:

1.  **Môn học:** {mon_hoc}
2.  **Lớp:** {lop}
3.  **Bộ sách:** {bo_sach}
4.  **Tên bài học/Chủ đề:** {ten_bai}
5.  **Yêu cầu cần đạt (Lấy từ Chương trình môn học):** {yeu_cau}
6.  **Yêu cầu Phiếu bài tập:** {yeu_cau_phieu}

YÊU CẦU ĐỐI VỚI SẢN PHẨM (GIÁO ÁN):

Bạn PHẢI soạn giáo án theo đúng cấu trúc 5 phần và định dạng 2 cột như các giáo án mẫu.

---

**PHẦN I. YÊU CẦU CẦN ĐẠT**
(Dựa trên {yeu_cau} để viết 3 mục rõ ràng):
1.  **Về kiến thức:** (Học sinh biết/nêu/hiểu/nhận biết được gì...)
2.  **Về năng lực:**
    * **Năng lực chung:** (Chọn trong 3 năng lực: Tự chủ và tự học, Giao tiếp và hợp tác, Giải quyết vấn đề và sáng tạo).
    * **Năng lực đặc thù:** (Nêu năng lực đặc thù của môn {mon_hoc} được phát triển qua bài {ten_bai}).
3.  **Về phẩm chất:** (Chọn trong 5 phẩm chất: Yêu nước, Nhân ái, Chăm chỉ, Trung thực, Trách nhiệm).

**PHẦN II. ĐỒ DÙNG DẠY HỌC**
1.  **Chuẩn bị của giáo viên (GV):** (Bài giảng điện tử, video, phiếu học tập, thẻ từ, tranh ảnh...)
2.  **Chuẩn bị của học sinh (HS):** (Sách giáo khoa, vở bài tập, đồ dùng học tập...)

**PHẦN III. CÁC HOẠT ĐỘNG DẠY HỌC CHỦ YẾU**
(QUAN TRỌNG: Trình bày dưới dạng bảng Markdown có 2 cột chính: "Hoạt động của giáo viên" và "Hoạt động của học sinh". Các hoạt động (Khởi động, Khám phá, Luyện tập, Vận dụng) là các hàng trong bảng này).

| Hoạt động của giáo viên | Hoạt động của học sinh |
| :--- | :--- |
| **1. Hoạt động 1: Khởi động** (3-5 phút) | |
| - **Mục tiêu:** Tạo tâm thế vui vẻ, hứng thú học tập, kết nối bài cũ vào bài mới. | - **Mục tiêu:** Tiếp nhận nhiệm vụ, tham gia hào hứng. |
| - **Cách tiến hành:** (Mô tả GV tổ chức: cho lớp hát, chơi trò chơi "Truyền điện", đặt câu hỏi gợi mở, chiếu video ngắn liên quan đến {ten_bai}). | - **Cách tiến hành:** (HS tham gia hát, chơi trò chơi, trả lời câu hỏi, quan sát...). |
| - **Đánh giá:** GV nhận xét, tuyên dương, dẫn dắt vào bài mới. | - **Đánh giá:** (HS lắng nghe). |
| | |
| **2. Hoạt động 2: Khám phá / Hình thành kiến thức mới** (15-20 phút) | |
| - **Mục tiêu:** Giúp HS đạt được {yeu_cau} về kiến thức. | - **Mục tiêu:** Nắm được kiến thức mới, phát triển năng lực (tư duy, ngôn ngữ...). |
| - **Cách tiến hành:** (GV sử dụng đồ dùng trực quan, trình chiếu, đặt câu hỏi, giao nhiệm vụ (ví dụ: đọc SGK, thảo luận cặp đôi/nhóm), yêu cầu HS làm Phiếu học tập). | - **Cách tiến hành:** (HS quan sát, lắng nghe, đọc SGK, thảo luận nhóm, làm PHT, trình bày kết quả, trả lời câu hỏi). |
| - **Đánh giá:** GV chốt lại kiến thức cốt lõi, nhận xét phần trình bày của HS, sửa lỗi (nếu có). | - **Đánh giá:** (HS báo cáo, tự sửa lỗi, lắng nghe). |
| | |
| **3. Hoạt động 3: Luyện tập / Thực hành** (10-15 phút) | |
| - **Mục tiêu:** Giúp HS áp dụng kiến thức vừa học, rèn luyện kỹ năng (tính toán, đọc, viết...). | - **Mục tiêu:** Hoàn thành bài tập, rèn luyện kỹ năng. |
| - **Cách tiến hành:** (GV giao bài tập (ví dụ: Bài 1, 2 trong SGK/VBT), tổ chức cho HS làm (bảng con, vở, phiếu), mời HS lên bảng chữa bài). | - **Cách tiến hành:** (HS làm bài cá nhân, làm bảng con, chữa bài trên bảng, đổi vở kiểm tra chéo). |
| - **Đánh giá:** GV chữa bài, nhận xét, tuyên dương HS làm tốt. | - **Đánh giá:** (HS tự nhận xét bài làm của mình và của bạn). |
| | |
| **4. Hoạt động 4: Vận dụng / Củng cố** (3-5 phút) | |
| - **Mục tiêu:** Giúp HS liên hệ kiến thức vào thực tế, củng cố lại toàn bộ bài học. | - **Mục tiêu:** Biết vận dụng kiến thức vào cuộc sống. |
| - **Cách tiến hành:** (GV đặt câu hỏi liên hệ thực tế (ví dụ: "Trong thực tế em thấy..."), tổ chức trò chơi củng cố nhanh, dặn dò về nhà). | - **Cách tiến hành:** (HS trả lời, nêu ví dụ thực tế, lắng nghe dặn dò). |
| - **Đánh giá:** GV nhận xét tiết học, khen ngợi HS tích cực. | - **Đánh giá:** (HS lắng nghe, ghi nhớ). |

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


# -----------------------------------------------------------------
# 2. XÂY DỰNG GIAO DIỆN "CHAT BOX" (Web App)
# -----------------------------------------------------------------

st.set_page_config(page_title="Trợ lý Soạn giáo án AI", page_icon="🤖")
st.title("🤖 Trợ lý Soạn giáo án Tiểu học")
st.write("Sản phẩm của thầy giáo Hoàng Trọng Nghĩa.")
st.markdown("*(Giáo án được soạn theo chuẩn trương trình GDPT 2018)*")


# Tạo 5 ô nhập liệu cho 5 biến số
mon_hoc = st.text_input("1. Môn học:", placeholder="Ví dụ: Tiếng Việt")
lop = st.text_input("2. Lớp:", placeholder="Ví dụ: 2")
bo_sach = st.text_input("3. Bộ sách:", placeholder="Ví dụ: Cánh Diều")
ten_bai = st.text_input("4. Tên bài học / Chủ đề:", placeholder="Ví dụ: Bài 2: Thời gian của em")
yeu_cau = st.text_area("5. Yêu cầu cần đạt:", placeholder="Điền Yêu cầu cần đạt ...", height=150)

# Thêm Checkbox cho tùy chọn Phiếu Bài Tập
tao_phieu = st.checkbox("✅ Tạo kèm Phiếu bài tập (cho hoạt động Luyện tập)")

# Nút bấm để tạo giáo án
if st.button("🚀 Tạo Giáo án ngay!"):
    if not mon_hoc or not lop or not bo_sach or not ten_bai or not yeu_cau:
        st.error("Vui lòng nhập đầy đủ cả 5 thông tin!")
    elif API_KEY == "PASTE_KEY_CUA_BAN_VAO_DAY":
        st.error("LỖI: Bạn chưa nhập API Key. Vui lòng kiểm tra lại file app.py")
    else:
        with st.spinner("Trợ lý AI đang soạn giáo án, vui lòng chờ trong giây lát..."):
            try:
                # Logic để xử lý checkbox
                # Quyết định giá trị cho biến số thứ 6 dựa trên việc người dùng có tick vào ô hay không
                yeu_cau_phieu_value = "CÓ" if tao_phieu else "KHÔNG"

                # 1. Điền 6 biến số vào "Prompt Gốc"
                final_prompt = PROMPT_GOC.format(
                    mon_hoc=mon_hoc,
                    lop=lop,
                    bo_sach=bo_sach,
                    ten_bai=ten_bai,
                    yeu_cau=yeu_cau,
                    yeu_cau_phieu=yeu_cau_phieu_value 
                )

                # 2. Gọi AI
                response = model.generate_content(final_prompt)

             # 3. Hiển thị kết quả
                st.balloons() # Hiệu ứng bóng bay khi thành công
                st.subheader("🎉 Giáo án của bạn đã sẵn sàng:")
                
                # --- SỬA LỖI: Thay thế chuỗi '<br/>' bằng ký tự xuống dòng để xuống dòng ---
                cleaned_text = response.text.replace("<br/>", "\n") 
                
                st.markdown(cleaned_text) # Hiển thị văn bản đã được làm sạch

            except Exception as e:
                st.error(f"Đã có lỗi xảy ra: {e}")
                st.error("Lỗi này có thể do API Key sai, hoặc do chính sách an toàn của Google. Vui lòng kiểm tra lại.")
st.sidebar.title("Giới thiệu")
st.sidebar.info(
    """
    Sản phẩm của Hoàng Tọng Nghĩa, Trường Tiểu học Hồng Gai. tham gia ngày hội "Nhà giáo sáng tạo với công nghệ số và trí tuệ nhân tạo".
    \n
    Sản phẩm ứng dụng AI để tự động soạn giáo án cho giáo viên Tiểu học theo đúng chuẩn Chương trình GDPT 2018.
    """

)






