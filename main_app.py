"""Project Sistem Basis Data - Aplikasi Wedding Organizer 'Caldera Party Planner'
   Kelompok 9 Kelas A"""

import os
import datetime
import psycopg2
from tabulate import tabulate

# Fungsi-fungsi Umum
def header(title=None):
    """Menampilkan header aplikasi."""
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=" * 33)
    print("===== Caldera Party Planner =====")
    if title:
        print(f"===== {title.center(21)} =====")
    print("=" * 33)


def connect_to_db():
    """Membuat koneksi ke database PostgreSQL dan mengembalikan koneksi dan cursor."""
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="basdawo",
            user="postgres",
            password="Kholish8306!"
        )
        cur = conn.cursor()
        return conn, cur
    except Exception as e:
        print(f"Terjadi kesalahan saat menghubungkan ke database: {e}")
        return None, None

# Fungsi Login dan Register
def login():
    """Fungsi untuk login (klien atau admin)"""
    while True:
        header("Login")
        username = input("Masukkan nama pengguna: ").strip()
        password = input("Masukkan kata sandi: ")

        if not username or not password:
            print("Nama pengguna dan kata sandi tidak boleh kosong. Silakan coba lagi.")
            retry = input("Apakah Anda ingin mencoba lagi? (y/n): ").strip().lower()
            if retry == 'n':
                input("Keluar dari proses login. Tekan Enter untuk melanjutkan...")
                return None, None
            continue

        conn, cur = connect_to_db()
        if conn is None or cur is None:
            print("Gagal terhubung ke database. Silakan coba lagi nanti.")
            return None, None
        try:
            query = "SELECT id_user, user_role, nama_user FROM users WHERE username = %s AND user_password = %s"
            cur.execute(query, (username, password))
            user = cur.fetchone()
            if user:
                print(f"Selamat datang, {user[2]}!")
                input("Tekan Enter untuk melanjutkan...")
                return user[0], user[1]
            else:
                print("Nama pengguna atau kata sandi salah.")
                retry = input("Apakah Anda ingin mencoba lagi? (y/n): ").strip().lower()
                if retry == 'n':
                    input("Keluar dari proses login. Tekan Enter untuk melanjutkan...")
                    return None, None
        except Exception as e:
            print(f"Terjadi kesalahan saat proses login: {e}")
        finally:
            cur.close()
            conn.close()

        while True:
            retry = input("Apakah Anda ingin mencoba lagi? (y/n): ").strip().lower()
            if retry == 'y':
                break
            elif retry == 'n':
                print("Keluar dari proses login.")
                return None, None
            else:
                print("Input tidak valid. Ketik 'y' untuk mencoba lagi atau 'n' untuk keluar.")

def register():
    """Fungsi untuk register (khusus klien)"""
    while True:
        header("Register")
        username = input("Masukkan username anda: ").strip()
        email = input("Masukkan email anda: ").strip()
        user_password = input("Masukkan password anda: ").strip()

        print("\nMasukkan data diri anda")
        nama_user = input("Masukkan nama anda: ").strip()
        no_telp = input("Masukkan nomor telepon anda: ").strip()

        if not username or not email or not user_password or not nama_user or not no_telp:
            print("Semua field harus diisi. Silakan coba lagi.")
            retry = input("Apakah Anda ingin mencoba lagi? (y/n): ").strip().lower()
            if retry == 'n':
                print("Pendaftaran dibatalkan.")
                return
            continue

        conn, cur = connect_to_db()
        try:
            cur.execute("SELECT 1 FROM users WHERE username = %s;", (username,))
            if cur.fetchone():
                print("Username sudah terdaftar. Silakan coba username lain.")
                retry = input("Apakah Anda ingin mencoba lagi? (y/n): ").strip().lower()
                if retry == 'n':
                    print("Pendaftaran dibatalkan.")
                    return
                continue

            cur.execute("SELECT 1 FROM users WHERE email = %s;", (email,))
            if cur.fetchone():
                print("Email sudah terdaftar. Silakan coba email lain.")
                retry = input("Apakah Anda ingin mencoba lagi? (y/n): ").strip().lower()
                if retry == 'n':
                    print("Pendaftaran dibatalkan.")
                    return
                continue

            cur.execute("SELECT 1 FROM users WHERE no_telp = %s;", (no_telp,))
            if cur.fetchone():
                print("Nomor telepon sudah terdaftar. Silakan coba nomor telepon lain.")
                retry = input("Apakah Anda ingin mencoba lagi? (y/n): ").strip().lower()
                if retry == 'n':
                    print("Pendaftaran dibatalkan.")
                    return
                continue

            cur.execute("""INSERT INTO users (nama_user, username, user_password, email, no_telp, user_role)
                           VALUES (%s, %s, %s, %s, %s, 'klien');""",
                        (nama_user, username, user_password, email, no_telp))
            conn.commit()
            print("Pendaftaran berhasil!")
            input("Tekan Enter untuk melanjutkan...")
            return

        except Exception as e:
            print(f"Terjadi kesalahan saat proses pendaftaran: {e}")

        finally:
            cur.close()
            conn.close()

def katalog_paket(user_id=None):
    """Fungsi untuk menampilkan katalog paket
       dan khusus untuk klien dapat memilih paket untuk dipesan."""
    conn, cur = connect_to_db()
    try:
        cur.execute("SELECT id_paket, nama_paket, harga FROM paket ORDER BY id_paket")
        packages = cur.fetchall()
        if not packages:
            print("Tidak ada paket yang tersedia.")
            return
        formatted_packages = []
        for pkg in packages:
            harga = f"Rp{pkg[2]:,}".replace(',', '.')
            formatted_packages.append((pkg[0], pkg[1], harga))
        while True:
            header("Katalog Paket")
            print(tabulate(formatted_packages, headers=["ID", "Nama Paket", "Harga"], tablefmt="fancy_grid"))
            if user_id:
                print("\nMenu:")
                print("1. Lihat Deskripsi Paket")
                print("2. Pesan Paket")
                print("0. Kembali")
                pilihan = input("Pilih menu (0/1/2): ").strip()
                if pilihan == '0':
                    break
                elif pilihan == '1':
                    id_paket = input("Masukkan ID paket: ").strip()
                    if not id_paket.isdigit():
                        print("ID paket harus angka.")
                        input("Tekan Enter untuk lanjut...")
                        continue
                    id_paket = int(id_paket)
                    cur.execute("SELECT nama_paket, deskripsi, harga FROM paket WHERE id_paket = %s", (id_paket,))
                    paket = cur.fetchone()
                    if not paket:
                        print("Paket tidak ditemukan.")
                        input("Tekan Enter untuk lanjut...")
                        continue
                    harga_formatted = f"Rp{paket[2]:,}".replace(',', '.')
                    header("Deskripsi Paket")
                    print(f"Nama Paket: {paket[0]}")
                    print(f"Harga: {harga_formatted}")
                    print("Deskripsi:")
                    print(paket[1])
                    input("Tekan Enter untuk kembali...")
                elif pilihan == '2':
                    id_paket = input("Masukkan ID paket: ").strip()
                    if not id_paket.isdigit():
                        print("ID paket harus angka.")
                        input("Tekan Enter untuk lanjut...")
                        continue
                    id_paket = int(id_paket)
                    cur.execute("SELECT nama_paket, harga FROM paket WHERE id_paket = %s", (id_paket,))
                    paket = cur.fetchone()
                    if not paket:
                        print("Paket tidak ditemukan.")
                        input("Tekan Enter untuk lanjut...")
                        continue
                    harga_paket = paket[1]
                    id_pesanan = pesan_paket(user_id, id_paket, cur, conn)
                    if id_pesanan:
                        proses_pembayaran(id_pesanan, harga_paket, cur, conn)
            else:
                print("\nMenu:")
                print("1. Lihat Deskripsi Paket")
                print("0. Kembali")
                pilihan = input("Pilih menu (0/1): ").strip()
                if pilihan == '0':
                    break
                elif pilihan == '1':
                    id_paket = input("Masukkan ID paket: ").strip()
                    if not id_paket.isdigit():
                        print("ID paket harus angka.")
                        input("Tekan Enter untuk lanjut...")
                        continue
                    id_paket = int(id_paket)
                    cur.execute("SELECT nama_paket, deskripsi, harga FROM paket WHERE id_paket = %s", (id_paket,))
                    paket = cur.fetchone()
                    if not paket:
                        print("Paket tidak ditemukan.")
                        input("Tekan Enter untuk lanjut...")
                        continue
                    harga_formatted = f"Rp{paket[2]:,}".replace(',', '.')
                    header("Deskripsi Paket")
                    print(f"Nama Paket: {paket[0]}")
                    print(f"Harga: {harga_formatted}")
                    print("Deskripsi:")
                    print(paket[1])
                    input("Tekan Enter untuk kembali...")
                else:
                    print("Pilihan tidak valid.")
                    input("Tekan Enter untuk lanjut...")
    except Exception as e:
        print(f"Kesalahan mengambil paket: {e}")
    finally:
        cur.close()
        conn.close()

def pesan_paket(user_id, paket_id, cur, conn):
    """Fungsi untuk memesan paket, memilih tempat, dan mengatur jadwal acara."""
    while True:
        try:
            jumlah_undangan = int(input("Jumlah undangan: "))
            if jumlah_undangan <= 0:
                print("Jumlah undangan harus lebih dari 0.")
                continue
            break
        except ValueError:
            print("Masukkan angka valid untuk jumlah undangan.")

    cur.execute("""
        SELECT t.id_tempat, t.nama_tempat, t.kapasitas 
        FROM tempat t
        JOIN detail_tempat_paket dtp ON t.id_tempat = dtp.id_tempat
        WHERE dtp.id_paket = %s AND t.kapasitas >= %s
    """, (paket_id, jumlah_undangan))

    tempat_tersedia = cur.fetchall()
    if not tempat_tersedia:
        print("Tidak ada tempat yang sesuai untuk undangan.")
        input("Tekan Enter untuk lanjut...")
        return None

    print(tabulate([(t[0], t[1], t[2]) for t in tempat_tersedia], headers=["ID Tempat","Nama Tempat","Kapasitas"], tablefmt="fancy_grid"))

    while True:
        try:
            id_tempat = int(input("Pilih ID tempat: "))
            if id_tempat not in [t[0] for t in tempat_tersedia]:
                print("ID tidak valid.")
                continue
            break
        except ValueError:
            print("Masukkan angka valid.")

    while True:
        tanggal_acara = input("Tanggal acara (YYYY-MM-DD): ")
        try:
            y, m, d = map(int, tanggal_acara.split('-'))
            datetime.datetime(y, m, d)
            break
        except Exception:
            print("Format tanggal salah.")

    cur.execute("""
        SELECT id_pesanan FROM pesanan 
        WHERE id_tempat = %s AND tanggal_acara = %s AND progress NOT IN ('selesai', 'dibatalkan')
    """, (id_tempat, tanggal_acara))
    pesanan_aktif = cur.fetchall()

    if pesanan_aktif:
        print("Ada pesanan aktif pada tanggal ini.")
        pilihan = input("Apakah Anda ingin memilih tempat lain? (y/n): ").strip().lower()
        if pilihan == 'y':
            return pesan_paket(user_id, paket_id, cur, conn)
        else:
            print("Pesanan dibatalkan.")
            return None

    while True:
        waktu_mulai = input("Waktu mulai (HH:MM:SS): ")
        try:
            datetime.datetime.strptime(waktu_mulai, "%H:%M:%S")
            break
        except Exception:
            print("Format waktu salah.")

    while True:
        waktu_berakhir = input("Waktu berakhir (HH:MM:SS): ")
        try:
            dt_berakhir = datetime.datetime.strptime(waktu_berakhir, "%H:%M:%S")
            dt_mulai = datetime.datetime.strptime(waktu_mulai, "%H:%M:%S")
            if dt_berakhir <= dt_mulai:
                print("Waktu berakhir harus setelah mulai.")
                continue
            break
        except Exception:
            print("Format waktu salah.")

    while True:
        nama_pria = input("Nama pengantin pria: ").strip()
        nama_wanita = input("Nama pengantin wanita: ").strip()
        if nama_pria and nama_wanita:
            break
        print("Nama pengantin tidak boleh kosong. Silakan coba lagi.")

    catatan = input("Catatan (opsional): ").strip()

    try:
        cur.execute("""
            INSERT INTO pesanan (
                id_user, id_paket, id_tempat,
                nama_pengantin_pria, nama_pengantin_wanita,
                tanggal_acara, waktu_mulai, waktu_berakhir,
                jumlah_undangan, catatan_klien, progress
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'draft')
            RETURNING id_pesanan
        """, (user_id, paket_id, id_tempat, nama_pria, nama_wanita, tanggal_acara, waktu_mulai, waktu_berakhir, jumlah_undangan, catatan))
        id_pesanan = cur.fetchone()[0]
        conn.commit()
        print(f"Pesanan dibuat dengan ID {id_pesanan}.")
        input("Tekan Enter untuk lanjut...")
        return id_pesanan
    except Exception as e:
        print(f"Kesalahan saat buat pesanan: {e}")
        input("Tekan Enter untuk lanjut...")
        return None

def proses_pembayaran(id_pesanan, harga_paket, cur, conn):
    """Fungsi untuk melakukan proses pembayaran."""
    try:
        cur.execute("SELECT id_metode_pembayaran, nama_metode_pembayaran FROM metode_pembayaran ORDER BY id_metode_pembayaran")
        daftar_metode = cur.fetchall()
        if not daftar_metode:
            print("Metode pembayaran tidak tersedia.")
            input("Tekan Enter untuk lanjut...")
            return
        while True:
            print(tabulate(daftar_metode, headers=["ID Metode","Nama Metode"], tablefmt="fancy_grid"))
            metode_input = input("Pilih ID metode pembayaran: ").strip()
            if not metode_input.isdigit():
                print("Masukkan angka valid.")
                continue
            id_metode = int(metode_input)
            if id_metode not in [m[0] for m in daftar_metode]:
                print("Metode tidak ditemukan.")
                continue
            break

        while True:
            nama_rekening = input("Nama pemilik rekening: ").strip()
            if not nama_rekening:
                print("Nama pemilik rekening tidak boleh kosong.")
                continue
            break

        while True:
            nominal_input = input(f"Nominal pembayaran (harus sama dengan harga paket Rp{harga_paket:,}): ").replace(',', '').strip()
            if not nominal_input.isdigit():
                print("Nominal harus angka.")
                continue
            nominal = int(nominal_input)
            if nominal != harga_paket:
                print("Nominal tidak sesuai.")
                continue
            break

        cur.execute("""INSERT INTO pembayaran (id_pesanan, id_metode_pembayaran, nama_pemilik_rekening, nominal, status_pembayaran)
                       VALUES (%s, %s, %s, %s, 'menunggu konfirmasi')""",
                    (id_pesanan, id_metode, nama_rekening, nominal))
        conn.commit()
        print("Pembayaran dicatat, menunggu konfirmasi.")
        input("Tekan Enter untuk lanjut...")
    except Exception as e:
        print(f"Kesalahan proses pembayaran: {e}")
        input("Tekan Enter untuk lanjut...")

def lihat_riwayat_pesanan(user_id):
    """Fungsi untuk melihat riwayat pesanan klien."""
    conn, cur = connect_to_db()

    try:
        while True:
            header("Riwayat Pesanan")
            print("1. Pesanan Aktif")
            print("2. Pesanan Selesai / Dibatalkan")
            print("0. Kembali")
            pilihan = input("Pilih opsi: ").strip()
            if pilihan == '0':
                break
            elif pilihan == '1':
                cur.execute("""
                    SELECT id_pesanan, id_paket, id_tempat, nama_pengantin_pria, nama_pengantin_wanita,
                    tanggal_acara, waktu_mulai, waktu_berakhir
                    FROM pesanan WHERE id_user = %s AND progress NOT IN ('selesai', 'dibatalkan') ORDER BY tanggal_acara DESC
                """, (user_id,))
                pesanan_aktif = cur.fetchall()
                if not pesanan_aktif:
                    print("Tidak ada pesanan aktif.")
                else:
                    print("\nPesanan Aktif:")
                    rows = []
                    for p in pesanan_aktif:
                        rows.append([p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7]])
                        headers=["ID Pesanan","ID Paket","ID Tempat","Pengantin Pria","Pengantin Wanita","Tanggal","Jam Mulai","Jam Berakhir"]
                    while True:
                        header("Pesanan Aktif")
                        print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))
                        print("Menu:")
                        print("1 Lihat Progress Pesanan")
                        print("2. Lihat Pembayaran")
                        print("0. Kembali")
                        pilihan = input("Pilih opsi: ").strip()
                        if pilihan == '0':
                            break
                        elif pilihan == '1':
                            id_pesanan = input("Masukkan ID Pesanan untuk melihat progress: ").strip()
                            if not id_pesanan.isdigit() or int(id_pesanan) not in [p[0] for p in pesanan_aktif]:
                                print("ID pesanan tidak valid.")
                                input("Tekan Enter untuk lanjut...")
                                continue
                            cur.execute("SELECT progress FROM pesanan WHERE id_pesanan = %s", (id_pesanan,))
                            progress = cur.fetchone()
                            if progress:
                                print(f"Progress Pesanan {id_pesanan} saat ini: {progress[0]}")
                                input("Tekan Enter untuk lanjut...")
                            else:
                                print("Pesanan tidak ditemukan.")
                                input("Tekan Enter untuk lanjut...")
                        elif pilihan == '2':
                            id_pesanan = input("Masukkan ID Pesanan untuk melihat pembayaran: ").strip()
                            if not id_pesanan.isdigit() or int(id_pesanan) not in [p[0] for p in pesanan_aktif]:
                                print("ID pesanan tidak valid.")
                                input("Tekan Enter untuk lanjut...")
                                continue
                            print_detail_pembayaran(id_pesanan)
                            input("Tekan Enter untuk lanjut...")
                        else:
                            print("Pilihan tidak valid.")
                    input("\nTekan Enter untuk kembali...")

            elif pilihan == '2':
                cur.execute("""
                    SELECT id_pesanan, id_paket, id_tempat, nama_pengantin_pria, nama_pengantin_wanita,
                    tanggal_acara, waktu_mulai, waktu_berakhir, progress
                    FROM pesanan WHERE id_user = %s AND progress IN ('selesai', 'dibatalkan') ORDER BY tanggal_acara DESC
                """, (user_id,))
                pesanan_selesai = cur.fetchall()
                if not pesanan_selesai:
                    print("Tidak ada pesanan selesai atau dibatalkan.")
                else:
                    print("\nPesanan Selesai / Dibatalkan:")
                    rows = []
                    for p in pesanan_selesai:
                        rows.append([p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8]])
                        headers=["ID Pesanan","ID Paket","ID Tempat","Pengantin Pria","Pengantin Wanita",
                                 "Tanggal","Jam Mulai","Jam Berakhir","Progress"]
                    print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))
                    input("\nTekan Enter untuk kembali...")
            else:
                print("Pilihan tidak valid.")
                input("Tekan Enter untuk lanjut...")

    except Exception as e:
        print(f"Kesalahan mengambil riwayat: {e}")
    finally:
        cur.close()
        conn.close()

def print_detail_pembayaran(id_pesanan):
    """Fungsi untuk melihat detail pembayaran dari pesanan tertentu."""
    conn, cur = connect_to_db()
    try:
        cur.execute("""
            SELECT p.id_pembayaran, p.id_metode_pembayaran, p.nama_pemilik_rekening, p.nominal, p.waktu_pembayaran, p.status_pembayaran
            FROM pembayaran p
            WHERE p.id_pesanan = %s
        """, (id_pesanan,))
        pembayaran = cur.fetchall()
        if not pembayaran:
            print("Tidak ada data pembayaran untuk pesanan ini.")
            return
        print("\n=== Detail Pembayaran ===")
        headers = ["ID Pembayaran", "ID Metode", "Nama Rekening", "Nominal", "Waktu Pembayaran", "Status"]
        print(tabulate(pembayaran, headers=headers, tablefmt="fancy_grid"))
    except Exception as e:
        print(f"Kesalahan mengambil detail pembayaran: {e}")
        input("Tekan Enter untuk lanjut...")
    finally:
        cur.close()
        conn.close()

# Fitur Khusus Admin
def konfirmasi_pembayaran():
    """Fitur admin untuk mengonfirmasi pembayaran yang menunggu konfirmasi."""
    conn, cur = connect_to_db()

    try:
        while True:
            header("Konfirmasi Pembayaran")
            cur.execute("""
                SELECT p.id_pembayaran, p.id_pesanan, p.nama_pemilik_rekening, p.nominal, p.waktu_pembayaran, u.nama_user, p.status_pembayaran
                FROM pembayaran p
                JOIN pesanan ps ON p.id_pesanan = ps.id_pesanan
                JOIN users u ON ps.id_user = u.id_user
                WHERE p.status_pembayaran = 'menunggu konfirmasi'
                ORDER BY p.waktu_pembayaran ASC
            """)
            results = cur.fetchall()
            if not results:
                print("Tidak ada pembayaran yang menunggu konfirmasi.")
                input("Tekan Enter untuk kembali.")
                break
            headers = ["ID Pembayaran", "ID Pesanan", "Nama Pemilik Rekening", "Nominal", "Waktu Pembayaran", "Nama Pengguna", "Status"]
            print(tabulate(results, headers=headers, tablefmt="fancy_grid"))

            pilih_id = input("Masukkan ID Pembayaran yang ingin dikonfirmasi (0 untuk kembali): ").strip()
            if pilih_id == '0':
                break
            if not pilih_id.isdigit() or int(pilih_id) not in [row[0] for row in results]:
                print("ID pembayaran tidak valid.")
                input("Tekan Enter untuk ulangi.")
                continue
            id_pembayaran = int(pilih_id)

            print("1. Setujui pembayaran")
            print("2. Tolak pembayaran")
            konfirmasi = input("Pilih opsi (1/2): ").strip()
            if konfirmasi not in ('1','2'):
                print("Pilihan tidak valid.")
                input("Tekan Enter untuk ulangi.")
                continue
            if konfirmasi == '1':
                cur.execute("UPDATE pembayaran SET status_pembayaran = 'disetujui' WHERE id_pembayaran = %s", (id_pembayaran,))
                conn.commit()
                print("Pembayaran disetujui. Pesanan tetap berstatus draft.")
            else:
                cur.execute("SELECT id_pesanan FROM pembayaran WHERE id_pembayaran = %s", (id_pembayaran,))
                id_pesanan = cur.fetchone()[0]
                cur.execute("UPDATE pembayaran SET status_pembayaran = 'ditolak' WHERE id_pembayaran = %s", (id_pembayaran,))
                cur.execute("UPDATE pesanan SET progress = 'dibatalkan' WHERE id_pesanan = %s", (id_pesanan,))
                conn.commit()
                print("Pembayaran ditolak. Pesanan diubah menjadi dibatalkan.")
            input("Tekan Enter untuk lanjut.")

    except Exception as e:
        print(f"Kesalahan dalam konfirmasi pembayaran: {e}")
        input("Tekan Enter untuk lanjut.")
    finally:
        cur.close()
        conn.close()

def lihat_update_pesanan():
    """
    Fitur admin untuk melihat dan update pesanan:
    - Pilihan pesanan aktif dan selesai/dibatalkan
    - Update progress pada pesanan aktif sesuai enum progress_enum
    - Melihat detail informasi pembayaran pada pesanan apapun
    """
    progress_enum = [
        'draft',
        'meeting klien',
        'persiapan acara',
        'gladi bersih',
        'acara berlangsung',
        'selesai',
        'dibatalkan'
    ]
    conn, cur = connect_to_db()

    try:
        while True:
            header("Lihat dan Update Pesanan")
            print("1. Pesanan Aktif")
            print("2. Pesanan Selesai / Dibatalkan")
            print("0. Kembali")
            pilihan = input("Pilih opsi: ").strip()
            if pilihan == '0':
                break
            elif pilihan not in ('1', '2'):
                print("Pilihan tidak valid.")
                input("Tekan Enter untuk lanjut...")
                continue
            if pilihan == '1':
                cur.execute("""
                    SELECT ps.id_pesanan, ps.id_user, u.nama_user, ps.id_paket, ps.id_tempat,
                        ps.nama_pengantin_pria, ps.nama_pengantin_wanita, ps.tanggal_acara,
                        ps.waktu_mulai, ps.waktu_berakhir, ps.progress
                    FROM pesanan ps
                    JOIN users u ON ps.id_user = u.id_user
                    WHERE ps.progress NOT IN ('selesai','dibatalkan')
                    ORDER BY ps.tanggal_acara DESC
                """)
                pesanan_aktif = cur.fetchall()
                if not pesanan_aktif:
                    print("\nTidak ada pesanan aktif.")
                    input("Tekan Enter untuk lanjut...")
                    continue
                header("Lihat dan Update Pesanan Aktif")
                headers = ["ID Pesanan","ID User","Nama User","ID Paket","ID Tempat","Pengantin Pria","Pengantin Wanita","Tanggal","Mulai","Berakhir","Progress"]
                print(tabulate(pesanan_aktif, headers=headers, tablefmt="fancy_grid"))

                pilih = input("\nMasukkan ID Pesanan untuk detail/update (0 kembali): ").strip()
                if pilih == '0':
                    continue
                if not pilih.isdigit() or int(pilih) not in [p[0] for p in pesanan_aktif]:
                    print("ID pesanan tidak valid.")
                    input("Tekan Enter untuk lanjut...")
                    continue

                id_pesanan = int(pilih)
                print_detail_dan_pembayaran(id_pesanan)
                print("\nEnum progress yang sah:")
                for idx, val in enumerate(progress_enum, start=1):
                    print(f"{idx}. {val}")
                while True:
                    prog_choice = input("Masukkan nomor progress baru (0 batal): ").strip()
                    if prog_choice == '0':
                        print("Update dibatalkan.")
                        break
                    if not prog_choice.isdigit() or not 1 <= int(prog_choice) <= len(progress_enum):
                        print("Pilihan tidak valid.")
                        continue
                    new_progress = progress_enum[int(prog_choice)-1]

                    cur.execute("UPDATE pesanan SET progress = %s WHERE id_pesanan = %s", (new_progress, id_pesanan))
                    conn.commit()
                    print(f"Progress pesanan {id_pesanan} berhasil diubah menjadi '{new_progress}'.")
                    input("Tekan Enter untuk lanjut...")
                    break

            elif pilihan == '2':
                cur.execute("""
                    SELECT ps.id_pesanan, ps.id_user, u.nama_user, ps.id_paket, ps.id_tempat,
                        ps.nama_pengantin_pria, ps.nama_pengantin_wanita, ps.tanggal_acara,
                        ps.waktu_mulai, ps.waktu_berakhir, ps.progress
                    FROM pesanan ps
                    JOIN users u ON ps.id_user = u.id_user
                    WHERE ps.progress IN ('selesai','dibatalkan')
                    ORDER BY ps.tanggal_acara DESC
                """)
                pesanan_selesai = cur.fetchall()
                if not pesanan_selesai:
                    print("\nTidak ada pesanan selesai atau dibatalkan.")
                    input("Tekan Enter untuk lanjut...")
                    continue
                header("Pesanan Selesai / Dibatalkan")
                headers = ["ID Pesanan","ID User","Nama User","ID Paket","ID Tempat","Pengantin Pria","Pengantin Wanita","Tanggal","Mulai","Berakhir","Status"]
                print(tabulate(pesanan_selesai, headers=headers, tablefmt="fancy_grid"))
                pilih = input("\nMasukkan ID Pesanan untuk lihat detail/pay info (0 kembali): ").strip()
                if pilih == '0':
                    continue
                if not pilih.isdigit() or int(pilih) not in [p[0] for p in pesanan_selesai]:
                    print("ID pesanan tidak valid.")
                    input("Tekan Enter untuk lanjut...")
                    continue
                id_pesanan = int(pilih)
                # Tampilkan detail dan info pembayaran, tanpa opsi update progress
                print_detail_dan_pembayaran(id_pesanan)
                input("Tekan Enter untuk kembali...")
    except Exception as e:
        print(f"Kesalahan: {e}")
        input("Tekan Enter untuk lanjut...")
    finally:
        cur.close()
        conn.close()

def print_detail_dan_pembayaran(id_pesanan):
    """Tampilkan info lengkap pesanan dan pembayaran terkait (Admin)."""
    conn, cur = connect_to_db()
    cur.execute("""
        SELECT id_pesanan, id_user, id_paket, id_tempat, nama_pengantin_pria, nama_pengantin_wanita,
               tanggal_acara, waktu_mulai, waktu_berakhir, jumlah_undangan, catatan_klien, progress
        FROM pesanan WHERE id_pesanan = %s
    """, (id_pesanan,))
    pesan = cur.fetchone()
    if not pesan:
        print("Pesanan tidak ditemukan.")
        return
    print("\n=== Detail Pesanan ===")
    labels = ["ID Pesanan", "ID User", "ID Paket", "ID Tempat", "Pengantin Pria", "Pengantin Wanita",
              "Tanggal Acara", "Waktu Mulai", "Waktu Berakhir", "Jumlah Undangan", "Catatan Klien", "Progress"]
    for label, val in zip(labels, pesan):
        print(f"{label}: {val}")

    cur.execute("""
        SELECT id_pembayaran, id_metode_pembayaran, nama_pemilik_rekening, nominal, waktu_pembayaran, status_pembayaran
        FROM pembayaran WHERE id_pesanan = %s
    """, (id_pesanan,))
    pembayaran = cur.fetchall()
    if pembayaran:
        print("\n=== Informasi Pembayaran ===")
        print(tabulate(pembayaran, headers=["ID Pembayaran","ID Metode","Nama Rekening","Nominal","Waktu Pembayaran","Status"], tablefmt="fancy_grid"))
    else:
        print("\nBelum ada data pembayaran untuk pesanan ini.")

    cur.close()
    conn.close()

def input_paket():
    """Fungsi untuk menambahkan paket baru ke database."""
    while True:
        header("Tambah Paket Baru")
        nama_paket = input("Masukkan nama paket: ").strip()
        harga = input("Masukkan harga paket (dalam angka): ").strip()
        deskripsi = input("Masukkan deskripsi paket: ").strip()

        if not nama_paket or not harga.isdigit() or not deskripsi:
            print("Semua field harus diisi dengan benar. Pastikan nama paket dan deskripsi tidak kosong, dan harga valid.")
            retry = input("Apakah Anda ingin mencoba lagi? (y/n): ").strip().lower()
            if retry == 'n':
                print("Paket tidak ditambahkan.")
                return
            continue

        conn, cur = connect_to_db()

        cur.execute("SELECT 1 FROM paket WHERE nama_paket = %s;", (nama_paket,))
        if cur.fetchone():
            print("Paket dengan nama ini sudah ada. Silakan coba nama lain.")
            retry = input("Apakah Anda ingin mencoba lagi? (y/n): ").strip().lower()
            if retry == 'n':
                print("Paket tidak ditambahkan.")
                return
            continue

        try:
            cur.execute("""INSERT INTO paket (nama_paket, harga, deskripsi) VALUES (%s, %s, %s);""",
                        (nama_paket, int(harga), deskripsi))
            conn.commit()
            print("Paket baru berhasil ditambahkan!")
            input("Tekan Enter untuk kembali...")
            return
        except Exception as e:
            print(f"Gagal menambahkan paket baru: {e}")

        finally:
            cur.close()
            conn.close()

def menu_edit_paket():
    """Fungsi untuk menampilkan menu edit paket."""
    while True:
        conn, cur = connect_to_db()

        if conn is None or cur is None:
            print("Gagal terhubung ke database. Silakan coba lagi nanti.")
            return

        header("Edit Paket")
        print("Daftar Paket:")
        headers = ["ID Paket", "Nama Paket", "Harga"]
        cur.execute("SELECT id_paket, nama_paket, harga FROM paket ORDER BY id_paket")
        packages = cur.fetchall()
        if not packages:
            print("Tidak ada paket yang tersedia untuk diedit.")
            input("Tekan Enter untuk kembali...")
            return
        formatted_packages = [(pkg[0], pkg[1], f"Rp{pkg[2]:,}".replace(',', '.')) for pkg in packages]
        print(tabulate(formatted_packages, headers=headers, tablefmt="fancy_grid"))
        try:
            id_paket = int(input("Masukkan ID paket yang ingin diedit: ").strip())
            if id_paket not in [pkg[0] for pkg in packages]:
                print("ID paket tidak valid. Silakan coba lagi.")
                continue
        except ValueError:
            print("ID paket harus berupa angka. Silakan coba lagi.")
            continue
        nama_baru = input("Masukkan nama baru (kosongkan jika tidak ingin mengubah): ").strip()
        deskripsi_baru = input("Masukkan deskripsi baru (kosongkan jika tidak ingin mengubah): ").strip()
        harga_baru = input("Masukkan harga baru (kosongkan jika tidak ingin mengubah): ").strip()
        if harga_baru:
            try:
                harga_baru = int(harga_baru.replace('.', '').replace(',', ''))
            except ValueError:
                print("Harga harus berupa angka. Silakan coba lagi.")
                continue
        else:
            harga_baru = None
        edit_paket(id_paket, nama_baru, deskripsi_baru, harga_baru)

        cur.close()


def edit_paket(id_paket, nama_baru=None, deskripsi_baru=None, harga_baru=None):
    """Fungsi untuk mengedit data paket berdasarkan ID."""
    conn, cur = connect_to_db()
    if conn is None or cur is None:
        return

    try:
        cur.execute("SELECT * FROM paket WHERE id_paket = %s", (id_paket,))
        paket = cur.fetchone()
        if not paket:
            print("Paket dengan ID tersebut tidak ditemukan.")
            return

        if nama_baru:
            cur.execute("UPDATE paket SET nama_paket = %s WHERE id_paket = %s", (nama_baru, id_paket))
        if deskripsi_baru:
            cur.execute("UPDATE paket SET deskripsi = %s WHERE id_paket = %s", (deskripsi_baru, id_paket))
        if harga_baru is not None:
            cur.execute("UPDATE paket SET harga = %s WHERE id_paket = %s", (harga_baru, id_paket))

        conn.commit()
        print("Data paket berhasil diperbarui.")
    except Exception as e:
        print("Terjadi kesalahan saat mengedit:", e)
    finally:
        cur.close()
        conn.close()

def delete_paket():
    """Fungsi untuk menghapus paket dari database."""
    conn, cur = connect_to_db()

    while True:
        header("Hapus Paket")

        print("Daftar Paket:")
        headers = ["ID Paket", "Nama Paket", "Harga"]
        cur.execute("SELECT id_paket, nama_paket, harga FROM paket ORDER BY id_paket")
        packages = cur.fetchall()
        if not packages:
            print("Tidak ada paket yang tersedia untuk dihapus.")
            input("Tekan Enter untuk kembali...")
            return
        formatted_packages = [(pkg[0], pkg[1], f"Rp{pkg[2]:,}".replace(',', '.')) for pkg in packages]
        print(tabulate(formatted_packages, headers=headers, tablefmt="fancy_grid"))

        try:
            paket_id = int(input("Masukkan ID paket yang ingin dihapus: ").strip())

            if paket_id not in [pkg[0] for pkg in packages]:
                print("ID paket tidak valid. Silakan coba lagi.")
                continue

        except ValueError:
            print("ID paket harus berupa angka. Silakan coba lagi.")
            retry = input("Apakah Anda ingin mencoba lagi? (y/n): ").strip().lower()
            if retry == 'n':
                print("Penghapusan paket dibatalkan.")
                return
            continue

        cur.execute("DELETE FROM paket WHERE id_paket = %s;", (paket_id,))
        conn.commit()
        print(f"Paket dengan ID {paket_id} berhasil dihapus.")
        retry = input("Apakah Anda ingin menghapus paket lain? (y/n): ").strip().lower()
        if retry == 'n':
            print("Penghapusan paket selesai.")
            break

        cur.close()
        conn.close()
        input("Tekan Enter untuk kembali...")

def main():
    """Fungsi utama untuk menjalankan sistem."""
    user_id = None
    user_role = None
    while True:
        if user_id:
            if user_role == 'klien':
                header("Menu Klien")
                print("1. Logout")
                print("2. Lihat Katalog Paket")
                print("3. Lihat Riwayat Pesanan")
                print("4. Keluar")
                pilihan = input("Pilih opsi: ").strip()
                if pilihan == '1':
                    user_id = None
                    user_role = None
                    print("Logout berhasil.")
                    input("Tekan Enter untuk lanjut...")
                elif pilihan == '2':
                    katalog_paket(user_id)
                elif pilihan == '3':
                    lihat_riwayat_pesanan(user_id)
                    input("Tekan Enter untuk lanjut...")
                elif pilihan == '4':
                    print("Terima kasih! Sampai jumpa.")
                    break
                else:
                    print("Pilihan tidak valid.")
                    input("Tekan Enter untuk lanjut...")
            elif user_role == 'admin':
                header("Menu Admin")
                print("1. Logout")
                print("2. Konfirmasi Pembayaran")
                print("3. Lihat dan Update Pesanan")
                print("4. Input Paket Baru")
                print("5. Hapus Paket")
                print("6. Edit Paket")
                print("7. Keluar")
                pilihan = input("Pilih opsi: ").strip()
                if pilihan == '1':
                    user_id = None
                    user_role = None
                    print("Logout berhasil.")
                    input("Tekan Enter untuk lanjut...")
                elif pilihan == '2':
                    konfirmasi_pembayaran()
                elif pilihan == '3':
                    lihat_update_pesanan()
                elif pilihan == '4':
                    input_paket()
                elif pilihan == '5':
                    delete_paket()
                elif pilihan == '6':
                    menu_edit_paket()
                    input("Tekan Enter untuk lanjut...")
                elif pilihan == '7':
                    print("Terima kasih! Sampai jumpa.")
                    break
                else:
                    print("Pilihan tidak valid.")
                    input("Tekan Enter untuk lanjut...")
            else:
                print("Role user tidak dikenali, logout otomatis.")
                user_id = None
                user_role = None
                input("Tekan Enter untuk lanjut...")
        else:
            header("Selamat Datang")
            print("1. Login")
            print("2. Daftar")
            print("3. Keluar")
            pilihan = input("Pilih opsi: ").strip()
            if pilihan == '1':
                user_id, user_role = login()
            elif pilihan == '2':
                register()
            elif pilihan == '3':
                print("Terima kasih! Sampai jumpa.")
                break
            else:
                print("Pilihan tidak valid.")
                input("Tekan Enter untuk lanjut...")

if __name__ == "__main__":
    main()
