class Item:
    def __init__(self, name, width, length, height, weight, destination, stop_order, color, fragile=False, can_rotate=True):
        self.name = name
        self.dims = [width, length, height] # [En, Boy, Yükseklik]
        self.weight = weight
        self.volume = width * length * height
        self.destination = destination
        self.stop_order = stop_order
        self.color = color
        self.fragile = fragile # Kırılgan mı? (Üstüne yük binemez)
        self.can_rotate = can_rotate # Döndürülebilir mi?
        
        # Konumlandırma verileri
        self.position = [0, 0, 0] 
        self.rotation_type = 0 # 0: Normal, 1: Döndürülmüş

    def get_dimension(self):
        # Döndürülmüşse En ve Boy yer değiştirir
        if self.rotation_type == 1:
            return [self.dims[1], self.dims[0], self.dims[2]]
        return self.dims

class Container:
    def __init__(self, width, length, height, max_weight):
        self.dims = [width, length, height]
        self.max_weight = max_weight
        self.placed_items = []
        self.total_volume = width * length * height
        
        # Aks Yükü için varsayılan dingil mesafeleri (cm cinsinden)
        # Ön aks: Kabine yakın, Arka aks: Dorsenin arkasında
        self.axle_front_pos = 100 
        self.axle_rear_pos = length - 150