
from pathlib import Path

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db.models import Case, When, Value, IntegerField, Prefetch
from django.http import FileResponse, Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import (
    Absensi,
    Acara,
    DailyMOM,
    FileKelompok,
    FormatDokumen,
    Kelompok,
    Konsultasi,
    LaporanLengkap,
    LaporanMingguan,
    Materi,
    Pengumuman,
    Peserta,
    ProgressAcara,
    Setting,
    Staff,
    TataTertib,
    TugasPendahuluan,
)

ACTIVE_STATUS = "aktif"
GUGUR_STATUS = "gugur"


# ============================================================
# HELPER
# ============================================================

def urutan_jabatan_peserta():
    return Case(
        When(jabatan__iexact="ketua", then=Value(0)),
        When(jabatan__iexact="ketua kelompok", then=Value(0)),
        When(jabatan__iexact="ketua_kelompok", then=Value(0)),
        When(jabatan__iexact="anggota", then=Value(1)),
        default=Value(2),
        output_field=IntegerField(),
    )


def get_setting():
    return Setting.objects.first()


def get_kelompok_login(request):
    kelompok_id = request.session.get("kelompok_id")
    if not kelompok_id:
        return None

    return (
        Kelompok.objects
        .filter(id=kelompok_id, aktif=True)
        .prefetch_related(
            Prefetch(
                "peserta",
                queryset=Peserta.objects.order_by(
                    urutan_jabatan_peserta(), "nama"
                ),
            ),
            "mentor",
        )
        .first()
    )


def get_user_kelompok(request):
    if not request.user.is_authenticated:
        return None

    return (
        Kelompok.objects
        .filter(akun_login=request.user, aktif=True)
        .prefetch_related(
            Prefetch(
                "peserta",
                queryset=Peserta.objects.order_by(
                    urutan_jabatan_peserta(), "nama"
                ),
            ),
            "mentor",
        )
        .first()
    )


def get_peserta_login(request):
    if not request.user.is_authenticated:
        return None

    return (
        Peserta.objects
        .select_related("kelompok")
        .filter(
            akun=request.user,
            aktif=True,
            status_kemajuan=ACTIVE_STATUS,
        )
        .first()
    )


def _kirim_file(field_file, filename=None, as_attachment=True):
    """Kirim file melalui storage Django dan tangani file yang hilang."""
    if not field_file or not getattr(field_file, "name", ""):
        raise Http404("File belum tersedia.")

    try:
        storage = field_file.storage
        nama_storage = field_file.name

        if not storage.exists(nama_storage):
            raise Http404(
                "File tidak ditemukan di penyimpanan server. "
                "Silakan unggah ulang file tersebut."
            )

        file_obj = storage.open(nama_storage, "rb")
        nama_file = filename or Path(nama_storage).name

        return FileResponse(
            file_obj,
            as_attachment=as_attachment,
            filename=nama_file,
        )

    except Http404:
        raise
    except (OSError, ValueError, FileNotFoundError):
        raise Http404(
            "File gagal dibuka dari penyimpanan server. "
            "Periksa konfigurasi penyimpanan media."
        )


def _admin_boleh_mengunduh(request, model_name, obj):
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


# ============================================================
# BERANDA PUBLIK
# ============================================================

def home(request):
    setting = get_setting()

    staff_list = Staff.objects.filter(
        aktif=True
    ).order_by("jabatan", "urutan", "nama")

    kelompok_list = (
        Kelompok.objects
        .filter(aktif=True)
        .prefetch_related(
            Prefetch(
                "mentor",
                queryset=Staff.objects.filter(
                    aktif=True
                ).order_by("id"),
            ),
            Prefetch(
                "peserta",
                queryset=Peserta.objects.filter(
                    aktif=True,
                    status_kemajuan=ACTIVE_STATUS,
                ).order_by(urutan_jabatan_peserta(), "nama"),
            ),
        )
        .order_by("id")
    )

    acara_list = (
        Acara.objects
        .select_related("penanggung_jawab")
        .prefetch_related(
            Prefetch(
                "pembawa_acara",
                queryset=Staff.objects.filter(aktif=True),
            )
        )
        .order_by("urutan", "tanggal_mulai")
    )

    materi_list = Materi.objects.select_related(
        "acara"
    ).order_by("-uploaded_at", "-id")

    pengumuman_list = Pengumuman.objects.filter(
        aktif=True
    ).order_by("-dibuat", "-id")

    peserta_list = (
        Peserta.objects
        .filter(aktif=True)
        .select_related("kelompok")
        .order_by(
            "kelompok_id", urutan_jabatan_peserta(), "nama"
        )
    )

    koordinator = staff_list.filter(
        jabatan="koordinator"
    ).first()

    penanggung_jawab = staff_list.filter(
        jabatan="penanggung_jawab"
    ).first()

    asisten_list = staff_list.filter(
        jabatan="asisten"
    ).order_by("urutan", "nama")

    format_list = FormatDokumen.objects.filter(
        aktif=True
    ).order_by("-uploaded_at", "-id")

    context = {
        "setting": setting,
        "staff": staff_list,
        "staff_list": staff_list,
        "personel": staff_list,
        "personel_list": staff_list,
        "asisten": asisten_list,
        "asisten_list": asisten_list,
        "koordinator": koordinator,
        "penanggung_jawab": penanggung_jawab,
        "kelompok": kelompok_list,
        "kelompok_list": kelompok_list,
        "acara": acara_list,
        "acara_list": acara_list,
        "materi": materi_list,
        "materi_list": materi_list,
        "pengumuman": pengumuman_list,
        "pengumuman_list": pengumuman_list,
        "items": pengumuman_list,
        "peserta": peserta_list,
        "peserta_list": peserta_list,
        "format_dokumen": format_list,
    }

    return render(request, "praktikum/home.html", context)


# ============================================================
# PERSONEL
# ============================================================

def personel(request):
    setting = get_setting()

    staff_list = Staff.objects.filter(
        aktif=True
    ).order_by("jabatan", "urutan", "nama")

    penanggung_jawab = staff_list.filter(
        jabatan="penanggung_jawab"
    ).order_by("urutan", "nama")

    koordinator = staff_list.filter(
        jabatan="koordinator"
    ).order_by("urutan", "nama")

    asisten_list = staff_list.filter(
        jabatan="asisten"
    ).order_by("urutan", "nama")

    return render(request, "praktikum/personel.html", {
        "setting": setting,
        "staff": staff_list,
        "staff_list": staff_list,
        "personel": staff_list,
        "personel_list": staff_list,
        "penanggung_jawab": penanggung_jawab,
        "koordinator": koordinator,
        "asisten": asisten_list,
        "asisten_list": asisten_list,
    })


# ============================================================
# KELOMPOK - INFORMASI PUBLIK
# ============================================================

def kelompok(request):
    setting = get_setting()

    kelompok_list = (
        Kelompok.objects
        .filter(aktif=True)
        .prefetch_related(
            Prefetch(
                "mentor",
                queryset=Staff.objects.filter(
                    aktif=True
                ).order_by("id"),
            ),
            Prefetch(
                "peserta",
                queryset=Peserta.objects.filter(
                    aktif=True,
                    status_kemajuan=ACTIVE_STATUS,
                ).order_by(urutan_jabatan_peserta(), "nama"),
            ),
        )
        .order_by("id")
    )

    # Daily MOM kelompok aktif untuk ditampilkan pada halaman publik.
    daily_mom_publik = (
        DailyMOM.objects
        .filter(kelompok__aktif=True)
        .select_related("kelompok", "acara", "dibuat_oleh")
        .order_by("-tanggal", "-id")
    )

    # Publik hanya memperoleh metadata laporan yang telah disetujui.
    # Jangan menyediakan tautan unduhan atau konten file laporan.
    laporan_mingguan_publik = (
        LaporanMingguan.objects
        .filter(kelompok__aktif=True, status="acc")
        .select_related("kelompok", "peserta", "acara")
        .order_by("kelompok__nama", "-uploaded_at", "-id")
    )

    laporan_lengkap_publik = (
        LaporanLengkap.objects
        .filter(kelompok__aktif=True, status="acc")
        .select_related("kelompok")
        .order_by("kelompok__nama", "-uploaded_at", "-id")
    )

    return render(request, "praktikum/kelompok.html", {
        "setting": setting,
        "kelompok": kelompok_list,
        "kelompok_list": kelompok_list,
        "daily_mom_publik": daily_mom_publik,
        "laporan_mingguan_publik": laporan_mingguan_publik,
        "laporan_lengkap_publik": laporan_lengkap_publik,
    })


# ============================================================
# JADWAL
# ============================================================

def jadwal(request):
    setting = get_setting()

    acara_list = (
        Acara.objects
        .select_related("penanggung_jawab")
        .prefetch_related(
            Prefetch(
                "pembawa_acara",
                queryset=Staff.objects.filter(aktif=True),
            )
        )
        .order_by("urutan", "tanggal_mulai")
    )

    return render(request, "praktikum/jadwal.html", {
        "setting": setting,
        "acara": acara_list,
        "acara_list": acara_list,
    })


# ============================================================
# MATERI
# ============================================================

def materi(request):
    setting = get_setting()

    materi_list = Materi.objects.select_related(
        "acara"
    ).order_by("-uploaded_at", "-id")

    return render(request, "praktikum/materi.html", {
        "setting": setting,
        "materi": materi_list,
        "materi_list": materi_list,
    })


# ============================================================
# ABSENSI
# ============================================================

def absensi(request):
    setting = get_setting()

    peserta_list = (
        Peserta.objects
        .filter(aktif=True)
        .select_related("kelompok")
        .prefetch_related("absensi")
        .order_by(
            "kelompok_id", urutan_jabatan_peserta(), "nama"
        )
    )

    rows = []

    for peserta in peserta_list:
        daftar_absensi = list(peserta.absensi.all())
        total_acara = len(daftar_absensi)
        total_nilai = sum(
            item.nilai_persentase for item in daftar_absensi
        )

        persentase = (
            round(total_nilai / total_acara, 2)
            if total_acara else 0
        )

        rows.append({
            "peserta": peserta,
            "total_acara": total_acara,
            "total_nilai": total_nilai,
            "persentase": persentase,
        })

    kelompok_list = Kelompok.objects.filter(
        aktif=True
    ).order_by("id")

    return render(request, "praktikum/absensi.html", {
        "setting": setting,
        "rows": rows,
        "peserta": peserta_list,
        "peserta_list": peserta_list,
        "kelompok": kelompok_list,
        "kelompok_list": kelompok_list,
    })


# ============================================================
# PENGUMUMAN
# ============================================================

def pengumuman(request):
    setting = get_setting()

    pengumuman_list = Pengumuman.objects.filter(
        aktif=True
    ).order_by("-dibuat", "-id")

    return render(request, "praktikum/pengumuman.html", {
        "setting": setting,
        "pengumuman": pengumuman_list,
        "pengumuman_list": pengumuman_list,
        "items": pengumuman_list,
    })


# ============================================================
# TATA TERTIB
# ============================================================

def tata_tertib(request):
    setting = get_setting()

    tata_tertib_list = TataTertib.objects.filter(
        aktif=True
    ).order_by("urutan", "id")

    return render(request, "praktikum/tata_tertib.html", {
        "setting": setting,
        "tata_tertib": tata_tertib_list,
        "tata_tertib_list": tata_tertib_list,
        "items": tata_tertib_list,
    })


# ============================================================
# TUGAS PENDAHULUAN
# ============================================================

def tugas_pendahuluan(request):
    setting = get_setting()

    tugas_list = (
        TugasPendahuluan.objects
        .filter(aktif=True)
        .select_related("acara")
        .order_by("-dibuat", "-id")
    )

    return render(request, "praktikum/tugas_pendahuluan.html", {
        "setting": setting,
        "tugas": tugas_list,
        "tugas_list": tugas_list,
    })


# ============================================================
# INFORMASI PESERTA
# ============================================================

def informasi_peserta(request):
    setting = get_setting()

    peserta_list = (
        Peserta.objects
        .filter(aktif=True)
        .select_related("kelompok")
        .order_by(
            "kelompok_id", urutan_jabatan_peserta(), "nama"
        )
    )

    total_peserta = peserta_list.count()

    total_aktif = peserta_list.filter(
        status_kemajuan=ACTIVE_STATUS
    ).count()

    total_gugur = Peserta.objects.filter(
        aktif=True,
        status_kemajuan=GUGUR_STATUS,
    ).count()

    total_kelompok = (
        peserta_list
        .filter(kelompok__isnull=False)
        .values("kelompok_id")
        .distinct()
        .count()
    )

    return render(request, "praktikum/informasi_peserta.html", {
        "setting": setting,
        "peserta": peserta_list,
        "peserta_list": peserta_list,
        "total_peserta": total_peserta,
        "total_aktif": total_aktif,
        "total_gugur": total_gugur,
        "total_kelompok": total_kelompok,
    })


# ============================================================
# FORMAT DOKUMEN
# ============================================================

def format_dokumen(request):
    setting = get_setting()

    format_list = FormatDokumen.objects.filter(
        aktif=True
    ).order_by("-uploaded_at", "-id")

    return render(request, "praktikum/format_dokumen.html", {
        "setting": setting,
        "format_dokumen": format_list,
        "format_dokumen_list": format_list,
        "items": format_list,
    })


# ============================================================
# LOGIN KELOMPOK
# ============================================================

def login_kelompok(request):
    if request.session.get("kelompok_id"):
        return redirect("praktikum:dashboard_kelompok")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:
            kelompok = Kelompok.objects.filter(
                akun_login=user,
                aktif=True,
            ).first()

            if kelompok:
                login(request, user)
                request.session["kelompok_id"] = kelompok.id
                request.session.set_expiry(60 * 60 * 12)

                messages.success(
                    request,
                    f"Selamat datang, {kelompok.nama}.",
                )
                return redirect("praktikum:dashboard_kelompok")

        messages.error(
            request,
            "Username atau password tidak valid.",
        )

    return render(request, "praktikum/login_kelompok.html")


# ============================================================
# LOGOUT
# ============================================================

def logout_kelompok(request):
    request.session.pop("kelompok_id", None)
    logout(request)

    messages.success(request, "Anda berhasil keluar dari akun.")
    return redirect("praktikum:home")


# ============================================================
# DASHBOARD KELOMPOK
# ============================================================

def dashboard_kelompok(request):
    kelompok = get_kelompok_login(request)

    if not kelompok:
        messages.warning(request, "Silakan login terlebih dahulu.")
        return redirect("praktikum:login_kelompok")

    setting = get_setting()

    anggota = Peserta.objects.filter(
        kelompok=kelompok,
        aktif=True,
        status_kemajuan=ACTIVE_STATUS,
    ).order_by(urutan_jabatan_peserta(), "nama")

    laporan = (
        LaporanMingguan.objects
        .filter(kelompok=kelompok)
        .select_related("peserta", "acara")
        .order_by("-uploaded_at", "-id")
    )

    daily_mom = (
        DailyMOM.objects
        .filter(kelompok=kelompok)
        .select_related("acara", "dibuat_oleh")
        .order_by("-tanggal", "-id")
    )

    progress_acara = (
        ProgressAcara.objects
        .filter(kelompok=kelompok)
        .select_related("acara")
        .order_by("acara__urutan", "acara__tanggal_mulai")
    )

    file_kelompok = (
        FileKelompok.objects
        .filter(kelompok=kelompok)
        .select_related("acara", "uploaded_by")
        .order_by("-uploaded_at", "-id")
    )

    laporan_lengkap = (
        LaporanLengkap.objects
        .filter(kelompok=kelompok)
        .order_by("-uploaded_at", "-id")
    )

    konsultasi = (
        Konsultasi.objects
        .filter(kelompok=kelompok)
        .select_related("peserta", "tujuan", "acara")
        .order_by("-dibuat", "-id")
    )

    acara_list = (
        Acara.objects
        .select_related("penanggung_jawab")
        .prefetch_related(
            Prefetch(
                "pembawa_acara",
                queryset=Staff.objects.filter(aktif=True),
            )
        )
        .order_by("urutan", "tanggal_mulai")
    )

    mentor_list = kelompok.mentor.filter(
        aktif=True
    ).order_by("jabatan", "urutan", "nama")

    context = {
        "setting": setting,
        "kelompok": kelompok,
        "anggota": anggota,
        "peserta": anggota,
        "laporan": laporan,
        "laporan_mingguan": laporan,
        "daily_mom": daily_mom,
        "progress_acara": progress_acara,
        "progress_list": progress_acara,
        "file_kelompok": file_kelompok,
        "file_kelompok_list": file_kelompok,
        "laporan_lengkap": laporan_lengkap,
        "laporan_lengkap_list": laporan_lengkap,
        "konsultasi": konsultasi,
        "konsultasi_list": konsultasi,
        "acara": acara_list,
        "acara_list": acara_list,
        "progress": getattr(kelompok, "progress_persen", 0),
        "mentor": mentor_list,
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
            "Akun peserta belum terhubung atau sudah tidak aktif.",
        )
        return redirect("praktikum:login_kelompok")

    setting = get_setting()
    kelompok = peserta.kelompok

    if not kelompok or not kelompok.aktif:
        messages.warning(request, "Kelompok peserta tidak aktif.")
        return redirect("praktikum:login_kelompok")

    laporan = (
        LaporanMingguan.objects
        .filter(kelompok=kelompok, peserta=peserta)
        .select_related("acara")
        .order_by("-uploaded_at", "-id")
    )

    absensi_list = (
        Absensi.objects
        .filter(peserta=peserta)
        .select_related("acara")
        .order_by("-acara__tanggal_mulai")
    )

    file_list = (
        FileKelompok.objects
        .filter(kelompok=kelompok)
        .select_related("acara", "uploaded_by")
        .order_by("-uploaded_at", "-id")
    )

    progress_list = (
        ProgressAcara.objects
        .filter(kelompok=kelompok)
        .select_related("acara")
        .order_by("acara__urutan", "acara__tanggal_mulai")
    )

    konsultasi_list = (
        Konsultasi.objects
        .filter(kelompok=kelompok, peserta=peserta)
        .select_related("tujuan", "acara")
        .order_by("-dibuat", "-id")
    )

    return render(request, "praktikum/dashboard_peserta.html", {
        "setting": setting,
        "peserta": peserta,
        "kelompok": kelompok,
        "laporan": laporan,
        "laporan_mingguan": laporan,
        "absensi": absensi_list,
        "absensi_list": absensi_list,
        "file_kelompok": file_list,
        "file_kelompok_list": file_list,
        "progress_acara": progress_list,
        "progress_list": progress_list,
        "konsultasi": konsultasi_list,
        "konsultasi_list": konsultasi_list,
    })


# ============================================================
# UPLOAD LAPORAN MINGGUAN
# ============================================================

@require_POST
def upload_laporan(request):
    kelompok = get_kelompok_login(request)

    if not kelompok:
        messages.warning(request, "Silakan login terlebih dahulu.")
        return redirect("praktikum:login_kelompok")

    file_laporan = request.FILES.get("file_laporan")
    judul = request.POST.get("judul", "").strip()
    acara_id = request.POST.get("acara", "").strip()
    peserta_id = request.POST.get("peserta", "").strip()

    if not file_laporan:
        messages.error(request, "File laporan belum dipilih.")
        return redirect("praktikum:dashboard_kelompok")

    if not acara_id:
        messages.error(request, "Acara laporan belum dipilih.")
        return redirect("praktikum:dashboard_kelompok")

    if not peserta_id:
        messages.error(request, "Peserta pengunggah belum dipilih.")
        return redirect("praktikum:dashboard_kelompok")

    peserta = get_object_or_404(
        Peserta,
        id=peserta_id,
        kelompok=kelompok,
        aktif=True,
        status_kemajuan=ACTIVE_STATUS,
    )

    acara = get_object_or_404(Acara, id=acara_id)

    LaporanMingguan.objects.create(
        peserta=peserta,
        kelompok=kelompok,
        acara=acara,
        judul=judul or "Laporan Mingguan",
        file=file_laporan,
    )

    messages.success(request, "Laporan berhasil diupload.")
    return redirect("praktikum:dashboard_kelompok")


# ============================================================
# DOWNLOAD MATERI
# ============================================================

def download_materi(request, materi_id):
    item = get_object_or_404(Materi, pk=materi_id)
    return _kirim_file(item.file)


# ============================================================
# DOWNLOAD FORMAT DOKUMEN
# ============================================================

def download_format_dokumen(request, dokumen_id):
    item = get_object_or_404(
        FormatDokumen,
        pk=dokumen_id,
        aktif=True,
    )
    return _kirim_file(item.file)


# ============================================================
# DOWNLOAD TUGAS PENDAHULUAN
# ============================================================

def download_tugas_pendahuluan(request, tugas_id):
    item = get_object_or_404(
        TugasPendahuluan,
        pk=tugas_id,
        aktif=True,
    )

    # Asumsi nama field file adalah "file".
    # Sesuaikan jika model TugasPendahuluan menggunakan nama lain.
    if not item.file or not item.file.name:
        messages.error(
            request,
            "File tugas pendahuluan belum tersedia.",
        )
        return redirect("praktikum:tugas_pendahuluan")

    return _kirim_file(item.file)


# ============================================================
# DOWNLOAD LAPORAN MINGGUAN OLEH ADMIN
# ============================================================

def download_laporan_mingguan_admin(request, laporan_id, jenis):
    laporan = get_object_or_404(LaporanMingguan, pk=laporan_id)

    if not _admin_boleh_mengunduh(
        request, "laporanmingguan", laporan
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
    laporan = get_object_or_404(LaporanLengkap, pk=laporan_id)

    if not _admin_boleh_mengunduh(
        request, "laporanlengkap", laporan
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
# DOWNLOAD LAPORAN MINGGUAN OLEH KELOMPOK PEMILIK
# ============================================================

def download_laporan_mingguan(request, laporan_id):
    kelompok = get_kelompok_login(request)

    if not kelompok:
        messages.warning(request, "Silakan login terlebih dahulu.")
        return redirect("praktikum:login_kelompok")

    laporan = get_object_or_404(
        LaporanMingguan,
        pk=laporan_id,
        kelompok=kelompok,
    )

    return _kirim_file(laporan.file)


def download_file_revisi(request, laporan_id):
    kelompok = get_kelompok_login(request)

    if not kelompok:
        messages.warning(request, "Silakan login terlebih dahulu.")
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
        messages.warning(request, "Silakan login terlebih dahulu.")
        return redirect("praktikum:login_kelompok")

    laporan = get_object_or_404(
        LaporanLengkap,
        pk=laporan_id,
        kelompok=kelompok,
    )

    return _kirim_file(laporan.file)


def download_laporan_lengkap_revisi(request, laporan_id):
    kelompok = get_kelompok_login(request)

    if not kelompok:
        messages.warning(request, "Silakan login terlebih dahulu.")
        return redirect("praktikum:login_kelompok")

    laporan = get_object_or_404(
        LaporanLengkap,
        pk=laporan_id,
        kelompok=kelompok,
    )

    return _kirim_file(laporan.file_revisi)


# ============================================================
# DOWNLOAD LAPORAN LENGKAP PUBLIK DINONAKTIFKAN
# ============================================================

def download_laporan_lengkap_publik(request, laporan_id):
    # Laporan yang disetujui hanya diumumkan di halaman publik.
    # File tetap hanya dapat diakses melalui hak akses yang sesuai.
    raise Http404(
        "Laporan lengkap hanya ditampilkan sebagai informasi "
        "persetujuan dan tidak dapat diunduh oleh publik."
    )


# ============================================================
# UPLOAD LAPORAN LENGKAP
# ============================================================

@require_POST
def upload_laporan_lengkap(request):
    kelompok = get_kelompok_login(request)

    if not kelompok:
        messages.warning(request, "Silakan login terlebih dahulu.")
        return redirect("praktikum:login_kelompok")

    file_laporan = (
        request.FILES.get("file_laporan")
        or request.FILES.get("file")
    )

    judul = request.POST.get(
        "judul", "Laporan Lengkap"
    ).strip()

    if not file_laporan:
        messages.error(
            request,
            "Pilih file laporan lengkap terlebih dahulu.",
        )
        return redirect("praktikum:dashboard_kelompok")

    LaporanLengkap.objects.create(
        kelompok=kelompok,
        judul=judul or "Laporan Lengkap",
        file=file_laporan,
        status="menunggu",
    )

    messages.success(
        request,
        "Laporan lengkap berhasil diunggah.",
    )
    return redirect("praktikum:dashboard_kelompok")


# ============================================================
# UPLOAD LOGO KELOMPOK
# ============================================================

@require_POST
def upload_logo_kelompok(request):
    kelompok = get_kelompok_login(request)

    if not kelompok:
        messages.warning(request, "Silakan login terlebih dahulu.")
        return redirect("praktikum:login_kelompok")

    logo_baru = (
        request.FILES.get("logo")
        or request.FILES.get("logo_kelompok")
    )

    if not logo_baru:
        messages.error(request, "Pilih file logo terlebih dahulu.")
        return redirect("praktikum:dashboard_kelompok")

    if logo_baru.size > 5 * 1024 * 1024:
        messages.error(request, "Ukuran logo maksimal 5 MB.")
        return redirect("praktikum:dashboard_kelompok")

    ekstensi = Path(logo_baru.name).suffix.lower()

    if ekstensi not in {".jpg", ".jpeg", ".png", ".webp"}:
        messages.error(
            request,
            "Logo harus berformat JPG, JPEG, PNG, atau WEBP.",
        )
        return redirect("praktikum:dashboard_kelompok")

    try:
        from PIL import Image

        gambar = Image.open(logo_baru)
        gambar.verify()
    except Exception:
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


# ============================================================
# DOWNLOAD FILE KELOMPOK OLEH KELOMPOK PEMILIK
# ============================================================

def download_file_kelompok(request, file_id):
    kelompok = get_kelompok_login(request)

    if not kelompok:
        messages.warning(request, "Silakan login terlebih dahulu.")
        return redirect("praktikum:login_kelompok")

    item = get_object_or_404(
        FileKelompok,
        pk=file_id,
        kelompok=kelompok,
    )

    return _kirim_file(item.file)
