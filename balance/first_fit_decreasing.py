class FirstFitDecreasing:
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
            for b_index in range(len(bins)):
                if bins[b_index].has_capacity_for(sorted_items_with_index[i_index][1:], type="offline"):
                    bins[b_index].add_item(sorted_items_with_index[i_index][1:])
                    mapping[sorted_items_with_index[i_index][0]] = b_index
                    break

        return {"algorithm": "first-fit-decreasing", "mapping": mapping}

