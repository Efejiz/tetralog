import numpy as np

class Packer:
    def __init__(self, container):
        self.container = container

    def pack(self, items, strategy="balanced"):
        # 1. STRATEJİ BELİRLEME (Sıralama Algoritması)
        # LIFO (Last In First Out) + Hacim + Yoğunluk
        if strategy == "Density":
            # Yoğunluk (kg/m3) yüksek olanları alta koymaya çalış
            items.sort(key=lambda x: (x.stop_order, x.weight/x.volume, x.volume), reverse=True)
        else:
            # Standart: Önce son durak, sonra büyük hacim
            items.sort(key=lambda x: (x.stop_order, x.volume), reverse=True)

        # Extreme Points mantığına benzer aday nokta yönetimi
        candidate_points = [[0, 0, 0]]

        for item in items:
            placed = False
            
            # --- DUVAR ÖRME & ZEMİN ÖNCELİĞİ ---
            # 1. Y (Derinlik - Tırın arkası)
            # 2. Z (Yükseklik - Zemin)
            # 3. X (Genişlik)
            candidate_points.sort(key=lambda p: (p[1], p[2], p[0]))

            for point in candidate_points:
                # İki yönü de dene (Eğer ürün döndürülebiliyorsa)
                rotations_to_try = [0, 1] if item.can_rotate else [0]
                
                for rot in rotations_to_try:
                    current_dims = item.dims if rot == 0 else [item.dims[1], item.dims[0], item.dims[2]]
                    
                    # 1. Sığma Kontrolü
                    if self._can_place(point, current_dims):
                        # 2. Fizik Kontrolü (Destek + Kırılganlık)
                        if self._is_physically_valid(point, current_dims, item.weight):
                            
                            # YERLEŞTİR
                            item.position = point
                            item.rotation_type = rot
                            self.container.placed_items.append(item)
                            
                            candidate_points.remove(point)
                            
                            # Yeni aday noktalar (Extreme Point mantığıyla)
                            self._add_candidate(candidate_points, [point[0] + current_dims[0], point[1], point[2]]) # Sağ
                            self._add_candidate(candidate_points, [point[0], point[1] + current_dims[1], point[2]]) # Ön
                            self._add_candidate(candidate_points, [point[0], point[1], point[2] + current_dims[2]]) # Üst
                            
                            placed = True
                            break 
                if placed: break
            
            if not placed:
                pass # Dışarıda kaldı

    def calculate_axle_loads(self):
        """Moment prensibiyle (M=F*d) ön ve arka dingil yüklerini hesaplar."""
        total_weight = sum([i.weight for i in self.container.placed_items])
        if total_weight == 0: return 0, 0
        
        total_moment = 0
        for item in self.container.placed_items:
            # Kutunun ağırlık merkezi Y ekseninin ortasıdır
            cog_y = item.position[1] + (item.get_dimension()[1] / 2)
            total_moment += item.weight * cog_y
            
        # Yükün ağırlık merkezi (Center of Gravity)
        load_cog = total_moment / total_weight
        
        # Dingil mesafesi
        wheelbase = self.container.axle_rear_pos - self.container.axle_front_pos
        
        # Arka aksa binen yük (Moment kolu kuralı)
        dist_from_front = load_cog - self.container.axle_front_pos
        rear_load = total_weight * (dist_from_front / wheelbase)
        front_load = total_weight - rear_load
        
        return front_load, rear_load

    def _can_place(self, pos, dims):
        # Sınır kontrolü
        if (pos[0] + dims[0] > self.container.dims[0] or 
            pos[1] + dims[1] > self.container.dims[1] or 
            pos[2] + dims[2] > self.container.dims[2]):
            return False
        
        # Çarpışma kontrolü (AABB)
        for p in self.container.placed_items:
            p_pos = p.position
            p_dims = p.get_dimension()
            if (pos[0] < p_pos[0] + p_dims[0] and pos[0] + dims[0] > p_pos[0] and
                pos[1] < p_pos[1] + p_dims[1] and pos[1] + dims[1] > p_pos[1] and
                pos[2] < p_pos[2] + p_dims[2] and pos[2] + dims[2] > p_pos[2]):
                return False
        return True

    def _is_physically_valid(self, pos, dims, weight):
        """Stabilite ve Kırılganlık Kontrolü"""
        if pos[2] == 0: return True # Zemindeyse OK
        
        # 1. Kırılganlık Kontrolü (Altımdaki kutu kırılgan mı?)
        # Altımdaki alanı tara
        contact_area = 0
        total_base_area = dims[0] * dims[1]
        
        # Kutunun alt tabanı
        z_bottom = pos[2]
        
        for p in self.container.placed_items:
            p_pos = p.position
            p_dims = p.get_dimension()
            
            # Eğer p kutusu, benim kutumun hemen altındaysa
            if abs((p_pos[2] + p_dims[2]) - z_bottom) < 0.1:
                # Kesişim alanını bul
                x_overlap = max(0, min(pos[0]+dims[0], p_pos[0]+p_dims[0]) - max(pos[0], p_pos[0]))
                y_overlap = max(0, min(pos[1]+dims[1], p_pos[1]+p_dims[1]) - max(pos[1], p_pos[1]))
                area = x_overlap * y_overlap
                
                if area > 0:
                    if p.fragile: return False # Kırılgan kutuya basamazsın!
                    contact_area += area
        
        # 2. Stabilite Kontrolü (En az %60 temas gerekli)
        if (contact_area / total_base_area) < 0.60:
            return False # Yeterli destek yok, devrilir
            
        return True

    def _add_candidate(self, candidates, point):
        if (point[0] < self.container.dims[0] and point[1] < self.container.dims[1] and point[2] < self.container.dims[2]):
            if point not in candidates:
                candidates.append(point)