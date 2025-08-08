USE univpartner_db;
SELECT user, host FROM mysql.user;
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;

CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    nickname VARCHAR(50),
    loginID VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
     role ENUM('student', 'editor', 'admin') DEFAULT 'student',
    univ VARCHAR(50),
    college VARCHAR(20),
    major VARCHAR(50)
);

DROP TABLE users;

CREATE TABLE departments (
    dept_id INT PRIMARY KEY AUTO_INCREMENT,
    major VARCHAR(100) NOT NULL,         -- 예: 컴퓨터공학과
    college VARCHAR(100) NOT NULL,      -- 예: 공과대학
    univ VARCHAR(100) NOT NULL,         -- 예: 서울대학교
    campus VARCHAR(100),        -- 예: 관악캠퍼스
    updated_at date
);

CREATE TABLE BenefitCategories (
    category_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) UNIQUE
);

CREATE TABLE BenefitTypes (
    type_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) UNIQUE
);

CREATE TABLE Partners (
    partner_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    address TEXT,
    scope VARCHAR(100),
    image_url VARCHAR(255),
    latitude DOUBLE,
    longitude DOUBLE,
    content TEXT,
    start_date DATE,
    end_date DATE,
    category_id INT,
    created_by_user_id INT,
    FOREIGN KEY (category_id) REFERENCES BenefitCategories(category_id),
    FOREIGN KEY (created_by_user_id) REFERENCES users(user_id)
    -- CHECK 제약은 일부 DBMS (ex: MySQL)에서는 ENUM 검사로 대체 필요
);
-- 연결테이블 (Many-to-Many)
CREATE TABLE PartnerBenefitTypes (
    partner_id INT,
    type_id INT,
    PRIMARY KEY (partner_id, type_id),
    FOREIGN KEY (partner_id) REFERENCES Partners(partner_id),
    FOREIGN KEY (type_id) REFERENCES BenefitTypes(type_id)
);

CREATE TABLE Editors (
	    editor_id INT PRIMARY KEY AUTO_INCREMENT,
	    submitted_by INT NOT NULL UNIQUE,
	    name VARCHAR(50) NOT NULL,
	    birthdate DATE NOT NULL,
	    sex ENUM('male', 'female') NOT NULL,
	    univ VARCHAR(50) NOT NULL,
	    college VARCHAR(50) NOT NULL,
	    major VARCHAR(50) NOT NULL,
	    aff_council ENUM('univ', 'college', 'major') DEFAULT 'univ'  NOT NULL,
	    student_card_url VARCHAR(255),
	    student_list_doc_url VARCHAR(255),
	    status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
	    submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
	    FOREIGN KEY (submitted_by) REFERENCES Users(user_id)
	);
    
CREATE TABLE Bookmarks (
    folder_name VARCHAR(50),
    user_id INT,
    partner_id INT,
    PRIMARY KEY (folder_name, user_id, partner_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (partner_id) REFERENCES Partners(partner_id)
);