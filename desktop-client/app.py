import tkinter as tk
from tkinter import ttk, scrolledtext
import requests
import json
import urllib.parse

PORTS = {
    'areaManager': 8080,
    'subscriptions': 8004,
    'publish': 50050,
    'getLoad': 8003,
    'findDescriptor': 8030,
    'last24h': 8005,
    'findPeriod': 8002,
    'deleteNews': 8001
}

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Consorcio de Noticias - Cliente de Escritorio")
        self.geometry("900x700")
        
        # IP config
        frame_top = tk.Frame(self)
        frame_top.pack(fill=tk.X, padx=10, pady=10)
        tk.Label(frame_top, text="IP del Swarm:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        self.ip_entry = tk.Entry(frame_top, font=('Arial', 10))
        self.ip_entry.insert(0, "localhost")
        self.ip_entry.pack(side=tk.LEFT, padx=10)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.create_areas_tab()
        self.create_subs_tab()
        self.create_news_tab()
        self.create_queries_tab()
        
        # Log Output
        tk.Label(self, text="Terminal de Resultados:", font=('Arial', 10, 'bold')).pack(anchor="w", padx=10)
        self.log_area = scrolledtext.ScrolledText(self, height=18, bg="#1e1e1e", fg="#4ade80", font=('Consolas', 10))
        self.log_area.pack(fill=tk.BOTH, padx=10, pady=5)
        self.log_area.insert(tk.END, "Esperando operaciones...\n")
        
    def log(self, text, is_error=False):
        prefix = "[ERROR]" if is_error else "[SUCCESS]"
        if self.log_area.get("1.0", tk.END).strip() == "Esperando operaciones...":
            self.log_area.delete("1.0", tk.END)
        self.log_area.insert(tk.END, f"\n> {prefix} {text}\n")
        self.log_area.see(tk.END)
        
    def api_call(self, port_name, endpoint, method, payload=None):
        ip = self.ip_entry.get()
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
        
        tk.Label(frame, text="Nombre del Área:").grid(row=0, column=0, pady=10, padx=10, sticky="e")
        name_entry = tk.Entry(frame, width=30)
        name_entry.grid(row=0, column=1, pady=10, sticky="w")
        
        tk.Label(frame, text="ID Autor:").grid(row=1, column=0, pady=10, padx=10, sticky="e")
        uid_entry = tk.Entry(frame, width=30)
        uid_entry.insert(0, "1")
        uid_entry.grid(row=1, column=1, pady=10, sticky="w")
        
        def create():
            self.api_call('areaManager', '/areas', 'POST', {"name": name_entry.get(), "user_id": int(uid_entry.get() or 0)})
            
        def delete():
            name = urllib.parse.quote(name_entry.get())
            self.api_call('areaManager', f'/areas/{name}', 'DELETE', {"user_id": int(uid_entry.get() or 0)})
            
        tk.Button(frame, text="Crear Área", command=create, width=15, bg="#3b82f6", fg="white").grid(row=2, column=0, pady=20, padx=10)
        tk.Button(frame, text="Eliminar Área", command=delete, width=15, bg="#ef4444", fg="white").grid(row=2, column=1, pady=20, sticky="w")

    def create_subs_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=" Suscripciones ")
        
        tk.Label(frame, text="ID Categoría:").grid(row=0, column=0, pady=10, padx=10, sticky="e")
        cat_entry = tk.Entry(frame, width=30)
        cat_entry.grid(row=0, column=1, pady=10, sticky="w")
        
        tk.Label(frame, text="ID Usuario:").grid(row=1, column=0, pady=10, padx=10, sticky="e")
        uid_entry = tk.Entry(frame, width=30)
        uid_entry.insert(0, "1")
        uid_entry.grid(row=1, column=1, pady=10, sticky="w")
        
        def sub():
            self.api_call('subscriptions', '/suscribir', 'POST', {"category_id": int(cat_entry.get() or 0), "user_id": int(uid_entry.get() or 0)})
            
        def unsub():
            self.api_call('subscriptions', '/desuscribir', 'DELETE', {"category_id": int(cat_entry.get() or 0), "user_id": int(uid_entry.get() or 0)})
            
        tk.Button(frame, text="Suscribir", command=sub, width=15, bg="#3b82f6", fg="white").grid(row=2, column=0, pady=20, padx=10)
        tk.Button(frame, text="Desuscribir", command=unsub, width=15, bg="#ef4444", fg="white").grid(row=2, column=1, pady=20, sticky="w")

    def create_news_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=" Publicar Noticia ")
        
        tk.Label(frame, text="Título:").grid(row=0, column=0, pady=5, padx=10, sticky="e")
        title_entry = tk.Entry(frame, width=50)
        title_entry.grid(row=0, column=1, pady=5, sticky="w")
        
        tk.Label(frame, text="ID Categoría:").grid(row=1, column=0, pady=5, padx=10, sticky="e")
        cat_entry = tk.Entry(frame, width=50)
        cat_entry.grid(row=1, column=1, pady=5, sticky="w")
        
        tk.Label(frame, text="ID Autor:").grid(row=2, column=0, pady=5, padx=10, sticky="e")
        uid_entry = tk.Entry(frame, width=50)
        uid_entry.insert(0, "1")
        uid_entry.grid(row=2, column=1, pady=5, sticky="w")
        
        tk.Label(frame, text="Contenido:").grid(row=3, column=0, pady=5, padx=10, sticky="ne")
        txt = tk.Text(frame, height=6, width=50)
        txt.grid(row=3, column=1, pady=5, sticky="w")
        
        def pub():
            payload = {
                "titulo": title_entry.get(),
                "id_categoria": int(cat_entry.get() or 0),
                "id_autor": int(uid_entry.get() or 0),
                "texto": txt.get("1.0", tk.END).strip()
            }
            self.api_call('publish', '/api/noticias', 'POST', payload)
            
        tk.Button(frame, text="Publicar Noticia", command=pub, width=20, bg="#10b981", fg="white").grid(row=4, column=1, pady=15, sticky="w")

    def create_queries_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=" Consultas Generales ")
        
        # Load
        tk.Button(frame, text="Ver Carga por Área", command=lambda: self.api_call('getLoad', '/api/news-load', 'GET'), width=25, bg="#3b82f6", fg="white").grid(row=0, column=0, pady=10, padx=10, sticky="w")
        
        # Descriptor
        desc_entry = tk.Entry(frame, width=25)
        desc_entry.grid(row=1, column=1, pady=10, padx=5, sticky="w")
        tk.Button(frame, text="Buscar por Descriptor ->", command=lambda: self.api_call('findDescriptor', f'/api/news-descriptor?descriptor={urllib.parse.quote(desc_entry.get())}', 'GET'), width=25, bg="#3b82f6", fg="white").grid(row=1, column=0, pady=10, padx=10, sticky="w")
        
        # 24h
        uid_entry = tk.Entry(frame, width=25)
        uid_entry.insert(0, "1")
        uid_entry.grid(row=2, column=1, pady=10, padx=5, sticky="w")
        tk.Button(frame, text="Últimas 24h (UserID) ->", command=lambda: self.api_call('last24h', f'/api/news-last-24h?user_id={uid_entry.get()}', 'GET'), width=25, bg="#3b82f6", fg="white").grid(row=2, column=0, pady=10, padx=10, sticky="w")
        
        # Period
        f_period = tk.Frame(frame)
        f_period.grid(row=3, column=1, pady=10, sticky="w")
        tk.Label(f_period, text="Inicio (YYYY-MM-DD):").pack(side=tk.LEFT)
        start_entry = tk.Entry(f_period, width=12)
        start_entry.pack(side=tk.LEFT, padx=5)
        tk.Label(f_period, text="Fin:").pack(side=tk.LEFT)
        end_entry = tk.Entry(f_period, width=12)
        end_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(frame, text="Buscar Por Período ->", command=lambda: self.api_call('findPeriod', f'/api/news-period?fecha_inicio={start_entry.get()}&fecha_fin={end_entry.get()}', 'GET'), width=25, bg="#3b82f6", fg="white").grid(row=3, column=0, pady=10, padx=10, sticky="w")

if __name__ == "__main__":
    app = App()
    app.mainloop()
