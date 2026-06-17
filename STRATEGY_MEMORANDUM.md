# Kantitatif Strateji Memorandumu

**Goldman Sachs Tarzı QIS (Quantitative Investment Strategies) Belgesi**

| | |
|---|---|
| **Strateji Adı** | TSMR-CX: Trend + Kısa Vadeli Ortalamaya Dönüş, Volatilite-Hedefli, Konveksite Overlay |
| **Varlık Sınıfları** | ABD Hisse Senedi, ETF, Listelenmiş Opsiyonlar |
| **Tasarım Sermayesi** | 1.000 USD (mikro-hesap kalibrasyonu) |
| **Yatırım Ufku** | ≥ 12 ay (yenilenebilir) |
| **Sınıflandırma** | Dahili — Yalnızca Eğitim/Araştırma |
| **Versiyon / Tarih** | v1.0 — 2026-06-17 |

> **YASAL UYARI:** Bu belge eğitim ve araştırma amaçlıdır; yatırım tavsiyesi değildir. Geçmiş performans gelecekteki sonuçların garantisi değildir. Kaldıraç ve opsiyonlar tüm sermayenin kaybına yol açabilir. Sermaye tahsisinden önce bağımsız profesyonel danışmanlık alın.

---

## 0. Yönetici Özeti (Executive Summary)

Bu memorandum, ABD likit hisse/ETF evreninde **iki ortogonal getiri kaynağını** (kesitsel trend ve kısa-vadeli ortalamaya dönüş) bir **volatilite-hedefli pozisyon boyutlandırma** çerçevesinde birleştiren, üzerine **tanımlı-riskli opsiyon konveksite katmanı** ekleyen sistematik bir stratejidir.

**Gerçekçi beklenti çerçevesi (taban senaryo):** Sharpe ≈ 0.8–1.3, yıllık getiri (CAGR) ≈ %12–%30, maksimum düşüş (MaxDD) hedefi ≤ %20.

**100x hedefi hakkında matematiksel hüküm (bkz. §11):** Hedef 1.000$ → 100.000$ (100x), ufuk ise *çok yıllı* (1 yıl beklentisi yok). Bu, problemi bir "lotere"den disiplinli bir **bileşik büyüme + düzenli katkı** problemine dönüştürür. Saf getiriyle 100x bile çok yılda zordur (10 yıl ≈ %58/yıl, 20 yıl ≈ %26/yıl); ancak **düzenli katkı (DCA)** eklendiğinde 100.000$ varlık hedefi gerçekçi ve matematiksel olarak savunulabilir hale gelir. Bu memo, çekirdek stratejinin sürdürülebilir bileşik büyümesini, küçük bir **konveksite dilimiyle (barbell)** birleştirir; "garantili/hızlı 100x" sunmaz çünkü matematik aceleyi cezalandırır, sabrı ödüllendirir.

---

## 1. Strateji Tezi (Strategy Thesis)

Strateji, akademik literatürde tekrar tekrar belgelenmiş ve farklı ekonomik mekanizmalardan beslenen **üç ayrı piyasa verimsizliğini** harmanlar:

### 1.1 Kesitsel Momentum (Trend) — Jegadeesh & Titman (1993), Asness et al. (2013)
**Verimsizlik:** Yatırımcıların bilgiye gecikmeli/eksik tepkisi (under-reaction) ve sürü davranışı, fiyat trendlerinin orta vadede (1–12 ay) devam etmesine yol açar.
**Ekonomik mantık:** Davranışsal yanlılıklar (disposition effect, herding) + risk primi rotasyonu. Edge kaynağı **kalıcı** çünkü davranışsal kökü var.

### 1.2 Kısa-Vadeli Ortalamaya Dönüş — Lehmann (1990), Lo & MacKinlay (1990)
**Verimsizlik:** Likidite sağlama primi. Kısa vadede (1–5 gün) aşırı satılan likit hisseler, likidite talebi normalleştikçe geri toparlar.
**Ekonomik mantık:** Piyasa yapıcı envanter riski primi. Momentum ile **negatif korelasyonlu** olduğundan portföy çeşitlendirme sağlar.

### 1.3 Volatilite Risk Primi (VRP) — Bakshi & Kapadia (2003), Carr & Wu (2009)
**Verimsizlik:** Opsiyon alıcıları sigorta için sürekli prim öder; implied volatilite gerçekleşen volatiliteyi ortalamada (~%3–4 puan) aşar.
**Ekonomik mantık:** Kuyruk-riskinden kaçınma. Tanımlı-riskli opsiyon satışıyla hasat edilir.

**Tezin özü:** Bu üç kaynak **düşük korelasyonludur**; birleştirildiğinde portföy Sharpe'ı tek bir kaynağı domine eder (çeşitlendirmenin matematiği: $SR_{port} = \frac{\sum w_i \mu_i}{\sqrt{w^T \Sigma w}}$, düşük $\rho$ paydayı küçültür).

---

## 2. Evren Seçimi (Universe Selection)

### 2.1 İşlem Evreni

| Katman | Enstrümanlar | Gerekçe |
|---|---|---|
| **Çekirdek ETF (likit)** | SPY, QQQ, IWM, DIA + 9 SPDR sektör ETF'i (XLK, XLF, XLE, XLV, XLI, XLY, XLP, XLU, XLB) | Dar spread, fraksiyonel alım, yüksek likidite; 1.000$ hesap için sektör rotasyonu mümkün |
| **Hisse senedi alt-evreni** | S&P 500 üyesi, ADV > 5M$, fiyat > 10$, opsiyonu listelenmiş | Likidite + işlem maliyeti kontrolü; survivorship-bias'tan kaçınmak için tarihsel üyelik kullanılır |
| **Opsiyon overlay** | Yukarıdaki ETF/hisselerin haftalık & aylık opsiyonları, bid-ask < %10, OI > 500 | Tanımlı-risk yapıları (vertical, iron condor) için yeterli derinlik |

### 2.2 Likidite & İşlenebilirlik Filtreleri
- **Ortalama Günlük Dolar Hacmi (ADV):** ≥ 5.000.000 $
- **Spread:** Bid-ask ≤ 5 bps (ETF), ≤ 20 bps (hisse)
- **Pozisyon başına hacim payı:** İşlem ≤ ADV'nin %1'i (1.000$ hesapta bu kısıt asla bağlamaz — kapasite bol)

### 2.3 Neden Bu Karışım?
- **ETF'ler:** 1.000$'lık hesabın çeşitlendirilmesini fraksiyonel hisselerle mümkün kılar; tek-isim risksiz beta erişimi.
- **Hisseler:** Kesitsel sinyallerin (momentum/reversal) en güçlü olduğu yer; opsiyon erişimi konveksite için.
- **Opsiyonlar:** Sınırlı sermayede **tanımlı riskle** asimetrik getiri ve VRP hasadı; çekirdeği riske atmadan kuyruk maruziyeti.
- **Vadeli işlemler dışarıda:** Tek mini/mikro vadeli kontratın nominal değeri (örn. MES ≈ 25k$ nominal) 1.000$ hesap için aşırı kaldıraç ve gap-riski yaratır; risk yönetimi granülaritesi yetersiz. Bu yüzden **kapsam dışı** bırakıldı.

---

## 3. Sinyal Üretim Mantığı (Signal Generation)

Tüm sinyaller **kesitsel z-skor** olarak standardize edilir, böylece farklı kaynaklar karşılaştırılabilir/birleştirilebilir.

### 3.1 Momentum Sinyali ($S_{mom}$)

12-1 ayı (son ayı atlayarak — kısa-vadeli reversal kirliliğini önlemek için) momentum:

$$
R_i^{12-1} = \frac{P_{i,t-21}}{P_{i,t-252}} - 1
$$

Volatiliteye göre düzeltilmiş (riske-ayarlı momentum):

$$
M_i = \frac{R_i^{12-1}}{\sigma_i^{63}}, \qquad \sigma_i^{63} = \text{son 63 günlük getiri std. sapması (yıllıklaştırılmış)}
$$

Kesitsel z-skor:

$$
S_{mom,i} = \frac{M_i - \mu_{cs}(M)}{\sigma_{cs}(M)}
$$

burada $\mu_{cs}, \sigma_{cs}$ evren genelinde (cross-section) hesaplanır.

### 3.2 Kısa-Vadeli Ortalamaya Dönüş Sinyali ($S_{rev}$)

5 günlük getirinin **tersi** (aşırı satılanı al, aşırı alınanı sat), beta-nötrlenmiş:

$$
r_i^{5} = \frac{P_{i,t}}{P_{i,t-5}} - 1, \qquad \tilde{r}_i^{5} = r_i^{5} - \beta_i \cdot r_{mkt}^{5}
$$

$$
S_{rev,i} = -\,\frac{\tilde{r}_i^{5} - \mu_{cs}(\tilde{r}^5)}{\sigma_{cs}(\tilde{r}^5)}
$$

Onay filtresi (whipsaw azaltıcı) — RSI(2) ekstremleri:

$$
\text{RSI}_2(i) < 10 \Rightarrow \text{long teyit}, \qquad \text{RSI}_2(i) > 90 \Rightarrow \text{short teyit}
$$

### 3.3 Birleşik Alfa Skoru

Rejim-koşullu ağırlıklarla birleştirilir. Rejim, SPY'ın 200-günlük SMA'sına göre tanımlanır:

$$
S_i =
\begin{cases}
0.70\, S_{mom,i} + 0.30\, S_{rev,i}, & \text{Risk-On } (P_{SPY} > SMA_{200}) \\[4pt]
0.30\, S_{mom,i} + 0.70\, S_{rev,i}, & \text{Risk-Off } (P_{SPY} \le SMA_{200})
\end{cases}
$$

**Mantık:** Trend ortamında momentum baskın; stresli/yatay ortamda ortalamaya dönüş baskın (momentum çökerken reversal güçlenir — negatif korelasyonun pratik kullanımı).

### 3.4 VRP / Opsiyon Sinyali

IV Rank (son 1 yıl içinde implied volatilitenin yüzdelik konumu):

$$
\text{IVR} = \frac{IV_t - \min(IV_{1y})}{\max(IV_{1y}) - \min(IV_{1y})}
$$

- $\text{IVR} > 0.50$ **ve** trend nötr → **prim sat** (tanımlı-risk: iron condor / kredi vertical)
- $\text{IVR} < 0.20$ **ve** güçlü yönlü sinyal → **prim al** (debit vertical — konveksite dilimi)

### 3.5 Pseudocode — Sinyal Motoru

```python
def generate_signals(universe, date):
    # 1. Özellikleri hesapla
    mom  = riskadj_momentum(universe, lookback=252, skip=21, vol_win=63)
    rev  = beta_neutral_reversal(universe, win=5, market="SPY")
    rsi2 = wilder_rsi(universe, period=2)

    # 2. Kesitsel z-skorlama (winsorize ±3σ ile aykırı kontrol)
    z_mom = cross_sectional_z(winsorize(mom, 3))
    z_rev = cross_sectional_z(winsorize(rev, 3))

    # 3. Rejim tespiti
    regime = "ON" if price("SPY", date) > sma("SPY", 200, date) else "OFF"
    w_mom, w_rev = (0.70, 0.30) if regime == "ON" else (0.30, 0.70)

    # 4. Birleşik alfa
    alpha = w_mom * z_mom + w_rev * z_rev

    # 5. RSI teyidi (reversal bacağı için)
    alpha = apply_rsi_confirmation(alpha, rsi2, lo=10, hi=90)

    # 6. Opsiyon overlay sinyali
    ivr = iv_rank(universe, window=252)
    opt_signal = option_overlay_logic(ivr, alpha)  # sat/al/yok

    return alpha, opt_signal, regime
```

---

## 4. Giriş Kuralları (Entry Rules)

Bir pozisyon açılmadan önce **tüm** koşullar (AND mantığı) sağlanmalıdır:

### 4.1 Hisse / ETF Yönlü Giriş

| # | Koşul | Eşik |
|---|---|---|
| E1 | Birleşik alfa skoru | \|S_i\| ≥ 1.0 (kesitsel z) — long için ≥ +1.0, short için ≤ −1.0 |
| E2 | Likidite | ADV ≥ 5M$, spread ≤ filtre |
| E3 | Portföy korelasyon kontrolü | Yeni pozisyon, mevcut kitap ile \|ρ\| ≤ 0.70 (60g pencere) |
| E4 | Risk bütçesi müsait | Yeni pozisyon sonrası portföy vol ≤ hedef vol (bkz §6) |
| E5 | Kazanç (earnings) takvimi | Yönlü hisse girişinde, 3 işlem günü içinde earnings YOKSA (gap riski filtresi) |
| E6 | Rejim kapısı | Risk-Off'ta brüt kaldıraç ≤ 1.0x'e indirilir |

### 4.2 Opsiyon Girişi (Tanımlı-Risk)

| # | Koşul | Eşik |
|---|---|---|
| O1 | IV Rank teyidi | Satış için IVR > 0.50; alış için IVR < 0.20 |
| O2 | Likidite | Bid-ask ≤ %10, OI ≥ 500, vega/gamma makul |
| O3 | Maks. tanımlı kayıp | Tek yapının maks. kaybı ≤ hesabın %1'i |
| O4 | Vade (DTE) | Satış: 30–45 DTE (theta optimal); Alış: ≥ 60 DTE (theta erozyonu yavaş) |
| O5 | Delta | Satış bacakları ~16 delta (≈1σ OTM); yönlü alış 30–40 delta |

### 4.3 İcra (Execution)
- **Emir tipi:** Limit (mid-price ± spread/4). Asla piyasa emri (slippage kontrolü).
- **Zamanlama:** Açılıştan ≥ 30 dk ve kapanıştan ≥ 30 dk uzak (auction gürültüsünden kaçın).
- **Kademeli giriş:** Yüksek inanç pozisyonlarında bile tek seferde tam boyut değil; 2 dilimde.

---

## 5. Çıkış Kuralları (Exit Rules)

Dört bağımsız çıkış mekanizması; **ilk tetiklenen** kazanır.

### 5.1 Kâr Hedefi (Profit Target)
- **Yönlü (hisse/ETF):** Volatilite-ölçekli hedef. Giriş ATR'sinin (14g) **+2.5×** kadarı.
  $$ PT = P_{entry} + 2.5 \cdot ATR_{14} \quad (\text{long}) $$
- **Opsiyon satışı:** Alınan primin **%50'si** yakalandığında kapat (Tastytrade'in istatistiksel olarak optimal kuralı — kalan theta'nın marjinal getirisi gamma riskini karşılamaz).

### 5.2 Stop-Loss
- **Yönlü:** Giriş ATR'sinin **−1.5×** kadarı (asimetrik: 2.5R kazanç / 1.5R kayıp → ~1.67 ödül/risk).
  $$ SL = P_{entry} - 1.5 \cdot ATR_{14} \quad (\text{long}) $$
- **Opsiyon satışı:** Kayıp, alınan primin **2×'ine** ulaşınca kapat (tanımlı-risk yapısında zaten maks. kayıp sınırlı).
- **Portföy-seviye devre kesici:** Günlük portföy kaybı > %4 → tüm yeni girişler durur, kitap %50 küçültülür (bkz §7).

### 5.3 Zaman-Bazlı Çıkış
- **Reversal pozisyonları:** Maks. 5 işlem günü (sinyalin yarı-ömrü ~3 gün; sonrası gürültü).
- **Momentum pozisyonları:** Aylık yeniden dengeleme (rebalance) günü gözden geçirilir.
- **Opsiyon satışı:** 21 DTE'de kapat/yenile (gamma riski hızla artar — "21 DTE kuralı").

### 5.4 Sinyal Tersine Dönme (Signal Reversal Exit)
- Birleşik alfa skoru işaret değiştirir **veya** \|S_i\| < 0.25'e düşerse (sinyal kayboldu) → pozisyon kapat.
- Rejim değişiminde (SPY 200-SMA kesişimi) ters yöndeki pozisyonlar öncelikli kapatılır.

### 5.5 Pseudocode — Çıkış Motoru
```python
def check_exits(position, market_data):
    pt, sl = vol_scaled_targets(position, atr=position.entry_atr)
    if position.is_option:
        if position.pnl >= 0.50 * position.credit: return "PROFIT_50PCT"
        if position.pnl <= -2.0 * position.credit: return "STOP_2X"
        if position.dte <= 21: return "TIME_21DTE"
    else:
        if market_data.price >= pt: return "PROFIT_TARGET"
        if market_data.price <= sl: return "STOP_LOSS"
        if position.holding_days >= max_hold(position.type): return "TIME_EXIT"
    if sign(position.current_alpha) != sign(position.entry_alpha): return "SIGNAL_FLIP"
    if abs(position.current_alpha) < 0.25: return "SIGNAL_DECAY"
    return None
```

---

## 6. Pozisyon Boyutlandırma Modeli (Position Sizing)

Üç katmanlı: **(a) volatilite hedefleme** → portföy düzeyi, **(b) fraksiyonel Kelly** → inanç ölçeklemesi, **(c) risk-parite** → pozisyonlar arası.

### 6.1 Volatilite Hedefleme (Portföy Düzeyi)
Hedef yıllık portföy volatilitesi $\sigma_{target} = 15\%$ (taban). Brüt kaldıraç:

$$
L_t = \frac{\sigma_{target}}{\sigma_{realized,t}}, \qquad \sigma_{realized,t} = \text{EWMA vol (} \lambda = 0.94 \text{)}
$$

Tavan: $L_t \le 1.5$ (1.000$ hesap için; marj ve gap riski kontrolü).

### 6.2 Fraksiyonel Kelly (İnanç Ölçekleme)
Tam Kelly kesri (tek varlık yaklaşımı):

$$
f^* = \frac{\mu - r_f}{\sigma^2}
$$

burada $\mu$ pozisyonun beklenen fazla getirisi (alfa skorundan kalibre), $\sigma^2$ varyansı. **Pratikte tam Kelly KULLANILMAZ** — parametre belirsizliği ve şişman kuyruklar nedeniyle iflas riski yüksektir. **Çeyrek Kelly** uygulanır:

$$
f_{used} = 0.25 \cdot f^*
$$

**Neden çeyrek Kelly?** Tam Kelly büyüme oranını maksimize eder ama %50 düşüş olasılığı ~%50'dir. Çeyrek Kelly, büyüme oranının ~%94'ünü korur ama volatiliteyi %75 azaltır — çok daha iyi risk-ayarlı sonuç (bkz. MacLean, Thorp & Ziemba).

### 6.3 Pozisyon Ağırlığı
İnanç (alfa z-skoru) ile ölçeklenen, risk-parite normalizasyonlu ağırlık:

$$
w_i = L_t \cdot f_{used} \cdot \underbrace{\frac{S_i}{\sum_j |S_j|}}_{\text{inanç payı}} \cdot \underbrace{\frac{1/\sigma_i}{\sum_j 1/\sigma_j}}_{\text{risk-parite}}
$$

Dolar tahsisi: $\$_i = w_i \cdot \text{NAV}$.

### 6.4 1.000$ Hesap İçin Pratik Granülarite
- Fraksiyonel hisse desteği ile min. pozisyon ~25$ (NAV'ın %2.5'i) → ~8–12 eşzamanlı yönlü pozisyon mümkün.
- Opsiyon: 1 kontrat = 100 hisse maruziyeti; tek tanımlı-risk yapısının maks. kaybı ≤ 10$ (%1) olacak şekilde dar spread'ler seçilir.
- **Komisyon eşiği:** Pozisyon başına gidiş-dönüş maliyeti < beklenen kârın %10'u olmalı (aksi halde işlem alınmaz).

### 6.5 Pseudocode
```python
def position_size(nav, alpha_scores, vols, realized_port_vol):
    L = min(0.15 / realized_port_vol, 1.5)         # vol-targeting + tavan
    kelly = 0.25                                    # çeyrek Kelly
    conviction = alpha_scores / sum(abs(alpha_scores))
    risk_parity = (1/vols) / sum(1/vols)
    weights = L * kelly * conviction * risk_parity
    weights = cap_weights(weights, max_single=0.20) # tek pozisyon ≤ %20
    dollars = weights * nav
    return drop_below_commission_threshold(dollars)
```

---

## 7. Risk Parametreleri (Risk Parameters)

### 7.1 Ana Risk Limitleri Tablosu

| Parametre | Limit | Tetiklenince Aksiyon |
|---|---|---|
| **Hedef yıllık volatilite** | %15 (taban), %25 (agresif mod tavan) | Kaldıraç yeniden ölçeklenir |
| **Maksimum düşüş (MaxDD) — yumuşak** | %15 | Risk bütçesi %50 kısılır |
| **Maksimum düşüş — sert (kill-switch)** | %25 | Tüm pozisyonlar kapatılır, 5 gün ara, strateji denetimi |
| **Günlük VaR (%99, 1g)** | NAV'ın %3'ü | Yeni giriş durur |
| **Tek pozisyon limiti** | NAV'ın %20'si (yönlü), %1 maks-kayıp (opsiyon) | Boyut kısılır |
| **Brüt kaldıraç** | ≤ 1.5x | Pozisyonlar ölçeklenir |
| **Net kaldıraç (yönlü beta)** | −0.5x … +1.5x | Hedge eklenir |
| **Sektör maruziyeti tavanı** | Tek sektör ≤ NAV'ın %30'u | Yeni sektör girişi bloke |
| **Çift korelasyon limiti** | Herhangi iki pozisyon \|ρ\| ≤ 0.70 (60g) | Daha düşük inançlı olan reddedilir |
| **Ortalama portföy korelasyonu** | Ortalama pairwise ρ ≤ 0.40 | Çeşitlendirme zorlanır |
| **Konveksite dilimi tavanı** | NAV'ın ≤ %10'u (bkz §11) | Aşılırsa yeni konveks bahis yok |
| **Günlük zarar devre kesici** | −%4/gün | Kitap %50 küçültülür, yeni giriş durur |

### 7.2 Düşüş Yönetimi — Kademeli De-risking
$$
\text{Risk ölçeği } k(DD) =
\begin{cases}
1.00, & DD < 8\% \\
0.50, & 8\% \le DD < 15\% \\
0.25, & 15\% \le DD < 25\% \\
0.00 \ (\text{kill-switch}), & DD \ge 25\%
\end{cases}
$$
Etkin pozisyon boyutu = nominal boyut × $k(DD)$.

### 7.3 VaR ve Beklenen Açık (Expected Shortfall)
Parametrik %99 günlük VaR ve tarihsel ES (CVaR) günlük izlenir:
$$
VaR_{99} = z_{0.99} \cdot \sigma_{port} \cdot NAV, \qquad ES_{99} = \mathbb{E}[L \mid L > VaR_{99}]
$$
ES, kuyruk riskinin gerçek ölçüsüdür (fat-tail'lerde VaR yanıltıcıdır).

### 7.4 Korelasyon İzleme
Pozisyonlar arası kovaryans matrisi $\Sigma$ günlük güncellenir (Ledoit-Wolf shrinkage ile, küçük örnek gürültüsünü azaltmak için). Portföy vol: $\sigma_{port} = \sqrt{w^T \Sigma w}$.

---

## 8. Geri Test Çerçevesi (Backtesting Framework)

> **İlke:** Geri test, edge'in var olduğunu *kanıtlamaz*; edge'i *çürütmeye* çalışır. Hedef, kendini kandırmamaktır.

### 8.1 Veri ve Bias Kontrolü
| Bias | Önlem |
|---|---|
| **Survivorship bias** | Delistelenmiş şirketler dahil tarihsel evren (point-in-time S&P üyeliği) |
| **Look-ahead bias** | Tüm sinyaller yalnızca $t$ anında bilinen veriyle; $t+1$ açılışında icra |
| **Restatement bias** | Point-in-time fundamental veri (raporlandığı an, düzeltilmiş değil) |
| **Sağkalım/seçim** | Evren kuralları tarihsel uygulanır, bugünkü bilgiyle değil |

### 8.2 İşlem Maliyeti Modeli
$$
\text{Cost} = \underbrace{\text{komisyon}}_{\text{sabit}} + \underbrace{\tfrac{1}{2}\,\text{spread}}_{\text{yarı-spread}} + \underbrace{\eta \cdot \sigma \cdot \sqrt{\tfrac{Q}{ADV}}}_{\text{market impact (Almgren)}}
$$
Konservatif kalibrasyon: gerçek maliyetin **1.5×'i** ile test (güvenlik marjı).

### 8.3 Doğrulama Metodolojisi
- **Walk-forward analizi:** Yuvarlanan pencere — 3 yıl in-sample optimize, 1 yıl out-of-sample test, kaydır, tekrarla.
- **Purged & Embargoed K-Fold CV** (López de Prado): Sızıntıyı önlemek için fold'lar arası gözlemler temizlenir + embargo periyodu. Zaman serisinde standart k-fold YANLIŞTIR.
- **Combinatorial Purged CV:** Birden çok test yolu → tek bir tarihsel yola aşırı uyumdan kaçınma.

### 8.4 Çoklu Test Düzeltmesi (Kritik)
Birçok parametre denenince Sharpe şişer. **Deflated Sharpe Ratio (DSR)** uygulanır:
$$
DSR = \Phi\!\left( \frac{(SR - SR_0)\sqrt{T-1}}{\sqrt{1 - \gamma_3 SR + \frac{\gamma_4 - 1}{4} SR^2}} \right)
$$
burada $SR_0$ çoklu denemeden beklenen maksimum şanssal Sharpe; $\gamma_3, \gamma_4$ getiri çarpıklık/basıklığı. **DSR > 0.95** olmadan strateji canlıya alınmaz.

### 8.5 Sağlamlık (Robustness) Testleri
- **Parametre duyarlılığı:** Lookback'leri ±%20 değiştir; Sharpe çökmemeli (overfit göstergesi).
- **Monte Carlo:** İşlem sırasını/getirileri bootstrap (1.000+ yol) → MaxDD ve CAGR dağılımı, %5 kuyruk senaryosu.
- **Rejim alt-örnekleri:** 2008, 2020-Mart, 2022 ayı piyasası ayrı raporlanır.
- **Maliyet stres testi:** Maliyetleri 2×, 3× yap; edge hayatta kalmalı.

### 8.6 Raporlanan Metrikler
CAGR, Yıllık Vol, **Sharpe**, **Sortino**, **Calmar** (CAGR/MaxDD), MaxDD, ortalama düşüş süresi, kazanma oranı, profit factor, ortalama R, turnover, kapasite, **DSR**, hit-rate rejim bazında.

---

## 9. Kıyaslama (Benchmark) Seçimi

| Kıyaslama | Rol | Gerekçe |
|---|---|---|
| **SPY (Total Return)** | Birincil — mutlak | Yatırımcının alternatif maliyeti; "neden basit indeks değil?" sorusunun cevabı |
| **MTUM (momentum faktörü ETF'i)** | İkincil — faktör | Momentum bacağının saf faktör getirisini aşıp aşmadığı (alfa mı, beta mı?) |
| **60/40 (SPY/AGG)** | Risk-ayarlı | Geleneksel dengeli portföye karşı Sharpe üstünlüğü |
| **Risk-free (3-ay T-Bill)** | Sharpe paydası | Fazla getiri hesabı |

**Ölçüm felsefesi:** Mutlak getiri yanıltıcıdır; **risk-ayarlı fazla getiri (alfa)** asıl ölçüttür. Regresyon:
$$
R_{strat} - r_f = \alpha + \beta_{mkt}(R_{mkt}-r_f) + \beta_{mom} MOM + \beta_{val} HML + \epsilon
$$
İstatistiksel olarak anlamlı **$\alpha > 0$ (t-stat > 2.5)** ve düşük $\beta_{mkt}$ aranır — getirinin gizli beta değil, gerçek alfa olduğunu kanıtlamak için.

---

## 10. Edge Bozulma İzleme (Edge Decay Monitoring)

> Her edge ölür. Soru *ölüp ölmeyeceği* değil, *ne zaman* olduğunu zamanında fark edip etmeyeceğinizdir.

### 10.1 Canlı vs. Backtest Tutarlılığı
- **Rolling Sharpe (63g & 252g):** Canlı Sharpe, backtest güven aralığının (örn. %5 alt persantil) altına düşerse → sarı bayrak.
- **Tracking error:** Canlı getiri ile beklenen getiri arasındaki sapma; t-test ile anlamlı negatif drift → kırmızı bayrak.

### 10.2 CUSUM Yapısal Kırılma Testi
Kümülatif PnL sapması için CUSUM kontrol grafiği:
$$
C_t^+ = \max(0,\; C_{t-1}^+ + (x_t - \mu_0 - k)), \qquad \text{alarm: } C_t^+ > h
$$
$x_t$ günlük PnL, $\mu_0$ beklenen ortalama, $k$ slack, $h$ eşik. Edge'in beklenenden sistematik sapmasını erken yakalar.

### 10.3 İzlenecek Bozulma Göstergeleri
| Gösterge | Sağlıklı | Alarm |
|---|---|---|
| 252g rolling Sharpe | > 0.7 × backtest SR | < 0.4 × backtest SR |
| Sinyal IC (information coefficient) | Spearman ρ(sinyal, ileri getiri) > 0.03 | < 0 (3 ay üst üste) |
| Hit rate | Backtest ± 5pp | Backtest − 10pp |
| Faktör kalabalıklaşması | Stabil | Crowding skoru artışı (short interest, faktör korelasyonu) |
| Turnover/maliyet oranı | Stabil | Maliyetler alfayı yiyor |
| Rejim performansı | Tüm rejimlerde + | Tek rejime bağımlı hale gelme |

### 10.4 Bozulma Protokolü (Karar Ağacı)
```
EĞER 252g_Sharpe < 0.4×backtest VE CUSUM_alarm:
    → Risk %50 kıs, 1 ay gözlem
EĞER sinyal_IC < 0 (3 ardışık ay):
    → Stratejiyi duraklat, yeniden araştırma
EĞER maliyet/alfa > 0.5:
    → Turnover düşür veya evreni daralt
EĞER DSR (canlı veri eklenerek) < 0.90:
    → Devre dışı bırak, post-mortem
```

### 10.5 Periyodik Yeniden Doğrulama
- **Aylık:** Performans atıfı (attribution) — getiri hangi bacaktan/sektörden geldi?
- **Çeyreklik:** Parametre yeniden kalibrasyonu (walk-forward'ın bir sonraki penceresi).
- **Yıllık:** Tez geçerliliği denetimi — verimsizlik hâlâ var mı, yoksa arbitraj kapandı mı?

---

## 11. 100x Hedefi (Çok-Yıllı): Bileşik Büyüme Matematiği ve Tutarlı Plan

> **Güncellenmiş varsayım:** Hedef 1.000$ → 100.000$ (100x). **1 yıl beklentisi yok**; ufuk çok yıllı (≥ birkaç yıl). Bu, problemi tamamen değiştirir: artık bir "lotere" değil, bir **bileşik büyüme + sabır + katkı** problemidir. Bu bölüm matematikten ayrılmadan, gerçekçi bir yol haritası verir.

### 11.1 Saf Getiriyle 100x — Ufka Göre Gereken CAGR
$$
\text{Gereken CAGR} = 100^{1/N} - 1 \quad (N = \text{yıl})
$$

| Ufuk $N$ | Gereken yıllık getiri (CAGR) | Gerçekçilik |
|---|---|---|
| 1 yıl | %9.900 | İmkânsıza yakın (lotere) |
| 3 yıl | %364 | İmkânsıza yakın |
| 5 yıl | %151 | Sürdürülemez |
| 10 yıl | %58.5 | Renaissance Medallion seviyesi — tarihsel olarak ~tek örnek |
| 15 yıl | %35.9 | Aşırı zor; en iyi fonların üstü |
| 20 yıl | %25.9 | Çok zor ama Buffett bandının üstü |
| 25 yıl | %20.2 | Buffett seviyesi (uzun vadeli) — hâlâ olağanüstü |

**Sonuç:** Sadece getiriyle 100x, en uzun ufuklarda bile tarihin en iyi yatırımcılarının seviyesini gerektirir. Tek başına "edge" bunu makul olasılıkla sağlamaz. **Ama denklemde ikinci bir kaldıraç var: katkı.**

### 11.2 Asıl Çözüm — Bileşik Büyüme + Düzenli Katkı (DCA)
Düzenli katkıyla nihai varlık (gelecek değer, yıllık katkı $C$, getiri $g$):
$$
FV = P_0 (1+g)^N + C \cdot \frac{(1+g)^N - 1}{g}
$$

**Gerçekçi senaryolar (100.000$ varlık hedefi):**

| Başlangıç | Aylık katkı | Varsayılan CAGR | 100k'ya ulaşma süresi |
|---|---|---|---|
| 1.000$ | 0$ (katkısız) | %15 | ~33 yıl |
| 1.000$ | 0$ | %25 | ~21 yıl |
| 1.000$ | 200$/ay | %15 | ~16 yıl |
| 1.000$ | 300$/ay | %20 | ~11 yıl |
| 1.000$ | 500$/ay | %20 | ~8.5 yıl |

**Kritik içgörü:** 100.000$ hedefine ulaşmanın matematiksel olarak baskın kaldıracı **katkı + zaman**, kahramanca getiri değildir. Sürdürülebilir %15–25 CAGR (bu memo'nun çekirdek stratejisinin makul hedefi) + düzenli birikim = hedef gerçekçi. Aşırı getiri kovalamak (ve iflas riski almak) yerine **strateji edge'ini koruyup zamanı çalıştırmak** matematiğin önerdiği yoldur.

### 11.3 Neden Aşırı Kaldıraçla "Hızlandırmak" Matematiksel Hatadır — Kelly & İflas
Geometrik (log-servet) büyüme oranı:
$$
g = \mathbb{E}[\ln(1 + f \cdot X)]
$$
Kaldıraç $f$'i optimal (Kelly) noktanın ötesine itmek $g$'yi **düşürür**, sonra **negatife** çevirir. Aşırı-Kelly bölgesinde:
$$
P(\text{ruin}) \approx \left(\frac{q}{p}\right)^{N} \to 1 \quad (\text{yeterli işlem sayısında})
$$
Yani "süreyi kısaltmak için kaldıracı artırmak" matematiksel olarak **medyan sonucu sıfıra** taşır. Uzun ufkunuz en büyük avantajınız — onu aşırı kaldıraçla yakmak, sahip olduğunuz tek gerçek edge'i (zaman + bileşik) imha eder.

### 11.4 Konveksite Dilimi (Barbell) — Ufku Kısaltma *Opsiyonalitesi*
Çekirdeği riske atmadan, yukarı kuyruğa maruz kalmak için (Taleb barbell):
$$
\text{Portföy} = \underbrace{90\%\ \text{Çekirdek (§1–§10)}}_{\text{bileşik büyüme + hayatta kalma}} + \underbrace{10\%\ \text{Konveksite Dilimi}}_{\text{tanımlı-riskli OTM opsiyon}}
$$
- Dilimde **maks. kayıp = sermayenin %10'u**; çekirdek %90 her zaman korunur.
- Asimetrik ödeme ($-1×$ aşağı / $+10×$…$+50×$ yukarı) iyi bir yılda hedefe ulaşmayı *hızlandırabilir* ama bu bir **vaat değil, opsiyonalitedir**.
- Her bahis dilimin ≤ %20'si; iflas yapısal olarak imkânsız.

### 11.5 Dürüst Yol Haritası Tablosu (Çok-Yıllı)

| Yıl | Strateji modu | Yıllık getiri hedefi | Beklenen NAV bandı (katkı varsayımıyla*) |
|---|---|---|---|
| 1–2 | Süreç inşası, paper→küçük canlı | %10–20 (öğrenme önceliği) | 1.200–2.500$ |
| 3–5 | Ölçeklenmiş çekirdek + barbell | %15–25 | 5.000–20.000$ |
| 6–10 | Olgun süreç, artan katkı | %15–25 | 30.000–100.000$+ |

\* *Aylık ~300$ katkı ve %20 civarı CAGR varsayımıyla. Getiriler garanti değildir; bant gösterimseldir. Katkı yoksa süre uzar.*

### 11.6 Yönetici Direktör Tavsiyesi
1.000$ ile çok-yıllı 100.000$ hedefi **ulaşılabilirdir** — ama yolu kahramanca getiri değil, **üç değişkenin matematiği** belirler: (1) sürdürülebilir edge (bu memo'nun çekirdeği, %15–25 CAGR), (2) **düzenli katkı**, (3) **zaman/bileşik**. İlk yıllarda asıl hedef hesap bakiyesi değil **süreç edge'ini ve disiplini inşa etmektir** — çünkü ölçeklenebilir bir edge, 100.000$'dan çok daha değerli bir varlıktır. Barbell, ufku kısaltma *ihtimalini* matematiği bozmadan masada tutar. Sermayeyi aşırı kaldıraçla "hızlandırmaya" çalışmak (§6 Kelly ve §7 risk limitlerinin ihlali) **reddedilir**: en büyük avantajınız olan zamanı yok eder.

---

## 12. Uygulama Yol Haritası (Implementation Roadmap)

| Faz | Süre | Çıktı |
|---|---|---|
| **0. Veri altyapısı** | 2–3 hafta | Point-in-time veri, temizleme, evren oluşturma |
| **1. Sinyal araştırması** | 4–6 hafta | §3 sinyallerinin IC analizi, deflated Sharpe |
| **2. Backtest & doğrulama** | 4 hafta | Walk-forward, purged CV, maliyet stres, robustness |
| **3. Kâğıt üzerinde işlem (paper)** | 8–12 hafta | Canlı-vs-backtest tutarlılık, icra kalitesi |
| **4. Küçük canlı dağıtım** | Sürekli | 1.000$ ile §6 boyutlandırma, §10 izleme aktif |
| **5. İzleme & yeniden doğrulama** | Sürekli | Aylık attribution, çeyreklik kalibrasyon |

---

## Ek A — Temel Formül Özeti

| Kavram | Formül |
|---|---|
| Riske-ayarlı momentum | $M_i = R_i^{12-1} / \sigma_i^{63}$ |
| Kesitsel z-skor | $z_i = (x_i - \mu_{cs})/\sigma_{cs}$ |
| Beta-nötr reversal | $\tilde r_i = r_i - \beta_i r_{mkt}$ |
| Vol hedefleme kaldıracı | $L = \sigma_{target}/\sigma_{realized}$ |
| Fraksiyonel Kelly | $f_{used} = 0.25 \cdot (\mu - r_f)/\sigma^2$ |
| Pozisyon ağırlığı | $w_i = L f_{used} \cdot \frac{S_i}{\sum|S_j|} \cdot \frac{1/\sigma_i}{\sum 1/\sigma_j}$ |
| Portföy vol | $\sigma_p = \sqrt{w^T \Sigma w}$ |
| VaR (%99) | $z_{0.99}\,\sigma_p\,NAV$ |
| Sharpe | $(R_p - r_f)/\sigma_p$ |
| Sortino | $(R_p - r_f)/\sigma_{down}$ |
| Calmar | $CAGR / MaxDD$ |
| Deflated Sharpe | $\Phi\big((SR-SR_0)\sqrt{T-1}/\sqrt{1-\gamma_3 SR + \frac{\gamma_4-1}{4}SR^2}\big)$ |
| Geometrik büyüme | $g = \mathbb{E}[\ln(1+fX)]$ |
| İflas olasılığı | $P(ruin) \approx (q/p)^N$ |

## Ek B — Referanslar (Akademik Temel)
- Jegadeesh & Titman (1993) — *Returns to Buying Winners and Selling Losers* (momentum)
- Asness, Moskowitz & Pedersen (2013) — *Value and Momentum Everywhere*
- Lehmann (1990); Lo & MacKinlay (1990) — kısa-vadeli reversal
- Bakshi & Kapadia (2003); Carr & Wu (2009) — volatilite risk primi
- Kelly (1956); Thorp; MacLean, Thorp & Ziemba — Kelly kriteri ve fraksiyonel uygulama
- López de Prado (2018) — *Advances in Financial Machine Learning* (purged CV, DSR)
- Bailey & López de Prado (2014) — *The Deflated Sharpe Ratio*
- Ledoit & Wolf (2004) — kovaryans shrinkage
- Almgren & Chriss (2000) — optimal icra / market impact
- Taleb (2007) — *The Black Swan* (barbell / konveksite)

---

*Belge sonu. Bu memorandum bir tasarım çerçevesidir; canlı sermaye dağıtımından önce tam backtest doğrulaması (§8) ve bağımsız risk denetimi gerektirir.*
