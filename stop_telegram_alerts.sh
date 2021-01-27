p_id=`pgrep -f send_orders_from_telegram.py`
echo "Stopping the script send_orders_from_telegram.py with PID $p_id"
`kill -9 $p_id`
