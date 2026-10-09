
from pathlib import Path

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db.models import Prefetch
from django.http import FileResponse, Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.dateparse import parse_date, parse_time
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
    Setting,
    Staff,
    TataTertib,
    TugasPendahuluan,
)


# ============================================================
# KONFIGURASI DAN HELPER
# ============================================================

ACTIVE_STATUS = "aktif"
GUGUR_STATUS = "gugur"


def get_setting():
    return Setting.objects.first()


def get_kelompok_login(request):
    kelompok_id = request.session.get("kelompok_id")

    if not kelompok_id:
        return None

    return (
        Kelompok.objects
        .filter(id=kelompok_id, aktif=True)
        .prefetch_related("mentor", "peserta")
        .first()
    )


def get_user_kelompok(request):
    if not request.user.is_authenticated:
        return None

    return (
        Kelompok.objects
        .filter(akun_login=request.user, aktif=True)
        .prefetch_related("mentor", "peserta")
        .first()
    )


def get_peserta_login(request):
    if not request.user.is_authenticated:
        return None

    return (
        Peserta.objects
        .filter(
            akun=request.user,
            aktif=True,
            status_kemajuan=ACTIVE_STATUS,
        )
        .select_related("kelompok")
        .first()
    )


def _kirim_file(field_file, *, as_attachment=True, filename=None):
    """Mengirim file menggunakan FileResponse Django."""

    if not field_file or not getattr(field_file, "name", ""):
        raise Http404("File tidak ditemukan.")

    try:
        file_obj = field_file.open("rb")
        return FileResponse(
            file_obj,
            as_attachment=as_attachment,
            filename=filename or Path(field_file.name).name,
        )
    except (OSError, ValueError, FileNotFoundError):
        raise Http404("File tidak tersedia di penyimpanan server.")


def _pastikan_admin(request):
    return bool(
        request.user.is_authenticated
        and (request.user.is_staff or request.user.is_superuser)
    )


def _redirect_dashboard_kelompok(request):
    if get_kelompok_login(request):
        return redirect("praktikum:dashboard_kelompok")

    request.session.pop("kelompok_id", None)
    return redirect("praktikum:login_kelompok")


# ============================================================
# BERANDA
# ============================================================

def home(request):
    setting = get_setting()

    staff_list = Staff.objects.filter(aktif=True).order_by(
        "jabatan", "urutan", "nama"
    )

    kelompok_list = (
        Kelompok.objects
        .filter(aktif=True)
        .prefetch_related(
            Prefetch(
                "mentor",
                queryset=Staff.objects.filter(aktif=True),
            ),
            Prefetch(
                "peserta",
                queryset=Peserta.objects.filter(
                    aktif=True,
                    status_kemajuan=ACTIVE_STATUS,
                ).order_by("jabatan", "nama"),
            ),
        )
        .order_by("nama")
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

    materi_list = Materi.objects.select_related("acara").order_by(
        "-uploaded_at", "-id"
    )

    pengumuman_list = Pengumuman.objects.filter(aktif=True).order_by(
        "-dibuat", "-id"
    )

    peserta_list = (
        Peserta.objects
        .filter(aktif=True)
        .select_related("kelompok")
        .order_by("kelompok__nama", "jabatan", "nama")
    )

    penanggung_jawab = staff_list.filter(
        jabatan="penanggung_jawab"
    ).first()

    koordinator = staff_list.filter(
        jabatan="koordinator"
    ).order_by("urutan", "nama").first()

    asisten_list = staff_list.filter(
        jabatan="asisten"
    ).order_by("urutan", "nama")

    format_list = FormatDokumen.objects.filter(aktif=True).order_by(
        "-uploaded_at", "-id"
    )

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

    # Ambil seluruh staff, diurutkan berdasarkan jabatan dan nama.
    staff_list = Staff.objects.filter(
        aktif=True
    ).order_by("jabatan", "urutan", "nama")

    # Ambil SELURUH penanggung jawab praktikum.
    # Tidak menggunakan .first() agar semua data ditampilkan.
    penanggung_jawab = staff_list.filter(
        jabatan__in=[
            "penanggung_jawab",
            "penanggung_jawab_praktikum",
            "penanggung jawab",
            "penanggung jawab praktikum",
        ]
    ).order_by("urutan", "nama")

    # Koordinator Asisten Dosen.
    koordinator = staff_list.filter(
        jabatan__in=[
            "koordinator",
            "koordinator_asisten_dosen",
            "koordinator asisten dosen",
        ]
    ).order_by("urutan", "nama")

    # Seluruh Asisten Dosen.
    asisten_list = staff_list.filter(
        jabatan__in=[
            "asisten",
            "asisten_dosen",
            "asisten dosen",
        ]
    ).order_by("urutan", "nama")

    context = {
        "setting": setting,
        "staff": staff_list,
        "staff_list": staff_list,
        "personel": staff_list,
        "personel_list": staff_list,
        "penanggung_jawab": penanggung_jawab,
        "koordinator": koordinator,
        "asisten": asisten_list,
        "asisten_list": asisten_list,
    }

    return render(
        request,
        "praktikum/personel.html",
        context,
    )


# ============================================================
# KELOMPOK DAN LAPORAN ACC UNTUK PUBLIK
# ============================================================

def kelompok(request):
    setting = get_setting()

    kelompok_list = (
        Kelompok.objects
        .filter(aktif=True)
        .prefetch_related(
            Prefetch(
                "mentor",
                queryset=Staff.objects.filter(aktif=True),
            ),
            Prefetch(
                "peserta",
                queryset=Peserta.objects.filter(
                    aktif=True,
                    status_kemajuan=ACTIVE_STATUS,
                ).order_by("jabatan", "nama"),
            ),
        )
        .order_by("nama")
    )

    laporan_lengkap_publik = (
        LaporanLengkap.objects
        .filter(kelompok__aktif=True, status="acc")
        .select_related("kelompok")
        .only(
            "id",
            "judul",
            "kelompok__nama",
            "uploaded_at",
            "updated_at",
        )
        .order_by("kelompok__nama", "-uploaded_at", "-id")
    )

    laporan_mingguan_publik = (
        LaporanMingguan.objects
        .filter(kelompok__aktif=True, status="acc")
        .select_related("kelompok", "acara")
        .only(
            "id",
            "judul",
            "kelompok__nama",
            "acara__nama",
            "uploaded_at",
            "updated_at",
        )
        .order_by("kelompok__nama", "-uploaded_at", "-id")
    )

    return render(
        request,
        "praktikum/kelompok.html",
        {
            "setting": setting,
            "kelompok": kelompok_list,
            "kelompok_list": kelompok_list,
            "laporan_lengkap_publik": laporan_lengkap_publik,
            "laporan_mingguan_publik": laporan_mingguan_publik,
        },
    )


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

    return render(
        request,
        "praktikum/jadwal.html",
        {
            "setting": setting,
            "acara": acara_list,
            "acara_list": acara_list,
        },
    )


# ============================================================
# MATERI
# ============================================================

def materi(request):
    setting = get_setting()

    materi_list = Materi.objects.select_related("acara").order_by(
        "-uploaded_at", "-id"
    )

    return render(
        request,
        "praktikum/materi.html",
        {
            "setting": setting,
            "materi": materi_list,
            "materi_list": materi_list,
        },
    )


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
        .order_by("kelompok__nama", "jabatan", "nama")
    )

    rows = []

    for peserta in peserta_list:
        absensi_list = list(peserta.absensi.all())
        total_acara = len(absensi_list)

        total_nilai = sum(
            item.nilai_persentase for item in absensi_list
        )

        persentase = (
            round(total_nilai / total_acara, 2)
            if total_acara
            else 0
        )

        rows.append({
            "peserta": peserta,
            "total_acara": total_acara,
            "total_nilai": total_nilai,
            "persentase": persentase,
        })

    kelompok_list = Kelompok.objects.filter(
        aktif=True
    ).order_by("nama")

    return render(
        request,
        "praktikum/absensi.html",
        {
            "setting": setting,
            "rows": rows,
            "peserta": peserta_list,
            "peserta_list": peserta_list,
            "kelompok": kelompok_list,
            "kelompok_list": kelompok_list,
        },
    )


# ============================================================
# PENGUMUMAN
# ============================================================

def pengumuman(request):
    setting = get_setting()

    pengumuman_list = Pengumuman.objects.filter(aktif=True).order_by(
        "-dibuat", "-id"
    )

    return render(
        request,
        "praktikum/pengumuman.html",
        {
            "setting": setting,
            "pengumuman": pengumuman_list,
            "pengumuman_list": pengumuman_list,
            "items": pengumuman_list,
        },
    )


# ============================================================
# TATA TERTIB
# ============================================================

def tata_tertib(request):
    setting = get_setting()

    tata_tertib_list = TataTertib.objects.filter(aktif=True).order_by(
        "urutan", "id"
    )

    return render(
        request,
        "praktikum/tata_tertib.html",
        {
            "setting": setting,
            "tata_tertib": tata_tertib_list,
            "tata_tertib_list": tata_tertib_list,
            "items": tata_tertib_list,
        },
    )


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

    return render(
        request,
        "praktikum/tugas_pendahuluan.html",
        {
            "setting": setting,
            "tugas": tugas_list,
            "tugas_list": tugas_list,
        },
    )


# ============================================================
# INFORMASI PESERTA
# ============================================================

def informasi_peserta(request):
    setting = get_setting()

    peserta_list = (
        Peserta.objects
        .filter(aktif=True)
        .select_related("kelompok")
        .order_by("kelompok__nama", "jabatan", "nama")
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

    return render(
        request,
        "praktikum/informasi_peserta.html",
        {
            "setting": setting,
            "peserta": peserta_list,
            "peserta_list": peserta_list,
            "total_peserta": total_peserta,
            "total_aktif": total_aktif,
            "total_gugur": total_gugur,
            "total_kelompok": total_kelompok,
        },
    )


# ============================================================
# FORMAT DOKUMEN
# ============================================================

def format_dokumen(request):
    setting = get_setting()

    format_list = FormatDokumen.objects.filter(aktif=True).order_by(
        "-uploaded_at", "-id"
    )

    return render(
        request,
        "praktikum/format_dokumen.html",
        {
            "setting": setting,
            "format_dokumen": format_list,
            "format_dokumen_list": format_list,
            "items": format_list,
        },
    )


# ============================================================
# LOGIN KELOMPOK
# ============================================================

def login_kelompok(request):
    kelompok_saat_ini = get_kelompok_login(request)

    if kelompok_saat_ini:
        return redirect("praktikum:dashboard_kelompok")

    # Bersihkan sesi jika kelompok sebelumnya sudah tidak aktif
    # atau tidak lagi ditemukan.
    request.session.pop("kelompok_id", None)

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:
            kelompok_obj = (
                Kelompok.objects
                .filter(
                    akun_login=user,
                    aktif=True,
                )
                .first()
            )

            if kelompok_obj:
                login(request, user)
                request.session["kelompok_id"] = kelompok_obj.id
                request.session.set_expiry(60 * 60 * 12)

                messages.success(
                    request,
                    f"Selamat datang, {kelompok_obj.nama}.",
                )

                return redirect("praktikum:dashboard_kelompok")

        messages.error(
            request,
            "Username atau password tidak valid, atau akun "
            "belum terhubung dengan kelompok aktif.",
        )

    return render(
        request,
        "praktikum/login_kelompok.html",
    )


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
    kelompok_obj = get_kelompok_login(request)

    if not kelompok_obj:
        request.session.pop("kelompok_id", None)
        messages.warning(request, "Silakan login terlebih dahulu.")
        return redirect("praktikum:login_kelompok")

    setting = get_setting()

    anggota = Peserta.objects.filter(
        kelompok=kelompok_obj,
        aktif=True,
        status_kemajuan=ACTIVE_STATUS,
    ).order_by("jabatan", "nama")

    laporan = (
        LaporanMingguan.objects
        .filter(kelompok=kelompok_obj)
        .select_related("peserta", "acara")
        .order_by("-uploaded_at", "-id")
    )

    daily_mom = (
        DailyMOM.objects
        .filter(kelompok=kelompok_obj)
        .select_related("acara", "dibuat_oleh")
        .order_by("-tanggal", "-id")
    )

    file_kelompok = (
        FileKelompok.objects
        .filter(kelompok=kelompok_obj)
        .select_related("acara", "uploaded_by")
        .order_by("-uploaded_at", "-id")
    )

    laporan_lengkap = (
        LaporanLengkap.objects
        .filter(kelompok=kelompok_obj)
        .order_by("-uploaded_at", "-id")
    )

    konsultasi = (
        Konsultasi.objects
        .filter(kelompok=kelompok_obj)
        .select_related("tujuan", "acara")
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

    mentor_list = kelompok_obj.mentor.filter(
        aktif=True
    ).order_by("jabatan", "urutan", "nama")

    context = {
        "setting": setting,
        "kelompok": kelompok_obj,
        "anggota": anggota,
        "peserta": anggota,
        "laporan": laporan,
        "laporan_mingguan": laporan,
        "daily_mom": daily_mom,
        "file_kelompok": file_kelompok,
        "file_kelompok_list": file_kelompok,
        "laporan_lengkap": laporan_lengkap,
        "laporan_lengkap_list": laporan_lengkap,
        "konsultasi": konsultasi,
        "konsultasi_list": konsultasi,
        "acara": acara_list,
        "acara_list": acara_list,
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

    kelompok_obj = peserta.kelompok

    if not kelompok_obj or not kelompok_obj.aktif:
        messages.warning(request, "Kelompok peserta tidak aktif.")
        return redirect("praktikum:login_kelompok")

    setting = get_setting()

    laporan = (
        LaporanMingguan.objects
        .filter(kelompok=kelompok_obj, peserta=peserta)
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
        .filter(kelompok=kelompok_obj)
        .select_related("acara", "uploaded_by")
        .order_by("-uploaded_at", "-id")
    )

    konsultasi_list = (
        Konsultasi.objects
        .filter(kelompok=kelompok_obj)
        .select_related("tujuan", "acara")
        .order_by("-dibuat", "-id")
    )

    context = {
        "setting": setting,
        "peserta": peserta,
        "kelompok": kelompok_obj,
        "laporan": laporan,
        "laporan_mingguan": laporan,
        "absensi": absensi_list,
        "absensi_list": absensi_list,
        "file_kelompok": file_list,
        "file_kelompok_list": file_list,
        "konsultasi": konsultasi_list,
        "konsultasi_list": konsultasi_list,
    }

    return render(
        request,
        "praktikum/dashboard_peserta.html",
        context,
    )


# ============================================================
# UPLOAD LAPORAN MINGGUAN
# ============================================================

@require_POST
def upload_laporan(request):
    kelompok_obj = get_kelompok_login(request)

    if not kelompok_obj:
        messages.warning(request, "Silakan login terlebih dahulu.")
        return redirect("praktikum:login_kelompok")

    file_laporan = request.FILES.get("file_laporan")
    judul = request.POST.get("judul", "").strip()
    acara_id = request.POST.get("acara", "").strip()
    peserta_id = request.POST.get("peserta", "").strip()

    if not file_laporan:
        messages.error(request, "File laporan belum dipilih.")
        return redirect("praktikum:dashboard_kelompok")

    if not acara_id or not peserta_id:
        messages.error(
            request,
            "Acara dan peserta pengunggah wajib dipilih.",
        )
        return redirect("praktikum:dashboard_kelompok")

    peserta = get_object_or_404(
        Peserta,
        id=peserta_id,
        kelompok=kelompok_obj,
        aktif=True,
        status_kemajuan=ACTIVE_STATUS,
    )

    acara = get_object_or_404(Acara, id=acara_id)

    LaporanMingguan.objects.create(
        peserta=peserta,
        kelompok=kelompok_obj,
        acara=acara,
        judul=judul or "Laporan Mingguan",
        file=file_laporan,
    )

    messages.success(request, "Laporan mingguan berhasil diunggah.")
    return redirect("praktikum:dashboard_kelompok")


# ============================================================
# UPLOAD LAPORAN LENGKAP
# ============================================================

@require_POST
def upload_laporan_lengkap(request):
    kelompok_obj = get_kelompok_login(request)

    if not kelompok_obj:
        messages.warning(request, "Silakan login terlebih dahulu.")
        return redirect("praktikum:login_kelompok")

    file_laporan = (
        request.FILES.get("file_laporan")
        or request.FILES.get("file")
    )

    judul = request.POST.get("judul", "").strip() or "Laporan Lengkap"

    if not file_laporan:
        messages.error(
            request,
            "File belum diterima server. Pastikan formulir menggunakan "
            'enctype="multipart/form-data" dan input bernama file_laporan.',
        )
        return redirect("praktikum:dashboard_kelompok")

    batas_ukuran = 25 * 1024 * 1024

    if file_laporan.size > batas_ukuran:
        messages.error(request, "Ukuran file maksimal 25 MB.")
        return redirect("praktikum:dashboard_kelompok")

    ekstensi_diizinkan = {
        ".pdf", ".doc", ".docx", ".xls", ".xlsx",
        ".ppt", ".pptx", ".zip",
    }

    ekstensi = Path(file_laporan.name).suffix.lower()

    if ekstensi not in ekstensi_diizinkan:
        messages.error(
            request,
            "Format file tidak didukung. Gunakan PDF, Word, Excel, "
            "PowerPoint, atau ZIP.",
        )
        return redirect("praktikum:dashboard_kelompok")

    try:
        laporan = LaporanLengkap(
            kelompok=kelompok_obj,
            judul=judul,
            file=file_laporan,
        )
        laporan.save()
    except Exception:
        messages.error(
            request,
            "Laporan gagal disimpan. Periksa konfigurasi media storage "
            "dan log server.",
        )
        return redirect("praktikum:dashboard_kelompok")

    messages.success(
        request,
        "Laporan lengkap berhasil diunggah dan menunggu pemeriksaan admin.",
    )
    return redirect("praktikum:dashboard_kelompok")


# ============================================================
# UNDUHAN MATERI DAN FORMAT DOKUMEN
# ============================================================

def download_materi(request, materi_id):
    materi_obj = get_object_or_404(Materi, pk=materi_id)
    return _kirim_file(materi_obj.file)


def download_format_dokumen(request, dokumen_id):
    dokumen = get_object_or_404(
        FormatDokumen,
        pk=dokumen_id,
        aktif=True,
    )
    return _kirim_file(dokumen.file)


# ============================================================
# UNDUHAN LAPORAN MINGGUAN OLEH KELOMPOK
# ============================================================

def download_laporan_mingguan(request, laporan_id):
    kelompok_obj = get_kelompok_login(request)

    if not kelompok_obj:
        messages.warning(request, "Silakan login terlebih dahulu.")
        return redirect("praktikum:login_kelompok")

    laporan_obj = get_object_or_404(
        LaporanMingguan,
        pk=laporan_id,
        kelompok=kelompok_obj,
    )

    return _kirim_file(laporan_obj.file)


def download_file_revisi(request, laporan_id):
    kelompok_obj = get_kelompok_login(request)

    if not kelompok_obj:
        messages.warning(request, "Silakan login terlebih dahulu.")
        return redirect("praktikum:login_kelompok")

    laporan_obj = get_object_or_404(
        LaporanMingguan,
        pk=laporan_id,
        kelompok=kelompok_obj,
    )

    return _kirim_file(
        getattr(laporan_obj, "file_revisi", None)
    )


# ============================================================
# UNDUHAN LAPORAN LENGKAP OLEH KELOMPOK
# ============================================================

def download_laporan_lengkap(request, laporan_id):
    kelompok_obj = get_kelompok_login(request)

    if not kelompok_obj:
        messages.warning(request, "Silakan login terlebih dahulu.")
        return redirect("praktikum:login_kelompok")

    laporan_obj = get_object_or_404(
        LaporanLengkap,
        pk=laporan_id,
        kelompok=kelompok_obj,
    )

    return _kirim_file(laporan_obj.file)


def download_laporan_lengkap_revisi(request, laporan_id):
    kelompok_obj = get_kelompok_login(request)

    if not kelompok_obj:
        messages.warning(request, "Silakan login terlebih dahulu.")
        return redirect("praktikum:login_kelompok")

    laporan_obj = get_object_or_404(
        LaporanLengkap,
        pk=laporan_id,
        kelompok=kelompok_obj,
    )

    return _kirim_file(
        getattr(laporan_obj, "file_revisi", None)
    )


# ============================================================
# UNDUHAN ADMIN
# ============================================================

def download_laporan_mingguan_admin(
    request,
    laporan_id,
    jenis="asli",
):
    if not _pastikan_admin(request):
        return HttpResponseForbidden(
            "Hanya admin yang dapat mengunduh file ini."
        )

    laporan_obj = get_object_or_404(
        LaporanMingguan,
        pk=laporan_id,
    )

    if jenis in ("revisi", "file_revisi"):
        field_file = getattr(laporan_obj, "file_revisi", None)
    else:
        field_file = laporan_obj.file

    return _kirim_file(field_file)


def download_laporan_lengkap_admin(
    request,
    laporan_id,
    jenis="asli",
):
    if not _pastikan_admin(request):
        return HttpResponseForbidden(
            "Hanya admin yang dapat mengunduh file ini."
        )

    laporan_obj = get_object_or_404(
        LaporanLengkap,
        pk=laporan_id,
    )

    if jenis in ("revisi", "file_revisi"):
        field_file = getattr(laporan_obj, "file_revisi", None)
    else:
        field_file = laporan_obj.file

    return _kirim_file(field_file)


# ============================================================
# UNDUHAN FILE KELOMPOK
# ============================================================

def download_file_kelompok(request, file_id):
    kelompok_obj = get_kelompok_login(request)

    if not kelompok_obj:
        messages.warning(request, "Silakan login terlebih dahulu.")
        return redirect("praktikum:login_kelompok")

    file_obj = get_object_or_404(
        FileKelompok,
        pk=file_id,
        kelompok=kelompok_obj,
    )

    return _kirim_file(file_obj.file)


# ============================================================
# DAILY MOM
# ============================================================

# Fungsi tambah/edit/hapus Daily MOM tetap menggunakan
# praktikum/daily_mom_views.py dan URL yang sudah ada.


# ============================================================
# KONSULTASI - JADWAL KELOMPOK DAN PENDAMPING
# ============================================================

@require_POST
def ajukan_konsultasi(request):
    kelompok_obj = get_kelompok_login(request)

    if not kelompok_obj:
        messages.warning(request, "Silakan login terlebih dahulu.")
        return redirect("praktikum:login_kelompok")

    tujuan_id = request.POST.get("tujuan", "").strip()
    acara_id = request.POST.get("acara", "").strip()
    tanggal_input = request.POST.get("tanggal_konsultasi", "").strip()
    mulai_input = request.POST.get("waktu_mulai", "").strip()
    selesai_input = request.POST.get("waktu_selesai", "").strip()
    lokasi = request.POST.get("lokasi", "").strip()

    tanggal = parse_date(tanggal_input) if tanggal_input else None
    waktu_mulai = parse_time(mulai_input) if mulai_input else None
    waktu_selesai = parse_time(selesai_input) if selesai_input else None

    if not all([
        tujuan_id,
        acara_id,
        tanggal,
        waktu_mulai,
        waktu_selesai,
        lokasi,
    ]):
        messages.error(
            request,
            "Pendamping, acara, tanggal, waktu mulai, waktu selesai, "
            "dan lokasi wajib diisi.",
        )
        return redirect("praktikum:dashboard_kelompok")

    tujuan_obj = get_object_or_404(
        Staff,
        pk=tujuan_id,
        aktif=True,
    )

    acara_obj = get_object_or_404(Acara, pk=acara_id)

    if waktu_selesai <= waktu_mulai:
        messages.error(
            request,
            "Waktu selesai harus lebih akhir daripada waktu mulai.",
        )
        return redirect("praktikum:dashboard_kelompok")

    Konsultasi.objects.create(
        topik=f"Konsultasi {kelompok_obj.nama}",
        kelompok=kelompok_obj,
        tujuan=tujuan_obj,
        acara=acara_obj,
        tanggal_konsultasi=tanggal,
        waktu_mulai=waktu_mulai,
        waktu_selesai=waktu_selesai,
        lokasi=lokasi,
    )

    messages.success(request, "Jadwal konsultasi berhasil disimpan.")
    return redirect("praktikum:dashboard_kelompok")
