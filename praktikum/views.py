from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render

from .models import (
    Absensi,
    Acara,
    DailyMOM,
    Kelompok,
    Laporan,
    Materi,
    Pengumuman,
    Peserta,
    Revisi,
    Setting,
    TataTertib,
    TugasPendahuluan,
)


# ============================================================
# KONFIGURASI
# ============================================================

ACTIVE_STATUS = [
    "aktif",
    "AKTIF",
]


# ============================================================
# HELPER
# ============================================================

def get_kelompok_login(request):
    """
    Mengambil kelompok yang sedang login melalui session.
    """
    kelompok_id = request.session.get("kelompok_id")

    if not kelompok_id:
        return None

    try:
        return Kelompok.objects.get(
            id=kelompok_id,
            aktif=True,
        )
    except Kelompok.DoesNotExist:
        return None


def get_user_kelompok(request):
    """
    Mengambil kelompok berdasarkan akun User Django.
    """
    if not request.user.is_authenticated:
        return None

    try:
        return Kelompok.objects.get(
            akun_login=request.user,
            aktif=True,
        )
    except Kelompok.DoesNotExist:
        return None


def get_peserta_login(request):
    """
    Mengambil peserta yang terhubung dengan akun User Django.
    """
    if not request.user.is_authenticated:
        return None

    try:
        return (
            Peserta.objects
            .select_related("kelompok")
            .get(user=request.user)
        )
    except Peserta.DoesNotExist:
        return None


# ============================================================
# PUBLIC - HOME
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

    koordinator = None

    for person in peserta_list:
        jabatan = str(
            getattr(
                person,
                "jabatan",
                "",
            ) or ""
        ).strip().lower()

        if "koordinator" in jabatan:
            koordinator = person
            break

    context = {
        "setting": setting,
        "kelompok": kelompok_list,
        "kelompok_list": kelompok_list,
        "acara": acara_list,
        "acara_list": acara_list,
        "materi": materi_list,
        "materi_list": materi_list,
        "pengumuman": pengumuman_list,
        "pengumuman_list": pengumuman_list,
        "peserta_list": peserta_list,
        "personel": peserta_list,
        "asisten": peserta_list,
        "koordinator": koordinator,
    }

    return render(
        request,
        "praktikum/home.html",
        context,
    )


# ============================================================
# PUBLIC - KELOMPOK
# ============================================================

def kelompok(request):
    setting = Setting.objects.first()

    kelompok_list = (
        Kelompok.objects
        .filter(aktif=True)
        .order_by("nama")
    )

    context = {
        "setting": setting,
        "kelompok": kelompok_list,
        "kelompok_list": kelompok_list,
    }

    return render(
        request,
        "praktikum/kelompok.html",
        context,
    )


# ============================================================
# PUBLIC - PERSONEL
# ============================================================

def personel(request):
    setting = Setting.objects.first()

    peserta_list = (
        Peserta.objects
        .filter(aktif=True)
        .select_related("kelompok")
        .order_by(
            "kelompok__nama",
            "nama",
        )
    )

    context = {
        "setting": setting,
        "peserta_list": peserta_list,
        "personel": peserta_list,
        "asisten": peserta_list,
    }

    return render(
        request,
        "praktikum/personel.html",
        context,
    )


# ============================================================
# PUBLIC - JADWAL
# ============================================================

def jadwal(request):
    setting = Setting.objects.first()

    acara_list = (
        Acara.objects
        .all()
        .order_by(
            "urutan",
            "tanggal_mulai",
        )
    )

    context = {
        "setting": setting,
        "acara": acara_list,
        "acara_list": acara_list,
    }

    return render(
        request,
        "praktikum/jadwal.html",
        context,
    )


# ============================================================
# PUBLIC - MATERI
# ============================================================

def materi(request):
    setting = Setting.objects.first()

    materi_list = (
        Materi.objects
        .all()
        .order_by("-uploaded_at")
    )

    context = {
        "setting": setting,
        "materi": materi_list,
        "materi_list": materi_list,
    }

    return render(
        request,
        "praktikum/materi.html",
        context,
    )


# ============================================================
# PUBLIC - ABSENSI
# ============================================================

def absensi(request):
    setting = Setting.objects.first()

    kelompok_list = (
        Kelompok.objects
        .filter(aktif=True)
        .order_by("nama")
    )

    context = {
        "setting": setting,
        "kelompok": kelompok_list,
        "kelompok_list": kelompok_list,
    }

    return render(
        request,
        "praktikum/absensi.html",
        context,
    )


# ============================================================
# PUBLIC - TATA TERTIB
# ============================================================

def tata_tertib(request):
    setting = Setting.objects.first()

    tata_tertib_list = (
        TataTertib.objects
        .filter(aktif=True)
        .order_by("urutan")
    )

    context = {
        "setting": setting,
        "tata_tertib": tata_tertib_list,
        "tata_tertib_list": tata_tertib_list,
    }

    return render(
        request,
        "praktikum/tata_tertib.html",
        context,
    )


# ============================================================
# PUBLIC - PENGUMUMAN
# ============================================================

def pengumuman(request):
    setting = Setting.objects.first()

    pengumuman_list = (
        Pengumuman.objects
        .filter(aktif=True)
        .order_by("-id")
    )

    context = {
        "setting": setting,
        "pengumuman": pengumuman_list,
        "pengumuman_list": pengumuman_list,
    }

    return render(
        request,
        "praktikum/pengumuman.html",
        context,
    )


# ============================================================
# PUBLIC - TUGAS PENDAHULUAN
# ============================================================

def tugas_pendahuluan(request):
    setting = Setting.objects.first()

    tugas_list = (
        TugasPendahuluan.objects
        .filter(aktif=True)
        .order_by("-dibuat")
    )

    context = {
        "setting": setting,
        "tugas": tugas_list,
        "tugas_list": tugas_list,
    }

    return render(
        request,
        "praktikum/tugas_pendahuluan.html",
        context,
    )


# ============================================================
# PUBLIC - INFORMASI PESERTA
# ============================================================

def informasi_peserta(request):
    setting = Setting.objects.first()

    peserta_list = (
        Peserta.objects
        .filter(aktif=True)
        .select_related("kelompok")
        .order_by(
            "kelompok__nama",
            "nama",
        )
    )

    total_peserta = peserta_list.count()

    total_aktif = (
        peserta_list
        .filter(
            status_kemajuan__in=ACTIVE_STATUS
        )
        .count()
    )

    total_gugur = (
        peserta_list
        .exclude(
            status_kemajuan__in=ACTIVE_STATUS
        )
        .count()
    )

    total_kelompok = (
        peserta_list
        .exclude(kelompok=None)
        .values("kelompok")
        .distinct()
        .count()
    )

    context = {
        "setting": setting,
        "peserta": peserta_list,
        "peserta_list": peserta_list,
        "total_peserta": total_peserta,
        "total_aktif": total_aktif,
        "total_gugur": total_gugur,
        "total_kelompok": total_kelompok,
    }

    return render(
        request,
        "praktikum/informasi_peserta.html",
        context,
    )


# ============================================================
# LOGIN KELOMPOK
# ============================================================

def login_kelompok(request):

    if request.session.get("kelompok_id"):
        return redirect(
            "praktikum:dashboard_kelompok"
        )

    if request.method == "POST":

        username = (
            request.POST
            .get("username", "")
            .strip()
        )

        password = (
            request.POST
            .get("password", "")
        )

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:

            kelompok = (
                Kelompok.objects
                .filter(
                    akun_login=user,
                    aktif=True,
                )
                .first()
            )

            if kelompok:

                login(
                    request,
                    user,
                )

                request.session[
                    "kelompok_id"
                ] = kelompok.id

                request.session.set_expiry(
                    60 * 60 * 12
                )

                messages.success(
                    request,
                    f"Selamat datang, {kelompok.nama}.",
                )

                return redirect(
                    "praktikum:dashboard_kelompok"
                )

        messages.error(
            request,
            "Username atau password tidak valid.",
        )

    return render(
        request,
        "praktikum/login_kelompok.html",
    )


# ============================================================
# LOGOUT
# ============================================================

def logout_kelompok(request):

    request.session.pop(
        "kelompok_id",
        None,
    )

    logout(request)

    messages.success(
        request,
        "Anda berhasil keluar dari akun.",
    )

    return redirect(
        "praktikum:home"
    )


# ============================================================
# DASHBOARD KELOMPOK
# ============================================================

def dashboard_kelompok(request):

    kelompok = get_kelompok_login(request)

    if not kelompok:
        messages.warning(
            request,
            "Silakan login terlebih dahulu.",
        )

        return redirect(
            "praktikum:login_kelompok"
        )

    setting = Setting.objects.first()

    anggota = (
        Peserta.objects
        .filter(
            kelompok=kelompok,
            aktif=True,
        )
        .order_by("nama")
    )

    laporan = (
        Laporan.objects
        .filter(
            kelompok=kelompok,
        )
        .order_by("-id")
    )

    revisi = (
        Revisi.objects
        .filter(
            laporan__kelompok=kelompok,
        )
        .order_by("-id")
    )

    daily_mom = (
        DailyMOM.objects
        .filter(
            kelompok=kelompok,
        )
        .order_by(
            "-tanggal",
            "-id",
        )
    )

    acara_list = (
        Acara.objects
        .all()
        .order_by(
            "urutan",
            "tanggal_mulai",
        )
    )

    context = {
        "setting": setting,
        "kelompok": kelompok,
        "anggota": anggota,
        "peserta": anggota,
        "laporan": laporan,
        "revisi": revisi,
        "daily_mom": daily_mom,
        "acara": acara_list,
        "acara_list": acara_list,
        "progress": getattr(
            kelompok,
            "progress_persen",
            0,
        ),
        "mentor": getattr(
            kelompok,
            "mentor",
            None,
        ),
    }

    return render(
        request,
        "praktikum/dashboard_kelompok.html",
        context,
    )


# ============================================================
# DASHBOARD PESERTA
# ============================================================

def dashboard_peserta(request):

    peserta = get_peserta_login(request)

    if not peserta:
        messages.warning(
            request,
            "Akun peserta belum terhubung.",
        )

        return redirect(
            "praktikum:login_kelompok"
        )

    setting = Setting.objects.first()

    kelompok = peserta.kelompok

    laporan = (
        Laporan.objects
        .filter(
            kelompok=kelompok,
        )
        .order_by("-id")
    )

    revisi = (
        Revisi.objects
        .filter(
            laporan__kelompok=kelompok,
        )
        .order_by("-id")
    )

    context = {
        "setting": setting,
        "peserta": peserta,
        "kelompok": kelompok,
        "laporan": laporan,
        "revisi": revisi,
    }

    return render(
        request,
        "praktikum/dashboard_peserta.html",
        context,
    )


# ============================================================
# UPLOAD LAPORAN
# ============================================================

def upload_laporan(request):

    kelompok = get_kelompok_login(request)

    if not kelompok:
        messages.warning(
            request,
            "Silakan login terlebih dahulu.",
        )

        return redirect(
            "praktikum:login_kelompok"
        )

    if request.method != "POST":
        return redirect(
            "praktikum:dashboard_kelompok"
        )

    file_laporan = request.FILES.get(
        "file_laporan"
    )

    judul = (
        request.POST
        .get("judul", "")
        .strip()
    )

    if not file_laporan:
        messages.error(
            request,
            "File laporan belum dipilih.",
        )

        return redirect(
            "praktikum:dashboard_kelompok"
        )

    Laporan.objects.create(
        kelompok=kelompok,
        judul=judul or "Laporan Kelompok",
        file=file_laporan,
    )

    messages.success(
        request,
        "Laporan berhasil diupload.",
    )

    return redirect(
        "praktikum:dashboard_kelompok"
    )


# ============================================================
# DOWNLOAD FILE REVISI
# ============================================================

def download_file_revisi(
    request,
    laporan_id,
):

    kelompok = get_kelompok_login(request)

    if not kelompok:
        messages.warning(
            request,
            "Silakan login terlebih dahulu.",
        )

        return redirect(
            "praktikum:login_kelompok"
        )

    laporan = get_object_or_404(
        Laporan,
        id=laporan_id,
        kelompok=kelompok,
    )

    revisi = (
        Revisi.objects
        .filter(
            laporan=laporan,
        )
        .order_by("-id")
        .first()
    )

    if not revisi:
        raise Http404(
            "File revisi tidak ditemukan."
        )

    file_field = getattr(
        revisi,
        "file",
        None,
    )

    if not file_field:
        raise Http404(
            "File revisi tidak tersedia."
        )

    try:
        return FileResponse(
            file_field.open("rb"),
            as_attachment=True,
            filename=file_field.name.split("/")[-1],
        )
    except Exception:
        raise Http404(
            "File revisi tidak dapat dibuka."
        )
