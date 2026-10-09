from pathlib import Path

from PIL import Image, UnidentifiedImageError

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Case, IntegerField, Prefetch, Q, Value, When
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


# ============================================================
# KONFIGURASI
# ============================================================

ACTIVE_STATUS = "aktif"
GUGUR_STATUS = "gugur"

MAX_FILE_SIZE = 25 * 1024 * 1024
MAX_LOGO_SIZE = 5 * 1024 * 1024


# ============================================================
# HELPER
# ============================================================

def peserta_jabatan_order():
    return Case(
        When(jabatan="ketua", then=Value(0)),
        When(jabatan="anggota", then=Value(1)),
        default=Value(99),
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
        .prefetch_related(
            Prefetch(
                "mentor",
                queryset=Staff.objects.filter(
                    aktif=True
                ).order_by("urutan", "id"),
            ),
            Prefetch(
                "peserta",
                queryset=Peserta.objects
                .filter(aktif=True)
                .annotate(jabatan_order=peserta_jabatan_order())
                .order_by("jabatan_order", "id"),
            ),
        )
        .filter(id=kelompok_id, aktif=True)
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
                "mentor",
                queryset=Staff.objects.filter(
                    aktif=True
                ).order_by("urutan", "id"),
            ),
            Prefetch(
                "peserta",
                queryset=Peserta.objects
                .filter(aktif=True)
                .annotate(jabatan_order=peserta_jabatan_order())
                .order_by("jabatan_order", "id"),
            ),
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


def _admin_boleh_mengunduh(request, model_name, obj):
    user = request.user

    if not user.is_authenticated or not user.is_staff:
        return False

    if user.is_superuser:
        return True

    app_label = obj._meta.app_label

    return (
        user.has_perm(f"{app_label}.view_{model_name}")
        or user.has_perm(f"{app_label}.change_{model_name}")
    )


def _kirim_file(field_file, filename=None, as_attachment=True):
    if not field_file or not getattr(field_file, "name", ""):
        raise Http404("File tidak ditemukan.")

    try:
        field_file.open("rb")
    except (OSError, ValueError, FileNotFoundError):
        raise Http404(
            "File tidak tersedia pada penyimpanan server."
        )

    return FileResponse(
        field_file,
        as_attachment=as_attachment,
        filename=filename or Path(field_file.name).name,
    )


def _validasi_file_umum(file_obj):
    if not file_obj:
        return "File belum dipilih."

    if file_obj.size <= 0:
        return "File yang dipilih kosong."

    if file_obj.size > MAX_FILE_SIZE:
        return "Ukuran file maksimal 25 MB."

    return None


def _validasi_logo(file_obj):
    if not file_obj:
        return "Logo belum dipilih."

    if file_obj.size <= 0:
        return "File logo kosong."

    if file_obj.size > MAX_LOGO_SIZE:
        return "Ukuran logo maksimal 5 MB."

    ekstensi = Path(file_obj.name).suffix.lower()

    if ekstensi not in {".jpg", ".jpeg", ".png", ".webp"}:
        return "Logo harus berupa JPG, JPEG, PNG, atau WEBP."

    try:
        file_obj.seek(0)

        with Image.open(file_obj) as gambar:
            if gambar.format not in {"JPEG", "PNG", "WEBP"}:
                return "Format gambar tidak didukung."

            gambar.verify()

        file_obj.seek(0)

    except (UnidentifiedImageError, OSError, ValueError):
        return "File bukan gambar yang valid atau gambar rusak."

    finally:
        file_obj.seek(0)

    return None


# ============================================================
# HOME / BERANDA PUBLIK
# ============================================================

def home(request):
    setting = get_setting()

    staff_list = (
        Staff.objects
        .filter(aktif=True)
        .order_by("jabatan", "urutan", "id")
    )

    kelompok_list = (
        Kelompok.objects
        .filter(aktif=True)
        .prefetch_related(
            Prefetch(
                "mentor",
                queryset=Staff.objects.filter(
                    aktif=True
                ).order_by("urutan", "id"),
            ),
            Prefetch(
                "peserta",
                queryset=Peserta.objects
                .filter(
                    aktif=True,
                    status_kemajuan=ACTIVE_STATUS,
                )
                .annotate(jabatan_order=peserta_jabatan_order())
                .order_by("jabatan_order", "id"),
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
        .order_by("urutan", "tanggal_mulai", "id")
    )

    materi_list = (
        Materi.objects
        .select_related("acara")
        .order_by("-uploaded_at", "-id")
    )

    pengumuman_list = (
        Pengumuman.objects
        .filter(aktif=True)
        .order_by("-dibuat", "-id")
    )

    peserta_list = (
        Peserta.objects
        .filter(
            aktif=True,
            status_kemajuan=ACTIVE_STATUS,
        )
        .select_related("kelompok")
        .annotate(jabatan_order=peserta_jabatan_order())
        .order_by("kelompok_id", "jabatan_order", "id")
    )

    koordinator = staff_list.filter(
        jabatan="koordinator"
    ).first()

    penanggung_jawab = staff_list.filter(
        jabatan="penanggung_jawab"
    ).order_by("urutan", "id")

    asisten_list = staff_list.filter(
        jabatan="asisten"
    ).order_by("urutan", "id")

    format_list = (
        FormatDokumen.objects
        .filter(aktif=True)
        .order_by("-uploaded_at", "-id")
    )

    laporan_lengkap_publik = (
        LaporanLengkap.objects
        .filter(kelompok__aktif=True, status="acc")
        .select_related("kelompok")
        .order_by("kelompok_id", "-uploaded_at", "-id")
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
        "laporan_lengkap_publik": laporan_lengkap_publik,
    }

    return render(request, "praktikum/home.html", context)


# ============================================================
# PERSONEL
# ============================================================

def personel(request):
    setting = get_setting()

    staff_list = (
        Staff.objects
        .filter(aktif=True)
        .order_by("jabatan", "urutan", "id")
    )

    context = {
        "setting": setting,
        "staff": staff_list,
        "staff_list": staff_list,
        "personel": staff_list,
        "personel_list": staff_list,
        "penanggung_jawab": staff_list.filter(
            jabatan="penanggung_jawab"
        ).order_by("urutan", "id"),
        "koordinator": staff_list.filter(
            jabatan="koordinator"
        ).order_by("urutan", "id"),
        "asisten": staff_list.filter(
            jabatan="asisten"
        ).order_by("urutan", "id"),
        "asisten_list": staff_list.filter(
            jabatan="asisten"
        ).order_by("urutan", "id"),
    }

    return render(request, "praktikum/personel.html", context)


# ============================================================
# KELOMPOK PUBLIK
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
                ).order_by("urutan", "id"),
            ),
            Prefetch(
                "peserta",
                queryset=Peserta.objects
                .filter(
                    aktif=True,
                    status_kemajuan=ACTIVE_STATUS,
                )
                .annotate(jabatan_order=peserta_jabatan_order())
                .order_by("jabatan_order", "id"),
            ),
            Prefetch(
                "daily_mom",
                queryset=DailyMOM.objects
                .select_related("acara", "dibuat_oleh")
                .order_by("-tanggal", "-id"),
                to_attr="public_daily_mom",
            ),
            Prefetch(
                "laporan_mingguan",
                queryset=LaporanMingguan.objects
                .filter(status="acc")
                .select_related("peserta", "acara")
                .order_by("-uploaded_at", "-id"),
                to_attr="public_laporan_mingguan",
            ),
        )
        .order_by("id")
    )

    laporan_lengkap_publik = (
        LaporanLengkap.objects
        .filter(kelompok__aktif=True, status="acc")
        .select_related("kelompok")
        .order_by("kelompok_id", "-uploaded_at", "-id")
    )

    return render(
        request,
        "praktikum/kelompok.html",
        {
            "setting": setting,
            "kelompok": kelompok_list,
            "kelompok_list": kelompok_list,
            "laporan_lengkap_publik": laporan_lengkap_publik,
        },
    )


# ============================================================
# JADWAL
# ============================================================

def jadwal(request):
    acara_list = (
        Acara.objects
        .select_related("penanggung_jawab")
        .prefetch_related(
            Prefetch(
                "pembawa_acara",
                queryset=Staff.objects.filter(aktif=True),
            )
        )
        .order_by("urutan", "tanggal_mulai", "id")
    )

    return render(
        request,
        "praktikum/jadwal.html",
        {
            "setting": get_setting(),
            "acara": acara_list,
            "acara_list": acara_list,
        },
    )


# ============================================================
# MATERI
# ============================================================

def materi(request):
    materi_list = (
        Materi.objects
        .select_related("acara")
        .order_by("-uploaded_at", "-id")
    )

    return render(
        request,
        "praktikum/materi.html",
        {
            "setting": get_setting(),
            "materi": materi_list,
            "materi_list": materi_list,
        },
    )


# ============================================================
# ABSENSI
# ============================================================

def absensi(request):
    peserta_list = (
        Peserta.objects
        .filter(aktif=True)
        .select_related("kelompok")
        .prefetch_related("absensi")
        .annotate(jabatan_order=peserta_jabatan_order())
        .order_by("kelompok_id", "jabatan_order", "id")
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
    ).order_by("id")

    return render(
        request,
        "praktikum/absensi.html",
        {
            "setting": get_setting(),
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
    pengumuman_list = (
        Pengumuman.objects
        .filter(aktif=True)
        .order_by("-dibuat", "-id")
    )

    return render(
        request,
        "praktikum/pengumuman.html",
        {
            "setting": get_setting(),
            "pengumuman": pengumuman_list,
            "pengumuman_list": pengumuman_list,
            "items": pengumuman_list,
        },
    )


# ============================================================
# TATA TERTIB
# ============================================================

def tata_tertib(request):
    tata_tertib_list = (
        TataTertib.objects
        .filter(aktif=True)
        .order_by("urutan", "id")
    )

    return render(
        request,
        "praktikum/tata_tertib.html",
        {
            "setting": get_setting(),
            "tata_tertib": tata_tertib_list,
            "tata_tertib_list": tata_tertib_list,
            "items": tata_tertib_list,
        },
    )


# ============================================================
# TUGAS PENDAHULUAN
# ============================================================

def tugas_pendahuluan(request):
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
            "setting": get_setting(),
            "tugas": tugas_list,
            "tugas_list": tugas_list,
        },
    )


# ============================================================
# INFORMASI PESERTA
# ============================================================

def informasi_peserta(request):
    query = request.GET.get("q", "").strip()
    status_filter = request.GET.get("status", "semua").strip().lower()

    if status_filter not in {"semua", ACTIVE_STATUS, GUGUR_STATUS}:
        status_filter = "semua"

    peserta_queryset = (
        Peserta.objects
        .filter(aktif=True)
        .select_related("kelompok")
    )

    if status_filter == ACTIVE_STATUS:
        peserta_queryset = peserta_queryset.filter(
            status_kemajuan=ACTIVE_STATUS
        )
    elif status_filter == GUGUR_STATUS:
        peserta_queryset = peserta_queryset.filter(
            status_kemajuan=GUGUR_STATUS
        )

    if query:
        peserta_queryset = peserta_queryset.filter(
            Q(nama__icontains=query)
            | Q(kelompok__nama__icontains=query)
        )

    peserta_list = (
        peserta_queryset
        .annotate(jabatan_order=peserta_jabatan_order())
        .order_by("kelompok_id", "jabatan_order", "id")
    )

    semua_peserta = Peserta.objects.filter(aktif=True)

    total_peserta = semua_peserta.count()
    total_aktif = semua_peserta.filter(
        status_kemajuan=ACTIVE_STATUS
    ).count()
    total_gugur = semua_peserta.filter(
        status_kemajuan=GUGUR_STATUS
    ).count()
    total_kelompok = (
        semua_peserta
        .filter(kelompok__isnull=False)
        .values("kelompok_id")
        .distinct()
        .count()
    )

    return render(
        request,
        "praktikum/informasi_peserta.html",
        {
            "setting": get_setting(),
            "peserta": peserta_list,
            "peserta_list": peserta_list,
            "query": query,
            "status_filter": status_filter,
            "jumlah_hasil": peserta_list.count(),
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
    format_list = (
        FormatDokumen.objects
        .filter(aktif=True)
        .order_by("-uploaded_at", "-id")
    )

    return render(
        request,
        "praktikum/format_dokumen.html",
        {
            "setting": get_setting(),
            "format_dokumen": format_list,
            "format_dokumen_list": format_list,
            "items": format_list,
        },
    )


# ============================================================
# LOGIN KELOMPOK
# ============================================================

def login_kelompok(request):
    if request.session.get("kelompok_id"):
        kelompok_obj = get_kelompok_login(request)

        if kelompok_obj:
            return redirect("praktikum:dashboard_kelompok")

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
                .filter(akun_login=user, aktif=True)
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
    kelompok_obj = get_kelompok_login(request)

    if not kelompok_obj:
        messages.warning(request, "Silakan login terlebih dahulu.")
        return redirect("praktikum:login_kelompok")

    anggota = (
        Peserta.objects
        .filter(
            kelompok=kelompok_obj,
            aktif=True,
            status_kemajuan=ACTIVE_STATUS,
        )
        .annotate(jabatan_order=peserta_jabatan_order())
        .order_by("jabatan_order", "id")
    )

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

    progress_acara = (
        ProgressAcara.objects
        .filter(kelompok=kelompok_obj)
        .select_related("acara")
        .order_by(
            "acara__urutan",
            "acara__tanggal_mulai",
            "acara__id",
        )
    )

    file_kelompok_list = (
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

    konsultasi_list = (
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
        .order_by("urutan", "tanggal_mulai", "id")
    )

    mentor_list = kelompok_obj.mentor.filter(
        aktif=True
    ).order_by("urutan", "id")

    return render(
        request,
        "praktikum/dashboard_kelompok.html",
        {
            "setting": get_setting(),
            "kelompok": kelompok_obj,
            "anggota": anggota,
            "peserta": anggota,
            "laporan": laporan,
            "laporan_mingguan": laporan,
            "daily_mom": daily_mom,
            "progress_acara": progress_acara,
            "progress_list": progress_acara,
            "file_kelompok": file_kelompok_list,
            "file_kelompok_list": file_kelompok_list,
            "laporan_lengkap": laporan_lengkap,
            "laporan_lengkap_list": laporan_lengkap,
            "konsultasi": konsultasi_list,
            "konsultasi_list": konsultasi_list,
            "acara": acara_list,
            "acara_list": acara_list,
            "progress": kelompok_obj.progress_persen,
            "mentor": mentor_list,
        },
    )


# ============================================================
# DASHBOARD PESERTA
# ============================================================

def dashboard_peserta(request):
    peserta_obj = get_peserta_login(request)

    if not peserta_obj:
        messages.warning(
            request,
            "Akun peserta belum terhubung atau sudah tidak aktif.",
        )
        return redirect("praktikum:login_kelompok")

    kelompok_obj = peserta_obj.kelompok

    if not kelompok_obj or not kelompok_obj.aktif:
        messages.warning(request, "Kelompok peserta tidak aktif.")
        return redirect("praktikum:login_kelompok")

    laporan = (
        LaporanMingguan.objects
        .filter(kelompok=kelompok_obj, peserta=peserta_obj)
        .select_related("acara")
        .order_by("-uploaded_at", "-id")
    )

    absensi_list = (
        Absensi.objects
        .filter(peserta=peserta_obj)
        .select_related("acara")
        .order_by("-acara__tanggal_mulai", "-id")
    )

    file_list = (
        FileKelompok.objects
        .filter(kelompok=kelompok_obj)
        .select_related("acara", "uploaded_by")
        .order_by("-uploaded_at", "-id")
    )

    progress_list = (
        ProgressAcara.objects
        .filter(kelompok=kelompok_obj)
        .select_related("acara")
        .order_by(
            "acara__urutan",
            "acara__tanggal_mulai",
            "acara__id",
        )
    )

    konsultasi_list = (
        Konsultasi.objects
        .filter(kelompok=kelompok_obj)
        .select_related("tujuan", "acara")
        .order_by("-dibuat", "-id")
    )

    return render(
        request,
        "praktikum/dashboard_peserta.html",
        {
            "setting": get_setting(),
            "peserta": peserta_obj,
            "kelompok": kelompok_obj,
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
        },
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

    error = _validasi_file_umum(file_laporan)

    if error:
        messages.error(request, error)
        return redirect("praktikum:dashboard_kelompok")

    if not acara_id:
        messages.error(request, "Acara laporan belum dipilih.")
        return redirect("praktikum:dashboard_kelompok")

    if not peserta_id:
        messages.error(request, "Peserta pengunggah belum dipilih.")
        return redirect("praktikum:dashboard_kelompok")

    peserta_obj = get_object_or_404(
        Peserta,
        id=peserta_id,
        kelompok=kelompok_obj,
        aktif=True,
        status_kemajuan=ACTIVE_STATUS,
    )

    acara_obj = get_object_or_404(Acara, id=acara_id)

    LaporanMingguan.objects.create(
        peserta=peserta_obj,
        kelompok=kelompok_obj,
        acara=acara_obj,
        judul=judul or "Laporan Mingguan",
        file=file_laporan,
    )

    messages.success(request, "Laporan berhasil diunggah.")
    return redirect("praktikum:dashboard_kelompok")


# ============================================================
# DOWNLOAD LAPORAN MINGGUAN ASLI
# ============================================================

def download_laporan_mingguan(request, laporan_id):
    kelompok_obj = get_kelompok_login(request)

    if not kelompok_obj:
        messages.warning(request, "Silakan login terlebih dahulu.")
        return redirect("praktikum:login_kelompok")

    laporan = get_object_or_404(
        LaporanMingguan,
        id=laporan_id,
        kelompok=kelompok_obj,
    )

    return _kirim_file(laporan.file)


# ============================================================
# DOWNLOAD REVISI LAPORAN MINGGUAN
# ============================================================

def download_file_revisi(request, laporan_id):
    kelompok_obj = get_kelompok_login(request)

    if not kelompok_obj:
        messages.warning(request, "Silakan login terlebih dahulu.")
        return redirect("praktikum:login_kelompok")

    laporan = get_object_or_404(
        LaporanMingguan,
        id=laporan_id,
        kelompok=kelompok_obj,
    )

    return _kirim_file(laporan.file_revisi)


# ============================================================
# UPLOAD LAPORAN LENGKAP
# ============================================================

@require_POST
def upload_laporan_lengkap(request):
    kelompok_obj = get_kelompok_login(request)

    if not kelompok_obj:
        messages.warning(request, "Silakan login terlebih dahulu.")
        return redirect("praktikum:login_kelompok")

    file_obj = request.FILES.get("file_laporan_lengkap")
    judul = request.POST.get(
        "judul_laporan_lengkap", ""
    ).strip()

    error = _validasi_file_umum(file_obj)

    if error:
        messages.error(request, error)
        return redirect("praktikum:dashboard_kelompok")

    if not judul:
        judul = "Laporan Lengkap"

    if len(judul) > 200:
        messages.error(
            request,
            "Judul laporan maksimal 200 karakter.",
        )
        return redirect("praktikum:dashboard_kelompok")

    LaporanLengkap.objects.create(
        kelompok=kelompok_obj,
        judul=judul,
        file=file_obj,
    )

    messages.success(
        request,
        "Laporan lengkap berhasil diunggah dan menunggu pemeriksaan admin.",
    )

    return redirect("praktikum:dashboard_kelompok")


# ============================================================
# DOWNLOAD LAPORAN LENGKAP ASLI
# ============================================================

def download_laporan_lengkap(request, laporan_id):
    kelompok_obj = get_kelompok_login(request)

    if not kelompok_obj:
        messages.warning(request, "Silakan login terlebih dahulu.")
        return redirect("praktikum:login_kelompok")

    laporan = get_object_or_404(
        LaporanLengkap,
        id=laporan_id,
        kelompok=kelompok_obj,
    )

    return _kirim_file(laporan.file)


# ============================================================
# DOWNLOAD REVISI LAPORAN LENGKAP
# ============================================================

def download_laporan_lengkap_revisi(request, laporan_id):
    kelompok_obj = get_kelompok_login(request)

    if not kelompok_obj:
        messages.warning(request, "Silakan login terlebih dahulu.")
        return redirect("praktikum:login_kelompok")

    laporan = get_object_or_404(
        LaporanLengkap,
        id=laporan_id,
        kelompok=kelompok_obj,
    )

    return _kirim_file(laporan.file_revisi)


# ============================================================
# DOWNLOAD LAPORAN LENGKAP PUBLIK
# HANYA LAPORAN ACC DARI KELOMPOK AKTIF
# ============================================================

def download_laporan_lengkap_publik(request, laporan_id):
    laporan = get_object_or_404(
        LaporanLengkap,
        id=laporan_id,
        status="acc",
        kelompok__aktif=True,
    )

    return _kirim_file(laporan.file)


# ============================================================
# DOWNLOAD LAPORAN MINGGUAN ADMIN
# ============================================================

@login_required
def download_laporan_mingguan_admin(
    request,
    laporan_id,
    jenis="asli",
):
    laporan = get_object_or_404(
        LaporanMingguan,
        id=laporan_id,
    )

    if not _admin_boleh_mengunduh(
        request,
        "laporanmingguan",
        laporan,
    ):
        return HttpResponseForbidden(
            "Anda tidak memiliki izin mengunduh laporan ini."
        )

    if jenis == "asli":
        field_file = laporan.file
    elif jenis == "revisi":
        field_file = laporan.file_revisi
    else:
        raise Http404("Jenis file tidak valid.")

    return _kirim_file(field_file)


# ============================================================
# DOWNLOAD LAPORAN LENGKAP ADMIN
# ============================================================

@login_required
def download_laporan_lengkap_admin(
    request,
    laporan_id,
    jenis="asli",
):
    laporan = get_object_or_404(
        LaporanLengkap,
        id=laporan_id,
    )

    if not _admin_boleh_mengunduh(
        request,
        "laporanlengkap",
        laporan,
    ):
        return HttpResponseForbidden(
            "Anda tidak memiliki izin mengunduh laporan ini."
        )

    if jenis == "asli":
        field_file = laporan.file
    elif jenis == "revisi":
        field_file = laporan.file_revisi
    else:
        raise Http404("Jenis file tidak valid.")

    return _kirim_file(field_file)


# ============================================================
# UPLOAD / GANTI LOGO KELOMPOK
# ============================================================

@require_POST
def upload_logo_kelompok(request):
    kelompok_obj = get_kelompok_login(request)

    if not kelompok_obj:
        messages.warning(request, "Silakan login terlebih dahulu.")
        return redirect("praktikum:login_kelompok")

    logo_baru = request.FILES.get("logo")
    error = _validasi_logo(logo_baru)

    if error:
        messages.error(request, error)
        return redirect("praktikum:dashboard_kelompok")

    kelompok_obj.logo = logo_baru
    kelompok_obj.save(update_fields=["logo"])

    messages.success(
        request,
        "Logo kelompok berhasil diperbarui.",
    )

    return redirect("praktikum:dashboard_kelompok")


# ============================================================
# DOWNLOAD FILE KELOMPOK
# ============================================================

def download_file_kelompok(request, file_id):
    kelompok_obj = get_kelompok_login(request)

    if not kelompok_obj:
        messages.warning(request, "Silakan login terlebih dahulu.")
        return redirect("praktikum:login_kelompok")

    item = get_object_or_404(
        FileKelompok,
        id=file_id,
        kelompok=kelompok_obj,
    )

    return _kirim_file(
        item.file,
        filename=item.nama_file or None,
        as_attachment=True,
    )


# ============================================================
# DOWNLOAD MATERI PUBLIK
# ============================================================

def download_materi(request, materi_id):
    materi_obj = get_object_or_404(Materi, id=materi_id)

    return _kirim_file(materi_obj.file)


# ============================================================
# DOWNLOAD FORMAT DOKUMEN AKTIF
# ============================================================

def download_format_dokumen(request, dokumen_id):
    dokumen = get_object_or_404(
        FormatDokumen,
        id=dokumen_id,
        aktif=True,
    )

    return _kirim_file(dokumen.file)
