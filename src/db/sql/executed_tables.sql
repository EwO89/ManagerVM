
CREATE TABLE IF NOT EXISTS virtual_machine (
    vm_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    ram INTEGER NOT NULL,
    cpu INTEGER NOT NULL,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS vm_disk (
    disk_id SERIAL PRIMARY KEY,
    vm_id INTEGER NOT NULL,
    disk_size INTEGER NOT NULL,
    FOREIGN KEY (vm_id) REFERENCES virtual_machine(vm_id)
);


CREATE TABLE IF NOT EXISTS ws_connection_history (
    id SERIAL PRIMARY KEY,
    vm_id INTEGER NOT NULL,
    connected_at TIMESTAMP NOT NULL,
    disconnected_at TIMESTAMP,
    FOREIGN KEY (vm_id) REFERENCES virtual_machine(vm_id)
);
