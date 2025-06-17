import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import io
from io import BytesIO

# ===============================
# Konfigurasi page
# ===============================
st.set_page_config(
    page_title="BatterHub 🍔",
    page_icon="🍔",
    layout="centered"
)

# ===============================
# 💰 Fungsi Format Rupiah
# ===============================
def format_rupiah(angka):
    return f"Rp {angka:,.0f}". replace(",", ".")

# ===============================
# 🔐 Login & Seession State
# ===============================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = None
if "username" not in st.session_state:
    st.session_state.username = None

# Dummy hardcoded credentials
USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "buyer": {"password": "buyer123", "role": "buyer"}
}

# =============================
# 🔐 Login & Register Page
# =============================
def login_page():
    st.title("🔐 Login / Register")
    tab_login, tab_register = st.tabs(["Login", "Buat Akun"])

    # --- LOGIN TAB ---
    with tab_login:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            user = USERS.get(username)
            if user and user["password"] == password:
                st.session_state.logged_in = True
                st.session_state.role = user["role"]
                st.session_state.username = username
                st.success(f"Selamat datang, {username} ({user['role']})!")
                st.rerun()
            else:
                conn = sqlite3.connect("users.db")
                c = conn.cursor()
                c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
                result = c.fetchone()
                conn.close()
                if result:
                    st.session_state.logged_in = True
                    st.session_state.username = result[4]
                    st.session_state.role = result[6]
                    st.success(f"Selamat datang, {result[4]} ({result[6]})!")
                    st.rerun()
                else:
                    st.error("Username atau password salah.")

    # --- REGISTER TAB ---
    with tab_register:
        new_name = st.text_input("Nama Lengkap")
        new_alamat = st.text_area("Alamat")
        new_hp = st.text_input("No. Telepon")
        new_username = st.text_input("Buat Username")
        new_password = st.text_input("Buat Password", type="password")
        admin_code = st.text_input("Kode Admin (opsional)")

        new_role = "admin" if admin_code == "BATTERADMIN2024" else "buyer"

        if st.button("Daftar"):
            if new_name and new_alamat and new_hp and new_username and new_password:
                try:
                    conn = sqlite3.connect("users.db")
                    c = conn.cursor()
                    c.execute("""
                        CREATE TABLE IF NOT EXISTS users ( 
                            id INTEGER PRIMARY KEY AUTOINCREMENT, 
                            nama TEXT, 
                            alamat TEXT, 
                            no_hp TEXT,
                            username TEXT UNIQUE,
                            password TEXT,
                            role TEXT
                        )
                    """)
                    c.execute("INSERT INTO users (nama, alamat, no_hp, username, password, role) VALUES (?, ?, ?, ?, ?, ?)",
                              (new_name, new_alamat, new_hp, new_username, new_password, new_role))
                    conn.commit()
                    conn.close()
                    st.success("Pendaftaran berhasil! Silakan login.")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("Username sudah digunakan. Coba yang lain.")
            else:
                st.warning("Harap isi semua data.")


if not st.session_state.logged_in:
    login_page()
    st.stop()

def logout():
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None
    st.session_state.clear()
    st.rerun()

# ====================
# Init DB for Keuangan
# ====================
def init_db():
    conn = sqlite3.connect("keuangan.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS transaksi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            menu TEXT,
            jumlah INTEGER,
            subtotal INTEGER,
            tanggal TEXT
        )      
    """)
    conn.commit()
    conn.close()

init_db()
def alter_table_transaksi():
    with sqlite3.connect("keuangan.db") as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(transaksi)")
        kolom = [row[1] for row in cursor.fetchall()]
        if "menu" not in kolom:
            cursor.execute("ALTER TABLE transaksi ADD COLUMN menu TEXT")
            conn.commit()

alter_table_transaksi()


# ===========================
# Custom CSS for UI
# ===========================
st.markdown("""
    <style>
        .stButton>button {
            background-color: #FF8000;
            color: white;
            font-weight: bold;
            border-radius: 10px;
        }
        .stSidebar {
            background-color: #E0FFE0;
        }
        .block-container {
            padding-top: 2rem;
        }
    </style>
""", unsafe_allow_html=True) 
                          
# ====================
# Daftar Menu Makanan
# ====================
if "menu" not in st.session_state:
    st.session_state.menu = {
        "Mentai Burn Paket": {"harga": 27000, "satuan" : "porsi"},
        "Spicy Lava Paket": {"harga": 27000, "satuan" : "porsi"},
        "Nashville Hot Paket": {"harga": 27000, "satuan" : "porsi"},
        "OG Chicken Paket": {"harga": 25000, "satuan" : "porsi"},
        "Cheesy Lovers Paket": {"harga": 27000, "satuan": "porsi"},
        "Velve Beef Paket": {"harga": 27000, "satuan": "porsi"},
        "Caramalized Honey Paket": {"harga": 28000, "satuan": "porsi"},
        "Mentai Burn Ala carte": {"harga": 20000, "satuan": "porsi"},
        "Spicy Lava Ala carte": {"harga": 20000, "satuan": "porsi"},
        "Nashville Ala carte": {"harga": 20000, "satuan": "porsi"},
        "OG Chicken Ala carte": {"harga": 18000, "satuan": "porsi"},
        "Cheesy Lovers Ala carte": {"harga": 20000, "satuan": "porsi"},
        "Velve Beef Ala carte": {"harga": 20000, "satuan": "porsi"},
        "Caramalized Honey Ala carte": {"harga": 20000, "satuan": "porsi"},
    }

# ====================
# Keranjang
# ====================
if "keranjang" not in st.session_state:
    st.session_state.keranjang = {}

# ====================
# Sidebar
# ====================
st.sidebar.title("🍔 BatterHub")
st.sidebar.markdown(f"Login sebagai: '{st.session_state.role}'")
if st.sidebar.button("Logout"):
    logout()
menu = st.sidebar.radio("Navigasi", ["Home", "Menu", "Checkout", "Transaksi", "Contact"])

# ====================
# Landing Page
# ====================
if menu == "Home":
    st.image(r"logo sim.jpg", width=120)
    st.title("Selamat Datang di BatterHub")
    st.image("background sim.jpg", use_container_width=True)
    st.subheader("Belanja Cepat")
    st.markdown("Kami hadir untuk memudahkan para pelanggan dalam memesan makanan")

# ====================
# Daftar Menu
# ====================
elif menu == "Menu":
    st.title("Daftar Menu")
    if st.session_state.role != "buyer":
       st.warning("Halaman ini hanya dapat diakses oleh pembeli.")
    else:
        for nama, info in st.session_state.menu.items():
            st.write(f" {nama}")
            st.write(f"Harga: Rp{info.get('harga', 'N/A')} / {info.get('satuan', 'N/A')} | menu: {info.get('menu', 'N/A')} {info.get('satuan', '')}")
            jumlah = st.number_input(
                f"Jumlah beli ({info['satuan']}) - {nama}",
                min_value=0,
                max_value =100,
                key=f"jumlah_{nama}"
            )
            if st.button(f"Tambah ke Keranjang - {nama}", key=f"btn_{nama}"):
                if jumlah > 0:
                    if nama in st.session_state.keranjang:
                        st.session_state.keranjang[nama] += jumlah
                    else:
                        st.session_state.keranjang[nama] = jumlah
                    st.success(f"{jumlah} {info['satuan']} {nama} ditambahkan ke keranjang.")
                else:
                    st.warning("Masukkan jumlah minimal 1.")

# ====================
# Checkout Page
# ====================
# Di bagian checkout (gabungkan 2 blok Checkout jadi 1)

elif menu == "Checkout":
    st.title("🛒 Checkout & Keranjang Belanja")

    if st.session_state.role != "buyer":
        st.warning("Halaman ini hanya untuk pembeli.")
    elif "keranjang" in st.session_state and st.session_state.keranjang:
        total = 0

        st.subheader("🧾 Ringkasan Belanja")
        for nama, jumlah in st.session_state.keranjang.items():
            harga = st.session_state.menu[nama]["harga"]
            satuan = st.session_state.menu[nama]["satuan"]
            subtotal = harga * jumlah
            st.write(f"{nama} - {jumlah} {satuan} x {format_rupiah(harga)} = {format_rupiah(subtotal)}")
            total += subtotal

        st.markdown(f"**Total Belanja: {format_rupiah(total)}**")

        # Input alamat
        st.subheader("📍 Alamat Pengiriman")
        alamat = st.text_area("Masukkan alamat lengkap Anda", placeholder="Contoh: Jl. Mawar No. 123, Bandung")

        # Pilih metode pembayaran
        st.subheader("💳 Metode Pembayaran")
        opsi_metode = ["--Pilih Bank--", "BCA", "Mandiri", "DANA"]
        metode = st.radio("Pilih metode pembayaran", opsi_metode)

        # Info nomor rekening
        if metode == "BCA":
            st.info("Nomor rekening: 58442352208 a.n. Batter Hub")
        elif metode == "Mandiri":
            st.info("Nomor rekening: 12344567890 a.n. Batter Hub")
        elif metode == "DANA":
            st.info("Nomor rekening: 085848110179 a.n. Batter Hub")

        st.markdown("""
        📩 Jangan lupa kirim bukti pembayaran ke email kami ya!
        Info lengkap ada di menu **Contact**. Terima kasih!
        """)

        # Tombol konfirmasi
        if st.button("✅ Konfirmasi Pesanan"):
            if not alamat.strip():
                st.error("Alamat pengiriman harus diisi.")
            elif metode == "--Pilih Bank--":
                st.error("Silakan pilih metode pembayaran.")
            else:
                try:
                    conn = sqlite3.connect("keuangan.db")
                    c = conn.cursor()

                    tanggal = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    for nama, jumlah in st.session_state.keranjang.items():
                        harga = st.session_state.menu[nama]["harga"]
                        subtotal = harga * jumlah

                        # Simpan transaksi (perbaikan di sini)
                        c.execute(
                            "INSERT INTO transaksi (menu, jumlah, subtotal, tanggal) VALUES (?, ?, ?, ?)",
                            (nama, jumlah, subtotal, tanggal)
                        )

                    conn.commit()
                    conn.close()

                    st.success("✅ Pesanan berhasil dikonfirmasi dan disimpan!")
                    st.session_state.keranjang.clear()

                except Exception as e:
                    st.error(f"Terjadi kesalahan saat menyimpan transaksi: {e}")
    else:
        st.info("Keranjang masih kosong.")


# =====================
# Transaksi Penjualan 
# =====================
elif menu == "Transaksi":
    st.title("📊 Riwayat Transaksi")

    if st.session_state.role != "admin":
        st.warning("Halaman ini hanya dapat diakses oleh admin.")
    else:
        conn = sqlite3.connect("keuangan.db")
        c = conn.cursor()
        c.execute("SELECT id, menu, jumlah, subtotal, tanggal FROM transaksi ORDER BY tanggal DESC")
        rows = c.fetchall()
        conn.close()

        if rows:
            df = pd.DataFrame(rows, columns=["ID", "Menu", "Jumlah", "Subtotal", "Tanggal"])

            # Konversi kolom tanggal ke datetime agar bisa filter
            df["Tanggal"] = pd.to_datetime(df["Tanggal"])

            # Filter tanggal
            st.subheader("Filter Tanggal")
            start_date = st.date_input("Dari tanggal", df["Tanggal"].min().date())
            end_date = st.date_input("Sampai tanggal", df["Tanggal"].max().date())

            # Filter dataframe sesuai tanggal
            mask = (df["Tanggal"].dt.date >= start_date) & (df["Tanggal"].dt.date <= end_date)
            filtered_df = df.loc[mask]

            # Format rupiah pada kolom subtotal
            filtered_df["Subtotal"] = filtered_df["Subtotal"].apply(format_rupiah)

            st.dataframe(filtered_df.reset_index(drop=True))

            # Fungsi ekspor ke Excel
            # Fungsi ekspor ke Excel
            def to_excel(dataframe):
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    dataframe.to_excel(writer, index=False, sheet_name='Transaksi')
                processed_data = output.getvalue()
                return processed_data

            excel_data = to_excel(filtered_df)

            st.download_button(
                label="📥 Unduh Data Transaksi (Excel)",
                data=excel_data,
                file_name='riwayat_transaksi.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

        else:
            st.info("Belum ada transaksi yang tercatat.")

# ====================
# 📞 Kontak
# ====================
elif menu == "Contact":
    st.title("📞 Hubungi Kami")
    st.write("📧 Email: batterhub@gmail.com")
    st.write("📱 WhatsApp: +628097646786")




        
