from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Hotel, Reservation
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from google import genai
import json
import os

# 1. ANA SAYFA
def home(request):
    oteller = Hotel.objects.all()
    return render(request, 'home.html', {'oteller': oteller})

def arama_sonuclari(request):
    sehir = request.GET.get('q', '').strip() 
    fiyat_max = request.GET.get('price_max')
    yildizlar = request.GET.getlist('star')
    
    oteller = Hotel.objects.all()
    
    if sehir:
        
        sehir_lower = sehir.replace('İ', 'i').replace('I', 'ı').lower()
        
        if sehir_lower.startswith('i'):
            sehir_title = 'İ' + sehir_lower[1:]
        elif sehir_lower.startswith('ı'):
            sehir_title = 'I' + sehir_lower[1:]
        else:
            sehir_title = sehir_lower.capitalize()

        # Hem kullanıcının yazdığı orijinal haliyle hem de baş harfi büyütülmüş özel haliyle arama yapıyoruz
        oteller = oteller.filter(
            Q(name__icontains=sehir) | 
            Q(city__icontains=sehir) |
            Q(district__icontains=sehir) |
            Q(name__icontains=sehir_title) | 
            Q(city__icontains=sehir_title) |
            Q(district__icontains=sehir_title)
        )
        
    if fiyat_max and fiyat_max.isdigit():
        oteller = oteller.filter(price__lte=fiyat_max)

    if yildizlar:
        oteller = oteller.filter(star_rating__in=yildizlar)
        
    return render(request, 'search.html', {
        'oteller': oteller, 
        'aranan_sehir': sehir
    })

# 3. OTEL DETAY
def otel_detay(request, id):
    otel = get_object_or_404(Hotel, id=id)
    mevcut_rezervasyonlar = None
    
    if request.user.is_authenticated:
        mevcut_rezervasyonlar = Reservation.objects.filter(
            user=request.user, 
            hotel=otel
        ).order_by('-check_in')
        
    return render(request, 'hotel_detail.html', {
        'otel': otel, 
        'mevcut_rezervasyonlar': mevcut_rezervasyonlar
    })

# 4. KAYIT OLMA
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = request.POST.get('email')
            user.save()
            messages.success(request, 'Başarıyla kayıt oldunuz. Şimdi giriş yapabilirsiniz.') 
            return redirect('login') # Kayıttan sonra login'e yönlendirmek daha mantıklı olabilir
    else:
        form = UserCreationForm()
    
    return render(request, 'register.html', {'form': form})

# 5. REZERVASYON KONTROL (AJAX)
@login_required
def rezervasyon_kontrol(request, hotel_id):
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')
    
    # Tarihlerin boş gelme ihtimaline karşı kontrol
    if not check_in or not check_out:
        return JsonResponse({'exists': False})

    exists = Reservation.objects.filter(
        user=request.user,
        hotel_id=hotel_id,
        check_in=check_in,
        check_out=check_out
    ).exists()
    
    return JsonResponse({'exists': exists})

# 6. REZERVASYON YAPMA
@login_required
def rezervasyon_yap(request, hotel_id):
    if request.method == 'POST':
        hotel = get_object_or_404(Hotel, id=hotel_id)
        check_in = request.POST.get('check_in')
        check_out = request.POST.get('check_out')

        
        cakisma_var_mi = Reservation.objects.filter(
            user=request.user,
            hotel=hotel,
            check_in=check_in,
            check_out=check_out
        ).exists()

        if cakisma_var_mi:
            messages.warning(request, 'Bu tarihler için zaten bir rezervasyonunuz bulunuyor.')
            return redirect('rezervasyonlarim')

        # Kaydetme işlemi
        Reservation.objects.create(
            user=request.user,
            hotel=hotel,
            check_in=check_in,
            check_out=check_out,
            adults=request.POST.get('adults', 1),
            children=request.POST.get('children', 0)
        )
        
        messages.success(request, f'{hotel.name} için rezervasyonunuz başarıyla oluşturuldu!')
        return redirect('rezervasyonlarim')


@login_required
def rezervasyonlarim(request):
    rezervasyonlar = Reservation.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'rezervasyonlarim.html', {'rezervasyonlar': rezervasyonlar})

# 8. REZERVASYON İPTAL ETME
@login_required
def rezervasyon_iptal(request, id):
    if request.method == 'POST':
        rezervasyon = get_object_or_404(Reservation, id=id, user=request.user)
        rezervasyon.delete()
        messages.info(request, 'Rezervasyonunuz başarıyla iptal edildi.')
    
    return redirect('rezervasyonlarim')


def password_reset_check(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            email = data.get('email')
            
            user_exists = User.objects.filter(username=username, email=email).exists()
            return JsonResponse({'success': user_exists})
        except (json.JSONDecodeError, AttributeError):
            return JsonResponse({'success': False}, status=400)
    
    return JsonResponse({'success': False}, status=405)



client = api_key = os.environ.get("GEMINI_API_KEY")

@csrf_exempt 
def chatbot_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            kullanici_mesaji = data.get('message', '')

           
            oteller = Hotel.objects.all()
            
            
            otel_listesi = ""
            for otel in oteller:
                otel_listesi += f"- {otel.name}: {otel.city}/{otel.district} konumunda, geceliği {otel.price} TL, {otel.star_rating} yıldızlı.\n"

            
            sistem_talimati = f"""
            Sen SmartTravel adlı bir otel rezervasyon platformunun asistanısın. 
            Görevin sadece platformdaki oteller hakkında kullanıcılara yardımcı olmaktır.
            Aşağıdaki otel listesinde olmayan hiçbir mekan hakkında bilgi verme. 
            Eğer kullanıcı oteller veya seyahat dışında bir şey sorarsa kibarca reddet.
            ÖNEMLİ KURALLAR:
            1. Otelleri karşılaştırırken mutlaka Markdown TABLO formatını kullan.
            2. Fiyatları, konumları ve yıldızları ayrı sütunlarda göster.
            3. Yanıtlarını kısa, öz ve okunabilir tut.
            
            Sistemimizdeki Güncel Oteller:
            {otel_listesi}
            """

           
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=kullanici_mesaji,
                config=genai.types.GenerateContentConfig(
                    system_instruction=sistem_talimati,
                    temperature=0.3 
                ),
            )

            return JsonResponse({'reply': response.text, 'status': 'success'})

        except Exception as e:
    
            if "503" in str(e):
                hata_mesaji = "Asistanımız şu an çok yoğun, lütfen birkaç saniye sonra tekrar dener misiniz?"
    else:
        hata_mesaji = "Küçük bir teknik aksaklık oldu, hemen ilgileniyorum."
        
    return JsonResponse({'reply': hata_mesaji, 'status': 'error'})