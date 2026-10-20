from flask import Flask, request, jsonify, render_template_string
from datetime import datetime

app = Flask(__name__)
historique = []
commande = {"led": 0}

PAGE = """
<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Station de surveillance</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
body{font-family:Arial;background:#0f172a;color:#fff;margin:0;padding:15px}
h1{text-align:center}
.cards{display:flex;gap:10px;flex-wrap:wrap}
.card{flex:1;min-width:140px;background:#1e293b;padding:15px;border-radius:12px;text-align:center}
.card b{font-size:28px;display:block}
.alerte{background:#dc2626!important}
button{width:100%;padding:14px;margin:15px 0;font-size:16px;border:0;border-radius:10px;background:#2563eb;color:#fff}
#msg{text-align:center;font-weight:bold;min-height:24px}
</style></head><body>
<h1>Station de surveillance en temps réel</h1>
<div id="msg"></div>
<div class="cards">
 <div class="card" id="cT">Température<b id="t">--</b>°C</div>
 <div class="card" id="cH">Humidité<b id="h">--</b>%</div>
 <div class="card" id="cS">Son<b id="s">--</b></div>
</div>
<button onclick="led()">Allumer / éteindre la LED</button>
<canvas id="graph"></canvas>
<script>
const SEUIL_T=35, SEUIL_S=2000;
const g=new Chart(document.getElementById('graph'),{type:'line',
 data:{labels:[],datasets:[
 {label:'Température',data:[],borderColor:'#f97316'},
 {label:'Humidité',data:[],borderColor:'#38bdf8'}]}});
async function maj(){
 const r=await fetch('/api/historique'); const d=await r.json();
 if(!d.length) return;
 const x=d[d.length-1];
 t.textContent=x.temperature; h.textContent=x.humidite; s.textContent=x.son;
 cT.classList.toggle('alerte',x.temperature>SEUIL_T);
 cS.classList.toggle('alerte',x.son>SEUIL_S);
 msg.textContent=(x.temperature>SEUIL_T||x.son>SEUIL_S)?'⚠️ ALERTE : seuil dépassé !':'';
 const l=d.slice(-30);
 g.data.labels=l.map(e=>e.heure);
 g.data.datasets[0].data=l.map(e=>e.temperature);
 g.data.datasets[1].data=l.map(e=>e.humidite);
 g.update();
}
async function led(){await fetch('/api/led',{method:'POST'});}
setInterval(maj,2000); maj();
</script></body></html>
"""

@app.route("/")
def accueil():
    return render_template_string(PAGE)

@app.route("/api/data", methods=["POST"])
def recevoir():
    d = request.get_json(force=True)
    d["heure"] = datetime.now().strftime("%H:%M:%S")
    historique.append(d)
    del historique[:-200]
    return jsonify(ok=True)

@app.route("/api/historique")
def lire():
    return jsonify(historique)

@app.route("/api/led", methods=["POST"])
def basculer_led():
    commande["led"] = 1 - commande["led"]
    return jsonify(commande)

@app.route("/api/commande")
def lire_commande():
    return jsonify(commande)
