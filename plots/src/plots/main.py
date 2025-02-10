#!/usr/bin/env python3
import argparse
from datetime import datetime

import matplotlib.pyplot as plt


def parse_commit_data(file_path=None, data_string=None):
    """Parse commit data from either a file or string input.

    Args:
        file_path (str, optional): Path to file containing commit data
        data_string (str, optional): String containing commit data

    Returns:
        tuple: Lists of dates and commit counts
    """
    if file_path:
        with open(file_path, "r") as f:
            content = f.read()
    else:
        content = data_string

    dates = []
    commits = []

    for line in content.strip().split("\n"):
        if not line:
            continue
        count, date = line.split()
        dates.append(datetime.strptime(date, "%Y-%m-%d"))
        commits.append(int(count))

    return dates, commits


def plot_commits(dates, commits, output_path=None):
    """Create a plot of commits over time.

    Args:
        dates (list): List of datetime objects
        commits (list): List of commit counts
        output_path (str, optional): Path to save the plot
    """
    plt.figure(figsize=(12, 6))
    plt.plot(dates, commits, marker="o", linestyle="-", linewidth=2)
    plt.title("Git Commits Per Day")
    plt.xlabel("Date")
    plt.ylabel("Number of Commits")
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.xticks(rotation=45)
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path)
    else:
        plt.show()


def main():
    parser = argparse.ArgumentParser(description="Plot git commit history")
    parser.add_argument("--input", "-i", help="Input file containing commit data")
    parser.add_argument("--output", "-o", help="Output file path for the plot")
    args = parser.parse_args()

    # Use sample data if no input file is provided
    sample_data = """
8 2024-07-23
2 2024-07-24
10 2024-08-12
8 2024-08-13
13 2024-08-14
14 2024-08-15
1 2024-08-16
2 2024-08-18
1 2024-08-19
1 2024-08-20
4 2024-08-21
12 2024-08-22
5 2024-08-23
2 2024-08-24
10 2024-08-26
2 2024-08-27
4 2024-08-28
"""

    dates, commits = parse_commit_data(
        file_path=args.input,
        data_string=sample_data if not args.input else None,
    )

    plot_commits(dates, commits, args.output)


if __name__ == "__main__":
    main()
