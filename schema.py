from __future__ import annotations

import sqlite3

SCHEMA_VERSION = 1


def apply_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS clients (
            id TEXT PRIMARY KEY,
            nome TEXT NOT NULL,
            telefone TEXT,
            email TEXT,
            nif TEXT,
            morada TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS products (
            id TEXT PRIMARY KEY,
            sku TEXT NOT NULL UNIQUE,
            nome TEXT NOT NULL,
            tipo_producao TEXT NOT NULL CHECK (tipo_producao IN ('print_on_demand','stock_fisico','misto')),
            preco REAL NOT NULL CHECK (preco >= 0),
            custo REAL NOT NULL DEFAULT 0 CHECK (custo >= 0),
            stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
            image_file TEXT,
            design_file TEXT,
            ativo INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS orders (
            id TEXT PRIMARY KEY,
            numero TEXT NOT NULL UNIQUE,
            client_id TEXT NOT NULL,
            estado_comercial TEXT NOT NULL CHECK (estado_comercial IN ('rascunho','aguarda pagamento','paga','cancelada')),
            estado_producao TEXT NOT NULL CHECK (estado_producao IN ('pendente','em produção','produzida')),
            estado_envio TEXT NOT NULL CHECK (estado_envio IN ('por enviar','enviada','entregue')),
            pago INTEGER NOT NULL DEFAULT 0,
            tracking TEXT,
            prazo_envio TEXT,
            notas TEXT,
            subtotal REAL NOT NULL DEFAULT 0 CHECK (subtotal >= 0),
            portes REAL NOT NULL DEFAULT 0 CHECK (portes >= 0),
            total REAL NOT NULL DEFAULT 0 CHECK (total >= 0),
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (client_id) REFERENCES clients(id)
        );

        CREATE TABLE IF NOT EXISTS order_items (
            id TEXT PRIMARY KEY,
            order_id TEXT NOT NULL,
            product_id TEXT NOT NULL,
            quantidade INTEGER NOT NULL CHECK (quantidade > 0),
            preco_unit REAL NOT NULL CHECK (preco_unit >= 0),
            tamanho TEXT,
            personalizacao TEXT,
            stock_deducted INTEGER NOT NULL DEFAULT 0,
            stock_returned INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(id)
        );

        CREATE TABLE IF NOT EXISTS logs (
            id TEXT PRIMARY KEY,
            user TEXT,
            action TEXT NOT NULL,
            details TEXT,
            created_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_orders_states ON orders(estado_comercial, estado_producao, estado_envio);
        CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
        CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku);
        CREATE INDEX IF NOT EXISTS idx_clients_nome ON clients(nome);
        PRAGMA user_version = 1;
        """
    )
