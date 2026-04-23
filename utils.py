# -*- coding: utf-8 -*-
from pypdf import PdfReader

def extract_and_analyze(file_path):
    text = ""
    try:
        reader = PdfReader(file_path)
        # Tum sayfalardaki metni birlestir
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
        
        # Eger metin hala bossa sozluk dondur
        if not text.strip():
            return {"error": "PDF icerigi bos (Belki de resim formatinda?)."}
            
        return {
            "text": text,
            "jobs": "Analiz Ediliyor..." # Gecici veri
        }
    except Exception as e:
        return {"error": f"PDF okuma hatasi: {str(e)}"}