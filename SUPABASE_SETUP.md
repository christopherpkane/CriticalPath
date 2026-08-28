# Asheville Critical Path

A four-week trade schedule for Brown Haven Homes — one HTML file, no build step.
The board, the rough-in tracker, per-job calendars and close-outs all live in it.

Published at **https://christopherpkane.github.io/CriticalPath/**

## Getting on the shared schedule

This page ships without connection details, so the first time you open it you need
two values from whoever runs the schedule:

1. Open the link.
2. Go to the **Sharing** tab.
3. Paste the **Project URL** and the **publishable key** you were sent.
4. Press **Connect**.

That is once, on each device. Your browser remembers it afterwards — through
refreshes and restarts — so you will not be asked again.

If you never see the Sharing setup screen and it already says **Sharing Is On**,
someone has already done this on that browser.

## Running the schedule (admin)

### The database

One table holds everything. In Supabase → **SQL Editor** → **New query**:

```sql
create table if not exists critical_path (
  id          text primary key,
  data        jsonb not null,
  updated_at  text  not null
);
alter table critical_path enable row level security;
create policy "app access" on critical_path
  for all to anon using (true) with check (true);
```

Each trade partner becomes one row, so two people editing different partners never
collide. The week-of date, job list, rough-in rows, close-outs and captured start
dates share a single `__settings` row. Expect 36 rows once it is running.

### The keys

| Key | Where it belongs |
|---|---|
| Project URL + **publishable** key (`sb_publishable_…`) | Sent to the team over Teams. Safe in a browser — it identifies the project and nothing more. |
| **Secret** key (`sb_secret_…`) | `.env.local` only, which is gitignored. It bypasses every table rule. Never in the app, never in git, never in an email. |
| Database password | A password manager. The app never uses it. |

### What the current setup does and does not protect

The table rule above lets the anonymous role read and write this one table. The
publishable key is what tells Supabase you are that anonymous role — it carries no
privileges itself, which is why Supabase considers it safe to publish.

Because this repo is public, the key is deliberately **not** in the page. That keeps
it out of a place strangers can find it. It is not a lock: anyone who gets the key
from a teammate has full access to the schedule.

If that ever needs to be a real boundary, the change is to require a sign-in —
swap the policy to `to authenticated` and add Supabase Auth. The key can then be
public and still be useless on its own.

**Encryption** (Sharing tab) is the lighter option: the schedule is scrambled before
it is stored, so anyone holding the key sees unreadable text. It does not stop them
deleting rows, and the passphrase cannot be recovered by anyone if it is lost.

### Files in this folder

| File | What it is |
|---|---|
| `index.html` | The published app. No connection details in it. |
| `index-with-key.html` | Same app with the connection written in — opens already connected. Gitignored; for your machine and for sending to the team directly. |
| `.env.local` | The Supabase keys. Gitignored. |

### Housekeeping

- **Save My Tracker** in the app produces a standalone snapshot file. Worth doing
  occasionally as a backup even with sharing on.
- Supabase free tier: 500 MB database, 5 GB transfer a month. This schedule is a few
  hundred KB.
- A free project pauses after 7 days with no activity. Daily use never pauses it; if
  it does, press **Restore** and nothing is lost.
