#!/bin/sh
set -e

apk add --no-cache curl jq

echo "Waiting for Metabase..."

until curl -s "$MB_URL/api/health" | grep -q "ok"; do
  sleep 5
done

echo "Metabase is ready"

SETUP_TOKEN=$(curl -s "$MB_URL/api/session/properties" | jq -r '.["setup-token"]')

if [ "$SETUP_TOKEN" = "null" ] || [ -z "$SETUP_TOKEN" ]; then
  echo "Metabase already configured, skipping setup"
  exit 0
fi

echo "Running Metabase setup..."

curl -s -X POST "$MB_URL/api/setup" \
  -H "Content-Type: application/json" \
  -d "{
    \"token\": \"$SETUP_TOKEN\",
    \"user\": {
      \"email\": \"$MB_ADMIN_EMAIL\",
      \"password\": \"$MB_ADMIN_PASSWORD\",
      \"first_name\": \"Admin\",
      \"last_name\": \"User\"
    },
    \"database\": {
      \"name\": \"GitHub Research DB\",
      \"engine\": \"postgres\",
      \"details\": {
        \"host\": \"$TARGET_DB_HOST\",
        \"port\": $TARGET_DB_PORT,
        \"dbname\": \"$TARGET_DB_DBNAME\",
        \"user\": \"$TARGET_DB_USER\",
        \"password\": \"$TARGET_DB_PASSWORD\",
        \"ssl\": false
      }
    },
    \"prefs\": {
      \"site_name\": \"GitHub Research\",
      \"allow_tracking\": false
    }
  }"

echo "Metabase setup complete"