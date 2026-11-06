-- consultations.plan_rooms
--
-- Nullable TEXT. JSON from the consult payload field planRooms:
-- rooms read from a known sample floor plan, after the visitor edits them.
--   [{"label":"Living Dining","size":"約30.3帖"}]
-- NULL when the request omits planRooms (a free upload, or an older client).
-- "[]" when the visitor cleared every room.
--
-- Run once, before deploying a Worker built from scripts/build_worker.py
-- that inserts plan_rooms. Do not run this against production until that
-- deploy; the current live INSERT does not mention the column.
-- Shipping the new Worker first makes every consult INSERT fail.

ALTER TABLE consultations ADD COLUMN plan_rooms TEXT;
