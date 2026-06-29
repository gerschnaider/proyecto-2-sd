import tkinter as tk
from tkinter import ttk, scrolledtext
import requests
import json
import urllib.parse
import threading
import websocket

PORTS = {
    'areaManager': 8080,
    'subscriptions': 8004,
    'publish': 50050,
    'getLoad': 8003,
    'findDescriptor': 8030,
    'last24h': 8005,
    'findPeriod': 8002,
    'deleteNews': 8001,
    'sendNews': 8765
}

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Consorcio de Noticias - Cliente de Escritorio")
        self.geometry("1200x750")
        
        # State variables for WebSocket
        self.ws = None
        self.ws_thread = None
        self.ws_connected = False

        # IP config
        frame_top = tk.Frame(self)
        frame_top.pack(fill=tk.X, padx=10, pady=10)
        tk.Label(frame_top, text="IP del Swarm:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        self.ip_entry = tk.Entry(frame_top, font=('Arial', 10))
        self.ip_entry.insert(0, "localhost")
        self.ip_entry.pack(side=tk.LEFT, padx=10)
        
        # Center container (holds left tabs and right real-time panel)
        frame_center = tk.Frame(self)
        frame_center.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Notebook for tabs (LEFT SIDE)
        self.notebook = ttk.Notebook(frame_center)
        self.notebook.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.create_areas_tab()
        self.create_subs_tab()
        self.create_news_tab()
        self.create_queries_tab()
        
        # Real-time WebSocket Panel (RIGHT SIDE)
        self.create_realtime_panel(frame_center)

        # Log Output (BOTTOM SIDE)
        tk.Label(self, text="Terminal de Resultados:", font=('Arial', 10, 'bold')).pack(anchor="w", padx=10, pady=(5, 0))
        self.log_area = scrolledtext.ScrolledText(self, height=14, bg="#1e1e1e", fg="#4ade80", font=('Consolas', 10))
        self.log_area.pack(fill=tk.BOTH, padx=10, pady=(0, 10))
        self.log_area.insert(tk.END, "Esperando operaciones...\n")
        
    def log(self, text, is_error=False):
        prefix = "[ERROR]" if is_error else "[SUCCESS]"
        if self.log_area.get("1.0", tk.END).strip() == "Esperando operaciones...":
            self.log_area.delete("1.0", tk.END)
        self.log_area.insert(tk.END, f"\n> {prefix} {text}\n")
        self.log_area.see(tk.END)

    def log_ws(self, text, is_incoming=False):
        prefix = "📥 [RECIBIDO]" if is_incoming else "ℹ️ [INFO]"
        self.ws_log_area.insert(tk.END, f"{prefix} {text}\n")
        self.ws_log_area.see(tk.END)
        
    def safe_get_int(self, entry, field_name):
        val = entry.get().strip()
        if not val:
            self.log(f"Error: El campo '{field_name}' está vacío.", True)
            raise ValueError(f"Campo vacío: {field_name}")
        try:
            return int(val)
        except ValueError:
            self.log(f"Error: El campo '{field_name}' debe ser un número entero válido (recibido: '{val}').", True)
            raise

    def api_call(self, port_name, endpoint, method, payload=None):
        ip = self.ip_entry.get().strip()
        port = PORTS.get(port_name)
        url = f"http://{ip}:{port}{endpoint}"
        
        try:
            if method == "GET":
                r = requests.get(url, timeout=5)
            elif method == "POST":
                r = requests.post(url, json=payload, timeout=5)
            elif method == "DELETE":
                r = requests.delete(url, json=payload, timeout=5)
                
            try:
                data = r.json()
                fmt = json.dumps(data, indent=2, ensure_ascii=False)
            except:
                fmt = r.text
                
            if r.status_code >= 400:
                self.log(f"{method} {url} - Falló (Status {r.status_code})\n{fmt}", True)
            else:
                self.log(f"{method} {url}\n{fmt}")
        except Exception as e:
            self.log(f"{method} {url} - Error de conexión: {str(e)}", True)

    def create_areas_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=" Áreas Temáticas ")
        
        tk.Label(frame, text="Nombre del Área:").grid(row=0, column=0, pady=(20, 10), padx=(20, 10), sticky="e")
        name_entry = tk.Entry(frame, width=35)
        name_entry.grid(row=0, column=1, pady=(20, 10), padx=(0, 20), sticky="w")
        
        tk.Label(frame, text="ID Autor:").grid(row=1, column=0, pady=10, padx=(20, 10), sticky="e")
        uid_entry = tk.Entry(frame, width=35)
        uid_entry.insert(0, "1")
        uid_entry.grid(row=1, column=1, pady=10, padx=(0, 20), sticky="w")
        
        def create():
            try:
                user_id = self.safe_get_int(uid_entry, "ID Autor")
                self.api_call('areaManager', '/areas', 'POST', {"name": name_entry.get(), "user_id": user_id})
            except ValueError:
                pass
            
        def delete():
            try:
                user_id = self.safe_get_int(uid_entry, "ID Autor")
                name = urllib.parse.quote(name_entry.get())
                self.api_call('areaManager', f'/areas/{name}', 'DELETE', {"user_id": user_id})
            except ValueError:
                pass
            
        btn_frame = tk.Frame(frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        tk.Button(btn_frame, text="Crear Área", command=create, width=15, bg="#3b82f6", fg="white").pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Eliminar Área", command=delete, width=15, bg="#ef4444", fg="white").pack(side=tk.LEFT, padx=10)

    def create_subs_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=" Suscripciones ")
        
        tk.Label(frame, text="ID Categoría:").grid(row=0, column=0, pady=(20, 10), padx=(20, 10), sticky="e")
        cat_entry = tk.Entry(frame, width=35)
        cat_entry.grid(row=0, column=1, pady=(20, 10), padx=(0, 20), sticky="w")
        
        tk.Label(frame, text="ID Usuario:").grid(row=1, column=0, pady=10, padx=(20, 10), sticky="e")
        uid_entry = tk.Entry(frame, width=35)
        uid_entry.insert(0, "1")
        uid_entry.grid(row=1, column=1, pady=10, padx=(0, 20), sticky="w")
        
        def sub():
            try:
                cat_id = self.safe_get_int(cat_entry, "ID Categoría")
                user_id = self.safe_get_int(uid_entry, "ID Usuario")
                self.api_call('subscriptions', '/suscribir', 'POST', {"category_id": cat_id, "user_id": user_id})
            except ValueError:
                pass
            
        def unsub():
            try:
                cat_id = self.safe_get_int(cat_entry, "ID Categoría")
                user_id = self.safe_get_int(uid_entry, "ID Usuario")
                self.api_call('subscriptions', '/desuscribir', 'DELETE', {"category_id": cat_id, "user_id": user_id})
            except ValueError:
                pass
            
        btn_frame = tk.Frame(frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        tk.Button(btn_frame, text="Suscribir", command=sub, width=15, bg="#3b82f6", fg="white").pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Desuscribir", command=unsub, width=15, bg="#ef4444", fg="white").pack(side=tk.LEFT, padx=10)

    def create_news_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=" Publicar Noticia ")
        
        tk.Label(frame, text="Título:").grid(row=0, column=0, pady=(20, 10), padx=(20, 10), sticky="e")
        title_entry = tk.Entry(frame, width=50)
        title_entry.grid(row=0, column=1, pady=(20, 10), padx=(0, 20), sticky="w")
        
        tk.Label(frame, text="ID Categoría:").grid(row=1, column=0, pady=10, padx=(20, 10), sticky="e")
        cat_entry = tk.Entry(frame, width=50)
        cat_entry.grid(row=1, column=1, pady=10, padx=(0, 20), sticky="w")
        
        tk.Label(frame, text="ID Autor:").grid(row=2, column=0, pady=10, padx=(20, 10), sticky="e")
        uid_entry = tk.Entry(frame, width=50)
        uid_entry.insert(0, "1")
        uid_entry.grid(row=2, column=1, pady=10, padx=(0, 20), sticky="w")
        
        tk.Label(frame, text="Contenido:").grid(row=3, column=0, pady=10, padx=(20, 10), sticky="ne")
        txt = tk.Text(frame, height=6, width=50)
        txt.grid(row=3, column=1, pady=10, padx=(0, 20), sticky="w")
        
        def pub():
            try:
                cat_id = self.safe_get_int(cat_entry, "ID Categoría")
                user_id = self.safe_get_int(uid_entry, "ID Autor")
                payload = {
                    "titulo": title_entry.get().strip(),
                    "id_categoria": cat_id,
                    "id_autor": user_id,
                    "texto": txt.get("1.0", tk.END).strip()
                }
                self.api_call('publish', '/api/noticias', 'POST', payload)
            except ValueError:
                pass
             
        tk.Button(frame, text="Publicar Noticia", command=pub, width=20, bg="#10b981", fg="white").grid(row=4, column=0, columnspan=2, pady=20)

    def create_queries_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=" Consultas Generales ")
        
        # Load
        tk.Button(frame, text="Ver Carga por Área", command=lambda: self.api_call('getLoad', '/api/news-load', 'GET'), width=25, bg="#3b82f6", fg="white").grid(row=0, column=0, pady=(20, 10), padx=(20, 10), sticky="w")
        
        # Descriptor
        desc_entry = tk.Entry(frame, width=35)
        desc_entry.grid(row=1, column=1, pady=10, padx=(0, 20), sticky="w")
        tk.Button(frame, text="Buscar por Descriptor ->", command=lambda: self.api_call('findDescriptor', f'/api/news-descriptor?descriptor={urllib.parse.quote(desc_entry.get().strip())}', 'GET'), width=25, bg="#3b82f6", fg="white").grid(row=1, column=0, pady=10, padx=(20, 10), sticky="w")
        
        # 24h
        uid_entry = tk.Entry(frame, width=35)
        uid_entry.insert(0, "1")
        uid_entry.grid(row=2, column=1, pady=10, padx=(0, 20), sticky="w")
        
        def search_24h():
            try:
                user_id = self.safe_get_int(uid_entry, "UserID")
                self.api_call('last24h', f'/api/news-last-24h?user_id={user_id}', 'GET')
            except ValueError:
                pass

        tk.Button(frame, text="Últimas 24h (UserID) ->", command=search_24h, width=25, bg="#3b82f6", fg="white").grid(row=2, column=0, pady=10, padx=(20, 10), sticky="w")
        
        # Period
        f_period = tk.Frame(frame)
        f_period.grid(row=3, column=1, pady=10, padx=(0, 20), sticky="w")
        tk.Label(f_period, text="Inicio (YYYY-MM-DD):").pack(side=tk.LEFT)
        start_entry = tk.Entry(f_period, width=12)
        start_entry.pack(side=tk.LEFT, padx=5)
        tk.Label(f_period, text="Fin:").pack(side=tk.LEFT, padx=(10, 0))
        end_entry = tk.Entry(f_period, width=12)
        end_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(frame, text="Buscar Por Período ->", command=lambda: self.api_call('findPeriod', f'/api/news-period?fecha_inicio={start_entry.get().strip()}&fecha_fin={end_entry.get().strip()}', 'GET'), width=25, bg="#3b82f6", fg="white").grid(row=3, column=0, pady=10, padx=(20, 10), sticky="w")

        # Delete News Endpoint Integration
        tk.Label(frame, text="ID Noticia a Borrar:").grid(row=4, column=0, pady=(20,10), padx=(20,10), sticky="e")
        del_news_entry = tk.Entry(frame, width=35)
        del_news_entry.grid(row=4, column=1, pady=(20,10), padx=(0,20), sticky="w")
        
        def delete_news_action():
            try:
                news_id = self.safe_get_int(del_news_entry, "ID Noticia a Borrar")
                # El microservicio delete-news espera DELETE a /api/noticias/{id}
                self.api_call('deleteNews', f'/api/noticias/{news_id}', 'DELETE')
            except ValueError:
                pass

        tk.Button(frame, text="Borrar Noticia (deleteNews)", command=delete_news_action, width=25, bg="#ef4444", fg="white").grid(row=5, column=0, columnspan=2, pady=10, padx=(20,10), sticky="w")

    def create_realtime_panel(self, parent):
        frame = tk.LabelFrame(parent, text=" Noticias en Vivo (WS) ", font=('Arial', 10, 'bold'), padx=10, pady=10)
        frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, width=340, padx=(10, 0))
        
        # Credentials Form
        f_fields = tk.Frame(frame)
        f_fields.pack(fill=tk.X, pady=(5, 10))
        
        tk.Label(f_fields, text="User ID:").grid(row=0, column=0, sticky="e", pady=2)
        self.ws_uid_entry = tk.Entry(f_fields, width=10)
        self.ws_uid_entry.insert(0, "1")
        self.ws_uid_entry.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        tk.Label(f_fields, text="Cat ID:").grid(row=1, column=0, sticky="e", pady=2)
        self.ws_cat_entry = tk.Entry(f_fields, width=10)
        self.ws_cat_entry.insert(0, "1")
        self.ws_cat_entry.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        # Toggle Button
        self.ws_btn = tk.Button(f_fields, text="Conectar WS", command=self.toggle_ws, bg="#10b981", fg="white", font=('Arial', 9, 'bold'), width=15)
        self.ws_btn.grid(row=0, column=2, rowspan=2, padx=15, pady=2, sticky="ns")
        
        # Log Output for WS
        tk.Label(frame, text="Feed de Noticias Recibidas:", font=('Arial', 9, 'bold')).pack(anchor="w", pady=(5, 2))
        self.ws_log_area = scrolledtext.ScrolledText(frame, height=22, bg="#111827", fg="#f59e0b", font=('Consolas', 9))
        self.ws_log_area.pack(fill=tk.BOTH, expand=True)
        self.ws_log_area.insert(tk.END, "Desconectado. Ingresa credenciales y haz clic en Conectar WS...\n")

    def toggle_ws(self):
        if self.ws_connected:
            self.disconnect_ws()
        else:
            self.connect_ws()

    def connect_ws(self):
        try:
            user_id = self.safe_get_int(self.ws_uid_entry, "WS User ID")
            category_id = self.safe_get_int(self.ws_cat_entry, "WS Cat ID")
        except ValueError:
            return
            
        ip = self.ip_entry.get().strip()
        port = PORTS.get('sendNews')
        
        self.ws_btn.config(text="Conectando...", state=tk.DISABLED, bg="#f59e0b")
        self.ws_log_area.delete("1.0", tk.END)
        self.log_ws(f"Conectando a ws://{ip}:{port}...")

        # Connection logic inside thread to prevent freezing main UI
        def ws_run():
            websocket.enableTrace(False)
            url = f"ws://{ip}:{port}"
            self.ws = websocket.WebSocketApp(
                url,
                on_open=lambda ws: self.ws_on_open(ws, user_id, category_id),
                on_message=self.ws_on_message,
                on_error=self.ws_on_error,
                on_close=self.ws_on_close
            )
            self.ws.run_forever()

        self.ws_thread = threading.Thread(target=ws_run)
        self.ws_thread.daemon = True
        self.ws_thread.start()

    def disconnect_ws(self):
        if self.ws:
            self.log_ws("Desconectando WebSocket...")
            self.ws.close()

    def ws_on_open(self, ws, user_id, category_id):
        self.ws_connected = True
        self.after(0, lambda: self.ws_btn.config(text="Desconectar", state=tk.NORMAL, bg="#ef4444"))
        self.after(0, lambda: self.log_ws(f"Conexión abierta. Enviando autenticación (User: {user_id}, Cat: {category_id})..."))
        
        # Enviar el JSON de autenticación requerido por el microservicio send-news
        auth_payload = {
            "user_id": user_id,
            "category_id": category_id
        }
        ws.send(json.dumps(auth_payload))

    def ws_on_message(self, ws, message):
        try:
            data = json.loads(message)
            formatted = json.dumps(data, indent=2, ensure_ascii=False)
            self.after(0, lambda: self.log_ws(formatted, is_incoming=True))
        except Exception as e:
            self.after(0, lambda: self.log_ws(message, is_incoming=True))

    def ws_on_error(self, ws, error):
        self.after(0, lambda: self.log_ws(f"Error: {str(error)}"))

    def ws_on_close(self, ws, close_status_code, close_msg):
        self.ws_connected = False
        self.ws = None
        self.after(0, lambda: self.ws_btn.config(text="Conectar WS", state=tk.NORMAL, bg="#10b981"))
        self.after(0, lambda: self.log_ws("Conexión WebSocket cerrada."))

if __name__ == "__main__":
    app = App()
    app.mainloop()
