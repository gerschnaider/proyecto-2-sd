package main

import (
	"context"
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

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

	maxRetries := 3
	for attempt := 1; attempt <= maxRetries; attempt++ {
		err := executeDeleteTransaction(r.Context(), areaName, req.UserID)
		if err == nil {
			// Éxito
			w.WriteHeader(http.StatusOK)
			fmt.Fprintf(w, `{"message": "Área '%s' eliminada exitosamente"}`, areaName)
			return
		}

		// Si es un error de PostgreSQL, verificamos si es por concurrencia
		if pqErr, ok := err.(*pq.Error); ok {
			// 40001 = serialization_failure, 40P01 = deadlock_detected
			if pqErr.Code == "40001" || pqErr.Code == "40P01" {
				log.Printf("Conflicto de concurrencia detectado (intento %d/%d). Reintentando...", attempt, maxRetries)
				time.Sleep(time.Millisecond * time.Duration(100*attempt)) // Backoff simple
				continue
			}
		}

		// Si es un error de negocio que nosotros definimos (ej. no encontrado, prohibido)
		if err.Error() == "not_found" {
			http.Error(w, "Área no encontrada", http.StatusNotFound)
			return
		}
		if err.Error() == "forbidden" {
			http.Error(w, "Prohibido: No sos el creador de esta área, no podés borrarla.", http.StatusForbidden)
			return
		}

		// Otros errores
		http.Error(w, "Error interno del servidor", http.StatusInternalServerError)
		log.Printf("Error inesperado en BD: %v", err)
		return
	}

	// Si se superaron los reintentos
	http.Error(w, "Error al procesar la operación por alta concurrencia", http.StatusConflict)
}

func executeDeleteTransaction(ctx context.Context, areaName string, userID int) error {
	tx, err := db.BeginTx(ctx, &sql.TxOptions{
		Isolation: sql.LevelSerializable,
	})
	if err != nil {
		return fmt.Errorf("error db.BeginTx: %w", err)
	}
	defer tx.Rollback() // Seguro de ejecutar, no hace nada si ya se hizo commit

	var ownerID, categoryID int
	querySelect := `SELECT category_id, user_id FROM areas WHERE name = $1 AND is_deleted = false FOR UPDATE`
	err = tx.QueryRowContext(ctx, querySelect, areaName).Scan(&categoryID, &ownerID)
	
	if err == sql.ErrNoRows {
		return fmt.Errorf("not_found")
	} else if err != nil {
		return err
	}

	if ownerID != userID {
		return fmt.Errorf("forbidden")
	}

	queryUpdateArea := `UPDATE areas SET is_deleted = true WHERE category_id = $1`
	_, err = tx.ExecContext(ctx, queryUpdateArea, categoryID)
	if err != nil {
		return err
	}

	queryUpdateNews := `UPDATE news SET is_deleted = true WHERE category_id = $1`
	_, err = tx.ExecContext(ctx, queryUpdateNews, categoryID)
	if err != nil {
		return err
	}

	return tx.Commit()
}