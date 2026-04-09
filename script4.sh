#!/bin/bash
echo "Start grblHAL simulator"

#!/bin/bash

PORT="/tmp/ttyV3"

echo "Attendo la porta $PORT..."

while true; do
    if [ -e "$PORT" ]; then
        if stty -F "$PORT" &>/dev/null; then
            echo "Porta valida trovata, avvio socat..."
            break
        else
            echo "Porta presente ma non valida, attendo..."
        fi
    fi
    sleep 1
done

# Loop infinito di socat
while true; do
    socat "$PORT",raw,echo=0 \
    EXEC:'./Simulator/build/grblHAL_sim -n',pty,raw,echo=0

    echo "socat terminato, riavvio tra 1s..."
    sleep 1
done
