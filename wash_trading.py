import time
from dataclasses import dataclass
from typing import Dict, List, Tuple

@dataclass
class ObjekSisiTransaksi:
    akunTujuan: str
    volumeAset: float
    stempelWaktu: int

class GrafDinamisBursa:
    def __init__(self, theta_max: int = 3, w_max: int = 60, k_depth: int = 3):
        self.tabelKetetanggaan: Dict[str, List[ObjekSisiTransaksi]] = {}
        
        self.theta_max = theta_max  
        self.w_max = w_max          
        self.k_depth = k_depth     

    def _pengecekan_dan_registrasi(self, idPenjual: str, idPembeli: str):
        """Langkah 1: Memastikan kedua entitas terdaftar di dalam graf bursa"""
        if idPenjual not in self.tabelKetetanggaan:
            self.tabelKetetanggaan[idPenjual] = []
        if idPembeli not in self.tabelKetetanggaan:
            self.tabelKetetanggaan[idPembeli] = []

    def _pembersihan_temporal(self, stempelWaktuKini: int):
        """Langkah 2: Menghapus sisi transaksi yang sudah kedaluwarsa secara temporal (Sliding Window)"""
        batasAmbangTemporal = stempelWaktuKini - self.w_max
        totalTerpangkas = 0
        
        for idAkun in self.tabelKetetanggaan:
            senaraiTransaksi = self.tabelKetetanggaan[idAkun]
            while senaraiTransaksi and senaraiTransaksi[0].stempelWaktu < batasAmbangTemporal:
                senaraiTransaksi.pop(0)
                totalTerpangkas += 1
                
        return totalTerpangkas

    def _hitung_derajat_keluar(self, idPenjual: str) -> int:
        """Langkah 3: Perhitungan kuantitatif derajat keluar akun penjual"""
        return len(self.tabelKetetanggaan[idPenjual])

    def _sirkular_dfs(self, simpulKini: str, simpulTarget: str, kedalamanSisa: int) -> bool:
        """Langkah 4: Algoritma DFS yang dimodifikasi untuk pembuktian sirkularitas tertutup"""
        if simpulKini == simpulTarget:
            return True 
            
        if kedalamanSisa <= 0:
            return False  
            
        if simpulKini in self.tabelKetetanggaan:
            for sisi in self.tabelKetetanggaan[simpulKini]:
                if self._sirkular_dfs(sisi.akunTujuan, simpulTarget, kedalamanSisa - 1):
                    return True
                    
        return False

    def proses_instruksi_transaksi(self, idPenjual: str, idPembeli: str, volume: float, waktuKini: int) -> str:
        """Fungsi utama OME mengevaluasi instruksi kecocokan harga (Order Match)"""
        
        self._pengecekan_dan_registrasi(idPenjual, idPembeli)
        
        terpangkas = self._pembersihan_temporal(waktuKini)
        
        derajat_keluar = self._hitung_derajat_keluar(idPenjual)
        
        if derajat_keluar < self.theta_max:
            sisi_baru = ObjekSisiTransaksi(akunTujuan=idPembeli, volumeAset=volume, stempelWaktu=waktuKini)
            self.tabelKetetanggaan[idPenjual].append(sisi_baru)
            return f"[SAH] Transaksi Organik Terpilih. Akun {idPenjual} -> Akun {idPembeli}. (Derajat keluar aman: {derajat_keluar})"
        
        else:
            wash_trading_terdeteksi = self._sirkular_dfs(simpulKini=idPembeli, simpulTarget=idPenjual, kedalamanSisa=self.k_depth)
            
            if wash_trading_terdeteksi:
                return f"[BLOKIR] Interupsi OME! Manipulasi WASH TRADING Terdeteksi pada Akun {idPenjual} (Rantai sirkular <= {self.k_depth} hop)."
            else:
                sisi_baru = ObjekSisiTransaksi(akunTujuan=idPembeli, volumeAset=volume, stempelWaktu=waktuKini)
                self.tabelKetetanggaan[idPenjual].append(sisi_baru)
                return f"[SAH] Transaksi Berhasil setelah Lolos Uji DFS. Akun {idPenjual} -> Akun {idPembeli}."

    def tampilkan_graf(self):
        """Fungsi pembantu untuk mencetak isi tabel ketetanggaan saat ini"""
        print("\n--- STATE STRUKTUR GRAF BURSA ---")
        for akun, senarai in self.tabelKetetanggaan.items():
            tujuan = [f"({s.akunTujuan}, Vol:{s.volumeAset}, T:{s.stempelWaktu})" for s in senarai]
            print(f"Akun {akun} -> {tujuan}")
        print("---------------------------------\n")


if __name__ == "__main__":
    bursa = GrafDinamisBursa(theta_max=3, w_max=60, k_depth=3)
    
    t_start = 1000  
    
    print("=== MEMULAI SIMULASI TRANSAKSI ORGANIK ===")
    print(bursa.proses_instruksi_transaksi("Akun_A", "Akun_B", 1.5, t_start))
    print(bursa.proses_instruksi_transaksi("Akun_A", "Akun_C", 2.0, t_start + 2))
    print(bursa.proses_instruksi_transaksi("Akun_A", "Akun_D", 0.5, t_start + 5))
    
    bursa.tampilkan_graf()
    
    print("=== MENGUJI STRUKTUR MANIPULASI (WASH TRADING) ===")
    print("Membuat rantai konspirasi melingkar pendek...")
    print(bursa.proses_instruksi_transaksi("Akun_B", "Akun_C", 1.2, t_start + 10))
    print(bursa.proses_instruksi_transaksi("Akun_C", "Akun_A", 1.2, t_start + 12))
    
    print("\nAkun_A mencoba mengirim order ke Akun_B lagi (Potensi menutup siklus langsung):")
    hasil_uji = bursa.proses_instruksi_transaksi("Akun_A", "Akun_B", 1.0, t_start + 15)
    print(hasil_uji)
    
    bursa.tampilkan_graf()
    
    print("=== MENGUJI EFEK SLIDING WINDOW (PEMBERSIHAN TEMPORAL) ===")
    t_baru = t_start + 75  
    print(f"Waktu bursa berjalan maju ke: {t_baru} (Transaksi lama di T < 1015 harusnya kedaluwarsa)")
    
    print(bursa.proses_instruksi_transaksi("Akun_A", "Akun_E", 3.0, t_baru))
    
    bursa.tampilkan_graf()
