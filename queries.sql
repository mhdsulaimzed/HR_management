    CREATE TABLE designation(id SERIAL PRIMARY KEY,
                            title VARCHAR(150) ,
                            total_leaves INTEGER ,
                            UNIQUE(id,title));

    INSERT INTO designation (title,total_leaves) VALUES ('Staff Engineer',20),('Senior Engineer',18),('Junior Engineer',12),('Tech Lead',12),('Project manager',12);


    CREATE TABLE employees(
                        s_no BIGSERIAL PRIMARY KEY,
                        first_name VARCHAR(50),
                        last_name VARCHAR(50) ,
                        designation INTEGER REFERENCES designation(id), 
                        email VARCHAR(50),
                            phone VARCHAR(50), 
                        company_address VARCHAR(100),
                        UNIQUE(email));

    CREATE TABLE employee_leave(
                        s_no BIGSERIAL PRIMARY KEY,
                        leave_date DATE,
                        employee_id INTEGER REFERENCES employees(s_no),
                        reason VARCHAR(200),
                        UNIQUE(employee_id,leave_date));

