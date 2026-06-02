myevn can ignore

Step
1) create data base
2) change password



For Create Table in Database

-- 1. 建立並切換至資料庫 (Schema)
CREATE SCHEMA IF NOT EXISTS `shida_mooc` DEFAULT CHARACTER SET utf8mb4;
USE `shida_mooc`;

-- 2. 建立使用者總表 (Users)
CREATE TABLE IF NOT EXISTS `Users` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `email` VARCHAR(255) UNIQUE NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  `name` VARCHAR(100) NOT NULL,
  `role_type` ENUM('STUDENT', 'EXTERNAL', 'ADMIN') NOT NULL DEFAULT 'EXTERNAL',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE = InnoDB;

-- 3. 建立學生詳細資料表 (Student_Details)
-- 此為 1:1 關係，僅在 role_type 為 STUDENT 時使用
CREATE TABLE IF NOT EXISTS `Student_Details` (
  `user_id` INT NOT NULL,
  `student_id` VARCHAR(50) UNIQUE NOT NULL,
  `department` VARCHAR(100) NOT NULL,
  PRIMARY KEY (`user_id`),
  CONSTRAINT `fk_student_user`
    FOREIGN KEY (`user_id`)
    REFERENCES `Users` (`id`)
    ON DELETE CASCADE
) ENGINE = InnoDB;

-- 4. 建立教師資訊表 (Instructors)
-- 僅作為課程顯示資訊，不具備登入功能
CREATE TABLE IF NOT EXISTS `Instructors` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(100) NOT NULL,
  `title` VARCHAR(100) NOT NULL,
  `department` VARCHAR(100) NOT NULL,
  `bio` TEXT NULL,
  PRIMARY KEY (`id`)
) ENGINE = InnoDB;

-- 5. 建立課程表 (Courses)
CREATE TABLE IF NOT EXISTS `Courses` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `instructor_id` INT NOT NULL,
  `title` VARCHAR(255) NOT NULL,
  `description` TEXT NULL,
  `price` DECIMAL(10, 2) NOT NULL,

  PRIMARY KEY (`id`),
  CONSTRAINT `fk_course_instructor`
    FOREIGN KEY (`instructor_id`)
    REFERENCES `Instructors` (`id`)
    ON DELETE RESTRICT
) ENGINE = InnoDB;

-- 6. 建立課程章節表 (Modules)
CREATE TABLE IF NOT EXISTS `Modules` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `course_id` INT NOT NULL,
  `title` VARCHAR(255) NOT NULL,
  `sort_order` INT DEFAULT 0,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_module_course`
    FOREIGN KEY (`course_id`)
    REFERENCES `Courses` (`id`)
    ON DELETE CASCADE
) ENGINE = InnoDB;

-- 7. 建立教材內容表 (Materials)
CREATE TABLE IF NOT EXISTS `Materials` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `module_id` INT NOT NULL,
  `type` ENUM('VIDEO', 'PDF') NOT NULL,
  `content_url` VARCHAR(500) NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_material_module`
    FOREIGN KEY (`module_id`)
    REFERENCES `Modules` (`id`)
    ON DELETE CASCADE
) ENGINE = InnoDB;

-- 8. 建立訂單總表 (Orders)
CREATE TABLE IF NOT EXISTS `Orders` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `total_amount` DECIMAL(10, 2) NOT NULL,
  `status` ENUM('PENDING', 'PAID', 'CANCELLED') DEFAULT 'PENDING',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_order_user`
    FOREIGN KEY (`user_id`)
    REFERENCES `Users` (`id`)
    ON DELETE NO ACTION
) ENGINE = InnoDB;

-- 9. 建立訂單項目表 (Order_Items)
-- 紀錄購買當下的價格快照 (Price Snapshot)
CREATE TABLE IF NOT EXISTS `Order_Items` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `order_id` INT NOT NULL,
  `course_id` INT NOT NULL,
  `price_at_purchase` DECIMAL(10, 2) NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_item_order`
    FOREIGN KEY (`order_id`)
    REFERENCES `Orders` (`id`)
    ON DELETE CASCADE,
  CONSTRAINT `fk_item_course`
    FOREIGN KEY (`course_id`)
    REFERENCES `Courses` (`id`)
    ON DELETE NO ACTION
) ENGINE = InnoDB;

-- 10. 建立課程所有權權限表 (Owned_Courses)
-- 此為 M:N 關係之中間表，用於開通權限
CREATE TABLE IF NOT EXISTS `Owned_Courses` (
  `user_id` INT NOT NULL,
  `course_id` INT NOT NULL,
  `acquired_date` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`, `course_id`), -- 複合主鍵防止重複購買
  CONSTRAINT `fk_owned_user`
    FOREIGN KEY (`user_id`)
    REFERENCES `Users` (`id`)
    ON DELETE CASCADE,
  CONSTRAINT `fk_owned_course`
    FOREIGN KEY (`course_id`)
    REFERENCES `Courses` (`id`)
    ON DELETE CASCADE
) ENGINE = InnoDB;



// Create data

==================================


USE `shida_mooc`;

-- add Users (role_type = 'EXTERNAL')
INSERT INTO `Users` (`email`, `password`, `name`, `role_type`) VALUES
('alice@example.com', 'pass123', 'Alice Johnson', 'EXTERNAL'),
('bob@example.com', 'pass123', 'Bob Smith', 'EXTERNAL'),
('charlie@example.com', 'pass123', 'Charlie Brown', 'EXTERNAL'),
('david@example.com', 'pass123', 'David Miller', 'EXTERNAL'),
('eva@example.com', 'pass123', 'Eva Green', 'EXTERNAL');


-- Create user NTNU student

======================================================

-- เพิ่มข้อมูลในตาราง Users (role_type = 'STUDENT')
INSERT INTO `Users` (`email`, `password`, `name`, `role_type`) VALUES
('st001@ntnu.edu.tw', 'ntnu123', 'John Doe', 'STUDENT'),
('st002@ntnu.edu.tw', 'ntnu123', 'Jane Watson', 'STUDENT'),
('st003@ntnu.edu.tw', 'ntnu123', 'Mike Ross', 'STUDENT'),
('st004@ntnu.edu.tw', 'ntnu123', 'Rachel Zane', 'STUDENT'),
('st005@ntnu.edu.tw', 'ntnu123', 'Harvey Specter', 'STUDENT');


INSERT INTO `Student_Details` (`user_id`, `student_id`, `department`) VALUES
(6, '41100001', 'Computer Science'),
(7, '41100002', 'Design'),
(8, '41100003', 'Mathematics'),
(9, '41100004', 'Physics'),
(10, '41100005', 'Music');


-- data for course

-- add instructor
INSERT INTO `Instructors` (`name`, `title`, `department`, `bio`) VALUES
('張鈞法', 'teacher', 'Computer Science.', 'Master of taekwondo');
('紀博文','teacher','Computer Science.','master of MMA');
('蔣宗哲','teacher','Computer Science.','Master of Muay Thai');


-- add course
INSERT INTO `Courses` (`instructor_id`, `title`, `description`, `price`) VALUES
(1, 'Python for Beginners', 'Learn Python from scratch', 1000.00),
(2, 'Database Systems', 'SQL and Relational Algebra', 1200.00),
(3, 'Web Development', 'Flask and MySQL Integration', 1500.00);

(1,'C language','Programming language',1400.00);
(2,'Quantum computer','Introduction quantum and computer programming',2500.00);





-- data for course module


INSERT INTO Modules (course_id, title, sort_order) VALUES 
(1, 'Chapter 1: Relational Algebra & Calculus', 1),
(1, 'Chapter 2: SQL Fundamentals', 2);


INSERT INTO Materials (module_id, type, content_url) VALUES 
(1, 'PDF', 'https://example.com/relational_algebra.pdf'),
(2, 'VIDEO', 'https://example.com/sql_video.mp4');

-- --------------------------------------------------------

INSERT INTO Modules (course_id, title, sort_order) VALUES 
(2, 'Chapter 1: OSI Model Basics', 1),
(2, 'Chapter 2: TCP/IP Protocols', 2);

INSERT INTO Materials (module_id, type, content_url) VALUES 
(3, 'VIDEO', 'https://example.com/osi_model.mp4'),
(4, 'PDF', 'https://example.com/tcp_ip.pdf');








//run 

ngrok http 5000