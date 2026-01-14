# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- tests: Add end-to-end test verifying UI shows "❌ занято" for fully booked masters (tests/test_busy_master_display.py). ✅
- tests: Add manual request flow tests and stabilize booking-related tests (tests/test_booking_manual_request.py).

### Fixed
- handlers: Ensure `InlineKeyboardMarkup` and `InlineKeyboardButton` are constructed compatibly with current test harness and aiogram usage (various small fixes in `app/handlers/booking.py`, `app/handlers/client.py`, `app/handlers/services.py`).

### Notes
- All tests pass locally: **33 passed, 1 warning**.
- Migration to aiogram 3.x and removal of temporary test shims postponed — will be scheduled as a separate task when a migration plan is approved.

---

(Generated on 2026-01-14)
