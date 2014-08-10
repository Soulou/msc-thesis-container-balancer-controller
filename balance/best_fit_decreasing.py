class BestFitDecreasing:
    @classmethod
    def pack(clazz, _items, _bins):
        bins = _bins.copy()
        items = _items.copy()
        items_with_index = []

        # The original index is added in pos 0
        for i in range(len(items)):
            items_with_index.append([i] + items[i])

        sorted_items_with_index = sorted(items_with_index, key=lambda i: -i[1])
        mapping = [None] * len(sorted_items_with_index)

        for i_index in range(len(sorted_items_with_index)):
            best_index = -1
            best_capacity = 10000
            for b_index in range(len(bins)):
                if bins[b_index].has_capacity_for(sorted_items_with_index[i_index][1:], type="offline"):
                    rem_cap = bins[b_index].get_remaining_capacity(type="offline")
                    if rem_cap[0] < best_capacity:
                        best_index = b_index
                        best_capacity = rem_cap[0]
            if best_index == -1:
                raise "not enough capacity to pack {}".format(sorted_items_with_index[i_index])
            bins[best_index].add_item(sorted_items_with_index[i_index][1:])
            mapping[sorted_items_with_index[i_index][0]] = best_index

        return {"algorithn": "best-fit-decreasing", "mapping": mapping}
