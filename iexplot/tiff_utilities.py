import numpy as np
import tifffile

def convert_dtype(dtype):
    """Map a TIFF tag dtype name to its single-character struct/tifffile code.

    Inspects the lowercased dtype string and returns the first matching
    code: 'h' (short), 'i' (int/long), 's' (string/ascii), or 'd' (double).
    If none of those characters is present, the lowercased string is
    returned unchanged.

    Parameters
    ----------
    dtype : str
        Name of the tag dtype (e.g. as reported by ``tifffile`` tags).

    Returns
    -------
    str
        The single-character dtype code, or the lowercased input if no
        known character is found.
    """
    dtype_str = dtype.lower()
    if 'h' in dtype_str:
        return 'h'
    elif 'i' in dtype_str:
        return 'i'
    elif 's' in dtype_str:
        return 's'
    elif 'd' in dtype_str:
        return 'd'
    else:
        return dtype_str

            
def save_tiff_w_metadata(target_path, data, metadata_path):
    """Write image data to a TIFF, carrying over private metadata tags.

    Reads the first page of an existing TIFF at ``metadata_path`` and copies
    its private tags (tag codes >= 60000) onto the new file. Standard TIFF
    tags (codes < 60000) are skipped so that ``tifffile`` sets them from the
    data itself. The data array is made C-contiguous if needed before writing.

    Parameters
    ----------
    target_path : str
        Path of the TIFF file to create.
    data : numpy.ndarray
        Image data to write.
    metadata_path : str
        Path of an existing TIFF whose private tags are copied to the output.

    Returns
    -------
    None
    """
    with tifffile.TiffFile(metadata_path) as src:
        src_tags = src.pages[0].tags

        new_tags = []
        for tag in src_tags:
            if tag.code < 60000:
                continue
            new_tags.append((tag.code, convert_dtype(tag.dtype), tag.count, tag.value, True))
    if not data.flags['C_CONTIGUOUS']:
        data = np.ascontiguousarray(data)
    tifffile.imwrite(target_path, data, extratags=new_tags)


def mask_bad_pixels(img, bp_x, bp_y, n_pixel=None, fill='nan'):
    """Replace bad pixels in an image, either with NaN or a local median.

    Each bad pixel at ``(bp_x[i], bp_y[i])`` is first set to NaN. If
    ``fill='nan'`` the NaN-filled image is returned. If ``fill='median'``
    each bad pixel is instead replaced by the ``np.nanmean`` of a local
    window of half-widths ``n_pixel[i] = (nx, ny)`` centered on it (so other
    bad pixels in the window, being NaN, are ignored).

    Parameters
    ----------
    img : numpy.ndarray
        2-D image array indexed as ``img[y, x]``.
    bp_x : sequence of int
        Column (x) indices of the bad pixels.
    bp_y : sequence of int
        Row (y) indices of the bad pixels, paired with ``bp_x``.
    n_pixel : sequence of (int, int), optional
        Per-pixel window half-widths ``(nx, ny)`` used when ``fill='median'``.
        Required for the ``'median'`` fill; unused for ``'nan'``.
    fill : {'nan', 'median'}, optional
        How to fill bad pixels. ``'nan'`` (default) leaves them as NaN;
        ``'median'`` replaces them with the local windowed mean.

    Returns
    -------
    numpy.ndarray
        A new image array with bad pixels filled. For ``fill='nan'`` the
        result is of float dtype (from multiplication by the NaN mask).
    """
    bp_x = np.asarray(bp_x, dtype=int)
    bp_y = np.asarray(bp_y, dtype=int)

    img_nan = img.astype(float, copy=True)
    img_nan[bp_y, bp_x] = np.nan

    if fill == 'nan':
        return img_nan
    elif fill == 'median':
        if n_pixel is None:
            raise ValueError("n_pixel is required when fill='median'")
        ny_img, nx_img = img.shape
        img_median = img_nan.copy()
        for bx, by, (nx, ny) in zip(bp_x, bp_y, n_pixel):
            y0, y1 = max(by - ny, 0), min(by + ny + 1, ny_img)
            x0, x1 = max(bx - nx, 0), min(bx + nx + 1, nx_img)
            img_median[by, bx] = np.nanmean(img_nan[y0:y1, x0:x1])
        return img_median
    else:
        raise ValueError(f"fill must be 'nan' or 'median', got {fill!r}")