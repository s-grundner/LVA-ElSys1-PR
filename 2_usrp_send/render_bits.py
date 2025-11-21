#!/usr/bin/env python3

import struct
import argparse
import numpy as np
import matplotlib.pyplot as plt


def read_gnc_file(file_path):
    """
    Reads binary data from a .gnc file and returns it as a numpy array.
    """
    data = []
    with open(file_path, "rb") as f:
        while chunk := f.read(4):  # Assuming 4-byte floats
            value = struct.unpack("f", chunk)[0]
            data.append(value)
    return np.array(data)


def plot_data(data, title, output_path=None, interactive=False):
    """
    Plots the data. Saves PNG if output_path is given.
    Shows interactive plot window if interactive=True.
    Sample rate is assumed to be 200ksps for x-axis labeling.
    """
    plt.figure(figsize=(10, 6))
    plt.plot(data, label=title)
    plt.title(title)
    plt.xlabel("Time (ms)")
    # rescale x to ms assuming 200ksps
    plt.xticks(
        ticks=np.linspace(0, len(data), num=11),
        labels=[f"{int(x / 20)}" for x in np.linspace(0, len(data), num=11)],
    )

    plt.ylabel("Amplitude")
    plt.legend()
    plt.grid(True)

    if output_path:
        plt.savefig(output_path)
        print(f"Saved: {output_path}")

    if interactive:
        plt.show()
    else:
        plt.close()


def main():
    parser = argparse.ArgumentParser(description="Plot multiple .gnc files")
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Enable interactive Matplotlib windows",
    )
    args = parser.parse_args()

    files = {
        "GFSK Signal, Data: 0xA5": ("gfsk.gnc", "gfsk.png"),
        "4-FSK Signal, Data: 0xA5": ("4fsk.gnc", "4fsk.png"),
        "2-FSK Signal, Data: 0xA5": ("2fsk.gnc", "2fsk.png"),
        "2-FSK Signal, Data: 0xA5": ("2fsk.gnc", "2fsk.png"),
        "4-FSK Signal, Data: 0xB3": ("4-fsk-b3.gnc", "4fsk-b3.png"),
    }

    for title, (input_file, output_file) in files.items():
        print(f"Reading {input_file}...")
        data = read_gnc_file(input_file)

        print(f"Plotting {title} → {output_file}...")
        plot_data(data, title, output_path=output_file, interactive=args.interactive)

    print("All plots complete.")


if __name__ == "__main__":
    main()
