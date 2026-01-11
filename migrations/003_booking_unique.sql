-- add unique index to prevent duplicate bookings for same master/date/time
CREATE UNIQUE INDEX IF NOT EXISTS idx_bookings_unique_slot ON bookings(master_id, date, time);