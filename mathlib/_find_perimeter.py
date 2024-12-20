import numpy as np
from ._find_perimeter_cy import _get_perimeter
from collections import deque

def find_perimeter(image, level,
                  *,
                  including_contours=False,
                  fully_connected='low'):
    """Find the perimeter of the iso-valued contours in a 2D array for a given level value.

    Uses the "marching squares" method to compute the iso-valued contours of
    the input 2D array for a particular level value. As segments are computed, 
    their lengths are added to a total perimeter value which is eventually returned.

    Parameters
    ----------
    image : 2D ndarray of double
        Input image in which to find contours.
    level : float
        Value along which to find contours in the array.

    Returns
    -------
    perimeter : float
        The perimeter of the computed contours, using the distance between two adjacent 
        image array points as the base unit.
    contour : list of (n,2)-ndarrays
        Each contour is an ndarray of shape ``(n, 2)``,
        consisting of n ``(row, column)`` coordinates along the contour.
        only returned if the

    See Also
    --------
    skimage.measure.find_contours

    Notes
    -----
    The marching squares algorithm is a special case of the marching cubes
    algorithm [1]_.  A simple explanation is available here:

    http://users.polytech.unice.fr/~lingrand/MarchingCubes/algo.html

    .. warning::

       Array coordinates/values are assumed to refer to the *center* of the
       array element. Take a simple example input: ``[0, 1]``. The interpolated
       position of 0.5 in this array is midway between the 0-element (at
       ``x=0``) and the 1-element (at ``x=1``), and thus would fall at
       ``x=0.5``.

    This means that to find reasonable contours, it is best to find contours
    midway between the expected "light" and "dark" values. In particular,
    given a binarized array, *do not* choose to find contours at the low or
    high value of the array. This will often yield degenerate contours,
    especially around structures that are a single array element wide. Instead
    choose a middle value, as above.

    References
    ----------
    .. [1] Lorensen, William and Harvey E. Cline. Marching Cubes: A High
           Resolution 3D Surface Construction Algorithm. Computer Graphics
           (SIGGRAPH 87 Proceedings) 21(4) July 1987, p. 163-170).
           :DOI:`10.1145/37401.37422`

    Examples
    --------
    >>> a = np.zeros((3, 3))
    >>> a[0, 0] = 1
    >>> a
    array([[1., 0., 0.],
           [0., 0., 0.],
           [0., 0., 0.]])
    >>> find_perimeter(a, 0.5)
    0.7071067811865476
    """
    if image.shape[0] < 2 or image.shape[1] < 2:
        raise ValueError("Input array must be at least 2x2.")
    if image.ndim != 2:
        raise ValueError('Only 2D arrays are supported.')
    (perimeter,segments) = _get_perimeter(image, float(level), fully_connected == 'high', including_contours)
    contours = []
    if including_contours:
        contours = _assemble_contours(segments)
    return perimeter, contours



def _assemble_contours(segments):
    current_index = 0
    contours = {}
    starts = {}
    ends = {}
    for from_point, to_point in segments:
        # Ignore degenerate segments.
        # This happens when (and only when) one vertex of the square is
        # exactly the contour level, and the rest are above or below.
        # This degenerate vertex will be picked up later by neighboring
        # squares.
        if from_point == to_point:
            continue

        tail, tail_num = starts.pop(to_point, (None, None))
        head, head_num = ends.pop(from_point, (None, None))

        if tail is not None and head is not None:
            # We need to connect these two contours.
            if tail is head:
                # We need to closed a contour: add the end point
                head.append(to_point)
            else:  # tail is not head
                # We need to join two distinct contours.
                # We want to keep the first contour segment created, so that
                # the final contours are ordered left->right, top->bottom.
                if tail_num > head_num:
                    # tail was created second. Append tail to head.
                    head.extend(tail)
                    # Remove tail from the detected contours
                    contours.pop(tail_num, None)
                    # Update starts and ends
                    starts[head[0]] = (head, head_num)
                    ends[head[-1]] = (head, head_num)
                else:  # tail_num <= head_num
                    # head was created second. Prepend head to tail.
                    tail.extendleft(reversed(head))
                    # Remove head from the detected contours
                    starts.pop(head[0], None)  # head[0] can be == to_point!
                    contours.pop(head_num, None)
                    # Update starts and ends
                    starts[tail[0]] = (tail, tail_num)
                    ends[tail[-1]] = (tail, tail_num)
        elif tail is None and head is None:
            # We need to add a new contour
            new_contour = deque((from_point, to_point))
            contours[current_index] = new_contour
            starts[from_point] = (new_contour, current_index)
            ends[to_point] = (new_contour, current_index)
            current_index += 1
        elif head is None:  # tail is not None
            # tail first element is to_point: the new segment should be
            # prepended.
            tail.appendleft(from_point)
            # Update starts
            starts[from_point] = (tail, tail_num)
        else:  # tail is None and head is not None:
            # head last element is from_point: the new segment should be
            # appended
            head.append(to_point)
            # Update ends
            ends[to_point] = (head, head_num)

    return [np.array(contour) for _, contour in sorted(contours.items())]
