# import streamlit as st

# # # 페이지 설정
# st.title("Pictures to PDF")
# # # 변환할 사진 파일 업로드
# pics = st.file_uploader("사진, 압축 파일 업로드 (동시 업로드 가능)", accept_multiple_files=True)

# if pics :
#     st.divider()

#     # # 표지 작성 과정에서 필요한 정보 입력
#     # 제목과 내용 입력
#     col1, col2 = st.columns(2)
#     with col1 :
#         title = st.text_area("제목 입력")
#     with col2 :
#         content = st.text_area("내용 입력")

#     # 날짜와 작성자 입력
#     col3, col4 = st.columns(2)
#     with col3 :
#         date = st.text_input("날짜 입력")
#     with col4 :
#         author = st.text_input("작성자 입력")

#     # 제목, 내용 폰트 설정
#     col5, col6 = st.columns(2)
#     with col5 :
#         title_font = st.number_input("제목 폰트 설정", value=50, step=1)
#     with col6 :
#         content_font = st.number_input("내용 폰트 설정", value=30, step=1)

#     # 날짜, 작성자 폰트 설정
#     col7, col8 = st.columns(2)
#     with col7 :
#         date_font = st.number_input("날짜 폰트 설정", value=20, step=1)
#     with col8 :
#         author_font = st.number_input("작성자 폰트 설정", value=15, step=1)

#     st.divider()

#     # # PDF 생성 버튼
#     buff1, col, buff2 = st.columns([0.5, 1, 0.5])
#     with col :
#         if st.button("PDF 생성", use_container_width=True) :
#             # <code>
#             pass



import streamlit as st
import os
import zipfile
from PIL import Image, ExifTags
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from io import BytesIO
from collections import Counter
import fitz  # PyMuPDF 라이브러리

# 한글 폰트 등록
pdfmetrics.registerFont(UnicodeCIDFont('HYSMyeongJo-Medium'))

# 함수들 정의
def get_font_size(prompt, default):
    return default  # Streamlit에서는 이미 폰트 크기를 입력받았으므로 필요 없음

def extract_images_from_zip(uploaded_zip):
    images = []
    try:
        with zipfile.ZipFile(uploaded_zip) as zip_ref:
            for file_info in zip_ref.infolist():
                # macOS 숨김 파일 건너뛰기
                if file_info.filename.startswith('__MACOSX/') or \
                   os.path.basename(file_info.filename).startswith('._'):
                    continue  # 숨김 파일 건너뛰기

                lower_name = file_info.filename.lower()
                if lower_name.endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff')):
                    try:
                        with zip_ref.open(file_info) as file:
                            img_data = file.read()
                            img = Image.open(BytesIO(img_data))
                            date_object = extract_date_from_image(img)
                            images.append((img, date_object))
                    except Exception as e:
                        st.write(f"{file_info.filename} 압축 파일에서 이미지 추출 중 오류 발생: {e}")
    except Exception as e:
        st.write(f"{uploaded_zip.name} 압축 파일을 열 수 없습니다: {e}")
    return images

def extract_date_from_image(img):
    try:
        exif_data = img._getexif()
        date_taken = None
        if exif_data:
            exif = {
                ExifTags.TAGS.get(k): v
                for k, v in exif_data.items()
                if k in ExifTags.TAGS
            }
            # 촬영 날짜 가져오기
            if 'DateTimeOriginal' in exif:
                date_taken = exif['DateTimeOriginal']
            elif 'DateTime' in exif:
                date_taken = exif['DateTime']
            elif 'DateTimeDigitized' in exif:
                date_taken = exif['DateTimeDigitized']
        if date_taken:
            # 문자열을 datetime 객체로 변환
            date_object = datetime.strptime(date_taken, '%Y:%m:%d %H:%M:%S')
        else:
            # EXIF 데이터가 없으면 현재 시간 사용
            date_object = datetime.now()
    except Exception as e:
        date_object = datetime.now()
    return date_object

# 페이지 설정
st.title("Pictures to PDF")

# 변환할 사진 파일 업로드
pics = st.file_uploader("사진, 압축 파일 업로드 (동시 업로드 가능)", accept_multiple_files=True)

if pics:
    st.divider()

    # 표지 작성 과정에서 필요한 정보 입력
    # 제목과 내용 입력
    col1, col2 = st.columns(2)
    with col1:
        title = st.text_area("제목 입력")
    with col2:
        content = st.text_area("내용 입력")

    # 날짜와 작성자 입력
    col3, col4 = st.columns(2)
    with col3:
        date = st.text_input("날짜 입력 (예: 2023-10-01)")
    with col4:
        author = st.text_input("작성자 입력")

    # 제목, 내용 폰트 설정
    col5, col6 = st.columns(2)
    with col5:
        title_font_size = st.number_input("제목 폰트 설정", value=50, step=1)
    with col6:
        content_font_size = st.number_input("내용 폰트 설정", value=30, step=1)

    # 날짜, 작성자 폰트 설정
    col7, col8 = st.columns(2)
    with col7:
        date_font_size = st.number_input("날짜 폰트 설정", value=20, step=1)
    with col8:
        author_font_size = st.number_input("작성자 폰트 설정", value=15, step=1)

    # PDF 파일 이름 설정
    pdf_name = st.text_input("PDF 파일의 이름 설정")

    st.divider()

    # PDF 생성 버튼
    buff1, col, buff2 = st.columns([0.5, 1, 0.5])
    with col:
        create_pdf_button = st.button("PDF 생성", use_container_width=True)

    if create_pdf_button:
        with st.spinner('PDF를 생성하는 중입니다...'):
            try:
                # PDF 생성 코드 시작
                images_with_dates = []

                # 업로드된 파일 처리
                for uploaded_file in pics:
                    file_name = uploaded_file.name.lower()
                    if file_name.endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff')):
                        # 이미지 파일 처리
                        img = Image.open(uploaded_file)
                        date_object = extract_date_from_image(img)
                        images_with_dates.append((img, date_object))
                    elif file_name.endswith('.zip'):
                        # ZIP 파일 처리
                        images_in_zip = extract_images_from_zip(uploaded_file)
                        images_with_dates.extend(images_in_zip)
                    else:
                        st.write(f"지원하지 않는 파일 형식입니다: {uploaded_file.name}")

                if not images_with_dates:
                    st.error("처리할 수 있는 이미지가 없습니다.")
                else:
                    # 이미지 정렬
                    images_with_dates.sort(key=lambda x: x[1])

                    # 이미지 크기와 방향 분석
                    orientations = []
                    sizes = []

                    for img, date_object in images_with_dates:
                        width, height = img.size
                        sizes.append((width, height))
                        if width >= height:
                            orientations.append('landscape')
                        else:
                            orientations.append('portrait')

                    # 가장 많은 방향 선택
                    orientation_counter = Counter(orientations)
                    if orientation_counter['portrait'] >= orientation_counter['landscape']:
                        common_orientation = 'portrait'
                    else:
                        common_orientation = 'landscape'

                    # 평균 크기 계산
                    avg_width = int(sum([size[0] for size in sizes]) / len(sizes))
                    avg_height = int(sum([size[1] for size in sizes]) / len(sizes))

                    # 표지 페이지 크기 설정
                    if common_orientation == 'portrait':
                        cover_width = min(avg_width, avg_height)
                        cover_height = max(avg_width, avg_height)
                    else:
                        cover_width = max(avg_width, avg_height)
                        cover_height = min(avg_width, avg_height)

                    # PDF 생성
                    pdf_buffer = BytesIO()
                    c = canvas.Canvas(pdf_buffer)

                    # 표지 페이지 생성
                    c.setPageSize((cover_width, cover_height))

                    y_position = cover_height * 0.75  # 시작 y 위치
                    margin = 10  # 여백

                    # 표지 내용 그리기
                    c.setFont("HYSMyeongJo-Medium", title_font_size)
                    text_width = c.stringWidth(title, "HYSMyeongJo-Medium", title_font_size)
                    c.drawString((cover_width - text_width) / 2, y_position, title)

                    y_position -= title_font_size + 20
                    c.setFont("HYSMyeongJo-Medium", content_font_size)
                    text_width = c.stringWidth(content, "HYSMyeongJo-Medium", content_font_size)
                    c.drawString((cover_width - text_width) / 2, y_position, content)

                    y_position -= content_font_size + 20
                    c.setFont("HYSMyeongJo-Medium", date_font_size)
                    text_width = c.stringWidth(date, "HYSMyeongJo-Medium", date_font_size)
                    c.drawString((cover_width - text_width) / 2, y_position, date)

                    y_position -= date_font_size + 20
                    c.setFont("HYSMyeongJo-Medium", author_font_size)
                    text_width = c.stringWidth(author, "HYSMyeongJo-Medium", author_font_size)
                    c.drawString((cover_width - text_width) / 2, y_position, author)

                    # 오른쪽 상단에 제목 추가
                    c.setFont("HYSMyeongJo-Medium", 8)
                    title_text_width = c.stringWidth(title, "HYSMyeongJo-Medium", 8)
                    c.drawString(cover_width - title_text_width - margin, cover_height - 10, title)

                    c.showPage()  # 다음 페이지로 이동

                    # 페이지 번호 초기화
                    page_num = 1

                    # 이미지 페이지 추가
                    for img, date_object in images_with_dates:
                        width, height = img.size

                        # 현재 이미지의 크기에 맞게 페이지 크기 설정
                        c.setPageSize((width, height))

                        # 이미지를 페이지에 추가 (원본 크기로)
                        img_buffer = BytesIO()
                        img.save(img_buffer, format='PNG')
                        img_buffer.seek(0)
                        image = ImageReader(img_buffer)
                        c.drawImage(image, 0, 0, width=width, height=height)

                        # 페이지 번호 추가 (하단 중앙)
                        page_number_text = f"-{page_num}-"
                        c.setFont("HYSMyeongJo-Medium", 12)
                        text_width = c.stringWidth(page_number_text, "HYSMyeongJo-Medium", 12)
                        c.drawString((width - text_width) / 2, 15, page_number_text)

                        # 오른쪽 상단에 제목 추가
                        c.setFont("HYSMyeongJo-Medium", 8)
                        title_text_width = c.stringWidth(title, "HYSMyeongJo-Medium", 8)
                        c.drawString(width - title_text_width - margin, height - 10, title)

                        c.showPage()
                        page_num += 1

                    c.save()
                    pdf_buffer.seek(0)

                    st.success("PDF 생성이 완료되었습니다.")
                    st.divider()

                    # PDF 미리보기 (앞 5페이지)
                    doc = fitz.open(stream=pdf_buffer.getvalue(), filetype="pdf")
                    num_pages = min(5, len(doc))

                    st.write("**PDF 미리보기**")
                    preview_images = []
                    for page_num in range(num_pages):
                        page = doc.load_page(page_num)
                        pix = page.get_pixmap()
                        img_data = pix.tobytes("png")
                        preview_images.append(img_data)

                    st.image(preview_images, width=None)  # 화면 전체 너비 사용

                    buff1, col, buff2 = st.columns([0.5, 1, 0.5])
                    # PDF 다운로드 버튼 추가 (크기 조정)
                    with col :
                        st.download_button(
                            label="PDF 다운로드",
                            data=pdf_buffer.getvalue(),
                            file_name=(pdf_name if pdf_name.lower().endswith('.pdf') else pdf_name + '.pdf') if pdf_name else "output.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
            except Exception as e:
                st.error(f"PDF 생성 중 오류가 발생하였습니다: {e}")
