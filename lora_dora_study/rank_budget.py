"""Exact discrete factor-budget allocation for a small, frozen module set."""
import math


def allocate(squared_spectra, costs, budget):
    """Maximize retained spectral energy at exactly `budget` factor elements.

    Rank zero is allowed. Ties prefer lexicographically smaller rank vectors.
    Energy is a local proxy, not a guarantee about model outputs.
    """
    names = sorted(squared_spectra)
    if not names or set(names) != set(costs):
        raise ValueError('Nonempty aligned modules required')
    if type(budget) is not int or budget < 0:
        raise ValueError('Invalid budget')
    for name in names:
        if type(costs[name]) is not int or costs[name] <= 0:
            raise ValueError('Invalid factor cost')
        values = squared_spectra[name]
        if any(not math.isfinite(x) or x < 0 for x in values):
            raise ValueError('Invalid spectral energy')
        if any(a < b for a, b in zip(values, values[1:])):
            raise ValueError('Spectrum must be descending')
    divisor = math.gcd(*costs.values())
    if budget % divisor:
        raise ValueError('Exact budget infeasible')
    limit = budget // divisor
    states = {0: (0., ())}
    for name in names:
        gains = [0.]
        for value in squared_spectra[name]:
            gains.append(gains[-1] + value)
        step = costs[name] // divisor
        following = {}
        for spent, (gain, ranks) in states.items():
            for rank, added in enumerate(gains):
                total = spent + rank * step
                if total > limit:
                    break
                candidate = (gain + added, ranks + (rank,))
                previous = following.get(total)
                if (previous is None or candidate[0] > previous[0] or
                        (candidate[0] == previous[0] and candidate[1] < previous[1])):
                    following[total] = candidate
        states = following
    if limit not in states:
        raise ValueError('Exact budget infeasible')
    gain, ranks = states[limit]
    return dict(zip(names, ranks)), gain
