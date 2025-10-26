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

# Khởi tạo mô hình AI (chúng ta dùng gemini-1.5-flash)
model = genai.GenerativeModel(model_name="gemini-2.5-flash")

# Đây là "Prompt Gốc" phiên bản Tiểu học chúng ta đã tạo
# Toàn bộ "bộ não" sư phạm nằm ở đây
PROMPT_GOC = """
Bạn là một chuyên gia giáo dục Tiểu học hàng đầu Việt Nam, am hiểu sâu sắc Chương trình GDPT 2018, đặc biệt là tâm lý học sinh Tiểu học. Bạn là bậc thầy trong việc thiết kế các hoạt động "học mà chơi, chơi mà học".

Nhiệm vụ của bạn là soạn một giáo án hoàn chỉnh, sáng tạo, tập trung vào phát triển năng lực và phẩm chất cho học sinh tiểu học.

DỮ LIỆU ĐẦU VÀO:

1.  **Môn học:** {mon_hoc}
2.  **Lớp:** {lop}
3.  **Bộ sách:** {bo_sach}
4.  **Tên bài học/Chủ đề:** {ten_bai}
5.  **Yêu cầu cần đạt (Lấy từ Chương trình môn học):** {yeu_cau}

YÊU CẦU ĐỐI VỚI SẢN PHẨM (GIÁO ÁN):

Bạn PHẢI tuân thủ tuyệt đối cấu trúc và các yêu cầu sau:

**PHẦN I. MỤC TIÊU BÀI HỌC**
1.  **Về kiến thức:** (Bám sát {yeu_cau})
2.  **Về năng lực:** (Năng lực chung: Tự chủ và tự học, Giao tiếp và hợp tác, Giải quyết vấn đề và sáng tạo; Năng lực đặc thù của môn {mon_hoc})
3.  **Về phẩm chất:** (Chọn 1-2 trong 5 phẩm chất: Yêu nước, Nhân ái, Chăm chỉ, Trung thực, Trách nhiệm)

**PHẦN II. ĐỒ DÙNG DẠY HỌC**
1.  **Chuẩn bị của giáo viên (GV):** (Tranh ảnh, video, phiếu học tập, link game...)
2.  **Chuẩn bị của học sinh (HS):** (SGK, Vở bài tập, bút màu...)

**PHẦN III. CÁC HOẠT ĐỘNG DẠY HỌC CHỦ YẾU**
(Mỗi hoạt động BẮT BUỘC phải có 2 mục: a. Mục tiêu, b. Cách tiến hành)

**HOẠT ĐỘNG 1: KHỞI ĐỘNG (WARM-UP)** (3-5 phút)
* a. Mục tiêu: Tạo tâm thế vui vẻ, hứng thú.
* b. Cách tiến hành: (Thiết kế một trò chơi, bài hát, câu đố vui liên quan đến {ten_bai})


**HOẠT ĐỘNG 2: KHÁM PHÁ (HÌNH THÀNH KIẾN THỨC MỚI)** (15-20 phút)
* a. Mục tiêu: (Bám sát {yeu_cau})
* b. Cách tiến hành: (Sử dụng trực quan, SGK, thảo luận nhóm để tìm ra kiến thức)


**HOẠT ĐỘNG 3: LUYỆN TẬP (THỰC HÀNH)** (10-15 phút)
* a. Mục tiêu: Áp dụng kiến thức, rèn kỹ năng.
* b. Cách tiến hành: (Làm bài tập, phiếu học tập, sắm vai...)


**HOẠT ĐỘNG 4: VẬN DỤNG (CỦNG CỐ)** (3-5 phút)
* a. Mục tiêu: Liên hệ thực tế, củng cố bài.
* b. Cách tiến hành: (Một câu hỏi liên hệ thực tế gần gũi hoặc trò chơi nhanh)


Hãy bắt đầu tạo giáo án.
"""

# -----------------------------------------------------------------
# 2. XÂY DỰNG GIAO DIỆN "CHAT BOX" (Web App)
# -----------------------------------------------------------------

st.set_page_config(page_title="Trợ lý Soạn giáo án AI", page_icon="🤖")
st.title("🤖 Trợ lý Soạn giáo án Tiểu học")
st.write("Sản phẩm của thầy giáo Hoàng Trọng Nghĩa.")

# Tạo 5 ô nhập liệu cho 5 biến số
mon_hoc = st.text_input("1. Môn học:", placeholder="Ví dụ: Tiếng Việt")
lop = st.text_input("2. Lớp:", placeholder="Ví dụ: 2")
bo_sach = st.text_input("3. Bộ sách:", placeholder="Ví dụ: Cánh Diều")
ten_bai = st.text_input("4. Tên bài học / Chủ đề:", placeholder="Ví dụ: Bài 2: Thời gian của em")
yeu_cau = st.text_area("5. Yêu cầu cần đạt:", placeholder="Copy và dán Yêu cầu cần đạt của bài này từ file phân phối chương trình...", height=150)

# Nút bấm để tạo giáo án
if st.button("🚀 Tạo Giáo án ngay!"):
    if not mon_hoc or not lop or not bo_sach or not ten_bai or not yeu_cau:
        st.error("Vui lòng nhập đầy đủ cả 5 thông tin!")

    else:
        with st.spinner("Trợ lý AI đang soạn giáo án, vui lòng chờ trong giây lát..."):
            try:
                # 1. Điền 5 biến số vào "Prompt Gốc"
                final_prompt = PROMPT_GOC.format(
                    mon_hoc=mon_hoc,
                    lop=lop,
                    bo_sach=bo_sach,
                    ten_bai=ten_bai,
                    yeu_cau=yeu_cau
                )

                # 2. Gọi AI
                response = model.generate_content(final_prompt)

                # 3. Hiển thị kết quả
                st.balloons() # Hiệu ứng bóng bay khi thành công
                st.subheader("🎉 Giáo án của bạn đã sẵn sàng:")
                st.markdown(response.text) # Dùng markdown để hiển thị đẹp hơn

            except Exception as e:
                st.error(f"Đã có lỗi xảy ra: {e}")
                st.error("Lỗi này có thể do API Key sai, hoặc do chính sách an toàn của Google. Vui lòng kiểm tra lại.")

st.sidebar.title("Giới thiệu")
st.sidebar.info(
    """
    Đây là sản phẩm demo tham gia ngày hội "Nhà giáo sáng tạo với công nghệ số và trí tuệ nhân tạo".
    \n
    Sản phẩm ứng dụng AI (Google Gemini) để tự động soạn giáo án cho giáo viên Tiểu học theo đúng chuẩn Chương trình GDPT 2018.
    """

)


