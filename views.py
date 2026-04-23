# -*- coding: utf-8 -*-
import google.generativeai as genai
import json
import re
from django.shortcuts import render
from .models import CV
from . import utils

# API Config
genai.configure(api_key="AIzaSyAOrli5WUo7HvsuRT48jcSlPbrILgn-Y_Y")

def cv_analiz_view(request):
    result = None
    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        pdf_file = request.FILES.get('pdf_file')
        job_description = request.POST.get('job_description')

        # 1. Kayit
        cv_obj = CV.objects.create(fullname=fullname, pdf_file=pdf_file)
        
        # 2. PDF Metin Cikarma
        cv_data = utils.extract_and_analyze(cv_obj.pdf_file.path)

        if cv_data and "error" not in cv_data:
            cv_text = cv_data.get('text', '')
            
            # Dinamik Prompt: Sayilari ve meslekleri tamamen AI belirliyor
            prompt = (
                f"Bugunun tarihi: 23 Nisan 2026. Aday: {fullname}. CV: {cv_text}. Hedef Is: {job_description}. "
                "Gorevin: Kariyer danismani olarak CV'yi analiz et ve SADECE JSON dondur. "
                "Kurallar: 1. Skorlari ve uyum yuzdelerini CV icerigine gore dinamik hesapla. "
                "2. 'grafik' alanina adayin yeteneklerine uygun 3 farkli gercek meslek unvani ve yuzdesini yaz. "
                "JSON Yapisi: "
                "{"
                "\"taktik\": \"CV gelisimi icin 3 kisa ve oz tavsiye.\","
                "\"pozisyon\": \"En uygun ideal unvan\","
                "\"eksikler\": \"Gelistirilmesi gereken 3 teknik beceri\","
                "\"skor\": 0,"
                "\"grafik\": \"Meslek1: %0 | Meslek2: %0 | Meslek3: %0\""
                "}"
            )

            try:
                # 404 HATASINI ONLEMEK ICIN MODEL TARAMA (Senin saglam yapin)
                available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                ai_response_text = ""
                
                target_model = "models/gemini-1.5-flash"
                if target_model not in available_models:
                    target_model = available_models[0] if available_models else "models/gemini-pro"

                model = genai.GenerativeModel(target_model)
                response = model.generate_content(prompt)
                ai_response_text = response.text

                # JSON Ayristirma (Regex ile)
                match = re.search(r'\{.*\}', ai_response_text, re.DOTALL)
                if match:
                    pj = json.loads(match.group(0))
                    
                    # HTML degisken isimleriyle tam uyum (Kutulari doldurur)
                    result = {
                        'ai_advice': pj.get('taktik', 'Oneri hazirlanamadi.'),
                        'top_match': pj.get('pozisyon', '-'),
                        'skills': pj.get('eksikler', '-'),
                        'ats': {'ats_score': pj.get('skor', 0)},
                        'jobs': pj.get('grafik', '') # Grafik isimleri ve yuzdeleri buradan gider
                    }
                else:
                    result = {'ai_advice': 'AI uygun formatta cevap vermedi.'}

            except Exception as e:
                result = {'ai_advice': f"AI Baglanti Hatasi: {str(e)}"}

            # Veritabanini guncelle
            cv_obj.skills = str(result.get('skills', ''))
            cv_obj.save()
        else:
            result = {"ai_advice": "Dosya okuma hatasi."}

    return render(request, 'upload.html', {'result': result})