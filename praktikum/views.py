from django.contrib import messages
from django.contrib.auth import authenticate
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods

from .models import Kelompok


# ============================================================
# HELPER
# ============================================================

def get_kelompok_login(request):
    """
    Mengambil kelompok yang sedang login berdasarkan session.

    Session yang digunakan:
        kelompok_id
        kelompok_nama
        login_type = kelompok
    """

    # --------------------------------------------------------
    # Pastikan session memang milik login kelompok
    # --------------------------------------------------------

    if request.session.get("login_type") != "kelompok":
        return None

    kelompok_id = request.session.get("kelompok_id")

    if not kelompok_id:
        return None

    # --------------------------------------------------------
    # Ambil data kelompok
    # --------------------------------------------------------

    try:
        kelompok = (
            Kelompok.objects
            .prefetch_related(
                "mentor",
                "peserta",
                "progress_acara__acara",
            )
            .select_related(
                "akun_login",
            )
            .get(
                id=kelompok_id,
                aktif=True,
            )
        )

    except Kelompok.DoesNotExist:
        request.session.flush()
        return None

    return kelompok


# ============================================================
# LOGIN KELOMPOK
# ============================================================

@never_cache
@require_http_methods(["GET", "POST"])
def login_kelompok(request):
    """
    Halaman login khusus akun kelompok.

    Login menggunakan:
        username
        password

    User Django harus terhubung dengan:
        Kelompok.akun_login
    """

    # --------------------------------------------------------
    # Jika sudah login sebagai kelompok
    # --------------------------------------------------------

    kelompok = get_kelompok_login(request)

    if kelompok is not None:
        return redirect(
            "praktikum:dashboard_kelompok"
        )

    # --------------------------------------------------------
    # Proses POST
    # --------------------------------------------------------

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        # ----------------------------------------------------
        # Validasi input
        # ----------------------------------------------------

        if not username or not password:

            messages.error(
                request,
                "Username dan password wajib diisi."
            )

            return render(
                request,
                "praktikum/login.html"
            )

        # ----------------------------------------------------
        # Authenticate User Django
        # ----------------------------------------------------

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is None:

            messages.error(
                request,
                "Username atau password salah."
            )

            return render(
                request,
                "praktikum/login.html"
            )

        # ----------------------------------------------------
        # User harus aktif
        # ----------------------------------------------------

        if not user.is_active:

            messages.error(
                request,
                "Akun ini tidak aktif."
            )

            return render(
                request,
                "praktikum/login.html"
            )

        # ----------------------------------------------------
        # Cari kelompok berdasarkan akun_login
        # ----------------------------------------------------

        try:

            kelompok = (
                Kelompok.objects
                .prefetch_related(
                    "mentor",
                    "peserta",
                    "progress_acara__acara",
                )
                .select_related(
                    "akun_login",
                )
                .get(
                    akun_login=user,
                    aktif=True,
                )
            )

        except Kelompok.DoesNotExist:

            messages.error(
                request,
                "Akun ini belum terhubung dengan kelompok."
            )

            return render(
                request,
                "praktikum/login.html"
            )

        # ----------------------------------------------------
        # Reset session
        #
        # Tujuan:
        # mencegah session lama digunakan kembali.
        # ----------------------------------------------------

        request.session.flush()

        # ----------------------------------------------------
        # Simpan session kelompok
        # ----------------------------------------------------

        request.session["kelompok_id"] = kelompok.id

        request.session["kelompok_nama"] = kelompok.nama

        request.session["login_type"] = "kelompok"

        # ----------------------------------------------------
        # Session berlaku 12 jam
        # ----------------------------------------------------

        request.session.set_expiry(
            60 * 60 * 12
        )

        # ----------------------------------------------------
        # Pesan sukses
        # ----------------------------------------------------

        messages.success(
            request,
            f"Selamat datang, {kelompok.nama}."
        )

        return redirect(
            "praktikum:dashboard_kelompok"
        )

    # --------------------------------------------------------
    # GET
    # --------------------------------------------------------

    return render(
        request,
        "praktikum/login.html"
    )


# ============================================================
# LOGOUT KELOMPOK
# ============================================================

@never_cache
@require_http_methods(["GET", "POST"])
def logout_kelompok(request):
    """
    Logout akun kelompok.
    """

    request.session.flush()

    messages.success(
        request,
        "Anda telah berhasil logout."
    )

    return redirect(
        "praktikum:login_kelompok"
    )


# ============================================================
# DASHBOARD KELOMPOK
# ============================================================

@never_cache
@require_http_methods(["GET"])
def dashboard_kelompok(request):
    """
    Dashboard utama kelompok.

    Data yang ditampilkan hanya milik kelompok
    yang sedang login.
    """

    # --------------------------------------------------------
    # Ambil kelompok dari session
    # --------------------------------------------------------

    kelompok = get_kelompok_login(request)

    if kelompok is None:

        messages.warning(
            request,
            "Silakan login terlebih dahulu."
        )

        return redirect(
            "praktikum:login_kelompok"
        )

    # --------------------------------------------------------
    # Mentor aktif
    # --------------------------------------------------------

    mentor = kelompok.mentor.filter(
        aktif=True
    )

    # --------------------------------------------------------
    # Anggota aktif
    #
    # Hanya peserta:
    #   aktif=True
    #   status_kemajuan="aktif"
    # --------------------------------------------------------

    anggota = (
        kelompok.peserta
        .filter(
            aktif=True,
            status_kemajuan="aktif",
        )
        .order_by(
            "jabatan",
            "nama",
        )
    )

    # --------------------------------------------------------
    # Progress per acara
    # --------------------------------------------------------

    progress_acara = (
        kelompok.progress_acara
        .select_related("acara")
        .order_by(
            "acara__urutan",
            "acara__tanggal_mulai",
        )
    )

    # --------------------------------------------------------
    # Hitung progress keseluruhan
    #
    # Prioritas:
    # 1. Jika ada ProgressAcara → rata-rata progress.
    # 2. Jika belum ada → gunakan field Kelompok.progress.
    # --------------------------------------------------------

    progress_list = [
        item.nilai_progress
        for item in progress_acara
    ]

    if progress_list:

        progress_persen = round(
            sum(progress_list) / len(progress_list)
        )

    else:

        progress_persen = kelompok.progress_persen

    # --------------------------------------------------------
    # Jumlah event/acara yang memiliki progress
    # --------------------------------------------------------

    jumlah_event = progress_acara.count()

    # --------------------------------------------------------
    # Username akun kelompok
    # --------------------------------------------------------

    username = ""

    if kelompok.akun_login:
        username = kelompok.akun_login.username

    # --------------------------------------------------------
    # Context dashboard
    # --------------------------------------------------------

    context = {
        "kelompok": kelompok,
        "mentor": mentor,
        "anggota": anggota,
        "progress_acara": progress_acara,
        "progress_persen": progress_persen,
        "jumlah_event": jumlah_event,
        "jumlah_anggota": anggota.count(),
        "username": username,
    }

    # --------------------------------------------------------
    # Render dashboard
    # --------------------------------------------------------

    return render(
        request,
        "praktikum/dashboard_kelompok.html",
        context,
    )
