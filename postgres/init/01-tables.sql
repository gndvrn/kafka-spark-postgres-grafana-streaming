-- Пример таблиц для транзакций в нескольких офлайн магазинах одной торговой сети
-- Создаем таблицу для филиалов сети
DO $$
BEGIN
    -- Проверяем существование таблицы branches
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'branches'
    ) THEN
        -- Создаем таблицу, если она не существует
        CREATE TABLE branches (
            branch_id SERIAL PRIMARY KEY,
            branch_name VARCHAR(100) NOT NULL,
            city VARCHAR(50) NOT NULL,
            address VARCHAR(255) NOT NULL,
            opening_date DATE NOT NULL,
            is_active BOOLEAN DEFAULT TRUE
        );
        
        RAISE NOTICE 'Таблица branches создана';
    ELSE
        RAISE NOTICE 'Таблица branches уже существует';
    END IF;

    -- Проверяем, пустая ли таблица
    IF NOT EXISTS (SELECT 1 FROM branches LIMIT 1) THEN
        -- Добавляем тестовые данные только если таблица пустая
        INSERT INTO branches (branch_name, city, address, opening_date) VALUES
        ('Центральный', 'Москва', 'ул. Тверская, 1', '2010-05-15'),
        ('Северный', 'Санкт-Петербург', 'Невский пр-т, 25', '2012-08-20'),
        ('Южный', 'Ростов-на-Дону', 'ул. Большая Садовая, 10', '2015-03-10'),
        ('Западный', 'Калининград', 'Ленинский пр-т, 30', '2018-06-05'),
        ('Восточный', 'Новосибирск', 'ул. Ленина, 15', '2019-11-12'),
        ('Северо-Западный', 'Мурманск', 'ул. Ленина, 82', '2020-07-22'),
        ('Сибирский', 'Красноярск', 'ул. Карла Маркса, 123', '2021-04-18');
        
        RAISE NOTICE 'Данные филиалов добавлены';
    ELSE
        RAISE NOTICE 'Таблица branches уже содержит данные, добавление пропущено';
    END IF;

    -- Создаем индекс, если его нет
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE schemaname = 'public' 
        AND tablename = 'branches' 
        AND indexname = 'idx_branches_city'
    ) THEN
        CREATE INDEX idx_branches_city ON branches(city);
        RAISE NOTICE 'Индекс idx_branches_city создан';
    END IF;

EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Ошибка при инициализации базы данных: %', SQLERRM;
END $$;

-- Создаем таблицу для транзакций
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id VARCHAR(50) PRIMARY KEY DEFAULT gen_random_uuid(),
    branch_id INTEGER REFERENCES branches(branch_id),
    transaction_time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    amount DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(20) NOT NULL CHECK (payment_method IN ('cash', 'card', 'mobile')),
    customer_id VARCHAR(30),
    items_count INTEGER NOT NULL,
    is_return BOOLEAN DEFAULT FALSE,
    operator_id VARCHAR(30) NOT NULL,
    additional_info TEXT,
    
    -- Индексы для ускорения запросов
    CONSTRAINT valid_amount CHECK (amount != 0)
);

CREATE TABLE IF NOT EXISTS branch_stats_realtime (
    branch_id INTEGER PRIMARY KEY REFERENCES branches(branch_id),
    transaction_count INTEGER NOT NULL,
    total_amount DECIMAL(12, 2) NOT NULL,
    avg_amount DECIMAL(10, 2) NOT NULL,
    return_count INTEGER NOT NULL,
    last_updated TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_transactions_branch ON transactions(branch_id);
CREATE INDEX idx_transactions_time ON transactions(transaction_time);
CREATE INDEX idx_transactions_payment ON transactions(payment_method);