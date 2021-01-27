CREATE TABLE telegram_messages( channel_id text, m_id int, timestamp text,	message text, reply_m_id text, reply_to_message text)

CREATE UNIQUE INDEX telegram_messages_PK ON telegram_messages(channel_id,m_id);

create table boxwood-veld-298509.turing_trades.telegram_messages( channel_id string, m_id int64, m_timestamp string,	message string, reply_m_id string, reply_to_message string);

create table boxwood-veld-298509.turing_trades.telegram_messages( channel_id string, m_id int64, m_timestamp TIMESTAMP,	message string, reply_m_id string, reply_to_message string);