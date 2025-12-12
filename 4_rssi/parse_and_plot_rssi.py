#!/usr/bin/env python3

import os
import re
import numpy as np
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


def calculate_friis_path_loss(
    distances, frequency_hz=433e6, reference_distance=1.0, reference_power_dbm=-40
):
    """
    Calculate the Friis transmission equation prediction for path loss.

    Args:
        distances (list): List of distances in meters.
        frequency_hz (float): Transmission frequency in Hz (default 2.4 GHz).
        reference_distance (float): Reference distance in meters for normalization.
        reference_power_dbm (float): Reference power at reference distance in dBm.

    Returns:
        list: Predicted received power in dBm at each distance.
    """
    c = 3e8  # Speed of light in m/s
    wavelength = c / frequency_hz

    # Calculate path loss in dB relative to reference distance
    # PL(d) = 20*log10(4*pi*d/lambda)
    # Relative PL = PL(d) - PL(d0) = 20*log10(d/d0)
    friis_prediction = []
    for d in distances:
        # Path loss increases with 20*log10(distance) for free space
        path_loss_db = 20 * np.log10(d / reference_distance)
        predicted_power = reference_power_dbm - path_loss_db
        friis_prediction.append(predicted_power)

    return friis_prediction


def analyze_antenna_gain(
    mean_rssi_dBm, pa_output_settings, distance_m=1.0, frequency_hz=433e6
):
    """
    Analyze path loss and estimate combined antenna gain from PA table measurements.

    Args:
        mean_rssi_dBm (list): Mean received power in dBm for each PA setting.
        pa_output_settings (list): PA output power settings in dBm.
        distance_m (float): Measurement distance in meters.
        frequency_hz (float): Transmission frequency in Hz (default 433 MHz).

    Returns:
        dict: Analysis results including path loss and antenna gain estimates.
    """
    c = 3e8  # Speed of light
    wavelength = c / frequency_hz

    # Free space path loss: FSPL = 20*log10(4*pi*d/lambda)
    fspl_dB = 20 * np.log10(4 * np.pi * distance_m / wavelength)

    print("\n" + "=" * 70)
    print("ANTENNA GAIN ANALYSIS (PA Table at 1m, 433 MHz)")
    print("=" * 70)
    print(f"Free Space Path Loss at {distance_m}m: {fspl_dB:.2f} dB")
    print(f"Wavelength: {wavelength:.3f} m")
    print(f"\nNominal PA vs Received Power (with calibration):")
    print("-" * 70)

    # Since path loss should be constant at fixed distance, use it to calibrate
    # Pr = Pt_actual + Gt + Gr - FSPL
    # Assume average antenna gain to calibrate actual Pt

    # First pass: estimate average system gain assuming nominal PA values
    nominal_gains = []
    for pt_nominal, pr_dBm in zip(
        pa_output_settings[: len(mean_rssi_dBm)], mean_rssi_dBm
    ):
        gain = pr_dBm - pt_nominal + fspl_dB
        nominal_gains.append(gain)

    avg_system_gain = np.mean(nominal_gains)

    # Second pass: calculate actual transmitted power assuming constant system gain
    print(f"Assumed system gain (Gt + Gr): {avg_system_gain:+.2f} dB\n")

    actual_pt_values = []
    for i, (pt_nominal, pr_dBm) in enumerate(
        zip(pa_output_settings[: len(mean_rssi_dBm)], mean_rssi_dBm)
    ):
        # Pt_actual = Pr - (Gt + Gr) + FSPL
        pt_actual = pr_dBm - avg_system_gain + fspl_dB
        calibration_error = pt_actual - pt_nominal
        actual_pt_values.append(pt_actual)

        print(
            f"PA: {pt_nominal:+4.0f} dBm (nominal) -> {pt_actual:+6.2f} dBm (actual) | "
            f"Rx: {pr_dBm:+6.2f} dBm | Error: {calibration_error:+5.2f} dB"
        )

    print("-" * 70)
    print(f"Average Combined Antenna Gain (Gt + Gr): {avg_system_gain:+.2f} dB")
    print(f"Assuming identical antennas: Gt = Gr ≈ {avg_system_gain / 2:+.2f} dB each")
    print(f"\nNote: Path loss variations indicate PA table miscalibration.")
    print(f"Actual transmitted power differs from nominal PA settings.")
    print("=" * 70 + "\n")

    return {
        "fspl_dB": fspl_dB,
        "combined_gain_dB": avg_system_gain,
        "individual_gain_dB": avg_system_gain / 2,
        "actual_pt_values": actual_pt_values,
    }


def analyze_outliers(rssi_values, range_count, ranges):
    """
    Analyze RSSI data for outliers in each bin.

    Args:
        rssi_values (list): List of raw RSSI values.
        range_count (int): Number of samples per bin.
        ranges (list): List of range labels.
    """
    print("\n" + "=" * 70)
    print("OUTLIER ANALYSIS")
    print("=" * 70)

    # Convert to dBm
    rssi_dBm_values = [
        (value - 256) / 2 - 74 if value >= 128 else value / 2 - 74
        for value in rssi_values
    ]

    # Split into bins
    binned_rssi = [
        rssi_values[i : i + range_count]
        for i in range(0, len(rssi_values), range_count)
    ]
    binned_rssi_dBm = [
        rssi_dBm_values[i : i + range_count]
        for i in range(0, len(rssi_dBm_values), range_count)
    ]

    for i, (bin_raw, bin_dbm) in enumerate(zip(binned_rssi, binned_rssi_dBm)):
        if i >= len(ranges):
            break

        mean_dbm = np.mean(bin_dbm)
        std_dbm = np.std(bin_dbm)

        print(f"\n{ranges[i]} (Bin {i}):")
        print(f"  Raw RSSI: {bin_raw}")
        print(f"  dBm values: {[f'{v:.2f}' for v in bin_dbm]}")
        print(f"  Mean (dBm): {mean_dbm:.2f}, Std: {std_dbm:.2f}")
        print(f"  Range (dBm): [{min(bin_dbm):.2f}, {max(bin_dbm):.2f}]")

        # Check for outliers using 2-sigma rule on dBm values only
        outliers_dbm = [v for v in bin_dbm if abs(v - mean_dbm) > 2 * std_dbm]

        if outliers_dbm:
            print(f"  ⚠️  OUTLIERS DETECTED (>2σ in dBm):")
            print(f"     dBm: {[f'{v:.2f}' for v in outliers_dbm]}")
        else:
            print(f"  ✓ No outliers detected (2σ threshold)")

    print("\n" + "=" * 70 + "\n")


def plot_all_rssi(
    file_path,
    output_path,
    output_dBm_path,
    interactive=False,
    range_count=None,
    enable_friis=False,
    x_labels=None,
    x_label_name="Distance",
):
    """
    Plot all RSSI values from a file into a single PNG.

    Args:
        file_path (str): Path to the RSSI data file.
        output_path (str): Path to save the plot.
        enable_friis (bool): Whether to generate Friis comparison plot (for distance measurements).
        x_labels (list): Custom x-axis labels (if None, uses ranges).
        x_label_name (str): Name for the x-axis label.
    """
    with open(file_path, "r") as file:
        content = file.read()

    # Extract RSSI values
    rssi_values = [
        int(match.group(1)) for match in re.finditer(r"RSSI:\s*(\d+)", content)
    ]

    # Convert RSSI values to dBm FIRST, then bin and average
    rssi_dBm_values = [
        (value - 256) / 2 - 74 if value >= 128 else value / 2 - 74
        for value in rssi_values
    ]

    # If range_count is provided, split RSSI values into bins
    if range_count:
        binned_rssi = [
            rssi_values[i : i + range_count]
            for i in range(0, len(rssi_values), range_count)
        ]
        # Bin the dBm values (already converted)
        binned_rssi_dBm = [
            rssi_dBm_values[i : i + range_count]
            for i in range(0, len(rssi_dBm_values), range_count)
        ]
        mean_rssi = [sum(bin) / len(bin) for bin in binned_rssi]
        # Calculate mean from already-converted dBm values
        mean_rssi_dBm = [sum(bin) / len(bin) for bin in binned_rssi_dBm]
    else:
        binned_rssi = [rssi_values]
        mean_rssi = [sum(rssi_values) / len(rssi_values)]
        mean_rssi_dBm = [sum(rssi_dBm_values) / len(rssi_dBm_values)]

    # Plot mean RSSI in dBm per bin with custom x-axis
    if range_count:
        # Use custom x_labels if provided, otherwise use ranges
        if x_labels is None:
            x_labels = ranges[: len(mean_rssi_dBm)]
        else:
            x_labels = x_labels[: len(mean_rssi_dBm)]

        plt.figure()
        plt.plot(x_labels, mean_rssi_dBm, marker="o", color="blue")
        plt.title(f"Mean RSSI in dBm per Bin from {os.path.basename(file_path)}")
        plt.xlabel(x_label_name)
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

        # Plot mean RSSI in dBm with Friis prediction comparison (only for distance measurements)
        if enable_friis:
            # Extract numeric distances from range strings
            distances_m = [
                float(r.replace("m", "")) for r in ranges[: len(mean_rssi_dBm)]
            ]

            # Fit Friis prediction offset A using least squares over 5m, 7m, 9m
            fit_distances = [5.0, 7.0, 9.0]
            fit_indices = []
            for fd in fit_distances:
                label = f"{int(fd)}m"
                if label in ranges[: len(mean_rssi_dBm)]:
                    fit_indices.append(ranges.index(label))
            fit_measurements = [
                mean_rssi_dBm[i] for i in fit_indices if i < len(mean_rssi_dBm)
            ]
            fit_d = [distances_m[i] for i in fit_indices if i < len(distances_m)]

            if len(fit_measurements) == len(fit_distances):
                # Model: Pr(d) = A - 20*log10(d), solve A by averaging A_i = Pr_i + 20*log10(d_i)
                terms = [m + 20 * np.log10(d) for m, d in zip(fit_measurements, fit_d)]
                A = np.mean(terms)
            else:
                # Fallback: normalize to first measurement
                A = mean_rssi_dBm[0] + 20 * np.log10(distances_m[0])

            friis_prediction = [A - 20 * np.log10(d) for d in distances_m]

            plt.figure()
            plt.plot(
                ranges[: len(mean_rssi_dBm)],
                mean_rssi_dBm,
                marker="o",
                color="blue",
                label="Measured RSSI",
            )
            plt.plot(
                ranges[: len(mean_rssi_dBm)],
                friis_prediction,
                marker="s",
                color="red",
                linestyle="--",
                label="Friis Prediction",
            )
            plt.title(f"Mean RSSI vs Friis Equation from {os.path.basename(file_path)}")
            plt.xlabel("Distance")
            plt.ylabel("Mean RSSI (dBm)")
            plt.legend()
            plt.grid(True)
            friis_output_path = output_path.replace(
                ".png", "_mean_dBm_against_friis.png"
            )
            os.makedirs(os.path.dirname(friis_output_path), exist_ok=True)
            if interactive:
                plt.show()
            else:
                plt.savefig(friis_output_path)
                plt.close()
                print(f"Saved Friis comparison plot: {friis_output_path}")

    # Plot RSSI values
    plt.figure()
    plt.plot(rssi_values, marker="o", label="Raw RSSI")
    plt.title(f"RSSI Values from {os.path.basename(file_path)}")
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

    # Analyze outliers for range.txt
    with open(range_file, "r") as file:
        content = file.read()
    rssi_values = [
        int(match.group(1)) for match in re.finditer(r"RSSI:\s*(\d+)", content)
    ]
    analyze_outliers(rssi_values, range_count, ranges)

    print("Generating plot for range.txt...")
    plot_all_rssi(
        range_file,
        "4_rssi/plots/range_plot.png",
        "4_rssi/plots/range_plot_dBm.png",
        args.interactive,
        range_count,
        enable_friis=True,
    )
    print("Generating plot for rssi_gfsk.txt...")

    # Parse rssi_gfsk for antenna gain analysis
    with open(rssi_gfsk_file, "r") as file:
        content = file.read()
    rssi_gfsk_values = [
        int(match.group(1)) for match in re.finditer(r"RSSI:\s*(\d+)", content)
    ]
    rssi_gfsk_dBm = [
        (value - 256) / 2 - 74 if value >= 128 else value / 2 - 74
        for value in rssi_gfsk_values
    ]
    binned_gfsk_dBm = [
        rssi_gfsk_dBm[i : i + range_count]
        for i in range(0, len(rssi_gfsk_dBm), range_count)
    ]
    mean_gfsk_dBm = [sum(bin) / len(bin) for bin in binned_gfsk_dBm]

    # Analyze antenna gain from PA table measurements at 1m
    analyze_antenna_gain(
        mean_gfsk_dBm, pa_output_settings, distance_m=1.0, frequency_hz=433e6
    )

    plot_all_rssi(
        rssi_gfsk_file,
        "4_rssi/plots/rssi_gfsk_plot.png",
        "4_rssi/plots/rssi_gfsk_plot_dBm.png",
        args.interactive,
        range_count,
        enable_friis=False,
        x_labels=pa_output_settings,
        x_label_name="PA Output Power (dBm)",
    )


if __name__ == "__main__":
    main()
