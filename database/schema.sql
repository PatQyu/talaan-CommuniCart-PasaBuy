CREATE DATABASE pasabuy_db;

CREATE TABLE consumers (
	user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    email VARCHAR(100),
    user_password VARCHAR(100),
    date_created DATE
);

CREATE TABLE stores (
	store_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    category_id INT NOT NULL,
    brand_id INT NOT NULL,
    store_name VARCHAR(100),
    latitude
    longitude
    contact_number VARCHAR(100),
    opening_hours VARCHAR(100),
    closing_hours VARCHAR(100),

	 FOREIGN KEY (product_id)
		REFERENCES products(product_id),
    
    FOREIGN KEY (category_id)
        REFERENCES categories(category_id),
        
	FOREIGN KEY (brand_id)
        REFERENCES brands(brand_id),
);

CREATE TABLE products (
	product_id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT NOT NULL,
    brand_id INT NOT NULL,
    product_name VARCHAR (100),
    price VARCHAR(50),
    
    FOREIGN KEY (category_id)
        REFERENCES categories(category_id),
        
	FOREIGN KEY (brand_id)
        REFERENCES brands(brand_id),
);


CREATE TABLE categories (
	category_id INT AUTO_INCREMENT PRIMARY KEY
);

CREATE TABLE brands (
	brand_id INT AUTO_INCREMENT PRIMARY KEY
);
