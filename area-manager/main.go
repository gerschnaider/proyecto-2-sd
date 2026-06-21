package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/lib/pq"
)

var db *sql.DB

// Estructura para recibir el JSON de creación
type AreaRequest struct {
	Name   string `json:"name"`
	UserID int    `json:"user_id"`
}

func main() {
	// 1. Conexión a PostgreSQL leyendo variables de entorno
	connStr := fmt.Sprintf("host=%s port=5432 user=%s password=%s dbname=%s sslmode=disable",
		os.Getenv("DB_HOST"), os.Getenv("DB_USER"), os.Getenv("DB_PASSWORD"), os.Getenv("DB_NAME"))
	
	var err error
	db, err = sql.Open("postgres", connStr)
	if err != nil {
		log.Fatalf("Error conectando a la BD: %v", err)
	}
	defer db.Close()

	// 2. Definición de Endpoints (Sintaxis moderna de Go 1.22)
	mux := http.NewServeMux()
	mux.HandleFunc("POST /areas", createAreaHandler)
	mux.HandleFunc("DELETE /areas/{name}", deleteAreaHandler) 

	port := ":8080"
	log.Printf("[*] Servicio de Áreas escuchando en el puerto %s", port)
	log.Fatal(http.ListenAndServe(port, mux))
}

func createAreaHandler(w http.ResponseWriter, r *http.Request) {
	var req AreaRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "JSON inválido", http.StatusBadRequest)
		return
	}

	var newID int
	query := `INSERT INTO areas (name, user_id) VALUES ($1, $2) RETURNING category_id`
	err := db.QueryRow(query, req.Name, req.UserID).Scan(&newID)
	
	if err != nil {
		// Hacemos el Type Assertion una sola vez
		if pqErr, ok := err.(*pq.Error); ok {
			// Evaluamos qué regla de negocio se rompió usando el código de Postgres
			switch pqErr.Code {
			case "23505": // unique_violation
				http.Error(w, "Conflicto: Ya existe un área con ese nombre", http.StatusConflict) // HTTP 409
				return
			case "23503": // foreign_key_violation
				http.Error(w, "Solicitud inválida: El user_id proporcionado no existe", http.StatusBadRequest) // HTTP 400
				return
			}
		}
		
		// Si es cualquier otro error (ej. base de datos caída, error de sintaxis)
		http.Error(w, "Error interno del servidor", http.StatusInternalServerError) // HTTP 500
		log.Printf("Error BD no manejado: %v", err)
		return
	}

	w.WriteHeader(http.StatusCreated) // HTTP 201
	fmt.Fprintf(w, `{"message": "Área creada", "category_id": %d}`, newID)
}

// Estructura para recibir el body del DELETE
type DeleteRequest struct {
	UserID int `json:"user_id"` // User requesting ID
}

func deleteAreaHandler(w http.ResponseWriter, r *http.Request) {
	areaName := r.PathValue("name")

	var req DeleteRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "JSON inválido en el cuerpo de la petición", http.StatusBadRequest)
		return
	}

	// Buscamos en la BD el user_id del dueño 
	var ownerID int
	querySelect := `SELECT user_id FROM areas WHERE name = $1`
	err := db.QueryRow(querySelect, areaName).Scan(&ownerID)
	
	if err == sql.ErrNoRows {
		// El área no existe
		http.Error(w, "Área no encontrada", http.StatusNotFound) // HTTP 404
		return
	} else if err != nil {
		// Error de conexión u otro fallo SQL
		http.Error(w, "Error interno del servidor", http.StatusInternalServerError)
		log.Printf("Error BD: %v", err)
		return
	}

	// 4. Verificamos la autorización comparando IDs
	if ownerID != req.UserID {
		http.Error(w, "Prohibido: No sos el creador de esta área, no podés borrarla.", http.StatusForbidden) // HTTP 403
		return
	}

	// 5. Si pasamos todas las validaciones, ejecutamos el DELETE
	queryDelete := `DELETE FROM areas WHERE name = $1`
	_, err = db.Exec(queryDelete, areaName)
	if err != nil {
		http.Error(w, "Error al intentar borrar el área", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, `{"message": "Área '%s' eliminada exitosamente"}`, areaName)
}