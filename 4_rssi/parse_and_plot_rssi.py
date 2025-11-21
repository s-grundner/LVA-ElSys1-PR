#!/usr/bin/env python3

import os
import re
import matplotlib.pyplot as plt
import argparse

# Define ranges and PA output settings
ranges = ["1m", "3m", "5m", "7m", "9m", "11m", "13m", "15m"]
range_count = [10, 10, 10, 10, 10, 10, 10, 10]
pa_output_settings = [-30, -20, -15, -10, 0, 5, 7, 10]


def parse_rssi_file(file_path):
    """
    Parse the RSSI values from the given file.

    Args:
        file_path (str): Path to the RSSI data file.

    Returns:
        dict: A dictionary mapping ranges to PA output settings and their RSSI values.
    """
    with open(file_path, "r") as file:
        content = file.read()

    # Extract RSSI values and ranges directly
    rssi_values = [
        int(match.group(1)) for match in re.finditer(r"RSSI:\s*(\d+)", content)
    ]
    data = {
        "ranges": ranges,
        "rssi": rssi_values[
            : len(ranges)
        ],  # Assume one RSSI value per range for simplicity
    }

    return data


def plot_all_rssi(
    file_path, output_path, output_dBm_path, interactive=False, range_count=None
):
    """
    Plot all RSSI values from a file into a single PNG.

    Args:
        file_path (str): Path to the RSSI data file.
        output_path (str): Path to save the plot.
    """
    with open(file_path, "r") as file:
        content = file.read()

    # Extract RSSI values
    rssi_values = [
        int(match.group(1)) for match in re.finditer(r"RSSI:\s*(\d+)", content)
    ]

    # If range_count is provided, split RSSI values into bins
    if range_count:
        binned_rssi = [
            rssi_values[i : i + range_count]
            for i in range(0, len(rssi_values), range_count)
        ]
        mean_rssi = [sum(bin) / len(bin) for bin in binned_rssi]
    else:
        binned_rssi = [rssi_values]
        mean_rssi = [sum(rssi_values) / len(rssi_values)]

    # Plot mean RSSI in dBm per bin with distances as x-axis
    if range_count:
        # Convert mean RSSI values to dBm
        mean_rssi_dBm = [
            (value - 256) / 2 - 74 if value >= 128 else value / 2 - 74
            for value in mean_rssi
        ]
        plt.figure()
        plt.plot(ranges[: len(mean_rssi_dBm)], mean_rssi_dBm, marker="o", color="blue")
        plt.title(f"Mean RSSI in dBm per Bin from {os.path.basename(file_path)}")
        plt.xlabel("Distance")
        plt.ylabel("Mean RSSI (dBm)")
        plt.grid(True)
        mean_output_path = output_path.replace(".png", "_mean_dBm.png")
        os.makedirs(os.path.dirname(mean_output_path), exist_ok=True)
        if interactive:
            plt.show()
        else:
            plt.savefig(mean_output_path)
            plt.close()
            print(f"Saved mean dBm plot: {mean_output_path}")

    # Convert RSSI values to dBm
    rssi_dBm_values = [
        (value - 256) / 2 - 74 if value >= 128 else value / 2 - 74
        for value in rssi_values
    ]

    # Plot RSSI values
    plt.figure()
    plt.plot(rssi_values, marker="o", label="Raw RSSI")
    plt.plot(mean_rssi, marker="x", label="Mean RSSI (per range bin)", color="green")
    plt.title(f"RSSI Values and Mean from {os.path.basename(file_path)}")
    plt.legend()
    plt.xlabel("Sample Index")
    plt.ylabel("RSSI")
    plt.grid(True)
    if interactive:
        plt.show()
    else:
        plt.savefig(output_path)
        plt.close()
        print(f"Saved plot: {output_path}")

    # Plot RSSI values in dBm
    plt.figure()
    plt.plot(rssi_dBm_values, marker="o", color="red")
    plt.title(f"RSSI Values in dBm from {os.path.basename(file_path)}")
    plt.xlabel("Sample Index")
    plt.ylabel("RSSI (dBm)")
    plt.grid(True)
    if interactive:
        plt.show()
    else:
        plt.savefig(output_dBm_path)
        plt.close()
        print(f"Saved plot: {output_dBm_path}")


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Parse and plot RSSI data.")
    parser.add_argument(
        "--interactive", action="store_true", help="Display plots interactively"
    )
    range_count = 10  # Predefined: Set the number of RSSI values per range bin
    args = parser.parse_args()
    # File paths
    range_file = "4_rssi/range.txt"
    rssi_gfsk_file = "4_rssi/rssi_gfsk.txt"
    output_dir = "4_rssi/plots"

    # Parse the files
    print("Parsing range.txt...")
    range_data = parse_rssi_file(range_file)
    print("Generating plot for range.txt...")
    plot_all_rssi(
        range_file,
        "4_rssi/plots/range_plot.png",
        "4_rssi/plots/range_plot_dBm.png",
        args.interactive,
        range_count,
    )
    print("Generating plot for rssi_gfsk.txt...")
    plot_all_rssi(
        rssi_gfsk_file,
        "4_rssi/plots/rssi_gfsk_plot.png",
        "4_rssi/plots/rssi_gfsk_plot_dBm.png",
        args.interactive,
    )


if __name__ == "__main__":
    main()
