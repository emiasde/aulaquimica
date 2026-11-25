# Gera as vozes da ElevenLabs e embute no jogo (index.html).
# 1) pip install requests
# 2) defina a chave:  Windows (cmd): set ELEVEN_API_KEY=sua_chave   |  Mac/Linux: export ELEVEN_API_KEY=sua_chave
# 3) python gerar_eleven.py COLE_O_VOICE_ID
#    (opcional) python gerar_eleven.py VOICE_ID eleven_v3
# Os mp3 ficam salvos na pasta "clips": se der erro no meio, rode de novo que ele continua de onde parou
# sem gastar credito de novo.
import base64, hashlib, json, os, sys, time, requests
if len(sys.argv) < 2: sys.exit("Uso: python gerar_eleven.py VOICE_ID [modelo]")
KEY = os.environ.get("ELEVEN_API_KEY") or sys.exit("Defina ELEVEN_API_KEY antes.")
VOICE = sys.argv[1]
MODEL = sys.argv[2] if len(sys.argv) > 2 else "eleven_multilingual_v2"
frases = json.load(open("frases.json", encoding="utf-8"))
html = open("jogo_base.html", encoding="utf-8").read()
os.makedirs("clips", exist_ok=True)
audios = {}
for i, s in enumerate(frases, 1):
    f = os.path.join("clips", hashlib.md5((VOICE + MODEL + s).encode()).hexdigest() + ".mp3")
    if not os.path.exists(f):
        for tent in range(4):
            r = requests.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}?output_format=mp3_44100_64",
                headers={"xi-api-key": KEY},
                json={"text": s, "model_id": MODEL,
                      "voice_settings": {"stability": 0.4, "similarity_boost": 0.8, "style": 0.3}},
                timeout=90)
            if r.status_code == 200:
                open(f, "wb").write(r.content); break
            if r.status_code == 429: time.sleep(3 * (tent + 1)); continue
            sys.exit(f"Erro {r.status_code} na frase {i}: {r.text[:300]}")
        else:
            sys.exit(f"Falhou na frase {i}, rode de novo.")
    audios[s] = base64.b64encode(open(f, "rb").read()).decode()
    print(f"{i}/{len(frases)}", end="\r")
out = html.replace("/*AUDIO_JSON*/{}/*END_AUDIO*/", json.dumps(audios, ensure_ascii=False))
open("index.html", "w", encoding="utf-8").write(out)
print("\nPronto! index.html criado. Suba ele no GitHub.")
