# "C:\Users\Hub IFNC\AppData\Local\Programs\Python\Python313\python.exe" alterarCena.py

import datetime
import time
import websocket
import json

# ==========================
# CONFIGURAÇÕES DO OBS
# ==========================
OBS_URL = "ws://localhost:4455"   # mesma porta das configs do OBS

# ==========================
# GRADE DE PROGRAMAÇÃO
# ==========================
# ATENÇÃO: os nomes das cenas abaixo devem existir IGUAIS no OBS
grade = {
    "segunda": [
        ("07:15", "11:00", "# MANHA SERTANEJA"),
        ("11:00", "14:00", "# BATE BOLA"),
        ("14:30", "18:00", "# SOLTA A BRABA"),
        ("18:00", "19:00", "# TARDE DE BENÇÃOS"),
        ("19:00", "21:30", "# AS BRABAS DO MOMENTO"),
        ("21:30", "22:30", "# CAMERA 24H"),
        ("22:30", "04:00", "# BAÚ DA BRABA"),  # cruza meia-noite
    ],
    "terca": [
        ("07:15", "11:00", "# MANHA SERTANEJA"),
        ("11:00", "14:00", "# NA BRABA INFORMA"),
        ("14:30", "18:00", "# SOLTA A BRABA"),
        ("18:00", "19:00", "# TARDE DE BENÇÃOS"),
        ("19:00", "21:30", "# AS BRABAS DO MOMENTO"),
        ("21:30", "22:30", "# CAMERA 24H"),
        ("22:30", "04:00", "# BAÚ DA BRABA"),
    ],
    "quarta": [
        ("07:15", "11:00", "# MANHA SERTANEJA"),
        ("11:00", "14:00", "# NA BRABA INFORMA"),
        ("14:30", "18:00", "# SOLTA A BRABA"),
        ("18:00", "19:00", "# TARDE DE BENÇÃOS"),
        ("19:00", "21:30", "# AS BRABAS DO MOMENTO"),
        ("21:30", "22:30", "# CAMERA 24H"),
        ("22:30", "04:00", "# BAÚ DA BRABA"),
    ],
    "quinta": [
        ("07:15", "11:00", "# MANHA SERTANEJA"),
        ("11:00", "14:00", "# NA BRABA INFORMA"),
        ("14:30", "18:00", "# SOLTA A BRABA"),
        ("18:00", "19:00", "# TARDE DE BENÇÃOS"),
        ("19:00", "21:30", "# AS BRABAS DO MOMENTO"),
        ("21:30", "22:30", "# CAMERA 24H"),
        ("22:30", "04:00", "# BAÚ DA BRABA"),
    ],
    "sexta": [
        ("07:15", "11:00", "# MANHA SERTANEJA"),
        ("11:00", "14:00", "# NA BRABA INFORMA"),
        ("14:30", "18:00", "# SOLTA A BRABA"),
        ("18:00", "19:00", "# TARDE DE BENÇÃOS"),
        ("19:00", "21:30", "# AS BRABAS DO MOMENTO"),
        ("21:30", "22:30", "# CAMERA 24H"),
        ("22:30", "04:00", "# BAÚ DA BRABA"),
    ],
    # Sábado e domingo: cena fixa o dia todo (ajuste se quiser separar melhor)
    "sabado": [
        ("00:00", "23:59", "# CAMERA 24H"),
    ],
    "domingo": [
        ("00:00", "23:59", "# CAMERA 24H"),
    ],
}


# ==========================
# FUNÇÃO: TROCAR CENA NO OBS (SEM AUTENTICAÇÃO)
# ==========================
def trocar_cena(scene_name: str):
    try:
        ws = websocket.WebSocket()
        ws.connect(OBS_URL, timeout=5)

        # 1) Recebe HELLO do OBS
        hello_raw = ws.recv()
        # print("HELLO:", hello_raw)  # debug opcional

        # 2) Envia Identify (sem authentication)
        identify_payload = {
            "op": 1,  # Identify
            "d": {
                "rpcVersion": 1,
                "eventSubscriptions": 0
            }
        }
        ws.send(json.dumps(identify_payload))

        # 3) (Opcional) recebe "Identified"
        _identified = ws.recv()
        # print("IDENTIFIED:", _identified)  # debug opcional

        # 4) Envia requisição pra trocar a cena
        request_payload = {
            "op": 6,
            "d": {
                "requestType": "SetCurrentProgramScene",
                "requestId": "auto-troca-cena",
                "requestData": {
                    "sceneName": scene_name
                }
            }
        }
        ws.send(json.dumps(request_payload))

        # 5) Lê resposta da requisição (só pra log)
        try:
            response_raw = ws.recv()
            response = json.loads(response_raw)
            status = response.get("d", {}).get("requestStatus", {})
            if status.get("result"):
                print(f"    ✅ OBS confirmou troca para: {scene_name}")
            else:
                print(f"    ⚠️ OBS respondeu erro na troca: {response_raw}")
        except Exception:
            # se não vier resposta, segue a vida
            pass

        ws.close()

    except Exception as e:
        agora = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[{agora}] ❌ Erro ao trocar cena para '{scene_name}': {e}")


# ==========================
# FUNÇÃO: DESCOBRIR CENA PELO HORÁRIO
# ==========================
def programa_atual():
    agora = datetime.datetime.now()
    hora = agora.strftime("%H:%M")

    # 0=segunda ... 6=domingo
    indice_dia = agora.weekday()
    dias = ["segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo"]
    dia = dias[indice_dia]

    print(f"[DEBUG] Dia: {dia} | Hora: {hora}")

    if dia not in grade:
        return None

    for inicio, fim, cena in grade[dia]:
        # faixa normal (não atravessa meia-noite)
        if inicio <= fim:
            if inicio <= hora < fim:
                return cena
        else:
            # faixa que atravessa meia-noite (ex: 22:30 -> 04:00)
            if hora >= inicio or hora < fim:
                return cena

    return None


# ==========================
# LOOP PRINCIPAL
# ==========================
if __name__ == "__main__":
    cena_atual = None
    print("▶ Sistema de troca automática de cenas iniciado...")

    while True:
        cena = programa_atual()
        agora_str = datetime.datetime.now().strftime("%H:%M:%S")

        if cena and cena != cena_atual:
            print(f"[{agora_str}] ⏰ Trocando para: {cena}")
            trocar_cena(cena)
            cena_atual = cena
        else:
            print(f"[{agora_str}] Nenhuma troca necessária. Cena atual: {cena_atual}")

        time.sleep(30)  # verifica a cada 30 segundos
