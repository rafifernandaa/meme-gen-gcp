import streamlit as st
import os
import google.generativeai as genai
import urllib.parse
import random
from image_processor import MemeEngine
from storage_manager import GCSManager
from io import BytesIO

# --- 1. CONFIGURATION & CSS INJECTION ---
st.set_page_config(page_title="MemeGen: Create Your Own Memes", layout="wide", page_icon="😼")

# CUSTOM CSS: This is what changes the look to "Kitten Wifhat" style
st.markdown("""
<style>
    /* IMPORT FONTS */
    @import url('https://fonts.googleapis.com/css2?family=Fredoka+One&family=Inter:wght@400;700&display=swap');

    /* GLOBAL THEME & SPACING FIX */
    .stApp {
        background-color: #121212;
        font-family: 'Inter', sans-serif;
    }
    
    /* MENGATUR JARAK ATAS HALAMAN AGAR LEBIH RAPI */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 5rem;
    }

    /* HEADERS */
    h1 {
        font-family: 'Fredoka One', cursive;
        color: #FF3399 !important;
        text-shadow: 4px 4px #000000;
        font-size: 3rem !important; /* Memperbesar Judul */
        margin-bottom: 0px;
    }
    
    h2, h3, h4 {
        font-family: 'Fredoka One', cursive;
        color: white !important;
        letter-spacing: 1px;
    }

    /* INPUT FIELDS */
    .stTextInput > div > div > input {
        background-color: #1E1E1E;
        color: white;
        border: 2px solid #FF6B35;
        border-radius: 10px;
        padding: 10px;
        font-weight: bold;
    }

    /* BUTTONS */
    .stButton > button {
        background: linear-gradient(90deg, #FF6B35 0%, #FF3399 100%);
        color: white;
        border: none;
        padding: 15px 30px;
        border-radius: 50px;
        font-family: 'Fredoka One', cursive;
        font-size: 20px;
        text-transform: uppercase;
        transition: transform 0.2s, box-shadow 0.2s;
        width: 100%;
        border: 2px solid white;
        box-shadow: 0px 5px 0px #b00b56; /* Efek 3D Button */
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0px 8px 0px #b00b56;
    }
    .stButton > button:active {
        transform: translateY(2px);
        box-shadow: 0px 2px 0px #b00b56;
    }

    /* TABS FIX (BAGIAN YANG MENUMPUK) */
    .stTabs {
        margin-top: 20px; /* Memberi jarak dari header */
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 15px; /* Jarak antar tab */
        background-color: transparent;
        padding: 10px 5px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: #1E1E1E;
        border: 2px solid #FF3399;
        border-radius: 12px;
        color: white;
        padding: 10px 25px;
        font-family: 'Fredoka One', cursive;
        font-size: 16px;
        transition: all 0.3s ease;
    }

    .stTabs [aria-selected="true"] {
        background-color: #FF3399 !important;
        color: white !important;
        border: 2px solid white !important;
        box-shadow: 5px 5px 0px #000000;
        transform: translate(-3px, -3px);
    }

    /* FILE UPLOADER & IMAGES */
    div[data-testid="stFileUploader"] {
        border: 2px dashed #FF6B35;
        border-radius: 15px;
        background-color: #1E1E1E;
        padding: 20px;
    }
    
    div[data-testid="stImage"] img {
        border: 4px solid #FF6B35;
        border-radius: 15px;
        box-shadow: 10px 10px 0px #000;
    }
</style>
""", unsafe_allow_html=True)

# --- DATA ---
MEME_STYLES = ["Classic", "Sarcastic", "Absurd", "Wholesome", "Crypto Bro", "Gen Z"]
RANDOM_PHRASES = [
    ("WAITING FOR", "THE DIP"),
    ("ME EXPLAINING", "WHY I NEED COFFEE"),
    ("POV:", "YOU DEPLOYED ON FRIDAY"),
    ("SERVERLESS", "MORE LIKE WALLET-LESS"),
]
FONT_OPTIONS = {
    "Impact (Classic)": "fonts/Impact.ttf", 
    "Barriecito (Playful)": "fonts/Barriecito-Regular.ttf", 
    "Birthstone (Fancy)": "fonts/Birthstone-Regular.ttf"
}

# --- SETUP ---
BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME", "meme-bucket-placeholder")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

meme_engine = MemeEngine()
try:
    storage_manager = GCSManager(BUCKET_NAME)
except:
    storage_manager = None

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')

# --- HEADER SECTION ---
col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.markdown("# WIF MEME GENERATOR 😼")
    st.markdown("**Create Your Own Meme** | Powered by Google Cloud Run")
with col_head2:
    if storage_manager:
        st.success(f"🟢 Storage Connected")
    else:
        st.warning("🔴 Storage Offline")

# --- MAIN LOGIC ---
tab1, tab2 = st.tabs(["⚡ GENERATOR", "🖼️ GALLERY"])

with tab1:
    # HERO LAYOUT (Split Screen)
    col_left, col_right = st.columns([1, 1.2], gap="large")
    
    with col_left:
        st.markdown("### 1. INPUT ZONE")
        
        # A. UPLOAD
        uploaded_file = st.file_uploader("📂 DROP IMAGE HERE", type=['jpg', 'png', 'jpeg'])

        # B. AI GENERATOR BOX
        with st.container():
            st.markdown("---")
            st.markdown("#### 🤖 AI AUTO-FILL")
            ai_col1, ai_col2 = st.columns([2, 1])
            with ai_col1:
                context = st.text_input("Context / Topic", placeholder="e.g. 'Coding Errors'")
            with ai_col2:
                meme_style = st.selectbox("Style", MEME_STYLES)
            
            if st.button("✨ GENERATE CAPTIONS"):
                if not GOOGLE_API_KEY:
                    st.error("API Key Missing!")
                elif not context:
                    st.warning("Enter a topic first!")
                else:
                    with st.spinner("AI IS COOKING..."):
                        try:
                            prompt = (f"Write a {meme_style} meme about: {context}. "
                                      "Format: TOP_TEXT | BOTTOM_TEXT. No quotes.")
                            response = model.generate_content(prompt)
                            text = response.text.strip()
                            if "|" in text:
                                parts = text.split("|")
                                st.session_state['top_text'] = parts[0].strip()
                                st.session_state['bottom_text'] = parts[1].strip()
                            else:
                                st.session_state['top_text'] = text
                        except Exception as e:
                            st.error(f"AI Died: {e}")

        # C. MANUAL CONTROLS
        st.markdown("---")
        st.markdown("#### ✍️ MANUAL EDIT")
        
        # Randomizer
        if st.button("🎲 I'M FEELING LUCKY"):
            t, b = random.choice(RANDOM_PHRASES)
            st.session_state['top_text'] = t
            st.session_state['bottom_text'] = b

        top_text = st.text_input("TOP TEXT", value=st.session_state.get('top_text', ''))
        bottom_text = st.text_input("BOTTOM TEXT", value=st.session_state.get('bottom_text', ''))
        
        # Advanced Settings Accordion
        with st.expander("⚙️ ADVANCED SETTINGS"):
            font_scale = st.slider("Font Size Multiplier", 0.5, 2.0, 1.0, 0.1)
            selected_font = st.selectbox("Font", list(FONT_OPTIONS.keys()))

    with col_right:
        st.markdown("### 2. PREVIEW")
        
        final_image = None
        
        if uploaded_file:
            # PROCESS
            final_image = meme_engine.process_image(
                uploaded_file, 
                top_text, 
                bottom_text, 
                font_path=FONT_OPTIONS[selected_font],
                font_scale=font_scale
            )
            st.image(final_image, caption="LIVE PREVIEW", use_column_width=True)
        else:
            # PLACEHOLDER (Use a generic placeholder URL)
            st.image("https://i.imgflip.com/1ur9b0.jpg", caption="UPLOAD AN IMAGE TO START", width=400)

        # ACTION BUTTONS
        if final_image:
            st.markdown("---")
            act_col1, act_col2 = st.columns(2)
            
            # Prepare buffer
            buf = BytesIO()
            final_image.save(buf, format="JPEG")
            byte_im = buf.getvalue()

            with act_col1:
                st.download_button(
                    "📥 DOWNLOAD", 
                    data=byte_im, 
                    file_name="meme_brutal.jpg", 
                    mime="image/jpeg"
                )
            with act_col2:
                if storage_manager:
                    if st.button("☁️ SAVE TO GALLERY"):
                        with st.spinner("UPLOADING..."):
                            url = storage_manager.upload_image(final_image)
                            st.success("SAVED!")
                            st.session_state['last_url'] = url

            # --- 4. SHARE SECTION (NEW) ---
            # Kita gunakan 'last_url' agar sesuai dengan tombol Save di atas
            last_url = st.session_state.get("last_url") 

            if last_url:
                st.markdown("---")
                st.markdown("#### 🚀 SHARE MEME")

                # Link yang bisa diklik
                st.markdown(f"🔗 **Link:** [Open in new tab]({last_url})")

                # Field yang mudah dicopy
                st.text_input(
                    "Copy Link:",
                    value=last_url,
                    key="share_link_display"
                )

                # Social Media Quick Links
                encoded_msg = urllib.parse.quote_plus(f"Look at this meme I made: {last_url}")
                
                # Menggunakan kolom agar tombol share rapi
                share_col1, share_col2 = st.columns(2)
                with share_col1:
                    st.markdown(
                        f"""<a href="https://wa.me/?text={encoded_msg}" target="_blank">
                        <button style="width:100%; background-color:#25D366; color:white; border:none; padding:10px; border-radius:10px; font-weight:bold;">
                        Share on WhatsApp 💬
                        </button></a>""", 
                        unsafe_allow_html=True
                    )
                with share_col2:
                    st.markdown(
                        f"""<a href="https://twitter.com/intent/tweet?text={encoded_msg}" target="_blank">
                        <button style="width:100%; background-color:#1DA1F2; color:white; border:none; padding:10px; border-radius:10px; font-weight:bold;">
                        Share on X 🐦
                        </button></a>""", 
                        unsafe_allow_html=True
                    )
            
            # Pesan jika belum disave
            elif final_image and not last_url:
                st.markdown("---")
                st.info("💡 Tip: Click 'Save to Gallery' to get a shareable link!")

# --- TEMPLATE CAROUSEL (STATIC FEATURE) ---
st.markdown("---")
st.markdown("### 🧩 OR PICK A TEMPLATE")
tmpl_col1, tmpl_col2, tmpl_col3 = st.columns(3)
# Note: In a real app, clicking these would set the 'uploaded_file' state, 
# but Streamlit file_uploader is read-only for security. 
# Just for UI Demo:
with tmpl_col1:
    st.image("https://i.imgflip.com/1g8my4.jpg", caption="Two Buttons")
with tmpl_col2:
    st.image("https://i.imgflip.com/26am.jpg", caption="Villager")
with tmpl_col3:
    st.image("https://i.imgflip.com/30b1gx.jpg", caption="Drake")


with tab2:
    st.markdown("## 🖼️ THE VAULT")
    if st.button("🔄 REFRESH VAULT"):
        st.rerun()
    
    if storage_manager:
        try:
            images = storage_manager.list_images()
            if images:
                # Masonry Grid Mockup
                grid_cols = st.columns(3)
                for idx, img in enumerate(images):
                    with grid_cols[idx % 3]:
                        # Using Markdown image for speed if URL is public, else use download logic
                        try:
                             # Assumes blob.media_link or public URL works
                            st.image(img.media_link if hasattr(img, 'media_link') else img, use_column_width=True)
                        except:
                             st.warning("Image Error")
            else:
                st.info("Vault is empty.")
        except Exception as e:
            st.error(str(e))
    else:
        st.error("Storage not connected.")