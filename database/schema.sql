CREATE DATABASE IF NOT EXISTS pasabuy_db;
USE pasabuy_db;

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    user_password VARCHAR(255) NOT NULL,
    date_created DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE brands (
    brand_id INT AUTO_INCREMENT PRIMARY KEY,
    brand_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT NOT NULL,
    brand_id INT,                     
    product_name VARCHAR(150) NOT NULL,
    unit VARCHAR(20) NOT NULL,           
    unit_per_qty DECIMAL(10,2) NOT NULL, 
    price DECIMAL(10,2) NOT NULL,        

    FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE CASCADE,
    FOREIGN KEY (brand_id) REFERENCES brands(brand_id) ON DELETE SET NULL
);

CREATE TABLE userinputs (
    input_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    elderly_count INT DEFAULT 0,
    adult_count INT DEFAULT 0,
    teen_count INT DEFAULT 0,
    children_count INT DEFAULT 0,
    budget DECIMAL(10,2) NOT NULL,
    ration_days INT NOT NULL,
    date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE grocery_list (
    list_id INT AUTO_INCREMENT PRIMARY KEY,
    input_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity DECIMAL(10,2) NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (input_id) REFERENCES userinputs(input_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);