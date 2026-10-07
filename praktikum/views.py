```python
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
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
    """

    kelompok_id = request.session.get("kelompok_id")

    if not kelompok_id:
        return None

    try:
        kelompok = (
            Kelompok.objects
            .prefetch_related(
                "mentor",
                "peserta",
                "progress_acara__acara",
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
        return redirect("absensi:dashboard_kelompok")

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
                "absensi/login.html"
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
                "absensi/login.html"
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
                "absensi/login.html"
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
                "absensi/login.html"
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
            "absensi:dashboard_kelompok"
        )

    # --------------------------------------------------------
    # GET
    # --------------------------------------------------------

    return render(
        request,
        "absensi/login.html"
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
        "absensi:login_kelompok"
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
            "absensi:login_kelompok"
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
            "nama"
```
