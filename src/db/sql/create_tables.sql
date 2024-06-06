CREATE TABLE IF NOT EXISTS virtual_machine (
    vm_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    ram INTEGER NOT NULL,
    cpu INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ws_connection_history (
    id SERIAL PRIMARY KEY,
    vm_id VARCHAR(100) NOT NULL,
    connected_at TIMESTAMP NOT NULL,
    disconnected_at TIMESTAMP
);