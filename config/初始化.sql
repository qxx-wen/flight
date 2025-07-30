-- 航司
CREATE TABLE airline (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(10) NOT NULL
);

-- 机场
CREATE TABLE airport (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(10) NOT NULL,
    city VARCHAR(50)
);


-- 人员
CREATE TABLE staff (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50),
    skill_level VARCHAR(20),
    status VARCHAR(20)
);

-- 航班
CREATE TABLE flight (
    id INT PRIMARY KEY AUTO_INCREMENT,
    flight_no VARCHAR(20) NOT NULL,
    airline_id INT NOT NULL,
    dep_airport_id INT NOT NULL,
    arr_airport_id INT NOT NULL,
    sched_dep_time DATETIME,
    sched_arr_time DATETIME,
    act_dep_time DATETIME,
    act_arr_time DATETIME,
    status VARCHAR(20),
    FOREIGN KEY (airline_id) REFERENCES airline(id),
    FOREIGN KEY (dep_airport_id) REFERENCES airport(id),
    FOREIGN KEY (arr_airport_id) REFERENCES airport(id)
);

-- 保障任务
CREATE TABLE task (
    id INT PRIMARY KEY AUTO_INCREMENT,
    flight_id INT NOT NULL,
    type VARCHAR(50),
    sched_ready_time DATETIME,
    sched_start_time DATETIME,
    sched_end_time DATETIME,
    act_ready_time DATETIME,
    act_start_time DATETIME,
    act_end_time DATETIME,
    duration INT,
    leader_id INT,
    assigner_id INT,
    FOREIGN KEY (flight_id) REFERENCES flight(id),
    FOREIGN KEY (leader_id) REFERENCES staff(id),
    FOREIGN KEY (assigner_id) REFERENCES staff(id)
);

-- 机场环境因素
CREATE TABLE environment (
    id INT PRIMARY KEY AUTO_INCREMENT,
    airport_id INT NOT NULL,
    record_time DATETIME,
    weather VARCHAR(50),
    visibility FLOAT,
    wind_speed FLOAT,
    wind_direction VARCHAR(20),
    temperature FLOAT,
    FOREIGN KEY (airport_id) REFERENCES airport(id)
);

-- 时间特征
CREATE TABLE time_feature (
    id INT PRIMARY KEY AUTO_INCREMENT,
    date DATE NOT NULL,
    is_holiday BOOLEAN,
    workday_type VARCHAR(20),
    time_period VARCHAR(20)
);

-- 排班
CREATE TABLE schedule (
    id INT PRIMARY KEY AUTO_INCREMENT,
    team_name VARCHAR(50),
    leader_id INT,
    schedule_type VARCHAR(20),
    shift VARCHAR(20),
    FOREIGN KEY (leader_id) REFERENCES staff(id)
);