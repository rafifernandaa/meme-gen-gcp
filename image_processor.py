from PIL import Image, ImageDraw, ImageFont

class MemeEngine:
    def __init__(self, font_path="fonts/impact.ttf"):
        # Font default jika user tidak memilih
        self.default_font_path = font_path

    # ... (kode sebelumnya sama)

    def process_image(self, image_file, top_text, bottom_text, font_path=None, font_scale=1.0):
        """
        Modified to accept font_scale (float).
        1.0 = Normal size, 0.5 = Half size, 2.0 = Double size.
        """
        active_font_path = font_path if font_path else self.default_font_path

        img = Image.open(image_file).convert("RGB")

        # Resize logic
        max_width = 800
        if img.width > max_width:
            ratio = max_width / float(img.width)
            new_height = int(float(img.height) * float(ratio))
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

        draw = ImageDraw.Draw(img)
        w, h = img.size

        # --- UPDATE DISINI: Mengalikan dengan font_scale ---
        # Default base adalah h/10, lalu dikali skala user
        base_font_size = int((h / 10) * font_scale)

        if top_text:
            self._draw_text(draw, w, h, top_text.upper(), base_font_size, active_font_path, position="top")
        if bottom_text:
            self._draw_text(draw, w, h, bottom_text.upper(), base_font_size, active_font_path, position="bottom")

        return img
    
    # ... (fungsi _draw_text dan lainnya tetap sama)

    def _load_font(self, font_path, font_size):
        try:
            return ImageFont.truetype(font_path, font_size)
        except IOError:
            print(f"WARNING: Font file '{font_path}' not found. Using default font.")
            return ImageFont.load_default()

    def _wrap_text_to_width(self, draw, text, font, max_width):
        """
        Membungkus teks berdasarkan lebar maksimum (pixel).
        """
        words = text.split()
        if not words:
            return []

        lines = []
        current_line = words[0]

        for word in words[1:]:
            test_line = current_line + " " + word
            bbox = draw.textbbox((0, 0), test_line, font=font)
            line_width = bbox[2] - bbox[0]
            if line_width <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word

        lines.append(current_line)
        return lines

    def _draw_text(self, draw, img_width, img_height, text, base_font_size, font_path, position="top"):
        """
        Logika inti: Resize font sampai muat, wrap text, lalu gambar dengan outline.
        """
        if not text:
            return

        max_width = img_width * 0.95  # margin kiri kanan
        font_size = base_font_size
        min_font_size = max(10, int(base_font_size / 3))

        # --- A. Cari font size yang pas ---
        while font_size >= min_font_size:
            font = self._load_font(font_path, font_size)
            lines = self._wrap_text_to_width(draw, text, font, max_width)

            if not lines:
                break

            # Cek apakah lebar baris terpanjang masih muat
            max_line_width = 0
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                line_width = bbox[2] - bbox[0]
                if line_width > max_line_width:
                    max_line_width = line_width

            if max_line_width <= max_width:
                break # Sudah muat
            
            font_size -= 2 # Kecilkan font

        # Gunakan font size terakhir yang berhasil
        font = self._load_font(font_path, font_size)
        lines = self._wrap_text_to_width(draw, text, font, max_width)

        # --- B. Hitung posisi Y ---
        total_height = 0
        line_heights = []
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_height = bbox[3] - bbox[1]
            line_heights.append(line_height)
            total_height += line_height + 5  # spacing

        margin = 15
        if position == "bottom":
            current_y = img_height - total_height - margin
        else:  # "top"
            current_y = margin

        # --- C. Gambar Text + Outline ---
        stroke_width = max(2, int(font_size / 15)) # Stroke dinamis mengikuti ukuran font
        
        for line, line_height in zip(lines, line_heights):
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x_pos = (img_width - text_width) / 2 # Center align

            # Gambar Outline (Hitam)
            draw.text((x_pos-stroke_width, current_y), line, font=font, fill="black")
            draw.text((x_pos+stroke_width, current_y), line, font=font, fill="black")
            draw.text((x_pos, current_y-stroke_width), line, font=font, fill="black")
            draw.text((x_pos, current_y+stroke_width), line, font=font, fill="black")
            
            # Gambar Text Utama (Putih)
            draw.text((x_pos, current_y), line, font=font, fill="white")

            current_y += line_height + 5