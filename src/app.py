import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
from io import BytesIO
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextBox, LTTextLine

from google_trans_new import google_translator  
translator = google_translator()  


if "slider_value" not in st.session_state:
    print("in if slider")
    st.session_state["slider_value"] = 1



@st.cache_data
def render_pdf_as_images(pdf_file):
    """Convert a PDF into a list of PIL images (one per page)."""
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    images = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        pix = page.get_pixmap()
        img = Image.open(BytesIO(pix.tobytes("png")))
        images.append(img)
    return images


def update_slider(increment,total_pages):
    # st.session_state["slider_value"] += increment
    
    st.session_state["slider_value"] = min(st.session_state["slider_value"]+increment, total_pages)
    if st.session_state["slider_value"]<1:
        st.session_state["slider_value"] = 1

def reset_slider():
    st.session_state["slider_value"] = 1

def convert_to_md(pdf_file,pagenum,m_down_col):
    container = m_down_col.container(height=500, border=True)
    for page_layout in extract_pages(pdf_file,page_numbers=[pagenum]):
        for element in page_layout:
            if isinstance(element, LTTextBox) or isinstance(element, LTTextLine):
                translate_text = translator.translate(element.get_text().strip(),lang_tgt=st.session_state["lang"])  
                # print(translate_text,int(element.x0), int(element.y0))                
                container.markdown(translate_text)

                

# Streamlit app
st.title("PDF Viewer and Tranlator")


# File upload
pdf_file, lang_select, m_down_col = st.columns([1,0.5,1])
with pdf_file:
    pdf_path = st.file_uploader("Upload First PDF", type="pdf", on_change=reset_slider)
with lang_select:
    selected_lang = st.selectbox( 'Choose your language?', ('en', 'cn', 'tn'))
    st.session_state["lang"] = selected_lang


# with open(pdf_path, "rb") as f:
    # Render PDF pages as images
if pdf_path and selected_lang:
    pdf_images = render_pdf_as_images(pdf_path)
        
    if pdf_images:
        # Create page selector
        total_pages = len(pdf_images)
        page_number = st.slider("Current Page", min_value = 1, max_value = total_pages, value=st.session_state["slider_value"])
        
        # Add navigation buttons
        
        col11, col22, _ = st.columns([1,1,4])
        with col11:
            st.button("Previous", on_click=update_slider,args=(-1,total_pages, )) #and page_number > 1:
                # page_number -= 1
                # update_slider(-1)
        with col22:
            st.button("Next", on_click=update_slider,args=(1, total_pages,)) #and page_number < total_pages:
                # page_number += 1
            # update_slider(1)
        pdf_file.image(
            pdf_images[page_number-1], 
            caption=f"Page {page_number} of {total_pages}",
            use_column_width=False
        )
        # Update the slider when using buttons
        # st.session_state["Current Page"] = page_number
        st.session_state.slider_value = page_number
        print(st.session_state.slider_value)
        st.write(f"Current Page: {st.session_state.slider_value}")
        
        # convert to markdown
        convert_to_md(pdf_path,page_number-1,m_down_col)
        
        
    else:
        st.warning("No pages found in PDF")
else:
    st.info("Upload a PDF to get started")