from flask import (
    Flask, render_template, request,
    redirect, url_for, session, jsonify
)
import json
import random
from difflib import get_close_matches
from somnia_brain import SomniaBrain
from database import (
    create_tables, register_user, check_login,
    get_security_question, check_security_answer,
    update_password, insert_sleep_record, fetch_all_records, get_db,
    get_model_stats, get_last_sleep_detail
)

app = Flask(__name__)
app.secret_key = "somnia-super-secret-key-change-this"

def load_intents():
    try:
        with open('somnia_chat_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"intents": []}

intents = load_intents()
brains: dict[int, SomniaBrain] = {}

def get_brain_for_user(user_id: int) -> SomniaBrain:
    if user_id not in brains:
        brains[user_id] = SomniaBrain()
    return brains[user_id]

def time_to_minutes(hhmm: str) -> int:
    if not hhmm: return 0
    h, m = map(int, hhmm.split(":"))
    return h * 60 + m

def is_logged_in() -> bool:
    return "user_id" in session


def generate_coach_feedback(bed_minutes, sleep_minutes, efficiency):
    """
    Kullanıcının istediği 'Düzenin ... ilerliyor. ... gerekli.' formatını üretir.
    """
    status = ""
    needed = ""
  
    normalized_bed = bed_minutes % 1440
    
    if 60 < normalized_bed < 300: # 01:00 ile 05:00 arası
        status = "biyolojik saatinle uyumsuz"
        needed = "yatış saatini öne çekmen"
    
   
    elif sleep_minutes < 360: # 6 saatten az
        status = "vücudunu yıpratacak"
        needed = "daha fazla dinlenme süresi"
        
    
    elif efficiency < 0.75:
        status = "kalitesiz ve kesintili"
        needed = "derin uyku ortamı (karanlık/sessizlik)"
        

    else:
        status = "oldukça sağlıklı ve dengeli"
        needed = "bu istikrarı koruman"

    return f"Yatma düzenin <strong>{status}</strong> şekilde ilerliyor.<br>Daha fazla <strong>{needed}</strong> gerekli."


def analyze_sleep_chat(efficiency, sleep_minutes, lifestyle):
    caffeine, alcohol, smoking, exercise = lifestyle
    bad_habits = []
    if alcohol > 0: bad_habits.append("Alkol")
    if caffeine > 50: bad_habits.append("Kafein")
    
    if efficiency < 0.75:
        msg = "Uyku verimin düşük. "
        if bad_habits: msg += f"{', '.join(bad_habits)} tüketimini azaltmalısın."
        else: msg += "Oda sıcaklığına dikkat et."
    else:
        msg = "Uyku verimin gayet iyi. Aynen devam!"
    return msg


@app.route("/register", methods=["GET", "POST"])
def register():
    if is_logged_in(): return redirect(url_for("index"))
    if request.method == "POST":
        u = request.form.get("username").strip(); p = request.form.get("password"); p2 = request.form.get("password2")
        qt = request.form.get("sec_type"); q = request.form.get("sec_question_custom") if qt=="custom" else request.form.get("sec_question_select"); a = request.form.get("sec_answer")
        if not u or not p or not p2: return render_template("register.html", error="Doldur")
        if p!=p2: return render_template("register.html", error="Uyuşmuyor")
        if register_user(u,p,q,a): session["user_id"]=check_login(u,p); session["username"]=u; return redirect(url_for("index"))
        else: return render_template("register.html", error="Kullanıcı adı dolu")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if is_logged_in(): return redirect(url_for("index"))
    if request.method == "POST":
        u = request.form.get("username").strip(); p = request.form.get("password")
        uid = check_login(u,p)
        if uid: session["user_id"]=uid; session["username"]=u; return redirect(url_for("index"))
        return render_template("login.html", error="Hatalı")
    return render_template("login.html")

@app.route("/logout")
def logout(): session.clear(); return redirect(url_for("login"))
@app.route("/forgot", methods=["GET", "POST"])
def forgot(): return render_template("forgot.html")
@app.route("/reset", methods=["GET", "POST"])
def reset_password(): return render_template("reset.html")
@app.route("/change_password", methods=["GET", "POST"])
def change_password(): return render_template("change_password.html")

# --- ANA SAYFA ---
@app.route("/", methods=["GET", "POST"])
def index():
    if not is_logged_in(): return redirect(url_for("login"))
    user_id = session["user_id"]
    brain = get_brain_for_user(user_id)
    suggestion = None
    suggestion_source = ""
    feedback_text = None 
    auto_chat_msg = None
    
    context = {"bed_time": "", "wake_time": "07:00", "efficiency": 80, 
               "caffeine": 0, "alcohol": 0, "smoking": 0, "exercise": 3}

    
    if request.method == "POST":
        bed = request.form.get("bed_time")
        wake = request.form.get("wake_time")
        eff_raw = request.form.get("efficiency") or "80"
        
        caffeine = int(request.form.get("caffeine") or 0)
        alcohol = int(request.form.get("alcohol") or 0)
        smoking = int(request.form.get("smoking") or 0)
        exercise = int(request.form.get("exercise") or 0)
        
        context.update({"bed_time": bed, "wake_time": wake, "efficiency": int(eff_raw),
                        "caffeine": caffeine, "alcohol": alcohol, "smoking": smoking, "exercise": exercise})

        if bed and wake:
            bed_m = time_to_minutes(bed)
            wake_m = time_to_minutes(wake)
            eff_input = int(eff_raw) / 100.0
            sleep_minutes = brain._sleep_minutes(bed_m, wake_m)
            lifestyle = [caffeine, alcohol, smoking, exercise]

            predicted_eff = brain.update_and_predict(bed_m, wake_m, eff_input, lifestyle)
            suggestion = brain.choose_optimal_bedtime(wake_m, lifestyle)
            
            feedback_text = generate_coach_feedback(bed_m, sleep_minutes, eff_input)
            
            
            auto_chat_msg = analyze_sleep_chat(eff_input, sleep_minutes, lifestyle)

            insert_sleep_record(user_id, bed, wake, eff_input, sleep_minutes, predicted_eff,
                                caffeine, alcohol, smoking, exercise, suggestion.best_bedtime_minutes)
            suggestion_source = "current"

    
    else:
        last_rec = get_last_sleep_detail(user_id)
        if last_rec:
            eff, mins, caf, alc, smk, exc, last_wake_str = last_rec
            last_wake_str = last_wake_str or "07:00"
            wake_m = time_to_minutes(last_wake_str)
            lifestyle = [caf, alc, smk, exc]
            
                        
            suggestion = brain.choose_optimal_bedtime(wake_m, lifestyle)
            
           
            feedback_text = generate_coach_feedback(0, mins, eff) # Saat 0 çünkü geçmiş yatışı şimdi hesaplamıyoruz
            
            suggestion_source = "history"
            context["wake_time"] = last_wake_str

    model_stats = get_model_stats(user_id)
    return render_template("index.html", 
                           username=session.get("username"), 
                           suggestion=suggestion, 
                           suggestion_source=suggestion_source,
                           feedback_text=feedback_text, # Template'e gidiyor
                           auto_chat_msg=auto_chat_msg, 
                           model_stats=model_stats,
                           **context)


@app.route("/api/chat", methods=["POST"])
def api_chat():
    if not is_logged_in(): return jsonify({"response": "Lütfen giriş yap."})
    msg = request.json.get("message", "").lower()
    user_id = session["user_id"]
    
    
    all_patterns = []
    pattern_map = {}
    for intent in intents['intents']:
        for pattern in intent['patterns']:
            all_patterns.append(pattern)
            pattern_map[pattern] = intent['tag']
            
    matches = get_close_matches(msg, all_patterns, n=1, cutoff=0.6)
    if matches:
        tag = pattern_map[matches[0]]
        for intent in intents['intents']:
            if intent['tag'] == tag:
                return jsonify({"response": random.choice(intent['responses'])})

   
    last_record = get_last_sleep_detail(user_id)
    if not last_record: return jsonify({"response": "Veri girmeden seni analiz edemem."})
    
    eff, mins, caf, alc, smk, exc, _ = last_record
    
    if any(x in msg for x in ["neden", "kötü", "sorun"]):
        reasons = []
        if alc > 0: reasons.append("alkol")
        if caf > 100: reasons.append("kafein")
        if smk == 1: reasons.append("sigara")
        if mins < 360: reasons.append("az uyku")
        if reasons: return jsonify({"response": f"Verilerine göre: {', '.join(reasons)} seni etkilemiş."})
        else: return jsonify({"response": "Verilerin temiz. Stres veya ortam olabilir."})
            
    elif any(x in msg for x in ["tavsiye", "öneri"]):
        if eff < 0.75: return jsonify({"response": "Bugün kafeini kes ve 22:00'de mavi ışıktan uzak dur."})
        else: return jsonify({"response": "Düzenin harika, aynen devam!"})

    return jsonify({"response": "Bunu tam anlamadım ama 'neden kötü uyudum' diye sorabilirsin."})

@app.route("/analiz")
def analiz(): return render_template("dashboard.html")

@app.route("/api/data")
def api_data():
    if not is_logged_in(): return jsonify([])
    return jsonify(fetch_all_records(session["user_id"]))

if __name__ == "__main__":
    create_tables()

    app.run(debug=True)
