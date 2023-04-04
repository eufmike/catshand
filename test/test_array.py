import numpy as np

def find_transition_indices(arr, side_of_edge = 'left'):
    if side_of_edge == 'left':
        return np.where ((arr[1:] - arr[:-1])==1)[0]
    elif side_of_edge == 'right':
        return np.where ((arr[1:] - arr[:-1])==-1)[0]

if __name__ == "__main__":
    arr = np.array([0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1])
    transition_indices = find_transition_indices(arr, 'left')
    print(transition_indices)
    transition_indices = find_transition_indices(arr, 'right')
    print(transition_indices)
