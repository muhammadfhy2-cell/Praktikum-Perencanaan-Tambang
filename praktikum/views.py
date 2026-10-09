
# ============================================================
# HELPER FILE DAN HAK AKSES ADMIN
# ============================================================

from pathlib import Path

from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST


def _admin_boleh_mengunduh(request, model_name, obj):
    """
    Unduhan melalui endpoint admin hanya diperbolehkan
    untuk staf yang memiliki izin melihat atau mengubah data.
    """
    user = request.user

    if not user.is_authenticated or not user.is_staff:
        return False

    if user.is_superuser:
        return True

    opts = obj._meta

    return (
        user.has_perm(f"{opts.app_label}.view_{model_name}")
        or user.has_perm(f"{opts.app_label}.change_{model_name}")
    )


def _kirim_file(field_file, filename=None, as_attachment=True):
    """
    Mengirim file dari storage Django.
    Jika file fisiknya hilang atau tidak dapat dibuka,
    kembalikan 404 dengan aman.
    """
    if not field_file or not getattr(field_file, "name", ""):
        raise Http404("File tidak ditemukan.")

    try:
        file_obj = field_file.open("rb")
        nama_file = filename or Path(field_file.name).name

        return FileResponse(
            file_obj,
            as_attachment=as_attachment,
            filename=nama_file,
        )
    except (OSError, ValueError, FileNotFoundError):
        raise Http404(
            "File tidak tersedia di penyimpanan server. "
            "Periksa apakah file masih tersimpan pada media storage."
        )


# ============================================================
# DOWNLOAD LAPORAN MINGGUAN OLEH ADMIN
# ============================================================

def download_laporan_mingguan_admin(request, laporan_id, jenis):
    laporan = get_object_or_404(
        LaporanMingguan,
        pk=laporan_id,
    )

    if not _admin_boleh_mengunduh(
        request,
        "laporanmingguan",
        laporan,
    ):
        return HttpResponseForbidden(
            "Akun Anda tidak memiliki izin untuk mengunduh laporan ini."
        )

    if jenis == "asli":
        field_file = laporan.file
    elif jenis == "revisi":
        field_file = laporan.file_revisi
    else:
        raise Http404("Jenis file tidak dikenal.")

    return _kirim_file(field_file)


# ============================================================
# DOWNLOAD LAPORAN LENGKAP OLEH ADMIN
# ============================================================

def download_laporan_lengkap_admin(request, laporan_id, jenis):
    laporan = get_object_or_404(
        LaporanLengkap,
        pk=laporan_id,
    )

    if not _admin_boleh_mengunduh(
        request,
        "laporanlengkap",
        laporan,
    ):
        return HttpResponseForbidden(
            "Akun Anda tidak memiliki izin untuk mengunduh laporan ini."
        )

    if jenis == "asli":
        field_file = laporan.file
    elif jenis == "revisi":
        field_file = laporan.file_revisi
    else:
        raise Http404("Jenis file tidak dikenal.")

    return _kirim_file(field_file)


# ============================================================
# DOWNLOAD LAPORAN MINGGUAN OLEH KELOMPOK
# ============================================================

def download_laporan_mingguan(request, laporan_id):
    kelompok = get_kelompok_login(request)

    if not kelompok:
        return redirect("praktikum:login_kelompok")

    laporan = get_object_or_404(
        LaporanMingguan,
        pk=laporan_id,
        kelompok=kelompok,
    )

    return _kirim_file(laporan.file)


# ============================================================
# DOWNLOAD REVISI LAPORAN MINGGUAN OLEH KELOMPOK
# ============================================================

def download_file_revisi(request, laporan_id):
    kelompok = get_kelompok_login(request)

    if not kelompok:
        return redirect("praktikum:login_kelompok")

    laporan = get_object_or_404(
        LaporanMingguan,
        pk=laporan_id,
        kelompok=kelompok,
    )

    return _kirim_file(laporan.file_revisi)


# ============================================================
# DOWNLOAD LAPORAN LENGKAP OLEH KELOMPOK PEMILIK
# ============================================================

def download_laporan_lengkap(request, laporan_id):
    kelompok = get_kelompok_login(request)

    if not kelompok:
        return redirect("praktikum:login_kelompok")

    laporan = get_object_or_404(
        LaporanLengkap,
        pk=laporan_id,
        kelompok=kelompok,
    )

    return _kirim_file(laporan.file)


# ============================================================
# DOWNLOAD REVISI LAPORAN LENGKAP OLEH KELOMPOK PEMILIK
# ============================================================

def download_laporan_lengkap_revisi(request, laporan_id):
    kelompok = get_kelompok_login(request)

    if not kelompok:
        return redirect("praktikum:login_kelompok")

    laporan = get_object_or_404(
        LaporanLengkap,
        pk=laporan_id,
        kelompok=kelompok,
    )

    return _kirim_file(laporan.file_revisi)


# ============================================================
# DOWNLOAD LAPORAN LENGKAP PUBLIK
# HANYA LAPORAN ACC DARI KELOMPOK AKTIF
# ============================================================

def download_laporan_lengkap_publik(request, laporan_id):
    laporan = get_object_or_404(
        LaporanLengkap.objects.select_related("kelompok"),
        pk=laporan_id,
        status="acc",
        kelompok__aktif=True,
    )

    return _kirim_file(laporan.file)


# ============================================================
# UPLOAD LOGO KELOMPOK
# ============================================================

@require_POST
def upload_logo_kelompok(request):
    kelompok = get_kelompok_login(request)

    if not kelompok:
        return redirect("praktikum:login_kelompok")

    logo_baru = request.FILES.get("logo")

    if not logo_baru:
        messages.error(request, "Pilih file logo terlebih dahulu.")
        return redirect("praktikum:dashboard_kelompok")

    ukuran_maksimum = 5 * 1024 * 1024

    if logo_baru.size > ukuran_maksimum:
        messages.error(
            request,
            "Ukuran logo maksimal 5 MB.",
        )
        return redirect("praktikum:dashboard_kelompok")

    ekstensi = Path(logo_baru.name).suffix.lower()

    if ekstensi not in {".jpg", ".jpeg", ".png", ".webp"}:
        messages.error(
            request,
            "Logo harus berformat JPG, JPEG, PNG, atau WEBP.",
        )
        return redirect("praktikum:dashboard_kelompok")

    try:
        from PIL import Image, UnidentifiedImageError

        gambar = Image.open(logo_baru)
        gambar.verify()

    except (ImportError, UnidentifiedImageError, OSError, ValueError):
        messages.error(
            request,
            "File logo tidak valid atau bukan gambar yang dapat dibaca.",
        )
        return redirect("praktikum:dashboard_kelompok")

    logo_baru.seek(0)

    kelompok.logo = logo_baru
    kelompok.save(update_fields=["logo"])

    messages.success(
        request,
        "Logo kelompok berhasil diperbarui.",
    )

    return redirect("praktikum:dashboard_kelompok")
