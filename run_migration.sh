#!/bin/bash
cd /Users/00avo/Projects/Net-Care/daycare-management-system/backend
psql -d daycare_db -c "ALTER TABLE parents ADD COLUMN IF NOT EXISTS invite_code VARCHAR(64); CREATE UNIQUE INDEX IF NOT EXISTS ix_parents_invite_code ON parents (invite_code); ALTER TABLE parents ADD COLUMN IF NOT EXISTS user_id UUID; CREATE INDEX IF NOT EXISTS ix_parents_user_id ON parents (user_id);"
echo ""
echo "✅ Migration done! You can close this window."
