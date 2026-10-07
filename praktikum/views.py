from django.contrib import messages
from django.contrib.auth import authenticate
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods

from .models import (
    Kelompok,
    Peserta,
    Staff,
    Acara,
    Materi,
    Absensi,
    Pengumuman,
    TataTertib,
    TugasPendahuluan,
    LaporanMingguan,
    ProgressAcara,
    FileKelompok,
    DailyMOM,
    LaporanLengkap,
    FormatDokumen,
    Konsultasi,
)


# ============================================================
# HELPER
# ============================================================

def get_kelompok_login(request):
    """
    Mengambil kelompok berdasarkan peserta yang sedang login.
    """

    peserta_id = request.session.get("peserta_id")

    if not peserta_id:
        return None

    try:
        peserta = Peserta.objects.select_related(
            "kelompok",
            "akun",
        ).get(
            id=peserta_id,
            aktif=True,
            status_kemajuan="aktif",
        )
    except Peserta.DoesNotExist:
        request.session.flush()
        return None

    if not peserta.kelompok or not peserta.kelompok.aktif:
        return None

    return peserta.kelompok


def get_peserta_login(request):
    """
    Mengambil peserta yang sedang login.
    """

    peserta_id = request.session.get("peserta_id")

    if not peserta_id:
        return None

    try:
        return Peserta.objects.select_related(
            "kelompok",
            "akun",
        ).get(
            id=peserta_id,
            aktif=True,
            status_kemajuan="aktif",
        )
    except Peserta.DoesNotExist:
        request.session.flush()
        return None


def get_role_peserta(request):
    """
    Mengambil role peserta:
    ketua / anggota.
    """

    peserta = get_peserta_login(request)

    if not peserta:
        return None

    return peserta.jabatan


# ============================================================
# HALAMAN PUBLIK
# ============================================================

def home(request):
    return render(
        request,
        "praktikum/home.html",
        {
            "kelompok_list": Kelompok.objects.filter(
                aktif=True
            ).order_by("nama"),
            "acara_list": Acara.objects.all(),
            "pengumuman_list": Pengumuman.objects.filter(
                aktif=True
            ),
        },
    )


def kelompok(request):
    kelompok_list = Kelompok.objects.filter(
        aktif=True
    ).order_by("nama")

    return render(
        request,
        "praktikum/kelompok.html",
        {
            "kelompok_list": kelompok_list,
        },
    )


def personel(request):
    peserta_list = Peserta.objects.filter(
        aktif=True,
        status_kemajuan="aktif",
    ).select_related(
        "kelompok"
    )

    return render(
        request,
        "praktikum/personel.html",
        {
            "peserta_list": peserta_list,
        },
    )


def jadwal(request):
    acara_list = Acara.objects.all().order_by(
        "urutan",
        "tanggal_mulai",
    )

    return render(
        request,
        "praktikum/jadwal.html",
        {
            "acara_list": acara_list,
        },
    )


def materi(request):
    materi_list = Materi.objects.all().order_by(
        "-uploaded_at"
    )

    return render(
        request,
        "praktikum/materi.html",
        {
            "materi_list": materi_list,
        },
    )


def absensi(request):
    return render(
        request,
        "praktikum/absensi.html",
    )


def tata_tertib(request):
    tata_tertib_list = TataTertib.objects.filter(
        aktif=True
    ).order_by(
        "urutan",
        "id",
    )

    return render(
        request,
        "praktikum/tata_tertib.html",
        {
            "tata_tertib_list": tata_tertib_list,
        },
    )


def pengumuman(request):
    pengumuman_list = Pengumuman.objects.filter(
        aktif=True
    )

    return render(
        request,
        "praktikum/pengumuman.html",
        {
            "pengumuman_list": pengumuman_list,
        },
    )


def tugas_pendahuluan(request):
    tugas_list = TugasPendahuluan.objects.filter(
        aktif=True
    ).order_by("-dibuat")

    return render(
        request,
        "praktikum/tugas_pendahuluan.html",
        {
            "tugas_list": tugas_list,
        },
    )


# ============================================================
# LOGIN KELOMPOK
# ============================================================

@never_cache
@require_http_methods(["GET", "POST"])
def login_kelompok(request):

    peserta = get_peserta_login(request)

    if peserta:
        return redirect(
            "praktikum:dashboard_kelompok"
        )

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        if not username or not password:

            messages.error(
                request,
                "Username dan password wajib diisi."
            )

            return render(
                request,
                "praktikum/login.html",
            )

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
                "praktikum/login.html",
            )

        if not user.is_active:

            messages.error(
                request,
                "Akun tidak aktif."
            )

            return render(
                request,
                "praktikum/login.html",
            )

        try:

            peserta = Peserta.objects.select_related(
                "kelompok",
                "akun",
            ).get(
                akun=user,
                aktif=True,
                status_kemajuan="aktif",
            )

        except Peserta.DoesNotExist:

            messages.error(
                request,
                "Akun belum terhubung dengan peserta."
            )

            return render(
                request,
                "praktikum/login.html",
            )

        if not peserta.kelompok:

            messages.error(
                request,
                "Peserta belum terhubung dengan kelompok."
            )

            return render(
                request,
                "praktikum/login.html",
            )

        if not peserta.kelompok.aktif:

            messages.error(
                request,
                "Kelompok ini sedang tidak aktif."
            )

            return render(
                request,
                "praktikum/login.html",
            )

        request.session.flush()

        request.session["peserta_id"] = peserta.id
        request.session["kelompok_id"] = peserta.kelompok.id
        request.session["kelompok_nama"] = peserta.kelompok.nama
        request.session["peserta_nama"] = peserta.nama
        request.session["peserta_role"] = peserta.jabatan
        request.session["login_type"] = "peserta"

        request.session.set_expiry(
            60 * 60 * 12
        )

        messages.success(
            request,
            f"Selamat datang, {peserta.nama}."
        )

        return redirect(
            "praktikum:dashboard_kelompok"
        )

    return render(
        request,
        "praktikum/login.html",
    )


# ============================================================
# LOGOUT
# ============================================================

@never_cache
def logout_kelompok(request):

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
def dashboard_kelompok(request):

    peserta = get_peserta_login(request)

    if not peserta:

        messages.warning(
            request,
            "Silakan login terlebih dahulu."
        )

        return redirect(
            "praktikum:login_kelompok"
        )

    kelompok_obj = peserta.kelompok

    anggota = Peserta.objects.filter(
        kelompok=kelompok_obj,
        aktif=True,
        status_kemajuan="aktif",
    ).order_by(
        "jabatan",
        "nama",
    )

    mentor = kelompok_obj.mentor.filter(
        aktif=True
    )

    progress_acara = ProgressAcara.objects.filter(
        kelompok=kelompok_obj
    ).select_related(
        "acara"
    ).order_by(
        "acara__urutan",
        "acara__tanggal_mulai",
    )

    progress_list = [
        item.nilai_progress
        for item in progress_acara
    ]

    if progress_list:

        progress_persen = round(
            sum(progress_list) / len(progress_list)
        )

    else:

        progress_persen = kelompok_obj.progress_persen

    laporan = LaporanMingguan.objects.filter(
        kelompok=kelompok_obj
    ).select_related(
        "peserta",
        "acara",
    )

    file_kelompok = FileKelompok.objects.filter(
        kelompok=kelompok_obj
    ).select_related(
        "uploaded_by",
        "acara",
    )

    daily_mom = DailyMOM.objects.filter(
        kelompok=kelompok_obj
    ).select_related(
        "acara",
        "dibuat_oleh",
    )[:10]

    laporan_lengkap = LaporanLengkap.objects.filter(
        kelompok=kelompok_obj
    ).order_by(
        "-uploaded_at"
    )

    konsultasi = Konsultasi.objects.filter(
        kelompok=kelompok_obj
    ).select_related(
        "peserta",
        "tujuan",
        "acara",
    ).order_by(
        "-dibuat"
    )

    context = {
        "peserta": peserta,
        "kelompok": kelompok_obj,
        "anggota": anggota,
        "mentor": mentor,
        "progress_acara": progress_acara,
        "progress_persen": progress_persen,
        "jumlah_anggota": anggota.count(),
        "laporan": laporan,
        "file_kelompok": file_kelompok,
        "daily_mom": daily_mom,
        "laporan_lengkap": laporan_lengkap,
        "konsultasi": konsultasi,
        "is_ketua": peserta.jabatan == "ketua",
        "is_anggota": peserta.jabatan == "anggota",
        "username": (
            peserta.akun.username
            if peserta.akun
            else ""
        ),
    }

    return render(
        request,
        "praktikum/dashboard_kelompok.html",
        context,
    )


# ============================================================
# DASHBOARD PESERTA LAMA
# ============================================================

def dashboard_peserta(request):

    peserta = get_peserta_login(request)

    if not peserta:

        return redirect(
            "praktikum:login_kelompok"
        )

    return redirect(
        "praktikum:dashboard_kelompok"
    )


# ============================================================
# UPLOAD LAPORAN MINGGUAN
# ============================================================

@require_http_methods(["GET", "POST"])
def upload_laporan(request):

    peserta = get_peserta_login(request)

    if not peserta:

        return redirect(
            "praktikum:login_kelompok"
        )

    kelompok_obj = peserta.kelompok

    if request.method == "POST":

        acara_id = request.POST.get("acara")
        peserta_id = request.POST.get("peserta")
        judul = request.POST.get("judul", "").strip()
        file = request.FILES.get("file")

        if peserta.jabatan not in ["ketua", "anggota"]:

            messages.error(
                request,
                "Anda tidak memiliki akses."
            )

            return redirect(
                "praktikum:dashboard_kelompok"
            )

        try:
            peserta_upload = Peserta.objects.get(
                id=peserta_id,
                kelompok=kelompok_obj,
                aktif=True,
            )
        except Peserta.DoesNotExist:

            messages.error(
                request,
                "Peserta tidak ditemukan."
            )

            return redirect(
                "praktikum:dashboard_kelompok"
            )

        if not acara_id or not judul or not file:

            messages.error(
                request,
                "Acara, judul, dan file wajib diisi."
            )

            return redirect(
                "praktikum:dashboard_kelompok"
            )

        try:
            acara_obj = Acara.objects.get(
                id=acara_id
            )
        except Acara.DoesNotExist:

            messages.error(
                request,
                "Acara tidak ditemukan."
            )

            return redirect(
                "praktikum:dashboard_kelompok"
            )

        LaporanMingguan.objects.create(
            peserta=peserta_upload,
            kelompok=kelompok_obj,
            acara=acara_obj,
            judul=judul,
            file=file,
        )

        messages.success(
            request,
            "Laporan mingguan berhasil diupload."
        )

        return redirect(
            "praktikum:dashboard_kelompok"
        )

    return render(
        request,
        "praktikum/dashboard_kelompok.html",
        {
            "peserta": peserta,
            "kelompok": kelompok_obj,
            "anggota": Peserta.objects.filter(
                kelompok=kelompok_obj,
                aktif=True,
            ),
            "acara_list": Acara.objects.all(),
            "is_ketua": peserta.jabatan == "ketua",
        },
    )


# ============================================================
# DOWNLOAD FILE REVISI
# ============================================================

def download_file_revisi(request, laporan_id):

    peserta = get_peserta_login(request)

    if not peserta:

        return redirect(
            "praktikum:login_kelompok"
        )

    try:

        laporan = LaporanMingguan.objects.get(
            id=laporan_id,
            kelompok=peserta.kelompok,
        )

    except LaporanMingguan.DoesNotExist:

        messages.error(
            request,
            "Laporan tidak ditemukan."
        )

        return redirect(
            "praktikum:dashboard_kelompok"
        )

    if not laporan.file_revisi:

        messages.error(
            request,
            "File revisi belum tersedia."
        )

        return redirect(
            "praktikum:dashboard_kelompok"
        )

    from django.http import FileResponse

    return FileResponse(
        laporan.file_revisi.open("rb"),
        as_attachment=True,
        filename=laporan.file_revisi.name.split("/")[-1],
    )
