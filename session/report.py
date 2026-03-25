import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
from datetime import datetime


def save_session_report(logger, ear_threshold, session_duration,
                        folder="data/reports"):
    ear_log           = logger.ear_log
    alert_timestamps  = logger.alert_timestamps
    drowsy_events     = logger.drowsy_events
    yawn_events       = logger.yawn_events

    if not ear_log:
        print("[REPORT] No data to save.")
        return

    timestamps   = [e[0] for e in ear_log]
    ear_values   = [e[1] for e in ear_log]
    score_values = [e[2] for e in ear_log]

    fig = plt.figure(figsize=(14, 10), facecolor='#1a1a2e')
    gs  = gridspec.GridSpec(3, 2, figure=fig, hspace=0.45, wspace=0.35)

    text_color = '#e0e0e0'
    accent     = '#ff4757'
    warn_color = '#ffa502'

    # EAR Timeline
    ax1 = fig.add_subplot(gs[0, :])
    ax1.set_facecolor('#16213e')
    ax1.plot(timestamps, ear_values, color='#70a1ff', linewidth=1.2, label='EAR')
    ax1.axhline(y=ear_threshold, color=accent, linestyle='--', linewidth=1.5,
                label=f'Threshold ({ear_threshold:.2f})')
    for t in alert_timestamps:
        ax1.axvline(x=t, color=accent, alpha=0.4, linewidth=1)
    ax1.set_title("EAR Over Session", color=text_color)
    ax1.set_xlabel("Time (s)", color=text_color)
    ax1.set_ylabel("EAR", color=text_color)
    ax1.tick_params(colors=text_color)
    ax1.legend(facecolor='#16213e', labelcolor=text_color)

    # Score Timeline
    ax2 = fig.add_subplot(gs[1, :])
    ax2.set_facecolor('#16213e')
    ax2.fill_between(timestamps, score_values, alpha=0.3, color='#ff6b81')
    ax2.plot(timestamps, score_values, color='#ff6b81', linewidth=1.2)
    ax2.axhline(y=60, color=accent,     linestyle='--', linewidth=1, label='HIGH RISK')
    ax2.axhline(y=30, color=warn_color, linestyle='--', linewidth=1, label='WARNING')
    ax2.set_title("Drowsiness Score Over Session", color=text_color)
    ax2.set_xlabel("Time (s)", color=text_color)
    ax2.set_ylabel("Score (0-100)", color=text_color)
    ax2.set_ylim(0, 105)
    ax2.tick_params(colors=text_color)
    ax2.legend(facecolor='#16213e', labelcolor=text_color)

    # Event bar
    ax3 = fig.add_subplot(gs[2, 0])
    ax3.set_facecolor('#16213e')
    bars = ax3.bar(["Drowsy Alerts", "Yawn Events"],
                   [drowsy_events, yawn_events],
                   color=[accent, warn_color], width=0.5)
    ax3.set_title("Event Summary", color=text_color)
    ax3.tick_params(colors=text_color)
    for bar in bars:
        ax3.text(bar.get_x() + bar.get_width() / 2,
                 bar.get_height() + 0.1,
                 str(int(bar.get_height())),
                 ha='center', color=text_color, fontsize=12)

    # Stats
    ax4 = fig.add_subplot(gs[2, 1])
    ax4.set_facecolor('#16213e')
    ax4.axis('off')
    avg_ear = np.mean(ear_values) if ear_values else 0
    stats = (
        f"Duration:      {session_duration:.1f}s\n"
        f"Drowsy Alerts: {drowsy_events}\n"
        f"Yawn Events:   {yawn_events}\n"
        f"Avg EAR:       {avg_ear:.3f}\n"
        f"Threshold:     {ear_threshold:.3f}\n"
        f"Generated:     {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    ax4.text(0.05, 0.85, stats, transform=ax4.transAxes,
             fontsize=10, verticalalignment='top', color=text_color,
             fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='#0f3460', alpha=0.8))
    ax4.set_title("Session Statistics", color=text_color)

    fig.suptitle("AI Driver Safety System — Session Report",
                 color='white', fontsize=15, fontweight='bold')

    path = f"{folder}/session_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    plt.savefig(path, dpi=120, bbox_inches='tight', facecolor='#1a1a2e')
    plt.close()
    print(f"[REPORT] Saved: {path}")