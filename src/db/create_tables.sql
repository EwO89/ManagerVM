
CREATE TABLE IF NOT EXISTS VirtualMachine (
    vm_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    ram INTEGER NOT NULL,
    cpu INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

