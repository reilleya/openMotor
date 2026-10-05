import math
import matplotlib.pyplot as plt
from scipy.optimize import fsolve

def get_float(prompt, default):
    try:
        val = input(f"{prompt} [Varsayılan: {default}]: ")
        if val.strip() == "":
            return default
        return float(val)
    except (ValueError, EOFError):
        print("Geçersiz giriş veya EOF, varsayılan değer kullanılıyor.")
        return default

def get_int(prompt, default):
    try:
        val = input(f"{prompt} [Varsayılan: {default}]: ")
        if val.strip() == "":
            return default
        return int(val)
    except (ValueError, EOFError):
        print("Geçersiz giriş veya EOF, varsayılan değer kullanılıyor.")
        return default

def eRatioFromPRatio(k, pRatio):
    """Returns the expansion ratio of a nozzle given the pressure ratio it causes."""
    return (((k+1)/2)**(1/(k-1))) * (pRatio ** (1/k)) * ((((k+1)/(k-1))*(1-(pRatio**((k-1)/k))))**0.5)

def getExitPressure(k, inputPressure, expansionRatio):
    """Solves for the nozzle's exit pressure, given an input pressure and the gas's specific heat ratio."""
    if inputPressure == 0:
        return 0
    return fsolve(lambda x: (1/expansionRatio) - eRatioFromPRatio(k, x / inputPressure), 0)[0]

def getDivergenceLosses(divAngleDeg):
    """Returns nozzle efficiency losses due to divergence angle"""
    divAngleRad = math.radians(divAngleDeg)
    return (1 + math.cos(divAngleRad)) / 2

def getThroatLosses(throatLength, throatDiameter):
    """Returns the losses caused by the throat aspect ratio"""
    if throatDiameter <= 0:
        return 0.99
    throatAspect = throatLength / throatDiameter
    if throatAspect > 0.45:
        return 0.95
    return 0.99 - (0.0333 * throatAspect)

def getSkinLosses():
    """Returns the losses due to drag on the nozzle surface"""
    return 0.99

def getIdealThrustCoeff(chamberPres, ambPres, gamma, throatArea, exitArea, exitPres=None):
    """Calculates C_f, the ideal thrust coefficient for the nozzle."""
    if chamberPres == 0:
        return 0

    if exitPres is None:
        expansionRatio = exitArea / throatArea
        exitPres = getExitPressure(gamma, chamberPres, expansionRatio)
        
    term1 = (2 * (gamma ** 2)) / (gamma - 1)
    term2 = (2 / (gamma + 1)) ** ((gamma + 1) / (gamma - 1))

    term3 = 1 - ((exitPres / chamberPres) ** ((gamma - 1) / gamma))
    if term3 < 0: term3 = 0

    momentumThrust = (term1 * term2 * term3) ** 0.5
    pressureThrust = ((exitPres - ambPres) * exitArea) / (throatArea * chamberPres)

    return momentumThrust + pressureThrust

def getAdjustedThrustCoeff(chamberPres, ambPres, gamma, throatArea, exitArea, divAngleDeg, throatLength, throatDiameter, efficiency, exitPres=None):
    """Calculates adjusted thrust coefficient for the nozzle."""
    thrustCoeffIdeal = getIdealThrustCoeff(chamberPres, ambPres, gamma, throatArea, exitArea, exitPres)
    divLoss = getDivergenceLosses(divAngleDeg)
    throatLoss = getThroatLosses(throatLength, throatDiameter)
    skinLoss = getSkinLosses()
    return divLoss * throatLoss * efficiency * (skinLoss * thrustCoeffIdeal + (1 - skinLoss))

def getPressureFromKn(kn, density, a, n, gamma, temp, molarMass):
    """Returns the steady-state pressure of the motor at a given Kn."""
    if kn <= 0:
        return 0
    num = kn * density * a
    exponent = 1 / (1 - n)
    gasConstant = 8314.462618
    denom = ((gamma / ((gasConstant / molarMass) * temp)) * ((2 / (gamma + 1)) ** ((gamma + 1) / (gamma - 1)))) ** 0.5
    return (num / denom) ** exponent

def run_simulation():
    print("="*65)
    print(" ROKET MOTORU İTKİ SİMÜLASYONU (openMotor Uyumlu Steady-State)")
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
    divAngleDeg = get_float("Divergence Half Angle (derece)", 15.0)
    throatLength_mm = get_float("Throat Length (mm)", 0.0)
    slagCoeff = get_float("Nozül Cüruf (Slag) Katsayısı ((m*Pa)/s)", 0.0)
    erosionCoeff = get_float("Nozül Aşınma Katsayısı (m/(s*Pa))", 0.0)
    eta_f = get_float("İtki Verimlilik Katsayısı (eta_f)", 0.95)

    print("\n--- Yakıt Kimyasal Özellikleri ---")
    a_lit = get_float("Yanma Hızı Katsayısı, a (mm/s / MPa^n)", 4.0) 
    n = get_float("Yanma Hızı Üssü, n", 0.35)
    rho_p = get_float("Yakıt Yoğunluğu (kg/m^3)", 1700.0)
    gamma = get_float("Özgül Isı Oranı (Gamma)", 1.20)
    T_c = get_float("Yanma Odası Sıcaklığı (K)", 3300.0)
    M_w = get_float("Gaz Molekül Ağırlığı (g/mol) [kg/kmol]", 27.5) # openMotor uses g/mol but we divide by 1000? No openMotor property defaults say g/mol but constant is J/(kmol*K). In propellant denom it divides gasConstant/molarMass.

    # openMotor's Molar mass is usually entered in g/mol and propellant.py doesn't convert it?! Let's check openMotor.
    # Ah, in propellant.py: tab['m'] is 'Exhaust Molar Mass', 'g/mol'.
    # denom = ((gamma / ((gasConstant / molarMass) * temp)) * ((2 / (gamma + 1)) ** ((gamma + 1) / (gamma - 1)))) ** 0.5
    # Wait, if molarMass is in g/mol and we use 8314.46 (J/(kmol*K)), then it matches because kmol = 1000 mol, and kg = 1000 g.
    # J/(kmol*K) / (kg/kmol) = J/(kg*K).
    # Since 1 kg/kmol = 1 g/mol, the numerical value is the same.
    
    print("\n--- Ortam Şartları ---")
    P_a = get_float("Ortam Basıncı (Pa)", 101325.0)

    # Simülasyon ayarları
    dt = get_float("Simülasyon Zaman Adımı (s)", 0.01)

    # Birim Dönüşümleri (mm -> m)
    D_o = D_o_mm / 1000.0
    D_i = D_i_mm / 1000.0
    L_g = L_g_mm / 1000.0
    D_t = D_t_init_mm / 1000.0
    D_e = D_e_mm / 1000.0
    throatLength = throatLength_mm / 1000.0
    
    # 'a' Katsayısını SI Birimine Çevirme (m/s / Pa^n)
    # lit -> m/s is /1000. MPa^n -> Pa^n is *(1e-6)**n
    a_si = (a_lit / 1000.0) * (1e-6)**n

    t = 0.0
    r_burn = 0.0 
    
    # Veri Listeleri
    times, thrusts, pressures, throats = [], [], [], []

    print("\nSimülasyon hesaplanıyor (Steady-State Çözüm)...")

    # Initial values at t=0
    # openMotor calculates initial Kn and P, but thrust starts at 0 or is calculated.
    # We will loop as long as there is web to burn (web = (D_o - D_i) / 2)
    burnoutWebThres = 2.54e-5 # openMotor default 2.54e-5 m (1 mil)

    while True:
        # Anlık Yakıt Geometrisi
        R_i = D_i / 2 + r_burn
        L = L_g - 2 * r_burn
        R_o = D_o / 2

        web_left = R_o - R_i

        # Sona erdiğinde çık
        if web_left <= burnoutWebThres or L <= 0:
            break
            
        # Alan Hesaplamaları
        A_core = 2 * math.pi * R_i * L
        A_end = 2 * math.pi * (R_o**2 - R_i**2)
        A_b = N_grains * (A_core + A_end)
        
        A_t = math.pi * (D_t**2) / 4
        A_e = math.pi * (D_e**2) / 4
        
        Kn = A_b / A_t
        
        # Basınç Hesabı
        Pc = getPressureFromKn(Kn, rho_p, a_si, n, gamma, T_c, M_w)
        
        if Pc <= 0:
            Pc = 0
            F = 0
        else:
            # Çıkış basıncı
            expansionRatio = A_e / A_t
            Pe = getExitPressure(gamma, Pc, expansionRatio)
            
            # İtki
            Cf_adj = getAdjustedThrustCoeff(Pc, P_a, gamma, A_t, A_e, divAngleDeg, throatLength, D_t, eta_f, Pe)
            F = Cf_adj * A_t * Pc
            F = max(0, F)

        # Veri Kaydetme
        times.append(t)
        thrusts.append(F)
        pressures.append(Pc / 1e5)
        throats.append(D_t * 1000)
            
        # İntegral adımları
        r_dot = a_si * (Pc ** n)
        r_burn += r_dot * dt
        
        # Nozül Aşınması
        if Pc > 0:
            slagRate = (1 / Pc) * slagCoeff
        else:
            slagRate = 0

        erosionRate = Pc * erosionCoeff
        change = dt * ((-2 * slagRate) + (2 * erosionRate))
        D_t += change
            
        t += dt

    if not times:
        print("HATA: Ateşleme başarısız veya geometri hatalı.")
        return

    total_impulse = sum((thrusts[i] + thrusts[i+1]) / 2 * (times[i+1] - times[i]) for i in range(len(times)-1))
    max_thrust = max(thrusts)
    max_pressure = max(pressures)
    burn_time = times[-1]

    if burn_time > 0:
        avg_thrust = total_impulse / burn_time
    else:
        avg_thrust = 0
    
    max_Pc_Pa = max_pressure * 1e5
    # Max çıkış basıncı yaklaşık hesap (en yüksek basınç anı için)
    # Tam Pe değerini listede tutmadık, sadece max için tekrar hesaplayalım:
    D_t_final = D_t
    A_t_final = math.pi * (D_t_final**2) / 4
    A_e = math.pi * (D_e**2) / 4
    if max_Pc_Pa > 0:
        max_Pe_Pa = getExitPressure(gamma, max_Pc_Pa, A_e / A_t_final)
    else:
        max_Pe_Pa = 0
    max_Pe_bar = max_Pe_Pa / 1e5

    print("="*65)
    print(f" SİMÜLASYON SONUÇLARI:")
    print(f" Yanma Süresi          : {burn_time:.3f} saniye")
    print(f" Maksimum İtki         : {max_thrust:.1f} N")
    print(f" Ortalama İtki         : {avg_thrust:.1f} N")
    print(f" Maks. Oda Basıncı     : {max_pressure:.1f} Bar")
    print(f" Maks. Çıkış Basıncı   : {max_Pe_bar:.2f} Bar")
    print(f" Toplam İmpuls         : {total_impulse:.1f} N*s")
    print(f" Final Nozül Boğaz Çapı: {D_t_final*1000:.2f} mm")
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

    plt.title('Roket Motoru İtki ve Basınç Eğrisi', fontsize=14, fontweight='bold')
    
    info_text = (f"Süre: {burn_time:.2f} s\n"
                 f"Max İtki: {max_thrust:.0f} N\n"
                 f"T. İmpuls: {total_impulse:.0f} Ns\n"
                 f"Max Basınç: {max_pressure:.1f} Bar")
                 
    ax1.text(burn_time*0.75, max_thrust*0.75, info_text, 
             bbox=dict(facecolor='white', alpha=0.9, edgecolor='#BDBDBD', boxstyle='round,pad=0.5'),
             fontsize=10, family='monospace')

    fig.tight_layout()  
    plt.show()

    try:
        input("\nÇıkmak için ENTER tuşuna basın...")
    except EOFError:
        pass

if __name__ == "__main__":
    try:
        run_simulation()
    except Exception as e:
        print(f"\nBeklenmeyen bir hata oluştu: {e}")
        try:
            input("\nÇıkmak için ENTER tuşuna basın...")
        except EOFError:
            pass
