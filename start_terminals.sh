#!/bin/bash

# ============================================================
#  launch_grid.sh
#  Apre una sessione tmux con 4 pannelli in griglia 2x2
#  e lancia script1.sh … script4.sh in ciascun pannello.
# ============================================================

SESSION="grid"
SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Chiudi la sessione se esiste già
tmux kill-session -t "$SESSION" 2>/dev/null

# --- Crea la sessione (pannello 0) ---
tmux new-session -d -s "$SESSION"
sleep 0.3

# --- Split orizzontale: pannello 0 (sx) | pannello 1 (dx) ---
tmux split-window -t "$SESSION:0" -h
sleep 0.3

# --- Split verticale pannello sinistro (0) → diventa 0 (alto-sx) e 2 (basso-sx) ---
tmux select-pane -t "$SESSION:0.0"
tmux split-window -t "$SESSION:0.0" -v
sleep 0.3

# --- Split verticale pannello destro (1) → diventa 1 (alto-dx) e 3 (basso-dx) ---
tmux select-pane -t "$SESSION:0.1"
tmux split-window -t "$SESSION:0.1" -v
sleep 0.3

# --- Equalizza i pannelli ---
tmux select-layout -t "$SESSION" tiled
sleep 0.2

# --- Lancia ogni script nel pannello corretto ---
tmux select-pane -t "$SESSION:0.0"
tmux send-keys -t "$SESSION:0.0" "bash '$SCRIPTS_DIR/script1.sh'" Enter

tmux select-pane -t "$SESSION:0.1"
tmux send-keys -t "$SESSION:0.1" "bash '$SCRIPTS_DIR/script2.sh'" Enter

tmux select-pane -t "$SESSION:0.2"
tmux send-keys -t "$SESSION:0.2" "bash '$SCRIPTS_DIR/script3.sh'" Enter

tmux select-pane -t "$SESSION:0.3"
tmux send-keys -t "$SESSION:0.3" "bash '$SCRIPTS_DIR/script4.sh'" Enter

# --- Focus su pannello 0 e attach ---
tmux select-pane -t "$SESSION:0.0"
tmux attach-session -t "$SESSION"