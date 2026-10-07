from django.contrib import messages
from django.contrib.auth import authenticate
from django.http import FileResponse
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods

from .models import (
    Setting,
    Kelompok,
    Peserta,
    Acara,
    Materi,
    Pengumuman,
    TataTertib,
    TugasPendahuluan,
    LaporanMingguan,
    ProgressAcara,
    FileKelompok,
    DailyMOM,
    LaporanLengkap,
    Konsultasi,
)


# ============================================================
# HELPER STATUS PESERTA
# ============================================================

ACTIVE_STATUS = ["aktif", "AKTIF"]


# ============================================================
# HELPER LOGIN KELOMPOK
# ============================================================

def get_kelompok_login(request):
    """
    Mengambil kelompok yang sedang login berdasarkan session.
    """

    kelompok_id = request.session.get("kelompok_id")

    if not kelompok_id:
        return None

    try:
        kelompok = Kelompok.objects.get(
            id=kelompok_id,
            aktif=True,
        )
    except Kelompok.DoesNotExist:
        request.session.flush()
        return None

    return kelompok


def get_user_kelompok(request):
    """
    Mengambil User yang digunakan oleh akun kelompok.
    """

    kelompok = get_kelompok_login(request)

    if not kelompok:
        return None

    return kelompok.akun_login


def get_peserta_login(request):
    """
    Mengambil peserta utama/ketua dari kelompok yang login.
    Digunakan untuk kompatibilitas dengan template lama.
    """

    kelompok = get_kelompok_login(request)

    if not kelompok:
        return None

    peserta = (
        Peserta.objects
        .filter(
            kelompok=kelompok,
            aktif=True,
            status_kemajuan__in=ACTIVE_STATUS,
        )
        .order_by(
            "jabatan",
            "nama",
        )
        .first()
    )

    return peserta


# ============================================================
# HALAMAN PUBLIK
# ============================================================

def home(request):

    setting = Setting.objects.first()

    kelompok_list = (
        Kelompok.objects
        .filter(aktif=True)
        .order_by("nama")
    )

    acara_list = (
        Acara.objects
        .all()
        .order_by(
            "urutan",
            "tanggal_mulai",
        )
    )

    materi_list = (
        Materi.objects
        .all()
        .order_by("-uploaded_at")
    )

    pengumuman_list = (
        Pengumuman.objects
        .filter(aktif=True)
        .order_by("-id")
    )

    peserta_list = (
        Peserta.objects
        .filter(
            aktif=True,
            status_kemajuan__in=ACTIVE_STATUS,
        )
        .select_related("kelompok")
        .order_by(
            "kelompok__nama",
            "nama",
        )
    )

    return render(
        request,
        "praktikum/home.html",
        {
            "setting": setting,

            "kelompok": kelompok_list,
            "acara": acara_list,
            "materi": materi_list,
            "pengumuman": pengumuman_list,
            "asisten": peserta_list,

            # Kompatibilitas template lama
            "kelompok_list": kelompok_list,
            "acara_list": acara_list,
            "materi_list": materi_list,
            "pengumuman_list": pengumuman_list,
            "peserta_list": peserta_list,
        },
    )


def kelompok(request):

    kelompok_list = (
        Kelompok.objects
        .filter(aktif=True)
        .order_by("nama")
    )

    return render(
        request,
        "praktikum/kelompok.html",
        {
            "kelompok_list": kelompok_list,
        },
    )


def personel(request):

    peserta_list = (
        Peserta.objects
        .filter(
            aktif=True,
            status_kemajuan__in=ACTIVE_STATUS,
        )
        .select_related("kelompok")
        .order_by(
            "kelompok__nama",
            "nama",
        )
    )

    return render(
        request,
        "praktikum/personel.html",
        {
            "peserta_list": peserta_list,
        },
    )


def jadwal(request):

    acara_list = (
        Acara.objects
        .all()
        .order_by(
            "urutan",
            "tanggal_mulai",
        )
    )

    return render(
        request,
        "praktikum/jadwal.html",
        {
            "acara_list": acara_list,
        },
    )


def materi(request):

    materi_list = (
        Materi.objects
        .all()
        .order_by("-uploaded_at")
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

    tata_tertib_list = (
        TataTertib.objects
        .filter(aktif=True)
        .order_by(
            "urutan",
            "id",
        )
    )

    return render(
        request,
        "praktikum/tata_tertib.html",
        {
            "tata_tertib_list": tata_tertib_list,
        },
    )


def pengumuman(request):

    pengumuman_list = (
        Pengumuman.objects
        .filter(aktif=True)
        .order_by("-id")
    )

    return render(
        request,
        "praktikum/pengumuman.html",
        {
            "pengumuman_list": pengumuman_list,
        },
    )


def tugas_pendahuluan(request):

    tugas_list = (
        TugasPendahuluan.objects
        .filter(aktif=True)
        .order_by("-dibuat")
    )

    return render(
        request,
        "praktikum/tugas_pendahuluan.html",
        {
            "tugas_list": tugas_list,
        },
    )


# ============================================================
# INFORMASI PESERTA
# ============================================================

def informasi_peserta(request):
    """
    Menampilkan seluruh peserta beserta kelompok dan status.
    Halaman publik.
    """

    peserta_list = (
        Peserta.objects
        .select_related("kelompok")
        .all()
        .order_by(
            "status_kemajuan",
            "kelompok__nama",
            "nama",
        )
    )

    total_peserta = peserta_list.count()

    total_aktif = (
        peserta_list
        .filter(
            aktif=True,
            status_kemajuan__in=ACTIVE_STATUS,
        )
        .count()
    )

    total_gugur = (
        peserta_list
        .filter(
            status_kemajuan__iexact="gugur",
        )
        .count()
    )

    total_kelompok = (
        Kelompok.objects
        .filter(aktif=True)
        .count()
    )

    return render(
        request,
        "praktikum/informasi_peserta.html",
        {
            "setting": Setting.objects.first(),

            "peserta": peserta_list,
            "peserta_list": peserta_list,

            "total_peserta": total_peserta,
            "total_aktif": total_aktif,
            "total_gugur": total_gugur,
            "total_kelompok": total_kelompok,
        },
    )


# ============================================================
# LOGIN KELOMPOK
# ============================================================

@never_cache
@require_http_methods(["GET", "POST"])
def login_kelompok(request):

    kelompok = get_kelompok_login(request)

    if kelompok:
        return redirect(
            "praktikum:dashboard_kelompok"
        )

    if request.method == "POST":

        username = request.POST.get(
            "username",
            "",
        ).strip()

        password = request.POST.get(
            "password",
            "",
        )

        if not username or not password:

            messages.error(
                request,
                "Username dan password wajib diisi.",
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
                "Username atau password salah.",
            )

            return render(
                request,
                "praktikum/login.html",
            )

        if not user.is_active:

            messages.error(
                request,
                "Akun tidak aktif.",
            )

            return render(
                request,
                "praktikum/login.html",
            )

        try:

            kelompok = (
                Kelompok.objects
                .select_related("akun_login")
                .get(
                    akun_login=user,
                    aktif=True,
                )
            )

        except Kelompok.DoesNotExist:

            messages.error(
                request,
                "Akun ini belum terhubung dengan kelompok aktif.",
            )

            return render(
                request,
                "praktikum/login.html",
            )

        # RESET SESSION
        request.session.flush()

        # SESSION KELOMPOK
        request.session["kelompok_id"] = kelompok.id
        request.session["kelompok_nama"] = kelompok.nama
        request.session["login_type"] = "kelompok"
        request.session["username"] = user.username

        # Session aktif selama 12 jam
        request.session.set_expiry(
            60 * 60 * 12
        )

        messages.success(
            request,
            f"Selamat datang, Kelompok {kelompok.nama}.",
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
        "Anda telah berhasil logout.",
    )

    return redirect(
        "praktikum:login_kelompok"
    )


# ============================================================
# DASHBOARD KELOMPOK
# ============================================================

@never_cache
def dashboard_kelompok(request):

    kelompok_obj = get_kelompok_login(request)

    if not kelompok_obj:

        messages.warning(
            request,
            "Silakan login terlebih dahulu.",
        )

        return redirect(
            "praktikum:login_kelompok"
        )

    # ========================================================
    # ANGGOTA KELOMPOK
    # ========================================================

    anggota = (
        Peserta.objects
        .filter(
            kelompok=kelompok_obj,
            aktif=True,
            status_kemajuan__in=ACTIVE_STATUS,
        )
        .order_by(
            "jabatan",
            "nama",
        )
    )

    # ========================================================
    # MENTOR
    # ========================================================

    mentor = kelompok_obj.mentor.filter(
        aktif=True
    )

    # ========================================================
    # PROGRESS ACARA
    # ========================================================

    progress_acara = (
        ProgressAcara.objects
        .filter(
            kelompok=kelompok_obj
        )
        .select_related("acara")
        .order_by(
            "acara__urutan",
            "acara__tanggal_mulai",
        )
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

    # ========================================================
    # LAPORAN MINGGUAN
    # ========================================================

    laporan = (
        LaporanMingguan.objects
        .filter(
            kelompok=kelompok_obj
        )
        .select_related(
            "peserta",
            "acara",
        )
        .order_by("-uploaded_at")
    )

    # ========================================================
    # FILE KELOMPOK
    # ========================================================

    file_kelompok = (
        FileKelompok.objects
        .filter(
            kelompok=kelompok_obj
        )
        .select_related(
            "uploaded_by",
            "acara",
        )
        .order_by("-uploaded_at")
    )

    # ========================================================
    # DAILY MOM
    # ========================================================

    daily_mom = (
        DailyMOM.objects
        .filter(
            kelompok=kelompok_obj
        )
        .select_related(
            "acara",
            "dibuat_oleh",
        )
        .order_by("-id")[:10]
    )

    # ========================================================
    # LAPORAN LENGKAP
    # ========================================================

    laporan_lengkap = (
        LaporanLengkap.objects
        .filter(
            kelompok=kelompok_obj
        )
        .order_by("-uploaded_at")
    )

    # ========================================================
    # KONSULTASI
    # ========================================================

    konsultasi = (
        Konsultasi.objects
        .filter(
            kelompok=kelompok_obj
        )
        .select_related(
            "peserta",
            "tujuan",
            "acara",
        )
        .order_by("-dibuat")
    )

    # ========================================================
    # PESERTA UTAMA / KETUA
    # ========================================================

    peserta = anggota.filter(
        jabatan__iexact="ketua"
    ).first()

    if not peserta:
        peserta = anggota.first()

    # ========================================================
    # DAFTAR ACARA
    # ========================================================

    acara_list = (
        Acara.objects
        .all()
        .order_by(
            "urutan",
            "tanggal_mulai",
        )
    )

    # ========================================================
    # CONTEXT
    # ========================================================

    context = {
        "setting": Setting.objects.first(),

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

        "is_ketua": True,

        "is_anggota": False,

        "username": (
            kelompok_obj.akun_login.username
            if kelompok_obj.akun_login
            else ""
        ),

        "acara_list": acara_list,
    }

    return render(
        request,
        "praktikum/dashboard_kelompok.html",
        context,
    )


# ============================================================
# DASHBOARD PESERTA LAMA
# ============================================================

@never_cache
def dashboard_peserta(request):

    kelompok = get_kelompok_login(request)

    if not kelompok:

        return redirect(
            "praktikum:login_kelompok"
        )

    return redirect(
        "praktikum:dashboard_kelompok"
    )


# ============================================================
# UPLOAD LAPORAN MINGGUAN
# ============================================================

@never_cache
@require_http_methods(["GET", "POST"])
def upload_laporan(request):

    kelompok_obj = get_kelompok_login(request)

    if not kelompok_obj:

        messages.warning(
            request,
            "Silakan login terlebih dahulu.",
        )

        return redirect(
            "praktikum:login_kelompok"
        )

    if request.method == "POST":

        acara_id = request.POST.get(
            "acara"
        )

        peserta_id = request.POST.get(
            "peserta"
        )

        judul = request.POST.get(
            "judul",
            "",
        ).strip()

        file = request.FILES.get(
            "file"
        )

        if (
            not acara_id
            or not peserta_id
            or not judul
            or not file
        ):

            messages.error(
                request,
                "Acara, peserta, judul, dan file wajib diisi.",
            )

            return redirect(
                "praktikum:dashboard_kelompok"
            )

        try:

            peserta_upload = (
                Peserta.objects
                .get(
                    id=peserta_id,
                    kelompok=kelompok_obj,
                    aktif=True,
                    status_kemajuan__in=ACTIVE_STATUS,
                )
            )

        except Peserta.DoesNotExist:

            messages.error(
                request,
                "Peserta tidak ditemukan dalam kelompok ini.",
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
                "Acara tidak ditemukan.",
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
            "Laporan mingguan berhasil diupload.",
        )

        return redirect(
            "praktikum:dashboard_kelompok"
        )

    anggota = (
        Peserta.objects
        .filter(
            kelompok=kelompok_obj,
            aktif=True,
            status_kemajuan__in=ACTIVE_STATUS,
        )
        .order_by(
            "jabatan",
            "nama",
        )
    )

    return render(
        request,
        "praktikum/dashboard_kelompok.html",
        {
            "setting": Setting.objects.first(),
            "kelompok": kelompok_obj,
            "anggota": anggota,
            "acara_list": (
                Acara.objects
                .all()
                .order_by(
                    "urutan",
                    "tanggal_mulai",
                )
            ),
            "is_ketua": True,
            "is_anggota": False,
        },
    )


# ============================================================
# DOWNLOAD FILE REVISI
# ============================================================

@never_cache
def download_file_revisi(request, laporan_id):

    kelompok_obj = get_kelompok_login(request)

    if not kelompok_obj:

        messages.warning(
            request,
            "Silakan login terlebih dahulu.",
        )

        return redirect(
            "praktikum:login_kelompok"
        )

    try:

        laporan = (
            LaporanMingguan.objects
            .get(
                id=laporan_id,
                kelompok=kelompok_obj,
            )
        )

    except LaporanMingguan.DoesNotExist:

        messages.error(
            request,
            "Laporan tidak ditemukan.",
        )

        return redirect(
            "praktikum:dashboard_kelompok"
        )

    if not laporan.file_revisi:

        messages.error(
            request,
            "File revisi belum tersedia.",
        )

        return redirect(
            "praktikum:dashboard_kelompok"
        )

    return FileResponse(
        laporan.file_revisi.open("rb"),
        as_attachment=True,
        filename=(
            laporan.file_revisi.name
            .split("/")[-1]
        ),
    )
