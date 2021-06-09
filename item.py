class Item:
    pass

class ItemStack:
    def __init__(self, itemType: Item, count: int):
        if count > 0:
            self.itemType = itemType
            self.count = count
        else:
            raise ValueError("ItemStack can't be of size 0")

class Carrot(Item):
    pass
