import math
import matplotlib.pyplot as plt

def get_float(prompt, default):
    try:
        val = input(f"{prompt} [Varsayılan: {default}]: ")
        if val.strip() == "":
            return default
        return float(val)
    except ValueError:
        print("Geçersiz giriş, varsayılan değer kullanılıyor.")
        return default

def get_int(prompt, default):
    try:
        val = input(f"{prompt} [Varsayılan: {default}]: ")
        if val.strip() == "":
            return default
        return int(val)
    except ValueError:
        print("Geçersiz giriş, varsayılan değer kullanılıyor.")
        return default

def solve_exit_mach(epsilon, gamma):
    """Süpersonik nozül çıkış Mach sayısını Newton-Raphson yöntemi ile hesaplar."""
    M = 2.0  
    for _ in range(50):
        term = (2 + (gamma - 1) * M**2) / (gamma + 1)
        power = (gamma + 1) / (2 * (gamma - 1))
        
        f = (1/M) * term**power - epsilon
        df_dM = - (1 / M**2) * term**power + (1/M) * power * term**(power - 1) * (2 * (gamma - 1) * M / (gamma + 1))
        
        M_new = M - f / df_dM
        if abs(M_new - M) < 1e-5:
            return M_new
        M = M_new
    return M

def run_simulation():
    print("="*65)
    print(" GELİŞMİŞ ROKET MOTORU İTKİ SİMÜLASYONU (Dinamik Diferansiyel)")
    print("="*65)
    print("Motor parametrelerini giriniz (Varsayılanları kullanmak için ENTER'a basınız):\n")

    print("--- Yakıt Geometrisi ---")
    D_o_mm = get_float("Yakıt Dış Çapı (mm)", 98.7)
    D_i_mm = get_float("Yakıt İç (Kor) Çapı (mm)", 43.7)
    L_g_mm = get_float("Tek Segment Uzunluğu (mm)", 145.0)
    N_grains = get_int("Segment (Grain) Sayısı", 2)

    print("\n--- Nozül ve Verimlilik ---")
    D_t_init_mm = get_float("Başlangıç Nozül Boğaz Çapı (mm)", 21.0)
    D_e_mm = get_float("Nozül Çıkış Çapı (mm)", 44.4)
    erosion_rate_mm = get_float("Nozül Aşınma Hızı (mm/s)", 0.2)
    eta_f = get_float("İtki Verimlilik Katsayısı (eta_f) [0.85 - 1.0]", 0.95)

    print("\n--- Yakıt Kimyasal Özellikleri ---")
    # Katsayı artık mm/s / MPa^n cinsinden alınıp arka planda çevriliyor (Madde 4)
    a_lit = get_float("Yanma Hızı Katsayısı, a (mm/s / MPa^n)", 4.0) 
    n = get_float("Yanma Hızı Üssü, n", 0.35)
    rho_p = get_float("Yakıt Yoğunluğu (kg/m^3)", 1700.0)
    gamma = get_float("Özgül Isı Oranı (Gamma)", 1.20)
    T_c = get_float("Yanma Odası Sıcaklığı (K)", 3300.0)
    M_w = get_float("Gaz Molekül Ağırlığı (kg/kmol)", 27.5)
    
    print("\n--- Erozyonlu Yanma (Erosive Burning) ---")
    # Basitleştirilmiş erozyon katsayısı (K) (Madde 5)
    k_erosive = get_float("Erozyon Çarpanı (Sıfır ise kapalıdır)", 0.0005)

    print("\n--- Ortam Şartları ---")
    P_a = get_float("Ortam Basıncı (Pa)", 101325.0)

    # Birim Dönüşümleri (mm -> m)
    D_o = D_o_mm / 1000.0
    D_i = D_i_mm / 1000.0
    L_g = L_g_mm / 1000.0
    D_t = D_t_init_mm / 1000.0
    D_e = D_e_mm / 1000.0
    erosion_rate = erosion_rate_mm / 1000.0
    
    # 'a' Katsayısını SI Birimine Çevirme (m/s / Pa^n)
    a_si = (a_lit / 1000.0) * (1e-6)**n

    # Gaz Sabitleri
    R_u = 8314.0 # J/(kmol*K)
    R = R_u / M_w
    
    # Karakteristik Hız (c*)
    c_star = math.sqrt(gamma * R * T_c) / (gamma * math.sqrt((2 / (gamma + 1)) ** ((gamma + 1) / (gamma - 1))))
    
    # Simülasyon Zaman Adımları
    dt = 0.0005      # Daha kararlı çözüm için dt küçültüldü (0.5 ms)
    dt_out = 0.01    # Grafik veri adımı (10 ms)
    
    t = 0.0
    last_out_time = -dt_out
    
    # Başlangıç Koşulları (Madde 2 - Dinamik Başlangıç)
    r_burn = 0.0 
    Pc = P_a      # Başlangıçta oda basıncı ortam basıncına eşit
    
    # Veri Listeleri
    times, thrusts, pressures, throats = [], [], [], []

    print("\nSimülasyon hesaplanıyor (Dinamik Diferansiyel Çözüm)...")

    while True:
        # 1. Anlık Yakıt Geometrisi
        R_i = D_i / 2 + r_burn
        L = L_g - 2 * r_burn
        R_o = D_o / 2

        if R_i >= R_o or L <= 0:
            # Sona erdiğinde kuyruk (tail-off) düşüşünü daha yumuşak bitirmek için kısa bir süre bekleme eklenebilir.
            # Şu an için gaz tamamen tahliye olana kadar döngü kırılarak bitiriliyor.
            break
            
        # Alan Hesaplamaları
        A_core = 2 * math.pi * R_i * L
        A_end = 2 * math.pi * (R_o**2 - R_i**2)
        A_b = N_grains * (A_core + A_end)
        
        A_t = math.pi * (D_t**2) / 4
        A_e = math.pi * (D_e**2) / 4
        epsilon = A_e / A_t
        
        # 2. Erozyonlu Yanma (Erosive Burning) Etkisi
        # Port (kor) akış kesit alanı
        A_port = math.pi * (R_i**2)
        # Temel yanma hızı
        r_base = a_si * (Pc ** n)
        
        if Pc > P_a * 1.5:  # Ateşleme sonrası anlamlı akış başladığında
            m_dot_in_approx = rho_p * A_b * r_base
            G = m_dot_in_approx / A_port # Kütle akısı (kg/m^2.s)
            # Erozyon çarpanı eklentisi
            r_dot = r_base * (1 + k_erosive * G)
        else:
            r_dot = r_base

        # 3. Dinamik Basınç Diferansiyel Çözümü (dp/dt)
        V_chamber = N_grains * (math.pi * R_o**2 * L_g) - N_grains * (math.pi * (R_o**2 - R_i**2) * L)
        # Eğer hacim sıfır veya negatifse küçük bir değer ata
        V_chamber = max(V_chamber, 1e-5)
        
        m_dot_in = rho_p * A_b * r_dot
        
        if Pc > P_a:
            # Kritik akış varsayımı ile lüle çıkış kütlesi
            m_dot_out = (Pc * A_t) / c_star
        else:
            m_dot_out = 0.0
            
        # Kütle Dengesi Diferansiyel Denklemi: dp/dt = (R*Tc / Vc) * (m_in - m_out)
        dPc_dt = (R * T_c / V_chamber) * (m_dot_in - m_dot_out)
        
        # Basıncı güncelle
        Pc += dPc_dt * dt
        
        # 4. İtki Hesabı ve Verimlilik (eta_f)
        if Pc > P_a * 1.1: # Choked flow (kritik akış) tam olarak oturduğunda
            M_e = solve_exit_mach(epsilon, gamma)
            Pe = Pc * (1 + (gamma - 1) / 2 * M_e**2) ** (-gamma / (gamma - 1))
            
            term1 = (2 * gamma**2 / (gamma - 1)) * (2 / (gamma + 1)) ** ((gamma + 1) / (gamma - 1))
            term2 = 1 - (Pe / Pc) ** ((gamma - 1) / gamma)
            
            if term2 < 0: term2 = 0
            
            Cf_ideal = math.sqrt(term1 * term2) + (Pe - P_a) / Pc * epsilon
            
            # Gerçek İtki Katsayısı ve İtki (Madde 3)
            F = Pc * A_t * Cf_ideal * eta_f
        else:
            F = 0.0

        # Veri Kaydetme
        if t - last_out_time >= dt_out - 1e-6:
            times.append(t)
            thrusts.append(max(0, F))
            pressures.append(Pc / 1e5)
            throats.append(D_t * 1000) # mm cinsinden kaydet
            last_out_time = t
            
        # İntegral adımları
        r_burn += r_dot * dt
        
        # 5. Nozül Aşınması (Ablation) (Madde 1)
        # Sadece anlamlı basınç ve yanma varken aşınma olur
        if Pc > P_a * 1.5:
            # Çap her iki taraftan aşındığı için 2 katı ile çarpılır
            D_t += 2 * erosion_rate * dt 
            
        t += dt

    if not times:
        print("HATA: Ateşleme başarısız.")
        return

    # Kuyruk (Tail-off) düşüşünü tamamlamak için basınç sönümleme döngüsü (Opsiyonel gerçeğe uygunluk)
    tail_t = 0
    while Pc > P_a * 1.1 and tail_t < 1.0: # Maks 1 saniye tail-off
        V_chamber = N_grains * (math.pi * R_o**2 * L_g) # Yakıt bitti, tüm hacim serbest
        m_dot_out = (Pc * A_t) / c_star
        dPc_dt = (R * T_c / V_chamber) * (0 - m_dot_out) # m_in artık 0
        Pc += dPc_dt * dt
        
        if Pc > P_a * 1.1:
            Pe = Pc * (1 + (gamma - 1) / 2 * M_e**2) ** (-gamma / (gamma - 1))
            Cf_ideal = math.sqrt(term1 * max(0, 1 - (Pe / Pc) ** ((gamma - 1) / gamma))) + (Pe - P_a) / Pc * epsilon
            F = Pc * A_t * Cf_ideal * eta_f
        else:
            F = 0.0
            
        if t - last_out_time >= dt_out - 1e-6:
            times.append(t)
            thrusts.append(max(0, F))
            pressures.append(Pc / 1e5)
            last_out_time = t
            
        t += dt
        tail_t += dt

    total_impulse = sum((thrusts[i] + thrusts[i+1]) / 2 * (times[i+1] - times[i]) for i in range(len(times)-1))
    max_thrust = max(thrusts)
    max_pressure = max(pressures)
    burn_time = times[-1]
    avg_thrust = total_impulse / burn_time
    
    max_Pc_Pa = max_pressure * 1e5
    max_Pe_Pa = max_Pc_Pa * (1 + (gamma - 1) / 2 * M_e**2) ** (-gamma / (gamma - 1))
    max_Pe_bar = max_Pe_Pa / 1e5
    T_e = T_c / (1 + (gamma - 1) / 2 * M_e**2)

    print("="*65)
    print(f" SİMÜLASYON SONUÇLARI:")
    print(f" Yanma Süresi          : {burn_time:.3f} saniye")
    print(f" Maksimum İtki         : {max_thrust:.1f} N")
    print(f" Ortalama İtki         : {avg_thrust:.1f} N")
    print(f" Maks. Oda Basıncı     : {max_pressure:.1f} Bar")
    print(f" Maks. Çıkış Basıncı   : {max_Pe_bar:.2f} Bar")
    print(f" Çıkış Sıcaklığı       : {T_e:.0f} K")
    print(f" Toplam İmpuls         : {total_impulse:.1f} N*s")
    print(f" Final Nozül Boğaz Çapı: {D_t*1000:.2f} mm")
    print("="*65)

    # Grafik Çizdirme (İtki ve Basınç Çift Eksen)
    fig, ax1 = plt.subplots(figsize=(10, 6))

    color1 = '#D32F2F'
    ax1.set_xlabel('Zaman (saniye)', fontweight='bold')
    ax1.set_ylabel('İtki (Newton)', color=color1, fontweight='bold')
    ax1.plot(times, thrusts, color=color1, linewidth=2.5, label='İtki Eğrisi')
    ax1.fill_between(times, thrusts, color=color1, alpha=0.2)
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.set_xlim(0, burn_time * 1.05)
    ax1.set_ylim(0, max_thrust * 1.1)
    ax1.grid(True, linestyle='--', alpha=0.5)

    ax2 = ax1.twinx()  
    color2 = '#1976D2'
    ax2.set_ylabel('Oda Basıncı (Bar)', color=color2, fontweight='bold')  
    ax2.plot(times, pressures, color=color2, linewidth=2, linestyle='-.', label='Basınç Eğrisi')
    ax2.tick_params(axis='y', labelcolor=color2)
    ax2.set_ylim(0, max_pressure * 1.1)

    plt.title('Dinamik Roket Motoru İtki ve Basınç Eğrisi', fontsize=14, fontweight='bold')
    
    info_text = (f"Süre: {burn_time:.2f} s\n"
                 f"Max İtki: {max_thrust:.0f} N\n"
                 f"T. İmpuls: {total_impulse:.0f} Ns\n"
                 f"Max Basınç: {max_pressure:.1f} Bar\n"
                 f"Lüle Aşınması: {(D_t*1000 - D_t_init_mm):.2f} mm")
                 
    ax1.text(burn_time*0.75, max_thrust*0.75, info_text, 
             bbox=dict(facecolor='white', alpha=0.9, edgecolor='#BDBDBD', boxstyle='round,pad=0.5'),
             fontsize=10, family='monospace')

    fig.tight_layout()  
    plt.show()

if __name__ == "__main__":
    run_simulation()