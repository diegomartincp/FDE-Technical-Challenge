CREATE TABLE loads (
    load_id SERIAL PRIMARY KEY,
    origin VARCHAR(100) NOT NULL,
    destination VARCHAR(100) NOT NULL,
    pickup_datetime TIMESTAMP NOT NULL,
    delivery_datetime TIMESTAMP NOT NULL,
    equipment_type VARCHAR(50),
    loadboard_rate NUMERIC(10, 2),
    notes TEXT,
    weight NUMERIC(10, 2),
    commodity_type VARCHAR(100),
    num_of_pieces INTEGER,
    miles INTEGER,
    dimensions VARCHAR(100)
);
INSERT INTO loads (
    origin, destination, pickup_datetime, delivery_datetime, equipment_type,
    loadboard_rate, notes, weight, commodity_type, num_of_pieces, miles, dimensions
) VALUES
('Atlanta, GA', 'Dallas, TX', '2025-07-10 08:00', '2025-07-12 17:00', 'Dry Van', 2000.00, 'No special requirements', 20000, 'Electronics', 22, 800, '48x102x110'),
('Chicago, IL', 'Miami, FL', '2025-07-15 09:00', '2025-07-17 18:00', 'Reefer', 3500.00, 'Temperature controlled', 18000, 'Produce', 18, 1300, '53x102x110'),
('Los Angeles, CA', 'Denver, CO', '2025-07-11 07:00', '2025-07-12 20:00', 'Flatbed', 2500.00, 'Straps required', 22000, 'Steel', 10, 1000, '40x96x100'),
('Houston, TX', 'Phoenix, AZ', '2025-07-13 10:00', '2025-07-14 15:00', 'Dry Van', 1800.00, 'No pallet jack needed', 15000, 'Clothing', 30, 1170, '48x102x110'),
('Newark, NJ', 'Boston, MA', '2025-07-16 06:00', '2025-07-16 20:00', 'Box Truck', 1200.00, 'Liftgate required', 7000, 'Books', 12, 225, '24x96x90');