CREATE DATABASE pasabuy_db;
USE pasabuy_db;

CREATE TABLE users (
	user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    user_password VARCHAR(255),
    date_created DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE categories (
	category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR (100) NOT NULL
);

CREATE TABLE brands (
	brand_id INT AUTO_INCREMENT PRIMARY KEY,
    brand_name VARCHAR(100) NOT NULL
);

CREATE TABLE products (
	product_id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT NOT NULL,
    brand_id INT NOT NULL,
    general_name VARCHAR (100) NOT NULL,
    product_name VARCHAR (100) NOT NULL,
    
    FOREIGN KEY (category_id)
        REFERENCES categories(category_id),
        
	FOREIGN KEY (brand_id)
        REFERENCES brands(brand_id)
);

CREATE TABLE stores (
	store_id INT AUTO_INCREMENT PRIMARY KEY,
    store_name VARCHAR(100) NOT NULL,
    latitude DECIMAL(10,7),
    longitude DECIMAL(10,7),
    contact_number VARCHAR(100),
    opening_time VARCHAR(100),
    closing_time VARCHAR(100)
);

CREATE TABLE store_products (
    store_product_id INT AUTO_INCREMENT PRIMARY KEY,
    store_id INT NOT NULL,
    product_id INT NOT NULL,
    stock INT,
    is_available BOOLEAN,
    current_price DECIMAL(10,2),

    FOREIGN KEY (store_id)
        REFERENCES stores(store_id),

    FOREIGN KEY (product_id)
        REFERENCES products(product_id)
);

CREATE TABLE userinputs (
	input_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    elderly_count INT,
    adult_count INT,
    teen_count INT,
    children_count INT,
    budget DECIMAL(10,2),
    ration_days INT,
    request_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id)
		REFERENCES users(user_id)
);

CREATE TABLE grocery_list (
    grocery_list_id INT AUTO_INCREMENT PRIMARY KEY,
    input_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2),
    subtotal DECIMAL(10,2),

    FOREIGN KEY (input_id)
        REFERENCES userinputs(input_id),

    FOREIGN KEY (product_id)
        REFERENCES products(product_id)
);
