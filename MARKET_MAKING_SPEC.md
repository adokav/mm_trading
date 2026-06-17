# Market Making Motoru — Sistem Spesifikasyonu

**Jane Street Tarzı Otomatik Piyasa Yapıcılığı (AMM) İşlem Sistemi Belgesi**

| | |
|---|---|
| **Sistem Adı** | XMM-CX: Cross-Crypto Market Making Engine (Avellaneda–Stoikov çekirdekli) |
| **Varlık Sınıfı** | Kripto spot (+ opsiyonel perpetual futures hedge) |
| **Borsa** | MEXC (spot ana, futures hedge) |
| **Tasarım Sermayesi** | 500 USDT (mikro-hesap kalibrasyonu) |
| **Strateji Sınıfı** | Likidite sağlama / spread yakalama, envanter-nötr |
| **Sınıflandırma** | Dahili — Yalnızca Eğitim/Araştırma |
| **Versiyon / Tarih** | v1.0 — 2026-06-17 |

> **YASAL UYARI:** Bu belge eğitim ve araştırma amaçlıdır; yatırım tavsiyesi değildir. Kripto piyasa yapıcılığı; ters seçim (adverse selection), borsa kesintisi, likidite çekilmesi ve toplam sermaye kaybı riski taşır. 500 USDT'lik bir hesapta MM **mutlak kâr** olarak küçüktür; bu çerçevenin değeri metodoloji, risk disiplini ve ölçeklenebilir altyapıdır. Sermaye tahsisinden önce bağımsız profesyonel danışmanlık alın.

---

## 0. Yönetici Özeti (Executive Summary)

Piyasa yapıcı, **iki taraflı kotasyon** (bid + ask) vererek bid-ask spread'ini hasat eder; karşılığında **envanter riski** ve **ters seçim riski** taşır. Kârlılık üç koşula bağlıdır:

1. **Yakalanan spread > İşlem maliyeti + Ters seçim maliyeti** olmalı (temel eşitsizlik, §1.1).
2. **Envanter nötr** tutulmalı — yönlü bahis yapan bir MM, MM değildir; trend takipçisidir ve patlar.
3. **Hız**, kotasyonların bayatlamadan (stale) güncellenmesine yetmeli.

**MEXC'e özgü kritik avantaj:** MEXC spot tarafında uzun süredir **%0 maker komisyonu** (ve çoğu çiftte %0 taker) uygular. Bu, MM'in temel maliyet kaleminden birini (komisyon) **sıfırlar** ve mikro-hesap için MM'i nadiren uygulanabilir kılan az sayıdaki ortamdan biridir. **UYARI:** Bu komisyon politikası borsanın takdirindedir ve değişebilir; sistem, pozitif komisyon altında da çalışacak şekilde parametrize edilmiştir (§9). Komisyonu **0 varsaymak yasaktır** — fiili komisyon her döngüde API'den okunur.

**Çekirdek model:** Avellaneda–Stoikov (2008) optimal MM çerçevesi + order-book imbalance mikro-fiyatı + ters-seçim (VPIN/markout) tetikleyicili kotasyon geri çekme + envanter-skew kotasyon kaydırma + futures delta hedge overlay.

**Gerçekçi beklenti çerçevesi (taban senaryo, 500 USDT, %0 spot maker):** Günlük net getiri hedefi %0.1–%0.5 (volatiliteye ve seçilen çifte güçlü bağımlı), envanter devir hızı > 20x/gün, maker-fill oranı > %95, intraday Sharpe (annualize) hedefi 2–5. **Bu rakamlar simülasyon hedefidir, garanti değildir.**

---

## 1. Strateji Tezi ve Temel Eşitsizlik

### 1.1 Piyasa Yapıcının Temel Eşitsizliği

Bir round-trip (alış + satış) işlemde beklenen net kâr:

$$
\mathbb{E}[\pi_{rt}] = \underbrace{S}_{\text{yakalanan spread}} - \underbrace{2c}_{\text{komisyon (gidiş-dönüş)}} - \underbrace{\mathbb{E}[\text{AS}]}_{\text{ters seçim maliyeti}} - \underbrace{R_{inv}}_{\text{envanter taşıma riski primi}}
$$

- $S$ = yakalanan yarım-spread'lerin toplamı (bid ve ask aynı mid etrafında dolarsa $S \approx$ kotasyon spread'i).
- $c$ = tek-yön komisyon (MEXC spot maker ≈ %0; pozitif senaryoda parametrize).
- $\mathbb{E}[\text{AS}]$ = bilgili akışın (informed flow) yarattığı beklenen markout zararı.
- $R_{inv}$ = envanteri taşırken fiyat hareketinden doğan risk (envanter nötr tutularak minimize edilir).

**MM yalnızca $\mathbb{E}[\pi_{rt}] > 0$ olduğunda kote eder.** Bu, çift seçimi (§7), spread kalibrasyonu (§2) ve ters-seçim kapısı (§5) bu eşitsizliği pozitif tutmak içindir.

### 1.2 Getiri Kaynağının Ekonomik Mantığı

Piyasa yapıcı **likidite sağlama primi** kazanır: anında işlem yapmak isteyen "likidite talep edenlere" (acele eden, gürültü trader'ları) karşı sabırlı tarafta durur. Edge **kalıcıdır** çünkü her zaman acil likiditeye ihtiyaç duyan katılımcılar (likidasyonlar, panik, arbitrajcı bacakları, perakende piyasa emirleri) vardır. Edge **erir** çünkü diğer MM'ler aynı spread'i kovalar — bu yüzden hız, çift seçimi ve ters-seçim savunması rekabet avantajının kaynağıdır.

---

## 2. Spread Hesaplama Modeli

### 2.1 Adil Değer (Fair Value) Tahmini — Mikro-fiyat

Naif orta fiyat $s = (P_{bid} + P_{ask})/2$ önyargılıdır; emir defteri dengesizliğini (imbalance) ihmal eder. **Mikro-fiyat** kullanılır:

$$
p_{micro} = \frac{P_{bid}\cdot V_{ask} + P_{ask}\cdot V_{bid}}{V_{bid} + V_{ask}}
$$

Dikkat: ağırlıklar **çapraz**tır — bid tarafında daha fazla hacim (alıcı baskısı) fiyatı **ask'e** yaklaştırır. Çok seviyeli (L-derinlikli) genelleme, üst $L$ seviyenin hacim-ağırlıklı dengesizliği:

$$
I = \frac{\sum_{i=1}^{L} w_i V_{bid,i} - \sum_{i=1}^{L} w_i V_{ask,i}}{\sum_{i=1}^{L} w_i (V_{bid,i}+V_{ask,i})}, \quad w_i = e^{-\kappa (i-1)}
$$

$$
p_{fair} = s + \tfrac{1}{2}\,(\text{tick})\cdot \phi \cdot I, \qquad I \in [-1, 1]
$$

$\phi$ = imbalance duyarlılığı (kalibre edilir; tipik 0.3–1.0). Bu $p_{fair}$, kotasyonların merkezlendiği referanstır.

### 2.2 Volatilite Tahmini — EWMA Gerçekleşen Vol

Log getiriler $r_t = \ln(p_{fair,t}/p_{fair,t-1})$ üzerinden EWMA varyans:

$$
\sigma^2_t = \lambda \sigma^2_{t-1} + (1-\lambda)\, r_t^2, \qquad \lambda \in [0.94, 0.99]
$$

Kotasyon horizonu $\Delta t$ (saniye) için ölçeklenir: $\sigma_{\Delta t} = \sigma_t \sqrt{\Delta t / \tau_{sample}}$.

### 2.3 Rezervasyon Fiyatı (Reservation / Indifference Price)

Avellaneda–Stoikov: MM'in envanterine bağlı kayıtsızlık fiyatı:

$$
r(q) = p_{fair} - q \cdot \gamma \cdot \sigma^2 \cdot (T-t)
$$

- $q$ = işaretli envanter (base varlık birimi; long > 0, short < 0).
- $\gamma$ = risk-kaçınma katsayısı (büyük $\gamma$ ⇒ envantere agresif tepki).
- $(T-t)$ = horizon. Kripto **7/24** olduğundan terminal zaman yoktur; pratikte **sabit envanter-zaman ölçeği** $\eta$ ile değiştirilir (sürekli/stationary yaklaşım): $r(q) = p_{fair} - q\,\gamma\,\sigma^2\,\eta$.

**Yorum:** Long isek ($q>0$), $r < p_{fair}$ olur ⇒ hem bid hem ask aşağı kayar ⇒ ask daha agresif (satışı kolaylaştırır), bid daha pasif (alımı zorlaştırır). Envanter kendiliğinden nötre çekilir. Bu, §4'teki kotasyon kaydırmanın **matematiksel temeli**dir.

### 2.4 Optimal Spread

AS optimal toplam spread (arrival yoğunluğu $\lambda(\delta)=A e^{-k\delta}$ varsayımıyla):

$$
\delta_{total} = \underbrace{\gamma \sigma^2 (T-t)}_{\text{envanter riski terimi}} + \underbrace{\frac{2}{\gamma}\ln\!\Big(1 + \frac{\gamma}{k}\Big)}_{\text{rekabet / arrival terimi}}
$$

Pratik MM spread'i, AS terimine **maliyet ve ters-seçim tabanı** eklenerek inşa edilir:

$$
\boxed{\;\delta_{total} = \max\Big(\delta_{AS},\; \delta_{min}\Big), \qquad \delta_{min} = 2c + \alpha_{AS}\cdot \widehat{AS} + n_{tick}\cdot \text{tick}\;}
$$

- $2c$ = gidiş-dönüş komisyonu (en az bunu geri almalı).
- $\widehat{AS}$ = ters-seçim tahmini (markout EWMA, §5), $\alpha_{AS}$ güvenlik çarpanı.
- $n_{tick}\cdot \text{tick}$ = en az birkaç tick'lik mutlak taban (kuyruk değeri + tick yapısı).

Yarım-spread'ler (skew sonrası, §4):

$$
\delta_{bid} = \tfrac{1}{2}\delta_{total} + \text{skew}^+ , \qquad \delta_{ask} = \tfrac{1}{2}\delta_{total} - \text{skew}^+
$$

Nihai kotasyonlar:

$$
P_{bid} = r(q) - \delta_{bid}, \qquad P_{ask} = r(q) + \delta_{ask}
$$

(skew hem $r(q)$ kaydırmasıyla hem de yarım-spread asimetrisiyle iki kanaldan uygulanabilir; §4.)

### 2.5 Hacim Koşullandırması

Yüksek hacim ⇒ daha fazla fill fırsatı ama daha fazla ters seçim; düşük hacim ⇒ kotasyon bayatlama riski. Spread, kısa pencere hacmi $V_{win}$ ile koşullandırılır:

$$
\delta_{total} \mathrel{*}= \Big(1 + \beta_V \cdot \big(\tfrac{V_{win}}{\bar{V}} - 1\big)_+\Big)
$$

Hacim ani patladığında (haber/likidasyon) spread genişler — pasif savunma.

### 2.6 Spread Parametre Tablosu

| Parametre | Sembol | Tipik Değer (500 USDT, likit major) | Not |
|---|---|---|---|
| Risk-kaçınma | $\gamma$ | 0.1 – 1.0 | Yüksek ⇒ envantere agresif |
| Envanter-zaman ölçeği | $\eta$ | 1 – 100 s | $(T-t)$ yerine sabit |
| Arrival decay | $k$ | veriye fit | $\lambda(\delta)=Ae^{-k\delta}$ |
| EWMA λ (vol) | $\lambda$ | 0.97 | ~33 örnek yarı-ömür |
| Min spread tick | $n_{tick}$ | 2 – 4 | Tick yapısına bağlı |
| AS güvenlik çarpanı | $\alpha_{AS}$ | 1.5 – 3.0 | Ters seçim tamponu |
| Imbalance duyarlılığı | $\phi$ | 0.3 – 1.0 | Mikro-fiyat eğimi |
| Hacim genişletme | $\beta_V$ | 0.2 – 0.5 | Hacim patlamasında |

---

## 3. Envanter Yönetimi

### 3.1 İlke: Nötr Kal

MM'in P&L'i iki bileşene ayrışır (§8): **spread yakalama** (istediğimiz) ve **envanter/yönlü** (istemediğimiz gürültü). Hedef, envanter dağılımını sıfır etrafında dar tutmaktır: $\mathbb{E}[q]\approx 0$, $\text{Var}(q)$ küçük.

### 3.2 Envanter Bandları (500 USDT için)

Envanteri **notional** (USDT cinsi) olarak ölçeriz: $Q = q \cdot p_{fair}$.

| Band | Notional Limit | Aksiyon |
|---|---|---|
| **Yeşil (nötr)** | $\lvert Q\rvert \le$ 80 USDT | Normal iki-taraflı kotasyon |
| **Sarı (skew)** | 80 < $\lvert Q\rvert \le$ 150 USDT | Skew artır, ağır taraf kotasyonu küçült/geri çek |
| **Turuncu (agresif flatten)** | 150 < $\lvert Q\rvert \le$ 200 USDT | Tek taraflı kote (sadece azaltan taraf) + pasif likit emir |
| **Kırmızı (hard limit)** | $\lvert Q\rvert >$ 200 USDT | Taker ile zorla düzleştir veya futures hedge (§6); yeni risk-artıran kotasyon YOK |

200 USDT ≈ sermayenin %40'ı; tek çiftte maksimum maruziyet. Çoklu çift çalışıyorsa **toplam** brüt envanter ≤ %60 (300 USDT).

### 3.3 Hedef Envanter ve Mean-Reversion

Envanteri 0'a çeken kontrol, §2.3 rezervasyon fiyatı tarafından **otomatik** sağlanır. Ek olarak ayrık skew (§4) ve sınır aksiyonları (§3.2) devreye girer. Envanter "yarı-ömrü" (kaç saniyede yarıya iner) bir sağlık metriğidir; hedef < birkaç dakika.

---

## 4. Kotasyon Ayarlama (Skew) Mantığı

Envanter bir tarafta biriktiğinde fiyatlar iki kanaldan kaydırılır:

### 4.1 Kanal A — Rezervasyon Fiyatı Kayması (sürekli)
§2.3'teki $r(q)$ zaten envanterle orantılı kayar. Long envanter ⇒ tüm kotasyon merkezini aşağı çeker ⇒ satış olasılığı artar.

### 4.2 Kanal B — Asimetrik Yarım-Spread (ayrık skew)
Envanter oranı $u = Q / Q_{max} \in [-1,1]$ ile:

$$
\text{skew}^+ = \theta \cdot u \cdot \tfrac{1}{2}\delta_{total}
$$

- $u>0$ (long): $\delta_{bid}$ büyür (bid uzaklaşır, alım zorlaşır), $\delta_{ask}$ küçülür (ask yaklaşır, satım kolaylaşır).
- $\theta \in [0,1]$ skew yoğunluğu.

### 4.3 Kanal C — Boyut Asimetrisi
Ağır tarafın **emir boyutu** küçültülür, hafif tarafınki korunur:

$$
\text{size}_{ask} = \text{size}_0 \cdot (1 - \rho\, u_+), \quad \text{size}_{bid} = \text{size}_0 \cdot (1 + \rho\, u_+) \;\; (\text{long iken tersi})
$$

### 4.4 Skew Sözde-Kodu

```text
function compute_quotes(book, q, sigma, params):
    p_fair  = microprice(book, params.phi, params.L)
    u       = clamp((q * p_fair) / params.Q_max, -1, +1)     # envanter oranı

    # Rezervasyon fiyatı (Kanal A)
    r = p_fair - q * params.gamma * sigma**2 * params.eta

    # Optimal + taban spread
    delta_AS  = params.gamma*sigma**2*params.eta + (2/params.gamma)*ln(1+params.gamma/params.k)
    delta_min = 2*fee_rate*p_fair + params.alpha_AS*AS_estimate + params.n_tick*tick
    delta     = max(delta_AS, delta_min)
    delta    *= volume_widen_factor(book, params.beta_V)      # §2.5

    # Asimetrik yarım-spread (Kanal B)
    skew      = params.theta * u * 0.5 * delta
    d_bid     = 0.5*delta + skew
    d_ask     = 0.5*delta - skew

    P_bid = round_to_tick(r - d_bid, DOWN)
    P_ask = round_to_tick(r + d_ask, UP)

    # Boyut asimetrisi (Kanal C)
    s_bid = params.size0 * (1 + params.rho*max(-u,0)) * (1 - params.rho*max(u,0))
    s_ask = params.size0 * (1 + params.rho*max(u,0))  * (1 - params.rho*max(-u,0))

    # Sınır bandı override (§3.2)
    if abs(u) > 1.0:        # kırmızı: risk artıran tarafı kapat
        if u > 0: s_bid = 0
        else:     s_ask = 0
    return (P_bid, s_bid), (P_ask, s_ask)
```

### 4.5 Skew Parametre Tablosu

| Parametre | Sembol | Tipik | Not |
|---|---|---|---|
| Skew yoğunluğu | $\theta$ | 0.3 – 0.8 | Kanal B |
| Boyut asimetrisi | $\rho$ | 0.3 – 0.6 | Kanal C |
| Maks notional | $Q_{max}$ | 200 USDT | Kırmızı band |
| Taban emir boyutu | $\text{size}_0$ | 5 – 15 USDT | Çift derinliğine göre |

---

## 5. Olumsuz Seçim (Adverse Selection) Tespiti

Bilgili (informed) trader'lar kotasyonu **yanlış tarafından** toplar: bizden alır, fiyat hemen yükselir (biz ucuza sattık) veya bize satar, fiyat düşer (biz pahalıya aldık). Tespit ve savunma katmanları:

### 5.1 Markout (post-fill drift) — Birincil Sinyal

Her fill sonrası $\tau$ saniyede mid hareketini ölçeriz:

$$
m_\tau(\text{fill}) = \text{side} \cdot \big(s_{t+\tau} - p_{fill}\big), \quad \text{side}=+1 \text{ alış}, -1 \text{ satış}
$$

(side: bizim aldığımız fill için fiyat yükselmesi **lehimize**; sattığımız fill için fiyat düşmesi lehimize — markout pozitif = iyi, negatif = ters seçim.) EWMA markout:

$$
\widehat{AS}_t = \lambda_m \widehat{AS}_{t-1} + (1-\lambda_m)\big(-m_\tau\big)_+
$$

Sürekli negatif markout ⇒ bilgili akış ⇒ spread genişlet ($\alpha_{AS}$ üzerinden, §2.4) veya kote durdur.

### 5.2 VPIN (Volume-Synchronized Probability of Informed Trading)

Hacmi eşit $V$ kovalarına böl; her kovada alıcı/satıcı-başlatılan hacmi (tick-rule veya Lee–Ready ile) ayır:

$$
\text{VPIN} = \frac{1}{n}\sum_{j=1}^{n} \frac{\lvert V_{buy,j} - V_{sell,j}\rvert}{V}
$$

Yüksek VPIN ⇒ tek yönlü toksik akış ⇒ savunma.

### 5.3 Order Flow Imbalance (OFI) ve Trade-through

- **OFI:** Top-of-book hacim/fiyat değişimlerinden net emir akışı. Kalıcı pozitif OFI + bizim ask'imizin sürekli vurulması ⇒ trend başlıyor, ask'i geri çek.
- **Trade-through / kuyruk tükenmesi:** Bizim seviyemizdeki kuyruk anormal hızlı eriyorsa, biri agresif süpürüyor ⇒ geri çekil.
- **Spread/derinlik çöküşü:** Karşı taraf derinliği aniden inceliyorsa, fiyat sıçramaya hazır.

### 5.4 Ters-Seçim Kapısı (Gate) Sözde-Kodu

```text
function adverse_selection_gate(state):
    score = 0
    if state.markout_ewma     > MK_TH:  score += 2     # birincil
    if state.vpin             > VPIN_TH: score += 1
    if abs(state.ofi_ewma)    > OFI_TH:  score += 1
    if state.queue_depletion  > QD_TH:   score += 1
    if state.spread_z         > SPRD_TH: score += 1

    if   score >= 4: return "HALT"          # kotasyonları çek, bekle
    elif score >= 2: return "WIDEN"         # spread'i 1.5–3x genişlet, boyut küçült
    else:            return "NORMAL"
```

### 5.5 Ters-Seçim Parametre Tablosu

| Sinyal | Eşik (TH) | Aksiyon ağırlığı |
|---|---|---|
| Markout EWMA | > 0 ve artıyor; z>2 | 2 (birincil) |
| VPIN | > 0.6 (0–1) | 1 |
| OFI EWMA (z-skor) | > 2 | 1 |
| Kuyruk tükenme hızı | > 2x normal | 1 |
| Spread z-skor | > 3 | 1 |

---

## 6. Korunma (Hedging) Stratejisi

### 6.1 Ne Zaman Hedge?

Envanter §3.2 turuncu/kırmızı banda girip skew ile **yeterince hızlı** düzleşmiyorsa, yönlü risk hedge edilir. Spot-only başlangıçta "hedge" = taker ile düzleştirme. Ölçeklendikçe **MEXC perpetual futures** ile delta hedge:

$$
\text{net delta} = q_{spot} + q_{futures} \approx 0
$$

### 6.2 Nasıl Hedge?

- **Spot taker flatten:** Kırmızı bandda, ağır envanteri karşı tarafa market emriyle azalt. Maliyet = taker fee + yarı-spread. Sadece son çare.
- **Futures delta hedge:** Long spot envanteri ⇒ aynı/benzer perp'te short aç. Spread yakalamaya spot tarafında devam ederken yönlü risk futures'ta nötrlenir. Maliyet = futures taker fee + **funding rate** (pozisyon süresince).
- **Eşik & histerezis:** Hedge'i $\lvert Q\rvert > Q_{hedge}$'de aç, $\lvert Q\rvert < Q_{hedge}/2$'de kapat (çırpınmayı önler).

### 6.3 Hedge Maliyet Muhasebesi

$$
\text{HedgeCost} = \underbrace{f_{taker}\cdot \text{notional}}_{\text{komisyon}} + \underbrace{\text{spread}/2 \cdot \text{notional}}_{\text{slippage}} + \underbrace{\sum \text{funding}_t}_{\text{taşıma}}
$$

Bu maliyet §8 PnL ayrıştırmasında **ayrı bir kalem**dir; spread kârından düşülür. Hedge yalnızca beklenen envanter zararı > hedge maliyeti olduğunda mantıklıdır.

### 6.4 Hedge Sözde-Kodu

```text
function manage_hedge(Q, fut_pos, params):
    target_fut = 0
    if abs(Q) > params.Q_hedge:
        target_fut = -Q / fut_contract_value          # delta-nötrle
    elif abs(Q) < params.Q_hedge/2:
        target_fut = 0                                  # histerezis: kapat
    else:
        return                                          # ölü bölge, dokunma
    delta_contracts = target_fut - fut_pos
    if abs(delta_contracts) > params.min_clip:
        place_futures_order(sign(delta_contracts), abs(delta_contracts), type="LIMIT_THEN_TAKER")
```

---

## 7. Piyasa Mikro Yapısı Analizi

### 7.1 Tick Boyutu ve Emir Defteri
- **Tick (fiyat adımı)** ve **lot (miktar adımı)** MEXC `exchangeInfo`/symbol filtrelerinden okunur. Spread, tick'in tam katı olarak kote edilir.
- **Spread / tick oranı kritik:** Spread = 1 tick ise yakalanacak edge yok (özellikle %0 fee dışı senaryoda). MM, **spread ≥ 2–3 tick** olan çiftleri hedefler.
- **Derinlik profili:** L1–L10 hacimleri, mikro-fiyat (§2.1) ve imbalance sinyalleri için izlenir.

### 7.2 Kuyruk Önceliği (Queue Priority)
- MEXC spot **price-time priority** kullanır: aynı fiyatta önce gelen önce dolar.
- **Kuyruk değeri:** İyi bir kuyruk pozisyonu = düşük ters seçim (önümüzde tampon var) + yüksek fill olasılığı. Gereksiz cancel-replace **kuyruk önceliğini sıfırlar** — bu yüzden kotasyon yalnızca anlamlı sapmada (Δ > tolerans) güncellenir (§8.5, no-churn).
- **Pegging:** Best bid/ask'e "join" mi "improve" mı? Join (aynı fiyat) kuyruk arkasına geçer ama ters seçimi düşürür; improve (1 tick içeri) önceliği alır ama daha çok toksik akışa maruz kalır. Karar imbalance ve markout'a göre dinamik.

### 7.3 MEXC'e Özgü Notlar
- **Komisyon:** Spot maker/taker uzun süredir birçok çiftte %0; **her döngüde API'den doğrulanır**, koda 0 gömülmez.
- **Veri:** WebSocket ile `depth` (diff/snapshot) ve `trades`/`deals` akışı. REST yalnızca başlangıç snapshot + rate-limit yedeği.
- **Rate limit:** Emir yerleştir/iptal API ağırlığı sınırlıdır; cancel-replace cadence buna göre bütçelenir. Limit aşımı = ban riski.
- **Kolokasyon yok:** MEXC perakende kolokasyon sunmaz; en iyi pratik, borsa sunucularına ağ-yakın bir bulut bölgesinde (örn. yakın AWS/GCP) VPS. Hedef tick-to-trade < 50 ms.

---

## 8. PnL Ayrıştırması (PnL Decomposition)

### 8.1 Temel Kimlik

Toplam değer = nakit + envanter·mid. Bir periyottaki değişim ayrıştırılır:

$$
\Delta \text{PnL} = \underbrace{\sum_{\text{fills}} \text{side}\cdot(p_{fair} - p_{fill})\cdot \text{size}}_{\text{(1) Spread Yakalama}} \;+\; \underbrace{q \cdot \Delta p_{fair}}_{\text{(2) Envanter / Yönlü}} \;+\; \underbrace{\sum \text{rebate} - \text{fee}}_{\text{(3) Komisyon/İade}} \;+\; \underbrace{\text{(4) Hedge PnL}}_{\text{futures + funding}}
$$

- **(1) Spread yakalama:** Her fill'in adil değere göre ne kadar "içeriden" gerçekleştiği. MM'in **gerçek edge'i** budur; pozitif ve istikrarlı olmalı.
- **(2) Envanter/yönlü:** Envanteri taşırken fiyatın hareketi. Sıfır-ortalamalı **gürültü** olmalı; sistematik negatifse ters seçim var (§5) veya skew yetersiz.
- **(3) Komisyon/iade:** MEXC %0 maker'da ≈ 0; taker flatten/hedge negatif.
- **(4) Hedge:** Futures realized + funding (§6.3).

### 8.2 Markout-Tabanlı Edge Atfı
Spread yakalama, çoklu horizonlarda markout ile doğrulanır: $\tau \in \{1s, 5s, 30s, 60s\}$. Anlık spread pozitif ama 30s markout negatifse, edge **sahte**dir (ters seçim onu yiyor). Gerçek edge = spread − ters seçim, $\tau\to\infty$'da kalan.

### 8.3 Raporlama Tablosu (her seans)

| Bileşen | Metrik | İşaret beklentisi |
|---|---|---|
| Spread yakalama | bps/round-trip, toplam USDT | (+) istikrarlı |
| Envanter/yönlü | toplam USDT, vol | ~0, düşük vol |
| Komisyon/iade | toplam USDT | ≥0 (maker) / <0 (taker) |
| Hedge | realized + funding | savunma maliyeti |
| **Net** | toplam USDT, Sharpe | (+) |

---

## 9. Risk Limitleri ve Otomatik Kapatma (Kill-Switch)

### 9.1 Risk Limit Tablosu (500 USDT hesap)

| Limit | Değer | Tetiklenince |
|---|---|---|
| Maks envanter (tek çift) | 200 USDT notional (%40) | Kırmızı band: zorla flatten/hedge |
| Maks brüt envanter (tüm çiftler) | 300 USDT (%60) | Yeni risk-artıran kote durur |
| Günlük maks kayıp (stop) | 15 USDT (%3) | **Tüm kotasyonları çek, gün sonuna kadar dur** |
| Intraday maks DD | 25 USDT (%5) | Sistem kapanır, manuel inceleme |
| Tek-çift saatlik kayıp | 8 USDT | O çiftte kote durdur |
| Maks emir/dakika | rate-limit bütçesi | Cadence yavaşlat |
| Maks açık emir | 8 (2 seviye × 2 taraf × çift) | Fazlasını iptal |

### 9.2 Kill-Switch Tetikleyicileri

```text
function kill_switch_check(state):
    triggers = []
    if state.daily_pnl       <= -DAILY_STOP:      triggers += "DAILY_LOSS"
    if state.intraday_dd      >= MAX_DD:           triggers += "DRAWDOWN"
    if state.ws_staleness     >  STALE_MS:         triggers += "DATA_STALE"     # veri bayatladı
    if state.reject_rate      >  REJECT_TH:        triggers += "API_DEGRADED"
    if state.vol_spike        >  VOL_TH:           triggers += "VOL_SHOCK"       # σ ani 3x
    if state.markout_ewma     >  AS_HALT_TH:       triggers += "TOXIC_FLOW"
    if state.clock_drift      >  DRIFT_MS:         triggers += "CLOCK"
    if triggers:
        cancel_all_orders()                         # ÖNCE iptal (en kritik)
        if "DRAWDOWN" in triggers or "DATA_STALE" in triggers:
            flatten_inventory(method="TAKER")       # riski kapat
        halt_quoting(triggers)
        alert(triggers)
```

**Tasarım ilkesi:** Kill-switch'te **önce iptal, sonra düzleştir**. Belirsizlikte (veri bayat, bağlantı koptu) varsayım her zaman "en kötü" — kote etme, riski kapat. Yeniden başlatma **manuel onay** ister (otomatik re-arm yalnızca geçici/yumuşak tetiklerde, histerezisle).

### 9.3 Bağlantı / Altyapı Güvenliği
- **Dead-man's switch:** Borsa destekliyorsa, bağlantı koparsa borsa otomatik tüm emirleri iptal etsin. Desteklenmiyorsa, heartbeat kaybında watchdog süreci `cancel_all` çağırır.
- **Idempotent client order ID:** Reconnect sonrası emir durumu güvenli senkronize edilir; çift-emir önlenir.

---

## 10. Performans Metrikleri ve Hedefler

### 10.1 Metrik Tanımları

| Metrik | Tanım | Hedef (500 USDT, likit major) |
|---|---|---|
| **Yakalanan spread** | Ort. (fair − fill)·side, bps/RT | > 2× ters-seçim maliyeti |
| **Maker-fill oranı** | maker fills / toplam fills | > %95 (taker pahalı) |
| **Yürütme/fill oranı** | dolan kote / verilen kote | %5–20 (sağlıklı; çok yüksek ⇒ spread dar/toksik) |
| **Envanter devir hızı** | günlük işlem hacmi / ort. envanter | > 20x/gün |
| **Envanter yarı-ömrü** | $\lvert q\rvert$'nin yarıya inme süresi | < birkaç dakika |
| **Markout (30s)** | post-fill drift, bps | ≥ 0 (negatifse ters seçim) |
| **Net Sharpe (annualize)** | intraday getiri Sharpe | 2 – 5 |
| **Uptime / kote süresi** | kote edilen / toplam süre | > %90 (sağlıklı piyasada) |
| **Günlük net getiri** | net PnL / sermaye | %0.1 – %0.5 (vol'e bağlı) |

### 10.2 Hedef-Aşımı Uyarıları (paradoks)
- **Fill oranı çok yüksek + markout negatif** ⇒ kotasyon çok agresif/toksik. Spread genişlet.
- **Fill oranı çok düşük** ⇒ spread çok geniş, edge yakalanmıyor. Daralt / kuyruk pozisyonunu iyileştir.
- **Sharpe yüksek ama mutlak PnL küçük** ⇒ 500 USDT'de beklenen; ölçek altyapı stabilse artırılır.

---

## 11. 500 USDT MEXC İçin Gerçekçi Hüküm

- **Ölçek gerçeği:** 500 USDT'de günlük %0.2 ≈ 1 USDT/gün. MM'in değeri burada **mutlak kâr değil**, (a) düşük-korelasyonlu/düşük-vol bir getiri akışı, (b) sermaye büyüdükçe ölçeklenen altyapı, (c) disiplinli risk çerçevesi. "Hızlı zenginleşme" matematiksel olarak desteklenmez.
- **MEXC %0 maker komisyonu**, mikro-hesap MM'ini *uygulanabilir* kılan nadir koşullardan biridir — ama politika değişebilir; sistem pozitif komisyona dayanıklı tasarlanmıştır.
- **En büyük tehlikeler:** (1) ters seçim (likit major'da rekabet yüksek, mid-cap'te toksisite yüksek), (2) borsa/bağlantı riski (kill-switch zorunlu), (3) trend günleri (envanter limitleri + hedge zorunlu).
- **Çift seçimi:** spread ≥ 2–3 tick, yeterli derinlik, makul (aşırı değil) volatilite, manipülasyona düşük açıklık. Aşırı ince/pump-dump çiftlerinden kaçın.

---

## 12. Sistem Mimarisi (Operasyonel)

```text
              +-------------------+        +------------------+
  MEXC WS --> | Market Data Feed  | -----> | Fair Value /     |
  (depth,     | (depth, trades)   |        | Vol / Imbalance  |
   trades)    +-------------------+        +--------+---------+
                                                    |
  MEXC WS --> +-------------------+                 v
  (orders,    | Order/Fill State  | ----> +------------------+   +-----------------+
   fills) <-- | (positions, q)    |       | Quoting Engine   |-->| Adverse-Sel Gate|
              +-------------------+       | (AS + skew, §2-4)|   | (§5)            |
                     ^                    +--------+---------+   +-----------------+
                     |                             |
              +------+--------+            +--------v---------+   +-----------------+
              | Risk / Kill   |<-----------| Order Manager    |-->| Hedge Manager   |
              | Switch (§9)   |  veto      | (place/cancel,   |   | (futures, §6)   |
              +---------------+            |  no-churn, §7.2) |   +-----------------+
                                           +------------------+
                                                    |
                                           +--------v---------+
                                           | PnL Attribution  | (§8)
                                           | + Metrics (§10)  |
                                           +------------------+
```

**Sıcak yol (hot path) gecikme bütçesi (hedef):** WS event → fair value → quote decision → order out: **< 50 ms**. Cancel/replace yalnızca |yeni − eski kote| > tolerans olduğunda (no-churn, kuyruk önceliğini korur).

---

## Ek A — Notasyon Sözlüğü

| Sembol | Anlam |
|---|---|
| $s, p_{fair}$ | mid / mikro-fiyat (adil değer) |
| $q, Q$ | envanter (base birim / USDT notional) |
| $r(q)$ | rezervasyon (kayıtsızlık) fiyatı |
| $\delta$ | yarım/toplam spread |
| $\gamma$ | risk-kaçınma |
| $\sigma$ | volatilite (EWMA) |
| $\eta$ | envanter-zaman ölçeği |
| $k, A$ | arrival yoğunluğu parametreleri |
| $I$ | order-book imbalance |
| $\widehat{AS}$ | ters-seçim tahmini (markout) |
| $u$ | envanter oranı $Q/Q_{max}$ |

---

> **TEKRAR UYARI:** Eğitim/araştırma amaçlıdır; yatırım tavsiyesi değildir. Simüle/geçmiş performans gelecek getiriyi garanti etmez. Kripto MM toplam sermaye kaybına yol açabilir. Canlı sermaye öncesi uzun paper-trading + ileri-test (forward test) zorunludur.
