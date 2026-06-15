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
