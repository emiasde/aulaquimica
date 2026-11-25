# Gera as vozes neurais da Microsoft (Francisca/Antonio) e embute no jogo.
# Uso:  pip install edge-tts   e depois   python gerar_audio.py
import asyncio, base64, json, sys, edge_tts
VOZ = "pt-BR-FranciscaNeural"   # troque por "pt-BR-AntonioNeural" se preferir voz masculina
frases = json.load(open("frases.json", encoding="utf-8"))
html = open("jogo_base.html", encoding="utf-8").read()
audios = {}
async def um(s, sem):
    async with sem:
        for t in range(4):
            try:
                c = edge_tts.Communicate(s, VOZ, rate="-4%")
                b = b""
                async for ch in c.stream():
                    if ch["type"] == "audio": b += ch["data"]
                if b: audios[s] = base64.b64encode(b).decode(); return
            except Exception as e:
                await asyncio.sleep(1.5)
        print("FALHOU:", s)
async def main():
    sem = asyncio.Semaphore(5)
    await asyncio.gather(*[um(s, sem) for s in frases])
asyncio.run(main())
print(len(audios), "de", len(frases), "frases geradas")
if len(audios) < len(frases): sys.exit("Faltaram frases, rode de novo.")
out = html.replace("/*AUDIO_JSON*/{}/*END_AUDIO*/", json.dumps(audios, ensure_ascii=False))
open("index.html", "w", encoding="utf-8").write(out)
print("Pronto! Arquivo index.html criado. Suba ele no GitHub.")
