#!/usr/bin/env python3
"""
Seed script for the kislorod-new-year-2025-bot project.

This script uses the existing async helpers in `app.database.requests` and
`app.database.models.async_main()` to create the database (if needed), then
inserts 29 users and 15 events. Each event's codeword is `event_<n>`.

Location: `scripts/seed_db.py` (project root)

How to run:
  1. Ensure your virtualenv is activated and Postgres is reachable using
     the connection configured in `config.py` / `.env`.
  2. Run the script:
       python scripts/seed_db.py

Notes:
  - The script calls `app.database.models.async_main()` to create the database
    and tables if they are missing. If you already run the main app (run.py)
    this is optional but safe.
  - The script relies only on public functions from `app.database.requests`:
    `create_user`, `create_event`, `get_all_users`, `get_all_events`,
    `mark_attendance`.
  - If your database schema differs from the models (PK types, missing
    columns), seeding may fail. Run migrations or recreate the DB tables first.
"""

import asyncio
from datetime import datetime, timedelta, timezone

from app.database.models import async_main
import app.database.requests as db


async def seed():
    # Ensure DB and tables exist
    await async_main()

    # Create 29 users. Telegram IDs are simulated but must be integers.
    users = []
    base_tg = 900000000
    for i in range(1, 30):  # 1..29
        tg = base_tg + i
        # a few users belong to KS (every 7th), others are regular
        first = f'User{i}'
        last = f'Last{i}'
        middle = f'Middle{i}'
        user = await db.create_user(tg, first, last, middle)
        users.append(user)

    # Create 15 events. codeword = event_<n>
    events = []
    # Use UTC datetimes. The DB column `events.date` is TIMESTAMP WITHOUT
    # TIME ZONE, so we must pass a naive datetime (no tzinfo). Create an
    # aware datetime for correctness then strip tzinfo before inserting.
    start = datetime.now(timezone.utc)
    for e in range(1, 16):
        title = f'Новогоднее событие {e}'
        # pass a datetime instance (timezone-aware) to create_event
        # compute UTC datetime then convert to naive by removing tzinfo
        date = (start + timedelta(days=e)).astimezone(timezone.utc).replace(tzinfo=None)
        score = 5 + e  # arbitrary score
        code = f'event_{e}'
        ev = await db.create_event(title, date, score, code)
        events.append(ev)

    # Link attendances. For each event n, mark attendance for a deterministic subset
    # of users so test data is reproducible. We'll add ~3-7 attendees per event.
    for idx, ev in enumerate(events, start=1):
        # pick users where (user_index % (idx % 5 + 2)) == 0 to get varying counts
        mod = (idx % 5) + 2
        for u_idx, user in enumerate(users, start=1):
            if u_idx % mod == 0:
                # codeword must match `event_<idx>` per requirement
                success, message, awarded = await db.mark_attendance(user_id=user.id, event_id=ev.id, codeword=f'event_{idx}')

    print('Seeding finished.')

if __name__ == '__main__':
    asyncio.run(seed())
