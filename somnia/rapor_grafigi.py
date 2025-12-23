import pandas as pd
import matplotlib.pyplot as plt
import joblib
from sklearn.model_selection import train_test_split

# -------------------------------------------------
# 1. VERİ SETİNİ YÜKLE
# -------------------------------------------------
df = pd.read_csv("Sleep_Efficiency.csv")

# -------------------------------------------------
# 2. FEATURE ENGINEERING (MODELLE UYUMLU)
# -------------------------------------------------

# Bedtime: tarih+saat -> sadece saat+dakika (dakika cinsinden)
bedtime_parsed = pd.to_datetime(df["Bedtime"], errors="coerce")
df["bed_minutes"] = bedtime_parsed.dt.hour * 60 + bedtime_parsed.dt.minute

# Uyku süresi (saat -> dakika)
df["duration_minutes"] = df["Sleep duration"] * 60

# Sayısal değişkenler (isim eşleştirme)
df["caffeine"] = df["Caffeine consumption"]
df["alcohol"] = df["Alcohol consumption"]
df["exercise"] = df["Exercise frequency"]

# Kategorik -> sayısal
df["gender"] = df["Gender"].map({"Male": 1, "Female": 0})
df["smoking"] = df["Smoking status"].map({"Yes": 1, "No": 0})

# -------------------------------------------------
# 3. MODELİN BEKLEDİĞİ FEATURE SETİ
# -------------------------------------------------
X = df[
    [
        "bed_minutes",
        "duration_minutes",
        "caffeine",
        "alcohol",
        "exercise",
        "gender",
        "smoking",
    ]
]

y = df["Sleep efficiency"]

# -------------------------------------------------
# 4. EKSİK VERİLERİ TEMİZLE (ÇÖKMESİN DİYE)
# -------------------------------------------------
data = pd.concat([X, y], axis=1).dropna()
X = data.drop("Sleep efficiency", axis=1)
y = data["Sleep efficiency"]

# -------------------------------------------------
# 5. TRAIN / TEST AYIR
# -------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# -------------------------------------------------
# 6. EĞİTİLMİŞ MODELİ YÜKLE
# -------------------------------------------------
model = joblib.load("somnia_model.pkl")

# -------------------------------------------------
# 7. TAHMİN AL
# -------------------------------------------------
y_pred = model.predict(X_test)

# -------------------------------------------------
# 8. GRAFİK OLUŞTUR (SADECE RAPOR İÇİN)
# -------------------------------------------------
plt.figure(figsize=(10, 5))

plt.plot(
    y_test.values[:50],
    label="Gerçek Uyku Verimliliği",
    linewidth=2
)

plt.plot(
    y_pred[:50],
    linestyle="--",
    label="AI Tahmini"
)

plt.xlabel("Test Örnekleri")
plt.ylabel("Uyku Verimliliği")
plt.title("Gerçek ve Tahmin Edilen Uyku Verimliliği")
plt.legend()
plt.grid(True)

# -------------------------------------------------
# 9. KAYDET (WORD / PDF İÇİN)
# -------------------------------------------------
plt.savefig(
    "somnia_gercek_vs_tahmin.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("Grafik başarıyla oluşturuldu: somnia_gercek_vs_tahmin.png")
