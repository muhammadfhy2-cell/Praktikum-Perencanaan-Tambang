from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db.models import (
    Case,
    IntegerField,
    Prefetch,
    Q,
    Value,
    When,
)
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render

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


# ============================================================
# HELPER URUTAN PESERTA
# ============================================================

def peserta_jabatan_order():
    """
    Menentukan urutan peserta:
    1. Ketua
    2. Anggota

    Jika ada data jabatan lain, diletakkan setelahnya.
    """

    return Case(
        When(
            jabatan="ketua",
            then=Value(0),
        ),
        When(
            jabatan="anggota",
            then=Value(1),
        ),
        default=Value(99),
        output_field=IntegerField(),
    )


# ============================================================
# HELPER SETTING
# ============================================================

def get_setting():

    return Setting.objects.first()


# ============================================================
# HELPER KELOMPOK LOGIN
# ============================================================

def get_kelompok_login(request):

    kelompok_id = request.session.get(
        "kelompok_id"
    )

    if not kelompok_id:
        return None

    return (
        Kelompok.objects
        .prefetch_related(
            Prefetch(
                "mentor",
                queryset=Staff.objects.filter(
                    aktif=True
                ).order_by(
                    "urutan",
                    "id",
                ),
            ),
            Prefetch(
                "peserta",
                queryset=Peserta.objects
                .filter(
                    aktif=True,
                )
                .annotate(
                    jabatan_order=peserta_jabatan_order()
                )
                .order_by(
                    "jabatan_order",
                    "id",
                ),
            ),
        )
        .filter(
            id=kelompok_id,
            aktif=True,
        )
        .first()
    )


# ============================================================
# HELPER USER -> KELOMPOK
# ============================================================

def get_user_kelompok(request):

    if not request.user.is_authenticated:
        return None

    return (
        Kelompok.objects
        .filter(
            akun_login=request.user,
            aktif=True,
        )
        .prefetch_related(
            Prefetch(
                "mentor",
                queryset=Staff.objects.filter(
                    aktif=True
                ).order_by(
                    "urutan",
                    "id",
                ),
            ),
            Prefetch(
                "peserta",
                queryset=Peserta.objects
                .filter(
                    aktif=True,
                )
                .annotate(
                    jabatan_order=peserta_jabatan_order()
                )
                .order_by(
                    "jabatan_order",
                    "id",
                ),
            ),
        )
        .first()
    )


# ============================================================
# HELPER USER -> PESERTA
# ============================================================

def get_peserta_login(request):

    if not request.user.is_authenticated:
        return None

    return (
        Peserta.objects
        .select_related(
            "kelompok"
        )
        .filter(
            akun=request.user,
            aktif=True,
            status_kemajuan=ACTIVE_STATUS,
        )
        .first()
    )


# ============================================================
# HOME / BERANDA PUBLIK
# ============================================================

def home(request):

    setting = get_setting()

    staff_list = (
        Staff.objects
        .filter(
            aktif=True
        )
        .order_by(
            "jabatan",
            "urutan",
            "id",
        )
    )

    # --------------------------------------------------------
    # KELOMPOK
    # --------------------------------------------------------

    kelompok_list = (
        Kelompok.objects
        .filter(
            aktif=True
        )
        .prefetch_related(
            Prefetch(
                "mentor",
                queryset=Staff.objects.filter(
                    aktif=True
                ).order_by(
                    "urutan",
                    "id",
                ),
            ),
            Prefetch(
                "peserta",
                queryset=Peserta.objects
                .filter(
                    aktif=True,
                    status_kemajuan=ACTIVE_STATUS,
                )
                .annotate(
                    jabatan_order=peserta_jabatan_order()
                )
                .order_by(
                    "jabatan_order",
                    "id",
                ),
            ),
        )
        .order_by(
            "id"
        )
    )

    # --------------------------------------------------------
    # ACARA
    # --------------------------------------------------------

    acara_list = (
        Acara.objects
        .select_related(
            "penanggung_jawab",
        )
        .prefetch_related(
            Prefetch(
                "pembawa_acara",
                queryset=Staff.objects.filter(
                    aktif=True
                ),
            )
        )
        .order_by(
            "urutan",
            "tanggal_mulai",
            "id",
        )
    )

    # --------------------------------------------------------
    # MATERI
    # --------------------------------------------------------

    materi_list = (
        Materi.objects
        .select_related(
            "acara"
        )
        .order_by(
            "-uploaded_at",
            "-id",
        )
    )

    # --------------------------------------------------------
    # PENGUMUMAN
    # --------------------------------------------------------

    pengumuman_list = (
        Pengumuman.objects
        .filter(
            aktif=True
        )
        .order_by(
            "-dibuat",
            "-id",
        )
    )

    # --------------------------------------------------------
    # PESERTA PUBLIK
    # --------------------------------------------------------
    #
    # Urutan:
    # Kelompok berdasarkan ID
    # -> Ketua
    # -> Anggota
    # -> ID peserta
    #

    peserta_list = (
        Peserta.objects
        .filter(
            aktif=True,
            status_kemajuan=ACTIVE_STATUS,
        )
        .select_related(
            "kelompok"
        )
        .annotate(
            jabatan_order=peserta_jabatan_order()
        )
        .order_by(
            "kelompok_id",
            "jabatan_order",
            "id",
        )
    )

    # --------------------------------------------------------
    # STAFF KHUSUS
    # --------------------------------------------------------

    koordinator = (
        staff_list
        .filter(
            jabatan="koordinator"
        )
        .first()
    )

    penanggung_jawab = (
        staff_list
        .filter(
            jabatan="penanggung_jawab"
        )
        .first()
    )

    asisten_list = (
        staff_list
        .filter(
            jabatan="asisten"
        )
        .order_by(
            "urutan",
            "id",
        )
    )

    context = {

        "setting": setting,

        # STAFF
        "staff": staff_list,
        "staff_list": staff_list,

        "personel": staff_list,
        "personel_list": staff_list,

        "asisten": asisten_list,
        "asisten_list": asisten_list,

        "koordinator": koordinator,
        "penanggung_jawab": penanggung_jawab,

        # KELOMPOK
        "kelompok": kelompok_list,
        "kelompok_list": kelompok_list,

        # ACARA
        "acara": acara_list,
        "acara_list": acara_list,

        # MATERI
        "materi": materi_list,
        "materi_list": materi_list,

        # PENGUMUMAN
        "pengumuman": pengumuman_list,
        "pengumuman_list": pengumuman_list,
        "items": pengumuman_list,

        # PESERTA
        "peserta": peserta_list,
        "peserta_list": peserta_list,

        # FORMAT DOKUMEN
        "format_dokumen": (
            FormatDokumen.objects
            .filter(
                aktif=True
            )
            .order_by(
                "-uploaded_at",
                "-id",
            )
        ),
    }

    return render(
        request,
        "praktikum/home.html",
        context,
    )


# ============================================================
# PERSONEL
# ============================================================

def personel(request):

    setting = get_setting()

    staff_list = (
        Staff.objects
        .filter(
            aktif=True
        )
        .order_by(
            "jabatan",
            "urutan",
            "id",
        )
    )

    penanggung_jawab = (
        staff_list
        .filter(
            jabatan="penanggung_jawab"
        )
        .first()
    )

    koordinator = (
        staff_list
        .filter(
            jabatan="koordinator"
        )
        .order_by(
            "urutan",
            "id",
        )
    )

    asisten_list = (
        staff_list
        .filter(
            jabatan="asisten"
        )
        .order_by(
            "urutan",
            "id",
        )
    )

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
# KELOMPOK
# ============================================================

def kelompok(request):

    setting = get_setting()

    kelompok_list = (
        Kelompok.objects
        .filter(
            aktif=True
        )
        .prefetch_related(

            # ------------------------------------------------
            # MENTOR
            # ------------------------------------------------

            Prefetch(
                "mentor",
                queryset=Staff.objects.filter(
                    aktif=True
                ).order_by(
                    "urutan",
                    "id",
                ),
            ),

            # ------------------------------------------------
            # PESERTA
            # ------------------------------------------------
            #
            # Ketua -> Anggota -> ID
            #

            Prefetch(
                "peserta",
                queryset=Peserta.objects
                .filter(
                    aktif=True,
                    status_kemajuan=ACTIVE_STATUS,
                )
                .annotate(
                    jabatan_order=peserta_jabatan_order()
                )
                .order_by(
                    "jabatan_order",
                    "id",
                ),
            ),

            # ------------------------------------------------
            # DAILY MOM PUBLIK
            # ------------------------------------------------

            Prefetch(
                "daily_mom",
                queryset=DailyMOM.objects
                .select_related(
                    "acara",
                    "dibuat_oleh",
                )
                .order_by(
                    "-tanggal",
                    "-id",
                ),
                to_attr="public_daily_mom",
            ),

            # ------------------------------------------------
            # LAPORAN MINGGUAN PUBLIK
            # HANYA ACC
            # ------------------------------------------------

            Prefetch(
                "laporan_mingguan",
                queryset=LaporanMingguan.objects
                .filter(
                    status="acc"
                )
                .select_related(
                    "peserta",
                    "acara",
                )
                .order_by(
                    "-uploaded_at",
                    "-id",
                ),
                to_attr="public_laporan_mingguan",
            ),
        )
        .order_by(
            "id"
        )
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
# JADWAL
# ============================================================

def jadwal(request):

    setting = get_setting()

    acara_list = (
        Acara.objects
        .select_related(
            "penanggung_jawab",
        )
        .prefetch_related(
            Prefetch(
                "pembawa_acara",
                queryset=Staff.objects.filter(
                    aktif=True
                ),
            )
        )
        .order_by(
            "urutan",
            "tanggal_mulai",
            "id",
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
# MATERI
# ============================================================

def materi(request):

    setting = get_setting()

    materi_list = (
        Materi.objects
        .select_related(
            "acara"
        )
        .order_by(
            "-uploaded_at",
            "-id",
        )
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
# ABSENSI
# ============================================================

def absensi(request):

    setting = get_setting()

    peserta_list = (
        Peserta.objects
        .filter(
            aktif=True,
        )
        .select_related(
            "kelompok"
        )
        .prefetch_related(
            "absensi"
        )
        .annotate(
            jabatan_order=peserta_jabatan_order()
        )
        .order_by(
            "kelompok_id",
            "jabatan_order",
            "id",
        )
    )

    rows = []

    for peserta in peserta_list:

        absensi_list = list(
            peserta.absensi.all()
        )

        total_acara = len(
            absensi_list
        )

        total_nilai = sum(
            absensi.nilai_persentase
            for absensi in absensi_list
        )

        persentase = (
            round(
                total_nilai / total_acara,
                2,
            )
            if total_acara
            else 0
        )

        rows.append(
            {
                "peserta": peserta,
                "total_acara": total_acara,
                "total_nilai": total_nilai,
                "persentase": persentase,
            }
        )

    kelompok_list = (
        Kelompok.objects
        .filter(
            aktif=True
        )
        .order_by(
            "id"
        )
    )

    context = {

        "setting": setting,

        "rows": rows,

        "peserta": peserta_list,
        "peserta_list": peserta_list,

        "kelompok": kelompok_list,
        "kelompok_list": kelompok_list,

    }

    return render(
        request,
        "praktikum/absensi.html",
        context,
    )


# ============================================================
# PENGUMUMAN
# ============================================================

def pengumuman(request):

    setting = get_setting()

    pengumuman_list = (
        Pengumuman.objects
        .filter(
            aktif=True
        )
        .order_by(
            "-dibuat",
            "-id",
        )
    )

    context = {

        "setting": setting,

        "pengumuman": pengumuman_list,
        "pengumuman_list": pengumuman_list,

        "items": pengumuman_list,

    }

    return render(
        request,
        "praktikum/pengumuman.html",
        context,
    )


# ============================================================
# TATA TERTIB
# ============================================================

def tata_tertib(request):

    setting = get_setting()

    tata_tertib_list = (
        TataTertib.objects
        .filter(
            aktif=True,
        )
        .order_by(
            "urutan",
            "id",
        )
    )

    context = {

        "setting": setting,

        "tata_tertib": tata_tertib_list,
        "tata_tertib_list": tata_tertib_list,

        "items": tata_tertib_list,

    }

    return render(
        request,
        "praktikum/tata_tertib.html",
        context,
    )


# ============================================================
# TUGAS PENDAHULUAN
# ============================================================

def tugas_pendahuluan(request):

    setting = get_setting()

    tugas_list = (
        TugasPendahuluan.objects
        .filter(
            aktif=True,
        )
        .select_related(
            "acara"
        )
        .order_by(
            "-dibuat",
            "-id",
        )
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
# INFORMASI PESERTA
# ============================================================

def informasi_peserta(request):

    setting = get_setting()

    # --------------------------------------------------------
    # PARAMETER PENCARIAN
    # --------------------------------------------------------

    query = request.GET.get(
        "q",
        "",
    ).strip()

    status_filter = request.GET.get(
        "status",
        "semua",
    ).strip().lower()

    # Jika status tidak valid,
    # kembalikan ke semua.
    if status_filter not in {
        "semua",
        ACTIVE_STATUS,
        GUGUR_STATUS,
    }:
        status_filter = "semua"

    # --------------------------------------------------------
    # BASE QUERY
    # --------------------------------------------------------

    peserta_queryset = (
        Peserta.objects
        .filter(
            aktif=True,
        )
        .select_related(
            "kelompok"
        )
    )

    # --------------------------------------------------------
    # FILTER STATUS
    # --------------------------------------------------------

    if status_filter == ACTIVE_STATUS:

        peserta_queryset = peserta_queryset.filter(
            status_kemajuan=ACTIVE_STATUS
        )

    elif status_filter == GUGUR_STATUS:

        peserta_queryset = peserta_queryset.filter(
            status_kemajuan=GUGUR_STATUS
        )

    # --------------------------------------------------------
    # FILTER PENCARIAN
    # --------------------------------------------------------

    if query:

        peserta_queryset = peserta_queryset.filter(
            Q(nama__icontains=query)
            |
            Q(kelompok__nama__icontains=query)
        )

    # --------------------------------------------------------
    # URUTAN
    # --------------------------------------------------------
    #
    # 1. Kelompok berdasarkan ID
    # 2. Ketua
    # 3. Anggota
    # 4. ID peserta
    #

    peserta_list = (
        peserta_queryset
        .annotate(
            jabatan_order=peserta_jabatan_order()
        )
        .order_by(
            "kelompok_id",
            "jabatan_order",
            "id",
        )
    )

    # --------------------------------------------------------
    # TOTAL
    # --------------------------------------------------------

    semua_peserta = (
        Peserta.objects
        .filter(
            aktif=True,
        )
    )

    total_peserta = (
        semua_peserta.count()
    )

    total_aktif = (
        semua_peserta
        .filter(
            status_kemajuan=ACTIVE_STATUS
        )
        .count()
    )

    total_gugur = (
        semua_peserta
        .filter(
            status_kemajuan=GUGUR_STATUS
        )
        .count()
    )

    # --------------------------------------------------------
    # TOTAL KELOMPOK
    # --------------------------------------------------------

    total_kelompok = (
        semua_peserta
        .filter(
            kelompok__isnull=False
        )
        .values(
            "kelompok_id"
        )
        .distinct()
        .count()
    )

    # --------------------------------------------------------
    # JUMLAH HASIL FILTER
    # --------------------------------------------------------

    jumlah_hasil = (
        peserta_list.count()
    )

    context = {

        "setting": setting,

        # PESERTA
        "peserta": peserta_list,
        "peserta_list": peserta_list,

        # PENCARIAN
        "query": query,
        "status_filter": status_filter,
        "jumlah_hasil": jumlah_hasil,

        # STATISTIK
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
# FORMAT DOKUMEN
# ============================================================

def format_dokumen(request):

    setting = get_setting()

    format_list = (
        FormatDokumen.objects
        .filter(
            aktif=True,
        )
        .order_by(
            "-uploaded_at",
            "-id",
        )
    )

    context = {

        "setting": setting,

        "format_dokumen": format_list,
        "format_dokumen_list": format_list,

        "items": format_list,

    }

    return render(
        request,
        "praktikum/format_dokumen.html",
        context,
    )


# ============================================================
# LOGIN KELOMPOK
# ============================================================

def login_kelompok(request):

    if request.session.get(
        "kelompok_id"
    ):

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

    kelompok = get_kelompok_login(
        request
    )

    if not kelompok:

        messages.warning(
            request,
            "Silakan login terlebih dahulu.",
        )

        return redirect(
            "praktikum:login_kelompok"
        )

    setting = get_setting()

    # --------------------------------------------------------
    # ANGGOTA
    # --------------------------------------------------------
    #
    # Ketua -> Anggota -> ID
    #

    anggota = (
        Peserta.objects
        .filter(
            kelompok=kelompok,
            aktif=True,
            status_kemajuan=ACTIVE_STATUS,
        )
        .annotate(
            jabatan_order=peserta_jabatan_order()
        )
        .order_by(
            "jabatan_order",
            "id",
        )
    )

    # --------------------------------------------------------
    # LAPORAN
    # --------------------------------------------------------

    laporan = (
        LaporanMingguan.objects
        .filter(
            kelompok=kelompok
        )
        .select_related(
            "peserta",
            "acara",
        )
        .order_by(
            "-uploaded_at",
            "-id",
        )
    )

    # --------------------------------------------------------
    # DAILY MOM
    # --------------------------------------------------------

    daily_mom = (
        DailyMOM.objects
        .filter(
            kelompok=kelompok
        )
        .select_related(
            "acara",
            "dibuat_oleh",
        )
        .order_by(
            "-tanggal",
            "-id",
        )
    )

    # --------------------------------------------------------
    # PROGRESS ACARA
    # --------------------------------------------------------

    progress_acara = (
        ProgressAcara.objects
        .filter(
            kelompok=kelompok
        )
        .select_related(
            "acara",
        )
        .order_by(
            "acara__urutan",
            "acara__tanggal_mulai",
            "acara__id",
        )
    )

    # --------------------------------------------------------
    # FILE KELOMPOK
    # --------------------------------------------------------

    file_kelompok = (
        FileKelompok.objects
        .filter(
            kelompok=kelompok
        )
        .select_related(
            "acara",
            "uploaded_by",
        )
        .order_by(
            "-uploaded_at",
            "-id",
        )
    )

    # --------------------------------------------------------
    # LAPORAN LENGKAP
    # --------------------------------------------------------

    laporan_lengkap = (
        LaporanLengkap.objects
        .filter(
            kelompok=kelompok
        )
        .order_by(
            "-uploaded_at",
            "-id",
        )
    )

    # --------------------------------------------------------
    # KONSULTASI
    # --------------------------------------------------------

    konsultasi = (
        Konsultasi.objects
        .filter(
            kelompok=kelompok
        )
        .select_related(
            "peserta",
            "tujuan",
            "acara",
        )
        .order_by(
            "-dibuat",
            "-id",
        )
    )

    # --------------------------------------------------------
    # ACARA
    # --------------------------------------------------------

    acara_list = (
        Acara.objects
        .select_related(
            "penanggung_jawab",
        )
        .prefetch_related(
            Prefetch(
                "pembawa_acara",
                queryset=Staff.objects.filter(
                    aktif=True
                ),
            )
        )
        .order_by(
            "urutan",
            "tanggal_mulai",
            "id",
        )
    )

    # --------------------------------------------------------
    # MENTOR
    # --------------------------------------------------------

    mentor_list = (
        kelompok.mentor
        .filter(
            aktif=True
        )
        .order_by(
            "urutan",
            "id",
        )
    )

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

        "progress": getattr(
            kelompok,
            "progress_persen",
            0,
        ),

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

    peserta = get_peserta_login(
        request
    )

    if not peserta:

        messages.warning(
            request,
            "Akun peserta belum terhubung atau sudah tidak aktif.",
        )

        return redirect(
            "praktikum:login_kelompok"
        )

    setting = get_setting()

    kelompok = peserta.kelompok

    if not kelompok or not kelompok.aktif:

        messages.warning(
            request,
            "Kelompok peserta tidak aktif.",
        )

        return redirect(
            "praktikum:login_kelompok"
        )

    laporan = (
        LaporanMingguan.objects
        .filter(
            kelompok=kelompok,
            peserta=peserta,
        )
        .select_related(
            "acara",
        )
        .order_by(
            "-uploaded_at",
            "-id",
        )
    )

    absensi_list = (
        Absensi.objects
        .filter(
            peserta=peserta,
        )
        .select_related(
            "acara",
        )
        .order_by(
            "-acara__tanggal_mulai",
            "-id",
        )
    )

    file_list = (
        FileKelompok.objects
        .filter(
            kelompok=kelompok,
        )
        .select_related(
            "acara",
            "uploaded_by",
        )
        .order_by(
            "-uploaded_at",
            "-id",
        )
    )

    progress_list = (
        ProgressAcara.objects
        .filter(
            kelompok=kelompok,
        )
        .select_related(
            "acara",
        )
        .order_by(
            "acara__urutan",
            "acara__tanggal_mulai",
            "acara__id",
        )
    )

    konsultasi_list = (
        Konsultasi.objects
        .filter(
            kelompok=kelompok,
            peserta=peserta,
        )
        .select_related(
            "tujuan",
            "acara",
        )
        .order_by(
            "-dibuat",
            "-id",
        )
    )

    context = {

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

    kelompok = get_kelompok_login(
        request
    )

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

    judul = request.POST.get(
        "judul",
        "",
    ).strip()

    acara_id = request.POST.get(
        "acara",
        "",
    ).strip()

    peserta_id = request.POST.get(
        "peserta",
        "",
    ).strip()

    if not file_laporan:

        messages.error(
            request,
            "File laporan belum dipilih.",
        )

        return redirect(
            "praktikum:dashboard_kelompok"
        )

    if not acara_id:

        messages.error(
            request,
            "Acara laporan belum dipilih.",
        )

        return redirect(
            "praktikum:dashboard_kelompok"
        )

    if not peserta_id:

        messages.error(
            request,
            "Peserta pengunggah belum dipilih.",
        )

        return redirect(
            "praktikum:dashboard_kelompok"
        )

    peserta = get_object_or_404(
        Peserta,
        id=peserta_id,
        kelompok=kelompok,
        aktif=True,
        status_kemajuan=ACTIVE_STATUS,
    )

    acara = get_object_or_404(
        Acara,
        id=acara_id,
    )

    LaporanMingguan.objects.create(
        peserta=peserta,
        kelompok=kelompok,
        acara=acara,
        judul=(
            judul
            or "Laporan Mingguan"
        ),
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

    kelompok = get_kelompok_login(
        request
    )

    if not kelompok:

        messages.warning(
            request,
            "Silakan login terlebih dahulu.",
        )

        return redirect(
            "praktikum:login_kelompok"
        )

    laporan = get_object_or_404(
        LaporanMingguan,
        id=laporan_id,
        kelompok=kelompok,
    )

    if not laporan.file_revisi:

        raise Http404(
            "File revisi tidak ditemukan."
        )

    try:

        return FileResponse(
            laporan.file_revisi.open(
                "rb"
            ),
            as_attachment=True,
            filename=(
                laporan.file_revisi.name
                .split("/")[-1]
            ),
        )

    except Exception:

        raise Http404(
            "File revisi tidak dapat dibuka."
        )
