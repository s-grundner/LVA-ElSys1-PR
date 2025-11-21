#!/usr/bin/env python3

import struct
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


def plot_and_save(data, output_path):
    """
    Plots the data and saves it as a PNG file.
    """
    plt.figure(figsize=(10, 6))
    plt.plot(data, label="Signal")
    plt.title("Bits Visualization")
    plt.xlabel("Sample Index")
    plt.ylabel("Amplitude")
    plt.legend()
    plt.grid(True)
    plt.savefig(output_path)
    plt.close()


def main():
    input_file = "bits.gnc"
    output_file = "1_bits_gnc.png"

    print(f"Reading data from {input_file}...")
    data = read_gnc_file(input_file)

    print(f"Generating plot and saving to {output_file}...")
    plot_and_save(data, output_file)

    print("Done.")


if __name__ == "__main__":
    main()
