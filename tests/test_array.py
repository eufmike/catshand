import numpy as np
import pytest


def find_transition_indices(arr: np.ndarray, side_of_edge: str = "left") -> np.ndarray:
    if side_of_edge == "left":
        return np.where((arr[1:] - arr[:-1]) == 1)[0]
    elif side_of_edge == "right":
        return np.where((arr[1:] - arr[:-1]) == -1)[0]
    else:
        raise ValueError(f"side_of_edge must be 'left' or 'right', got {side_of_edge!r}")


@pytest.fixture
def sample_array() -> np.ndarray:
    return np.array([0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1])


def test_left_transitions(sample_array: np.ndarray) -> None:
    indices = find_transition_indices(sample_array, "left")
    # Transitions 0→1 occur at positions 2, 5, 9, 12
    np.testing.assert_array_equal(indices, [1, 4, 8, 11])


def test_right_transitions(sample_array: np.ndarray) -> None:
    indices = find_transition_indices(sample_array, "right")
    # Transitions 1→0 occur after positions 3, 6, 11
    np.testing.assert_array_equal(indices, [3, 6, 10])


def test_invalid_side_raises() -> None:
    arr = np.array([0, 1, 0])
    with pytest.raises(ValueError):
        find_transition_indices(arr, "center")


def test_all_zeros() -> None:
    arr = np.zeros(5, dtype=int)
    assert len(find_transition_indices(arr, "left")) == 0
    assert len(find_transition_indices(arr, "right")) == 0


def test_all_ones() -> None:
    arr = np.ones(5, dtype=int)
    assert len(find_transition_indices(arr, "left")) == 0
    assert len(find_transition_indices(arr, "right")) == 0
