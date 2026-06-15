USE `shida_mooc`;

-- =====================================
-- INSERT USERS
-- =====================================
INSERT INTO `Users`
(`email`, `password`, `name`, `role_type`)
VALUES
('alice@example.com', 'pass123', 'Alice Johnson', 'STUDENT'),
('bob@example.com', 'pass123', 'Bob Smith', 'EXTERNAL'),
('charlie@example.com', 'pass123', 'Charlie Brown', 'ADMIN');

-- =====================================
-- INSERT STUDENT DETAILS
-- =====================================
INSERT INTO `Student_Details`
(`user_id`, `student_id`, `department`)
VALUES
(1, 'S1123456', 'Computer Science');

-- =====================================
-- INSERT INSTRUCTORS
-- =====================================
INSERT INTO `Instructors`
(`name`, `title`, `department`, `bio`)
VALUES
(
    'Dr. Wang',
    'Professor',
    'Computer Science',
    'Expert in database systems'
),
(
    'Dr. Lin',
    'Associate Professor',
    'Electrical Engineering',
    'Researcher in AI and machine learning'
);

-- =====================================
-- INSERT COURSES
-- =====================================
INSERT INTO `Courses`
(`instructor_id`, `title`, `description`, `price`)
VALUES
(
    1,
    'Database Systems',
    'Learn SQL and database design',
    1000
),
(
    2,
    'Introduction to AI',
    'Basic AI concepts and applications',
    1200
),
(
    1,
    'SQL Basics',
    'Introduction to SQL language',
    0
);

-- =====================================
-- INSERT MODULES
-- =====================================
INSERT INTO `Modules`
(`course_id`, `title`, `sort_order`)
VALUES
(1, 'Introduction to Database', 1),
(1, 'SQL Queries', 2),
(2, 'What is AI?', 1);

-- =====================================
-- INSERT MATERIALS
-- =====================================
INSERT INTO `Materials`
(`module_id`, `type`, `content_url`)
VALUES
(
    1,
    'VIDEO',
    'https://example.com/videos/db_intro.mp4'
),
(
    1,
    'PDF',
    'https://example.com/pdfs/db_notes.pdf'
),
(
    2,
    'VIDEO',
    'https://example.com/videos/sql_queries.mp4'
);

-- =====================================
-- INSERT ORDERS
-- =====================================
INSERT INTO `Orders`
(`user_id`, `total_amount`, `status`)
VALUES
(1, 1000, 'PAID'),
(2, 1200, 'PAID');

-- =====================================
-- INSERT ORDER ITEMS
-- =====================================
INSERT INTO `Order_Items`
(`order_id`, `course_id`, `price_at_purchase`)
VALUES
(1, 1, 1000),
(2, 2, 1200);

-- =====================================
-- INSERT OWNED COURSES
-- =====================================
INSERT INTO `Owned_Courses`
(`user_id`, `course_id`)
VALUES
(1, 1),
(2, 2);

-- =====================================
-- BASIC JOIN QUERY
-- Show all courses with instructors
-- =====================================
SELECT
    c.id AS course_id,
    c.title AS course_title,
    i.name AS instructor_name,
    c.price
FROM Courses c
JOIN Instructors i
ON c.instructor_id = i.id;

-- =====================================
-- JOIN QUERY
-- Show user purchase history
-- =====================================
SELECT
    u.name AS user_name,
    o.id AS order_id,
    c.title AS course_name,
    oi.price_at_purchase
FROM Users u
JOIN Orders o
    ON u.id = o.user_id
JOIN Order_Items oi
    ON o.id = oi.order_id
JOIN Courses c
    ON oi.course_id = c.id;

-- =====================================
-- UPDATE EXAMPLE
-- =====================================
UPDATE Courses
SET price = 800
WHERE id = 1;

-- =====================================
-- DELETE EXAMPLE
-- =====================================
DELETE FROM Materials
WHERE id = 3;

-- =====================================
-- AGGREGATE FUNCTION
-- Total revenue for each course
-- =====================================
SELECT
    c.title,
    SUM(oi.price_at_purchase) AS total_revenue
FROM Courses c
JOIN Order_Items oi
    ON c.id = oi.course_id
GROUP BY c.id, c.title;

-- =====================================
-- COUNT QUERY
-- Most popular courses
-- =====================================
SELECT
    c.title,
    COUNT(oc.user_id) AS total_students
FROM Courses c
JOIN Owned_Courses oc
    ON c.id = oc.course_id
GROUP BY c.id, c.title
ORDER BY total_students DESC;

-- =====================================
-- SET MEMBERSHIP QUERY
-- =====================================
SELECT name
FROM Users
WHERE id IN (
    SELECT user_id
    FROM Owned_Courses
    WHERE course_id = 1
);

-- =====================================
-- TRANSACTION EXAMPLE
-- =====================================
START TRANSACTION;

INSERT INTO Orders
(user_id, total_amount, status)
VALUES
(1, 1200, 'PAID');

INSERT INTO Order_Items
(order_id, course_id, price_at_purchase)
VALUES
(LAST_INSERT_ID(), 2, 1200);

COMMIT;
