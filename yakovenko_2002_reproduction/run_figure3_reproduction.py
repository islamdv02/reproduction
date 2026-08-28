"""
Master runner script for Figure 3 of Yakovenko et al. (2002).
Generates publication plots of 27-muscle EMG profiles.
"""

import sys, os

# Add src to path
src_dir = os.path.join(os.path.dirname(__file__), 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from figure3_analysis import generate_figure3_complete


def main():
    print("=================================================================")
    print("  RUNNING FIGURE 3 REPRODUCTION: YAKOVENKO ET AL. (2002)")
    print("=================================================================")

    plots_dir = os.path.join(os.path.dirname(__file__), 'plots')
    os.makedirs(plots_dir, exist_ok=True)

    # Generate publication plot
    plot_path = generate_figure3_complete(output_dir=plots_dir)
    print(f"[+] Generated Figure 3 publication figure: {plot_path}")

    print("\n[OK] Figure 3 reproduction completed successfully.")


if __name__ == '__main__':
    main()
