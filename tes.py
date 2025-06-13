import os
import datetime
import psycopg2
from tabulate import tabulate

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def connect_to_db():
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="basdawo",
            user="postgres",
            password="" # your password here
        )
        cur = conn.cursor()
        return conn, cur
    except Exception as e:
        print(f"Terjadi kesalahan saat menghubungkan ke database: {e}")
        return None, None

def login():
    while True:
        clear_console()
        print("\n=== Masuk ke Sistem ===")
        username = input("Masukkan nama pengguna: ").strip()
        password = input("Masukkan kata sandi: ")
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
                print(f"ID Pengguna: {user[0]}, Role: {user[1]}")
                input("Tekan Enter untuk melanjutkan...")
                return user[0], user[1]
            else:
                print("Nama pengguna atau kata sandi salah.")
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
    while True:
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
        if conn is None or cur is None:
            print("Gagal terhubung ke database. Silakan coba lagi nanti.")
            return

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

def katalog_paket(user_id):
    conn, cur = connect_to_db()
    if conn is None or cur is None:
        print("Gagal terhubung ke database.")
        return
    try:
        cur.execute("SELECT id_paket, nama_paket, harga FROM paket ORDER BY id_paket")
        packages = cur.fetchall()
        if not packages:
            print("Tidak ada paket yang tersedia.")
            return
        formatted_packages = []
        for pkg in packages:
            harga_formatted = f"Rp{pkg[2]:,}".replace(',', '.')
            formatted_packages.append((pkg[0], pkg[1], harga_formatted))
        while True:
            clear_console()
            print("=== Katalog Paket ===")
            print(tabulate(formatted_packages, headers=["ID", "Nama Paket", "Harga"], tablefmt="grid"))
            print("\nMenu:")
            print("1. Lihat Deskripsi Paket")
            print("2. Pesan Paket")
            print("0. Kembali")
            pilihan = input("Pilih menu (0/1/2): ").strip()
            if pilihan == '0':
                break
            if pilihan not in ('1', '2'):
                print("Pilihan tidak valid.")
                input("Tekan Enter untuk lanjut...")
                continue
            paket_id_input = input("Masukkan ID paket: ").strip()
            if not paket_id_input.isdigit():
                print("ID paket harus angka.")
                input("Tekan Enter untuk lanjut...")
                continue
            paket_id = int(paket_id_input)
            cur.execute("SELECT nama_paket, deskripsi, harga FROM paket WHERE id_paket = %s", (paket_id,))
            paket = cur.fetchone()
            if not paket:
                print("Paket tidak ditemukan.")
                input("Tekan Enter untuk lanjut...")
                continue
            if pilihan == '1':
                harga_formatted = f"Rp{paket[2]:,}".replace(',', '.')
                clear_console()
                print(f"Nama Paket: {paket[0]}")
                print(f"Harga: {harga_formatted}")
                print("Deskripsi:")
                print(paket[1])
                input("Tekan Enter untuk kembali...")
            else: # pilihan == '2'
                id_pesanan = pesan_paket(user_id, paket_id, cur, conn)
                if id_pesanan:
                    proses_pembayaran(id_pesanan, paket[2], cur, conn)
    except Exception as e:
        print(f"Kesalahan mengambil paket: {e}")
    finally:
        cur.close()
        conn.close()

def pesan_paket(user_id, paket_id, cur, conn):
    while True:
        try:
            jumlah_undangan = int(input("Masukkan jumlah undangan: "))
            if jumlah_undangan <= 0:
                print("Jumlah undangan harus lebih dari 0.")
                continue
            break
        except ValueError:
            print("Masukkan angka yang valid.")
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
    print(tabulate([(t[0], t[1], t[2]) for t in tempat_tersedia], headers=["ID Tempat","Nama Tempat","Kapasitas"], tablefmt="grid"))
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
            y,m,d = map(int, tanggal_acara.split('-'))
            datetime.datetime(y,m,d)
            break
        except Exception:
            print("Format tanggal salah.")
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
    cur.execute("""
        SELECT waktu_mulai, waktu_berakhir FROM pesanan 
        WHERE id_tempat = %s AND tanggal_acara = %s AND progress NOT IN ('selesai','dibatalkan')
    """, (id_tempat, tanggal_acara))
    pesanan_aktif = cur.fetchall()
    def tabrakan(w_start_baru, w_end_baru, w_start_lama, w_end_lama):
        return not (w_end_baru <= w_start_lama or w_start_baru >= w_end_lama)
    for p in pesanan_aktif:
        w_mulai_lama = datetime.datetime.strptime(str(p[0]), "%H:%M:%S")
        w_berakhir_lama = datetime.datetime.strptime(str(p[1]), "%H:%M:%S")
        if tabrakan(dt_mulai, dt_berakhir, w_mulai_lama, w_berakhir_lama):
            print("Jadwal bentrok dengan pesanan lain.")
            input("Tekan Enter untuk lanjut...")
            return None
    nama_pria = input("Nama pengantin pria: ").strip()
    nama_wanita = input("Nama pengantin wanita: ").strip()
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
    try:
        cur.execute("SELECT id_metode_pembayaran, nama_metode_pembayaran FROM metode_pembayaran ORDER BY id_metode_pembayaran")
        daftar_metode = cur.fetchall()
        if not daftar_metode:
            print("Metode pembayaran tidak tersedia.")
            input("Tekan Enter untuk lanjut...")
            return
        while True:
            print(tabulate(daftar_metode, headers=["ID Metode","Nama Metode"], tablefmt="grid"))
            metode_input = input("Pilih ID metode pembayaran: ").strip()
            if not metode_input.isdigit():
                print("Masukkan angka valid.")
                continue
            id_metode = int(metode_input)
            if id_metode not in [m[0] for m in daftar_metode]:
                print("Metode tidak ditemukan.")
                continue
            break
        nama_rekening = input("Nama pemilik rekening: ").strip()
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
    conn, cur = connect_to_db()
    if conn is None or cur is None:
        print("Gagal terhubung ke database.")
        return
    try:
        while True:
            clear_console()
            print("=== Riwayat Pesanan ===")
            print("1. Pesanan Aktif")
            print("2. Pesanan Selesai / Dibatalkan")
            print("0. Kembali")
            pilihan = input("Pilih opsi: ").strip()
            if pilihan == '0':
                break
            elif pilihan == '1':
                cur.execute("""
                    SELECT id_pesanan, id_paket, id_tempat, nama_pengantin_pria, nama_pengantin_wanita,
                    tanggal_acara, waktu_mulai, waktu_berakhir, progress
                    FROM pesanan WHERE id_user = %s AND progress NOT IN ('selesai', 'dibatalkan') ORDER BY tanggal_acara DESC
                """, (user_id,))
                pesanan_aktif = cur.fetchall()
                if not pesanan_aktif:
                    print("Tidak ada pesanan aktif.")
                else:
                    print("\nPesanan Aktif:")
                    rows = []
                    for p in pesanan_aktif:
                        rows.append([p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8]])
                    print(tabulate(rows, headers=["ID Pesanan","ID Paket","ID Tempat","Pengantin Pria","Pengantin Wanita","Tanggal","Mulai","Berakhir","Progress"], tablefmt="grid"))
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
                    print(tabulate(rows, headers=["ID Pesanan","ID Paket","ID Tempat","Pengantin Pria","Pengantin Wanita","Tanggal","Mulai","Berakhir","Status"], tablefmt="grid"))
                    input("\nTekan Enter untuk kembali...")
            else:
                print("Pilihan tidak valid.")
                input("Tekan Enter untuk lanjut...")

    except Exception as e:
        print(f"Kesalahan mengambil riwayat: {e}")
    finally:
        cur.close()
        conn.close()

def konfirmasi_pembayaran():
    """Fitur admin untuk mengonfirmasi pembayaran yang menunggu konfirmasi."""
    conn, cur = connect_to_db()
    if conn is None or cur is None:
        print("Gagal terhubung ke database.")
        return
    try:
        while True:
            clear_console()
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
            print("=== Pembayaran Menunggu Konfirmasi ===")
            headers = ["ID Pembayaran", "ID Pesanan", "Nama Pemilik Rekening", "Nominal", "Waktu Pembayaran", "Nama Pengguna", "Status"]
            print(tabulate(results, headers=headers, tablefmt="grid"))

            pilih_id = input("Masukkan ID Pembayaran yang ingin dikonfirmasi (0 untuk kembali): ").strip()
            if pilih_id == '0':
                break
            if not pilih_id.isdigit() or int(pilih_id) not in [row[0] for row in results]:
                print("ID pembayaran tidak valid.")
                input("Tekan Enter untuk ulangi.")
                continue
            id_pembayaran = int(pilih_id)
            # Pilihan setujui/tolak
            print("1. Setujui pembayaran")
            print("2. Tolak pembayaran")
            konfirmasi = input("Pilih opsi (1/2): ").strip()
            if konfirmasi not in ('1','2'):
                print("Pilihan tidak valid.")
                input("Tekan Enter untuk ulangi.")
                continue
            if konfirmasi == '1':
                # Update status pembayaran jadi disetujui dan pesanan tetap draft
                cur.execute("UPDATE pembayaran SET status_pembayaran = 'disetujui' WHERE id_pembayaran = %s", (id_pembayaran,))
                conn.commit()
                print("Pembayaran disetujui. Pesanan tetap berstatus draft.")
            else:
                # Update status pembayaran jadi ditolak dan pesanan jadi dibatalkan
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
    if conn is None or cur is None:
        print("Gagal terhubung ke database.")
        input("Tekan Enter untuk lanjut...")
        return

    try:
        while True:
            clear_console()
            print("=== Lihat dan Update Pesanan (Admin) ===")
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
                # Pesanan aktif = progress bukan 'selesai' atau 'dibatalkan'
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
                print("\nPesanan Aktif:")
                headers = ["ID Pesanan","ID User","Nama User","ID Paket","ID Tempat","Pengantin Pria","Pengantin Wanita","Tanggal","Mulai","Berakhir","Progress"]
                print(tabulate(pesanan_aktif, headers=headers, tablefmt="grid"))
                # Pilih pesanan untuk detail atau update
                pilih = input("\nMasukkan ID Pesanan untuk detail/update (0 kembali): ").strip()
                if pilih == '0':
                    continue
                if not pilih.isdigit() or int(pilih) not in [p[0] for p in pesanan_aktif]:
                    print("ID pesanan tidak valid.")
                    input("Tekan Enter untuk lanjut...")
                    continue
                id_pesanan = int(pilih)
                # Detail pesanan + info pembayaran
                print_detail_dan_pembayaran(id_pesanan, cur)
                # Update progress
                print("\nEnum progress yang sah:")
                for idx, val in enumerate(progress_enum, start=1):
                    print(f"{idx}. {val}")
                while True:
                    prog_choice = input("Masukkan nomor progress baru (0 batal): ").strip()
                    if prog_choice == '0':
                        print("Update dibatalkan.")
                        break
                    if not prog_choice.isdigit() or not (1 <= int(prog_choice) <= len(progress_enum)):
                        print("Pilihan tidak valid.")
                        continue
                    new_progress = progress_enum[int(prog_choice)-1]
                    # Update di DB
                    cur.execute("UPDATE pesanan SET progress = %s WHERE id_pesanan = %s", (new_progress, id_pesanan))
                    conn.commit()
                    print(f"Progress pesanan {id_pesanan} berhasil diubah menjadi '{new_progress}'.")
                    input("Tekan Enter untuk lanjut...")
                    break
            elif pilihan == '2':
                # Pesanan selesai/dibatalkan = progress 'selesai' atau 'dibatalkan'
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
                print("\nPesanan Selesai / Dibatalkan:")
                headers = ["ID Pesanan","ID User","Nama User","ID Paket","ID Tempat","Pengantin Pria","Pengantin Wanita","Tanggal","Mulai","Berakhir","Status"]
                print(tabulate(pesanan_selesai, headers=headers, tablefmt="grid"))
                pilih = input("\nMasukkan ID Pesanan untuk lihat detail/pay info (0 kembali): ").strip()
                if pilih == '0':
                    continue
                if not pilih.isdigit() or int(pilih) not in [p[0] for p in pesanan_selesai]:
                    print("ID pesanan tidak valid.")
                    input("Tekan Enter untuk lanjut...")
                    continue
                id_pesanan = int(pilih)
                # Tampilkan detail dan info pembayaran, tanpa opsi update progress
                print_detail_dan_pembayaran(id_pesanan, cur)
                input("Tekan Enter untuk kembali...")
    except Exception as e:
        print(f"Kesalahan: {e}")
        input("Tekan Enter untuk lanjut...")
    finally:
        cur.close()
        conn.close()
def print_detail_dan_pembayaran(id_pesanan, cur):
    """Tampilkan info lengkap pesanan dan pembayaran terkait."""
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
    # Tampilkan pembayaran
    cur.execute("""
        SELECT id_pembayaran, id_metode_pembayaran, nama_pemilik_rekening, nominal, waktu_pembayaran, status_pembayaran
        FROM pembayaran WHERE id_pesanan = %s
    """, (id_pesanan,))
    pembayaran = cur.fetchall()
    if pembayaran:
        print("\n=== Informasi Pembayaran ===")
        print(tabulate(pembayaran, headers=["ID Pembayaran","ID Metode","Nama Rekening","Nominal","Waktu Pembayaran","Status"], tablefmt="grid"))
    else:
        print("\nBelum ada data pembayaran untuk pesanan ini.")

def main():
    user_id = None
    user_role = None
    while True:
        clear_console()
        print("=== Selamat Datang di Sistem ===")
        if user_id:
            if user_role == 'klien':
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
                elif pilihan == '4':
                    print("Terima kasih! Sampai jumpa.")
                    break
                else:
                    print("Pilihan tidak valid.")
                    input("Tekan Enter untuk lanjut...")
            elif user_role == 'admin':
                print("1. Logout")
                print("2. Konfirmasi Pembayaran")
                print("3. Lihat dan Update Pesanan")
                print("4. Keluar")
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
