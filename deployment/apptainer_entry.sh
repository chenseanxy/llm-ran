
HOME=/root ollama serve >> /app/logs/ollama.log 2>&1 &
PID1=$!

cloudflared access tcp --hostname ran-k-test.chenxy.tech \
    --url 127.0.0.1:1234 --log-level debug >> /app/logs/cloudflared.log 2>&1 &
PID2=$!

cleanup() {
  echo "Shutting down background processes..."
  kill "$PID1" "$PID2" 2>/dev/null
}

# Set up trap to call cleanup on EXIT
trap cleanup EXIT

# Activate virtualenv
. /root/.cache/pypoetry/virtualenvs/llm-ran-9TtSrW0h-py3.12/bin/activate

"$@"
