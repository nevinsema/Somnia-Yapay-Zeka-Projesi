import pandas as pd
import numpy as np
import os

def prepare_data():
    input_file = "Sleep_Efficiency.csv"
    output_file = "somnia_dataset.csv"

   
    if not os.path.exists(input_file):
        print(f"⚠️ '{input_file}' bulunamadı! Lütfen dosyayı proje klasörüne koyduğundan emin ol.")
        return

    print(f"📂 '{input_file}' okunuyor ve işleniyor...")
    
    
    df = pd.read_csv(input_file)

   
    df["Caffeine consumption"] = df["Caffeine consumption"].fillna(0)
    df["Alcohol consumption"] = df["Alcohol consumption"].fillna(0)
    df["Exercise frequency"] = df["Exercise frequency"].fillna(0)
    df["Awakenings"] = df["Awakenings"].fillna(0)

    
    if df["Smoking status"].dtype == object:
        df["Smoking status"] = df["Smoking status"].map({"Yes": 1, "No": 0}).fillna(0)

   
    def parse_minutes(dt_str):
        try:
            dt = pd.to_datetime(dt_str)
            return dt.hour * 60 + dt.minute
        except:
            return 0

    df["bed_minutes"] = df["Bedtime"].apply(parse_minutes)
    df["wake_minutes"] = df["Wakeup time"].apply(parse_minutes)

    
    def calc_duration(row):
        bed = row["bed_minutes"]
        wake = row["wake_minutes"]
        if wake < bed:
            return (wake + 24 * 60) - bed
        return wake - bed

    df["duration_minutes"] = df.apply(calc_duration, axis=1)

   
    df_somnia = pd.DataFrame({
        "bed_minutes": df["bed_minutes"],
        "wake_minutes": df["wake_minutes"],
        "duration_minutes": df["duration_minutes"],
        "caffeine": df["Caffeine consumption"],
        "alcohol": df["Alcohol consumption"],
        "smoking": df["Smoking status"],
        "exercise": df["Exercise frequency"],
        "sleep_efficiency": df["Sleep efficiency"]
    })

    
    df_somnia.to_csv(output_file, index=False)
    print(f"✅ Başarılı! '{output_file}' oluşturuldu. Artık Somnia bu veriyi kullanabilir.")

if __name__ == "__main__":

    prepare_data()
