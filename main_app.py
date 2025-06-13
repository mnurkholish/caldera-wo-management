import os
import psycopg2

def clear_console():
    """
    Fungsi untuk membersihkan konsol.
    Menggunakan perintah yang sesuai untuk sistem operasi yang digunakan.
    """
    os.system('cls' if os.name == 'nt' else 'clear')

def connect_to_db():
    """
    Fungsi untuk menghubungkan ke database PostgreSQL.
    Mengembalikan koneksi dan cursor jika berhasil, atau None jika gagal.
    """
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

def login():
    """
    Fungsi login yang meminta username dan password.
    Menangani kesalahan dengan opsi untuk mencoba kembali atau keluar (hanya setelah kesalahan atau gagal login).
    Output dalam bahasa Indonesia.
    Menggunakan f-string pada query sesuai permintaan (tidak aman untuk produksi).
    """
    while True:
        clear_console()
        print("\n=== Masuk ke Sistem ===")
        username = input("Masukkan nama pengguna: ").strip()

        password = input("Masukkan kata sandi: ")

        conn, cur = connect_to_db()
        if conn is None or cur is None:
            print("Gagal terhubung ke database. Silakan coba lagi nanti.")
            return None

        try:
            # Gunakan f-string sesuai permintaan (perhatikan keamanan)
            query = f"SELECT * FROM users WHERE username = '{username}' AND user_password = '{password}'"
            cur.execute(query)
            user = cur.fetchone()
            if user:
                print(f"Selamat datang, {user[1]}!")
                return user[0]
            else:
                print("Nama pengguna atau kata sandi salah.")
        except Exception as e:
            print(f"Terjadi kesalahan saat proses login: {e}")
        finally:
            cur.close()
            conn.close()

        # Tanyakan apakah ingin mencoba lagi atau keluar setelah gagal login/kesalahan
        while True:
            retry = input("Apakah Anda ingin mencoba lagi? (y/n): ").strip().lower()
            if retry == 'y':
                break
            elif retry == 'n':
                print("Keluar dari proses login.")
                return None
            else:
                print("Input tidak valid. Ketik 'y' untuk mencoba lagi atau 'n' untuk keluar.")\

def register():
    while True:
        username = input("Masukkan username anda: ")
        email = input("Masukkan email anda: ")
        user_password = input("Masukkan password anda: ")

        print("\nMasukkan data diri anda")
        nama_user = input("Masukkan nama anda: ")
        no_telp = input("Masukkan nomor telepon anda: ")

        # cek apakah input kosong
        if not username or not email or not user_password or not nama_user or not no_telp:
            print("Semua field harus diisi. Silakan coba lagi.")
            retry = input("Apakah Anda ingin mencoba lagi? (y/n): ").strip().lower()
            if retry == 'n':
                print("Pendaftaran dibatalkan.")
                return
            continue

        conn, cur = connect_to_db()
        if conn is None:
            return

        try:
            # Memeriksa apakah username sudah terdaftar
            cur.execute("SELECT * FROM users WHERE username = %s;", (username,))
            if cur.fetchone():
                print("Username sudah terdaftar. Silakan coba username lain.")
                retry = input("Apakah Anda ingin mencoba lagi? (y/n): ").strip().lower()
                if retry == 'n':
                    print("Pendaftaran dibatalkan.")
                    return
                continue

            # Memeriksa apakah email sudah terdaftar
            cur.execute("SELECT * FROM users WHERE email = %s;", (email,))
            if cur.fetchone():
                print("Email sudah terdaftar. Silakan coba email lain.")
                retry = input("Apakah Anda ingin mencoba lagi? (y/n): ").strip().lower()
                if retry == 'n':
                    print("Pendaftaran dibatalkan.")
                    return
                continue

            # Memeriksa apakah nomor telepon sudah terdaftar
            cur.execute("SELECT * FROM users WHERE no_telp = %s;", (no_telp,))
            if cur.fetchone():
                print("Nomor telepon sudah terdaftar. Silakan coba nomor telepon lain.")
                retry = input("Apakah Anda ingin mencoba lagi? (y/n): ").strip().lower()
                if retry == 'n':
                    print("Pendaftaran dibatalkan.")
                    return
                continue

            # Jika tidak ada yang terdaftar, lanjutkan dengan pendaftaran
            cur.execute("""INSERT INTO users (nama_user, username, user_password, email, no_telp, user_role)
                           VALUES (%s, %s, %s, %s, %s, 'klien');""",
                        (nama_user, username, user_password, email, no_telp))
            conn.commit()
            print("Registration successful!")

        except Exception as e:
            print(f"An error occurred during registration: {e}")

        finally:
            cur.close()
            conn.close()

def main():
    pass

if __name__ == "__main__":
    main()
