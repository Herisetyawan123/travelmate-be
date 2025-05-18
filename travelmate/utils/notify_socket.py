import requests

def notify(event):
    try:
        response = requests.post("http://localhost:8002/trigger", json={
            "trip_id": event,
            "event": event,
            
        })
        print(f"[+] Notifikasi websocket: {response.status_code} {response.text}")
    except Exception as e:
        print(f"[!] Gagal kirim notifikasi websocket: {e}")