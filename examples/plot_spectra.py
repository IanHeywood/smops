#!/usr/bin/env python3
"""
Compare spectra of the brightest components in the smops output with the
input sub-band model images.

For each component, the plot shows:
  * input sub-band values as points, with horizontal bars spanning each
    sub-band's width;
  * smops output channels as a step line, each step spanning one output
    channel.

Since both are band averages of the same fitted polynomial, the steps should
follow a smooth curve through the input points (exactly through them if the
spectrum is a polynomial of the fitted order or lower). Also printed for each
component: the RMS difference between the input values and the output
channels averaged over each input sub-band.

Requires matplotlib, which is not a smops dependency:
    pip install matplotlib

Example:
    python plot_spectra.py -ip img -op smops-interp-model -n 6
"""
import argparse
import glob
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from astropy.io import fits  # noqa: E402


def freq_axis(header):
    for i in range(1, header.get("NAXIS", 0) + 1):
        ctype = str(header.get(f"CTYPE{i}", "")).upper()
        cunit = str(header.get(f"CUNIT{i}", "")).strip().lower()
        if ctype.startswith("FREQ") or cunit == "hz":
            return i
    raise ValueError("no frequency axis in header")


def find_files(prefix, stokes):
    pref = glob.escape(os.path.abspath(prefix))
    chan = "[0-9]" * 4
    names = glob.glob(f"{pref}-{chan}-{stokes}-model.fits")
    if not names and stokes == "I":
        names = glob.glob(f"{pref}-{chan}-model.fits")
    if not names:
        raise SystemExit(f"No model images found for prefix {prefix}, "
                         f"Stokes {stokes}")
    return names


def read_stack(names, pixels):
    """
    Read frequency, width and the given (y, x) pixel values from each image,
    without loading whole images. Sorted by frequency.
    """
    rows = []
    for name in names:
        with fits.open(name, memmap=True) as hdul:
            hdu = hdul[0]
            ax = freq_axis(hdu.header)
            freq = float(hdu.header[f"CRVAL{ax}"])
            width = abs(float(hdu.header[f"CDELT{ax}"]))
            lead = (0,) * (hdu.header["NAXIS"] - 2)
            vals = np.array([hdu.section[lead + (y, x)]
                             for y, x in pixels], dtype=float)
        rows.append((freq, width, vals))
    rows.sort(key=lambda r: r[0])
    freqs = np.array([r[0] for r in rows])
    widths = np.array([r[1] for r in rows])
    return freqs, widths, np.stack([r[2] for r in rows])


def band_sum(names):
    """Sum of the input images, read one at a time to limit memory use."""
    total = None
    for name in names:
        with fits.open(name, memmap=True) as hdul:
            hdu = hdul[0]
            lead = (0,) * (hdu.header["NAXIS"] - 2)
            plane = np.nan_to_num(np.asarray(
                hdu.section[lead + (slice(None),) * 2], dtype=np.float32))
        total = plane if total is None else total + plane
    return total


def brightest_components(summed, n, min_sep):
    """n brightest pixels in |sum over bands|, at least min_sep apart."""
    score = np.abs(summed)
    # only rank pixels that are non-zero (model images are mostly empty)
    nz = np.flatnonzero(score)
    order = nz[np.argsort(score.flat[nz])[::-1]]
    picked = []
    for idx in order:
        if len(picked) == n:
            break
        y, x = np.unravel_index(idx, score.shape)
        if all(max(abs(y - py), abs(x - px)) >= min_sep
               for py, px in picked):
            picked.append((int(y), int(x)))
    return picked


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument("-ip", "--input-prefix", required=True)
    p.add_argument("-op", "--output-prefix", default="smops-interp-model")
    p.add_argument("-s", "--stokes", default="I")
    p.add_argument("-n", "--ncomp", type=int, default=6,
                   help="number of components to plot (default 6)")
    p.add_argument("--pix", nargs="+", default=None, metavar="X,Y",
                   help="plot these pixels (0-based x,y) instead of the "
                        "brightest ones")
    p.add_argument("--min-sep", type=int, default=5,
                   help="minimum separation in pixels between automatically "
                        "chosen components (default 5)")
    p.add_argument("-o", "--outfile", default="smops-spectra.png")
    args = p.parse_args()
    stokes = args.stokes.upper()

    in_names = find_files(args.input_prefix, stokes)
    out_names = find_files(args.output_prefix, stokes)

    if args.pix:
        pixels = [tuple(int(v) for v in s.split(","))[::-1] for s in args.pix]
    else:
        summed = band_sum(in_names)
        pixels = brightest_components(summed, args.ncomp, args.min_sep)
        del summed
        if not pixels:
            raise SystemExit("Input images are all zero")

    in_f, in_w, in_v = read_stack(in_names, pixels)
    out_f, out_w, out_v = read_stack(out_names, pixels)
    print(f"{len(in_names)} input images, {len(out_names)} output images")

    ncol = min(3, len(pixels))
    nrow = int(np.ceil(len(pixels) / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(5 * ncol, 3.6 * nrow),
                             squeeze=False)
    print(f"{'x':>6} {'y':>6} {'input mean':>12} {'rms(in - out)':>14}")
    for k, (y, x) in enumerate(pixels):
        ax = axes.flat[k]
        # step line: edges of each output channel
        edges = np.append(out_f - out_w / 2, out_f[-1] + out_w[-1] / 2)
        ax.stairs(out_v[:, k], edges / 1e6, baseline=None, color="C0",
                  lw=1.5,
                  label=f"smops output ({len(out_f)} ch)")
        ax.errorbar(in_f / 1e6, in_v[:, k], xerr=in_w / 2e6, fmt="o",
                    color="C3", ms=5, capsize=0, zorder=3,
                    label=f"input ({len(in_f)} bands)")

        # output averaged over each input band, weighted by overlap
        resid = []
        for f, w, v in zip(in_f, in_w, in_v[:, k]):
            lo, hi = f - w / 2, f + w / 2
            overlap = np.clip(np.minimum(edges[1:], hi)
                              - np.maximum(edges[:-1], lo), 0, None)
            if overlap.sum() > 0:
                resid.append(v - np.sum(overlap * out_v[:, k])
                             / overlap.sum())
        rms = np.sqrt(np.mean(np.square(resid))) if resid else np.nan
        print(f"{x:6d} {y:6d} {in_v[:, k].mean():12.4g} {rms:14.4g}")

        ax.set_title(f"pixel x={x}, y={y}", fontsize=10)
        ax.set_xlabel("Frequency (MHz)")
        ax.set_ylabel("Model flux (Jy/pixel)")
    for ax in axes.flat[len(pixels):]:
        ax.set_visible(False)
    axes.flat[0].legend(fontsize=8)
    fig.suptitle(f"Stokes {stokes}: {os.path.basename(args.input_prefix)} "
                 f"vs {os.path.basename(args.output_prefix)}")
    fig.tight_layout()
    fig.savefig(args.outfile, dpi=120)
    print(f"Plot written to {args.outfile}")


if __name__ == "__main__":
    main()
