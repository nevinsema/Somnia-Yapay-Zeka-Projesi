import os
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor

class Suggestion:
    def __init__(self, best_minutes: int, score: float):
        self.best_bedtime_minutes = best_minutes
        self.best_bedtime_hour = best_minutes // 60
        self.best_bedtime_minute = best_minutes % 60
        self.score = score

class SomniaBrain:
    def __init__(self, data_path="somnia_dataset.csv", model_path="somnia_model.pkl"):
        self.data_path = data_path
        self.model_path = model_path
        self.model = None
        
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
        else:
            self.train_model()

    def train_model(self):
        if not os.path.exists(self.data_path):
            print("⚠️ Veri seti bulunamadı! Lütfen önce generate_data.py çalıştırın.")
            return

        df = pd.read_csv(self.data_path)
        
        features = ["bed_minutes", "wake_minutes", "duration_minutes", 
                    "caffeine", "alcohol", "smoking", "exercise"]
        X = df[features]
        y = df["sleep_efficiency"]

        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X, y)
        joblib.dump(self.model, self.model_path)
        print("✅ Model eğitildi.")

    def _sleep_minutes(self, bed_m: int, wake_m: int) -> int:
        if wake_m < bed_m:
            wake_m += 24 * 60
        return wake_m - bed_m

    def predict_efficiency(self, bed_m, wake_m, caffeine, alcohol, smoking, exercise):
        if self.model is None: return 0.5
            
        duration = self._sleep_minutes(bed_m, wake_m)
        input_data = pd.DataFrame([{
            "bed_minutes": bed_m,
            "wake_minutes": wake_m,
            "duration_minutes": duration,
            "caffeine": caffeine,
            "alcohol": alcohol,
            "smoking": smoking,
            "exercise": exercise
        }])
        
        return float(self.model.predict(input_data)[0])

    def update_and_predict(self, bed_m, wake_m, efficiency_actual, lifestyle_list):
        caffeine, alcohol, smoking, exercise = lifestyle_list
        duration = self._sleep_minutes(bed_m, wake_m)

        new_row = {
            "bed_minutes": bed_m,
            "wake_minutes": wake_m,
            "duration_minutes": duration,
            "caffeine": caffeine,
            "alcohol": alcohol,
            "smoking": smoking,
            "exercise": exercise,
            "sleep_efficiency": efficiency_actual
        }
        
        if os.path.exists(self.data_path):
            df = pd.read_csv(self.data_path)
            new_df = pd.DataFrame([new_row])
            df = pd.concat([df, new_df], ignore_index=True)
            df.to_csv(self.data_path, index=False)
            self.train_model()
        
        return self.predict_efficiency(bed_m, wake_m, caffeine, alcohol, smoking, exercise)

    def choose_optimal_bedtime(self, wake_minutes, lifestyle_list):
        best_score = -1.0
        best_bed = None
        caffeine, alcohol, smoking, exercise = lifestyle_list

        for hours_back in np.linspace(5, 10, num=21):
            bed_candidate = wake_minutes - int(hours_back * 60)
            if bed_candidate < 0: bed_candidate += 24 * 60
            
            score = self.predict_efficiency(bed_candidate, wake_minutes, caffeine, alcohol, smoking, exercise)
            if score > best_score:
                best_score = score
                best_bed = bed_candidate

        if best_bed is None: best_bed = wake_minutes - 8 * 60
        return Suggestion(best_bed, best_score)